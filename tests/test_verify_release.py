"""Synthetic release evidence, including the observed b9/b10 ordering case."""

import hashlib
import importlib
import io
import json
import stat
import struct
import subprocess
from unittest.mock import patch
import warnings
import zipfile

import pytest

from tools import verify_release as v

SHA = "a" * 40
REPO = "synthetic/nuheat"
TAG = "v0.1.0b10"


def zipped(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return stream.getvalue()


class Evidence:
    def __init__(self):
        self.calls = []
        self.ref = {"object": {"type": "commit", "sha": SHA}}
        self.runs = [
            {
                "name": name,
                "head_sha": SHA,
                "id": i,
                "run_number": 1,
                "status": "completed",
                "conclusion": "success",
            }
            for i, name in enumerate(v.WORKFLOWS)
        ]
        self.source = {
            "tools/package.py": b"COMPONENT_FILES = {'manifest.json', 'climate.py'}\n",
            "custom_components/nuheat/manifest.json": json.dumps(
                {
                    "domain": "nuheat",
                    "version": "0.1.0b10",
                    "requirements": ["chemelex-nuheat==0.1.3"],
                }
            ).encode(),
            "custom_components/nuheat/climate.py": b"# synthetic runtime\n",
        }
        self.package = {
            k: val
            for k, val in self.source.items()
            if k.startswith("custom_components/")
        }
        self.release = {
            "tag_name": TAG,
            "draft": False,
            "prerelease": False,
            "assets": [
                {
                    "name": "nuheat-0.1.0b10.zip",
                    "browser_download_url": "https://github.com/asset",
                },
                {
                    "name": "nuheat-0.1.0b10.zip.sha256",
                    "browser_download_url": "https://github.com/checksum",
                },
            ],
        }
        self.latest = TAG
        self.listed = [
            {"tag_name": "v0.1.0b9", "draft": False, "prerelease": False},
            self.release,
        ]
        self.sdk = {
            "info": {"version": "0.1.3"},
            "urls": [{"packagetype": "bdist_wheel"}],
        }
        self.bad_checksum = False

    def api(self, path):
        self.calls.append(path)
        if "/git/ref/tags/" in path:
            return self.ref
        if "/git/tags/" in path:
            return {"object": {"type": "commit", "sha": SHA}}
        if "/releases/tags/" in path:
            return self.release
        if path.endswith("/releases/latest"):
            return {"tag_name": self.latest}
        if "/actions/runs?" in path:
            return {"workflow_runs": self.runs}
        if "/releases?" in path:
            return self.listed
        raise AssertionError("Unexpected synthetic API request")

    def download(self, url):
        self.calls.append(url)
        if url == "https://github.com/asset":
            return zipped(self.package)
        if url == "https://github.com/checksum":
            digest = (
                "0" * 64
                if self.bad_checksum
                else hashlib.sha256(zipped(self.package)).hexdigest()
            )
            return f"{digest}  nuheat-0.1.0b10.zip\n".encode()
        if url.startswith("https://codeload.github.com/"):
            return zipped({"repo-root/" + k: val for k, val in self.source.items()})
        if url.startswith("https://pypi.org/"):
            return json.dumps(self.sdk).encode()
        raise AssertionError("Unexpected synthetic download")


def run(evidence, **kwargs):
    return v.verify(REPO, TAG, SHA, remote=evidence, **kwargs)


def category(report):
    return report["checks"][-1].get("category")


def test_regular_release_with_b9_first_is_explicitly_installable():
    report, code = run(Evidence(), expect_latest=True)
    assert code == 0
    assert report["hacs"] == {
        "visible_without_beta": True,
        "beta_visibility_required": False,
        "first_regular_matches": False,
        "explicit_tag_source_verified": True,
        "ui_installation_tested": False,
    }
    assert run(Evidence(), require_default=True)[1] == 1


def test_prerelease_is_not_regular_only_visible():
    e = Evidence()
    e.release["prerelease"] = True
    report, code = run(e, kind="prerelease")
    assert code == 0
    assert report["hacs"]["beta_visibility_required"]
    assert not report["hacs"]["visible_without_beta"]
    assert category(run(e)[0]) == "release_kind"


def test_annotated_tag_and_wrong_commit():
    e = Evidence()
    e.ref = {"object": {"type": "tag", "sha": "b" * 40}}
    assert run(e)[1] == 0
    e.ref = {"object": {"type": "commit", "sha": "c" * 40}}
    assert category(run(e)[0]) == "tag_commit_mismatch"


def test_tag_cycle_is_rejected():
    e = Evidence()
    e.ref = {"object": {"type": "tag", "sha": SHA}}
    original = e.api
    e.api = lambda path: e.ref if "/git/tags/" in path else original(path)
    assert category(run(e)[0]) == "tag_cycle"


@pytest.mark.parametrize(
    ("status", "conclusion", "expected"),
    [
        ("in_progress", None, 2),
        ("completed", "failure", 1),
    ],
)
def test_latest_exact_commit_ci_required(status, conclusion, expected):
    e = Evidence()
    e.runs.append(
        {
            **e.runs[0],
            "id": 20,
            "run_number": 2,
            "status": status,
            "conclusion": conclusion,
        }
    )
    assert run(e)[1] == expected


def test_other_revision_ci_cannot_satisfy_required_checks():
    e = Evidence()
    e.runs[0]["head_sha"] = "b" * 40
    assert category(run(e)[0]) == "ci_missing"


@pytest.mark.parametrize(
    "mutation",
    [
        "checksum",
        "digest",
        "bytes",
        "extra",
        "version",
        "sdk_dev",
        "sdk_missing",
        "sdk_yanked",
        "draft",
        "latest",
    ],
)
def test_mismatched_evidence_fails(mutation):
    e = Evidence()
    if mutation == "checksum":
        e.bad_checksum = True
    elif mutation == "digest":
        e.release["assets"][0]["digest"] = "sha256:" + "0" * 64
    elif mutation == "bytes":
        e.package["custom_components/nuheat/climate.py"] = b"# stale\n"
    elif mutation == "extra":
        e.package["custom_components/nuheat/unexpected.json"] = b"{}"
    elif mutation in ("version", "sdk_dev"):
        m = json.loads(e.package["custom_components/nuheat/manifest.json"])
        m["version" if mutation == "version" else "requirements"] = (
            "0.1.0b9" if mutation == "version" else ["chemelex-nuheat==0.1.3.dev0"]
        )
        data = json.dumps(m).encode()
        e.package["custom_components/nuheat/manifest.json"] = data
        e.source["custom_components/nuheat/manifest.json"] = data
    elif mutation == "sdk_missing":
        e.sdk["urls"] = []
    elif mutation == "sdk_yanked":
        e.sdk["urls"][0]["yanked"] = True
    elif mutation == "draft":
        e.release["draft"] = True
    else:
        e.latest = "v0.1.0b9"
    assert run(e, expect_latest=True)[1] == 1


@pytest.mark.parametrize(
    "name", ["../escape", "/absolute", "a/./b", "a\\b", "C:/file", "a//b"]
)
def test_unsafe_zip_paths(name):
    with pytest.raises(v.Invalid, match="archive_path"):
        v.archive_members(zipped({name: b"data"}))


def test_duplicate_symlink_size_and_encrypted_archives(monkeypatch):
    stream = io.BytesIO()
    with warnings.catch_warnings(), zipfile.ZipFile(stream, "w") as z:
        warnings.simplefilter("ignore", UserWarning)
        z.writestr("same", b"one")
        z.writestr("same", b"two")
    with pytest.raises(v.Invalid, match="archive_path"):
        v.archive_members(stream.getvalue())
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as z:
        m = zipfile.ZipInfo("link")
        m.external_attr = (stat.S_IFLNK | 0o777) << 16
        z.writestr(m, "target")
    with pytest.raises(v.Invalid, match="archive_type"):
        v.archive_members(stream.getvalue())
    monkeypatch.setattr(v, "MAX_EXPANDED", 1)
    with pytest.raises(v.Invalid, match="archive_size"):
        v.archive_members(zipped({"large": b"123"}))


def test_missing_metadata_and_transport_errors_are_sanitized():
    e = Evidence()
    e.api = lambda path: (_ for _ in ()).throw(v.Incomplete("github_unavailable"))
    report, code = run(e)
    assert code == 2 and category(report) == "github_unavailable"
    with patch.object(
        v.subprocess,
        "run",
        side_effect=subprocess.TimeoutExpired("private-token-command", 30),
    ):
        with pytest.raises(v.Incomplete) as err:
            v.Remote().api("repos/synthetic/repo")
    assert "private-token" not in str(err.value)


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/a",
        "https://evil.invalid/a",
        "https://token@github.com/a",
        "https://github.com:444/a",
    ],
)
def test_redirect_policy_rejects_unapproved_hosts(url):
    with pytest.raises(v.Invalid, match="download_host"):
        v.PublicRedirect().redirect_request(None, None, 302, "redirect", {}, url)


def test_cli_help_and_invalid_input_are_read_only(capsys):
    with patch.object(
        v.subprocess, "run", side_effect=AssertionError("network attempted")
    ):
        with pytest.raises(SystemExit) as err:
            v.main(["--help"])
        assert err.value.code == 0
        report, code = v.verify("bad/repo/extra", TAG, SHA)
        assert code == 1 and category(report) == "repository"
    assert "NuHeat" in capsys.readouterr().out


def test_import_does_not_call_network_or_processes():
    with (
        patch("subprocess.run", side_effect=AssertionError("process attempted")),
        patch(
            "urllib.request.OpenerDirector.open",
            side_effect=AssertionError("network attempted"),
        ),
    ):
        importlib.reload(v)


def test_encrypted_malformed_and_member_count_limits(monkeypatch):
    data = bytearray(zipped({"file": b"data"}))
    # Mark the local header and central directory encrypted, without decrypting.
    struct.pack_into("<H", data, 6, 1)
    central = data.index(b"PK\x01\x02")
    struct.pack_into("<H", data, central + 8, 1)
    with pytest.raises(v.Invalid, match="archive_encrypted"):
        v.archive_members(data)
    with pytest.raises(v.Invalid, match="archive_invalid"):
        v.archive_members(b"not a zip")
    monkeypatch.setattr(v, "MAX_MEMBERS", 1)
    with pytest.raises(v.Invalid, match="archive_member_count"):
        v.archive_members(zipped({"one": b"", "two": b""}))


def test_download_limit_timeout_and_http_errors(monkeypatch):
    from types import SimpleNamespace
    from urllib.error import HTTPError
    from unittest.mock import MagicMock

    response = MagicMock()
    response.__enter__.return_value = response
    response.geturl.return_value = "https://github.com/asset"
    response.read1.side_effect = [b"1234", b""]
    opener = SimpleNamespace(open=lambda *a, **kw: response)
    monkeypatch.setattr(v, "build_opener", lambda *a: opener)
    monkeypatch.setattr(v, "MAX_DOWNLOAD", 3)
    with pytest.raises(v.Invalid, match="download_size"):
        v.Remote().download("https://github.com/asset")
    with patch.object(v.time, "monotonic", side_effect=[0, 31]):
        with pytest.raises(v.Incomplete, match="download_timeout"):
            v.Remote().download("https://github.com/asset")
    for code, error in [(404, v.Invalid), (503, v.Incomplete)]:
        opener.open = MagicMock(
            side_effect=HTTPError("private-url", code, "private-body", {}, None)
        )
        with pytest.raises(error) as exc:
            v.Remote().download("https://github.com/asset")
        assert "private" not in str(exc.value)


def test_missing_assets_and_unlisted_tag_fail():
    e = Evidence()
    e.release["assets"] = []
    assert category(run(e)[0]) == "assets_missing"
    e = Evidence()
    e.listed = []
    assert category(run(e)[0]) == "release_not_listed"


def test_corrupt_compressed_member_is_a_sanitized_failure():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("file", b"synthetic payload" * 10)
    data = bytearray(stream.getvalue())
    filename_length, extra_length = struct.unpack_from("<HH", data, 26)
    payload_start = 30 + filename_length + extra_length
    data[payload_start] = 7  # Invalid DEFLATE block type.
    with pytest.raises(v.Invalid, match="archive_invalid"):
        v.archive_members(data)


def test_remote_api_invalid_json_and_error_body_are_not_disclosed():
    for stdout, returncode in [
        (b"private malformed body", 0),
        (b"private response", 1),
    ]:
        with patch.object(
            v.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                [], returncode, stdout, b"private error"
            ),
        ):
            with pytest.raises(v.Incomplete) as exc:
                v.Remote().api("repos/synthetic/repo")
            assert "private" not in str(exc.value)
