"""Read-only, version-independent verification of a published NuHeat release."""

import argparse
import ast
import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import stat
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import zipfile
import zlib

MAX_DOWNLOAD = 32 * 1024 * 1024
MAX_EXPANDED = 128 * 1024 * 1024
MAX_MEMBERS = 5000
WORKFLOWS = (
    "Validate unpublished NuHeat candidate",
    "Validate NuHeat specifications",
)
HOSTS = {
    "github.com",
    "api.github.com",
    "codeload.github.com",
    "release-assets.githubusercontent.com",
    "objects.githubusercontent.com",
    "pypi.org",
    "files.pythonhosted.org",
}


class Invalid(Exception):
    """Confirmed invalid evidence; message is a safe fixed category."""


class Incomplete(Exception):
    """Unavailable evidence; message is a safe fixed category."""


def require(condition, category):
    """Reject evidence without including its contents in the error."""
    if not condition:
        raise Invalid(category)


def safe_url(url):
    """Permit only public distribution hosts and no user information."""
    parsed = urlsplit(url)
    require(
        parsed.scheme == "https"
        and parsed.hostname in HOSTS
        and parsed.username is None
        and parsed.password is None
        and parsed.port in (None, 443),
        "download_host",
    )


class PublicRedirect(HTTPRedirectHandler):
    """Check each redirect before sending any request."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Remote:
    """Bounded public reads; gh supplies its own existing authentication."""

    def api(self, path):
        try:
            result = subprocess.run(
                ["gh", "api", "--method", "GET", path],
                capture_output=True,
                timeout=30,
                check=False,
            )
        except OSError, subprocess.TimeoutExpired:
            raise Incomplete("github_unavailable") from None
        if result.returncode or len(result.stdout) > MAX_DOWNLOAD:
            raise Incomplete("github_unavailable")
        try:
            return json.loads(result.stdout)
        except ValueError, UnicodeError:
            raise Incomplete("github_response") from None

    def download(self, url):
        safe_url(url)
        deadline = time.monotonic() + 30
        try:
            request = Request(url, headers={"User-Agent": "NuHeat-release-verifier"})
            with build_opener(PublicRedirect()).open(request, timeout=30) as response:
                safe_url(response.geturl())
                chunks = []
                length = 0
                while True:
                    if time.monotonic() >= deadline:
                        raise Incomplete("download_timeout")
                    chunk = response.read1(min(65536, MAX_DOWNLOAD + 1 - length))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    length += len(chunk)
                    require(length <= MAX_DOWNLOAD, "download_size")
                data = b"".join(chunks)
        except HTTPError as err:
            if err.code == 404:
                raise Invalid("remote_not_found") from None
            raise Incomplete("download_unavailable") from None
        except OSError, URLError, TimeoutError:
            raise Incomplete("download_unavailable") from None
        require(len(data) <= MAX_DOWNLOAD, "download_size")
        return data


def archive_members(data):
    """Read bounded regular files without extracting or executing anything."""
    require(len(data) <= MAX_DOWNLOAD, "download_size")
    result = {}
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            require(len(members) <= MAX_MEMBERS, "archive_member_count")
            require(sum(m.file_size for m in members) <= MAX_EXPANDED, "archive_size")
            seen = set()
            for member in members:
                name = member.filename
                path = PurePosixPath(name)
                require(
                    name not in seen
                    and not name.startswith("/")
                    and "\\" not in name
                    and ":" not in name
                    and all(
                        p not in ("", ".", "..") for p in name.rstrip("/").split("/")
                    )
                    and not path.is_absolute(),
                    "archive_path",
                )
                seen.add(name)
                kind = stat.S_IFMT(member.external_attr >> 16)
                require(kind in (0, stat.S_IFREG, stat.S_IFDIR), "archive_type")
                require(not member.flag_bits & 1, "archive_encrypted")
                if not member.is_dir():
                    result[name] = archive.read(member)
    except (
        zipfile.BadZipFile,
        RuntimeError,
        NotImplementedError,
        OSError,
        EOFError,
        zlib.error,
    ):
        raise Invalid("archive_invalid") from None
    return result


def tag_commit(remote, repo, tag):
    """Resolve a lightweight or annotated tag with a finite depth."""
    obj = remote.api(f"repos/{repo}/git/ref/tags/{quote(tag, safe='')}")["object"]
    seen = set()
    for _ in range(8):
        sha = obj["sha"]
        require(bool(re.fullmatch(r"[0-9a-f]{40}", sha)), "tag_object")
        require(sha not in seen, "tag_cycle")
        seen.add(sha)
        if obj["type"] == "commit":
            return sha
        require(obj["type"] == "tag", "tag_object")
        obj = remote.api(f"repos/{repo}/git/tags/{sha}")["object"]
    raise Invalid("tag_depth")


def source_members(data):
    """Remove exactly one common source-archive root."""
    members = archive_members(data)
    roots = {n.split("/", 1)[0] for n in members}
    require(len(roots) == 1 and all("/" in n for n in members), "source_root")
    return {n.split("/", 1)[1]: value for n, value in members.items()}


def runtime_allowlist(source):
    """Read the selected tag's literal allowlist without importing its code."""
    tree = ast.parse(source)
    assignments = [
        n
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == "COMPONENT_FILES" for t in n.targets
        )
    ]
    require(len(assignments) == 1, "runtime_allowlist")
    names = ast.literal_eval(assignments[0].value)
    require(isinstance(names, (set, list, tuple)) and bool(names), "runtime_allowlist")
    require(
        all(
            isinstance(n, str)
            and not n.startswith("/")
            and all(p not in ("", ".", "..") for p in n.split("/"))
            and "\\" not in n
            and ":" not in n
            for n in names
        ),
        "runtime_allowlist",
    )
    return {"custom_components/nuheat/" + n for n in names}


def ci_evidence(remote, repo, commit, workflows):
    runs = remote.api(f"repos/{repo}/actions/runs?head_sha={commit}&per_page=100")[
        "workflow_runs"
    ]
    evidence = []
    for workflow in workflows:
        matching = [
            r for r in runs if r.get("head_sha") == commit and r.get("name") == workflow
        ]
        if not matching:
            raise Incomplete("ci_missing")
        newest = max(matching, key=lambda r: (r.get("run_number", 0), r["id"]))
        if newest.get("status") != "completed":
            raise Incomplete("ci_pending")
        require(newest.get("conclusion") == "success", "ci_failed")
        evidence.append({"workflow": workflow, "run_id": newest["id"]})
    return evidence


def verify(
    repo,
    tag,
    expected_commit,
    *,
    kind="regular",
    expect_latest=False,
    require_default=False,
    workflows=WORKFLOWS,
    remote=None,
):
    """Return safe JSON evidence and an exit code; never modify local or remote state."""
    remote = remote or Remote()
    report = {"schema_version": 1, "checks": [], "read_only": True}
    check = "inputs"

    def passed(name, **details):
        report["checks"].append({"check": name, "status": "passed", **details})

    try:
        require(
            bool(re.fullmatch(r"[A-Za-z0-9][\w.-]*/[A-Za-z0-9][\w.-]*", repo)),
            "repository",
        )
        require(
            bool(re.fullmatch(r"[A-Za-z0-9][\w./-]*", tag)) and ".." not in tag, "tag"
        )
        require(bool(re.fullmatch(r"[0-9a-f]{40}", expected_commit)), "expected_commit")
        require(kind in ("regular", "prerelease") and bool(workflows), "policy")
        check = "tag"
        commit = tag_commit(remote, repo, tag)
        require(commit == expected_commit, "tag_commit_mismatch")
        passed(check, commit=commit)
        check = "publication"
        release = remote.api(f"repos/{repo}/releases/tags/{quote(tag, safe='')}")
        require(release["tag_name"] == tag and not release["draft"], "release_identity")
        require(release["prerelease"] == (kind == "prerelease"), "release_kind")
        latest = remote.api(f"repos/{repo}/releases/latest")["tag_name"]
        require(not expect_latest or latest == tag, "release_latest")
        passed(check, prerelease=release["prerelease"], latest_matches=latest == tag)
        check = "ci"
        passed(check, runs=ci_evidence(remote, repo, commit, workflows))
        check = "package"
        version = tag.removeprefix("v")
        filename = f"nuheat-{version}.zip"
        assets = {a["name"]: a for a in release["assets"]}
        require(
            len(assets) == len(release["assets"])
            and filename in assets
            and filename + ".sha256" in assets,
            "assets_missing",
        )
        data = remote.download(assets[filename]["browser_download_url"])
        digest = hashlib.sha256(data).hexdigest()
        sidecar = (
            remote.download(assets[filename + ".sha256"]["browser_download_url"])
            .decode("ascii")
            .split()
        )
        require(
            sidecar == [digest, filename] or sidecar == [digest, "*" + filename],
            "checksum",
        )
        api_digest = assets[filename].get("digest")
        require(api_digest is None or api_digest == "sha256:" + digest, "asset_digest")
        packaged = archive_members(data)
        source = source_members(
            remote.download(f"https://codeload.github.com/{repo}/zip/{commit}")
        )
        allowed = runtime_allowlist(source["tools/package.py"])
        require(
            {n for n in source if n.startswith("custom_components/")} == allowed,
            "source_runtime_members",
        )
        actual = {n for n in packaged if n.startswith("custom_components/")}
        require(actual == allowed, "runtime_members")
        require(
            all(n in source and source[n] == value for n, value in packaged.items()),
            "source_mismatch",
        )
        manifest = json.loads(packaged["custom_components/nuheat/manifest.json"])
        require(
            manifest["domain"] == "nuheat" and manifest["version"] == version,
            "manifest",
        )
        passed(check, sha256=digest, runtime_files=len(actual))
        check = "sdk"
        pins = manifest["requirements"]
        require(isinstance(pins, list) and len(pins) == 1, "sdk_pin")
        match = re.fullmatch(r"chemelex-nuheat==(\d+\.\d+\.\d+)", pins[0])
        require(match is not None, "sdk_pin")
        sdk = match[1]
        metadata = json.loads(
            remote.download(f"https://pypi.org/pypi/chemelex-nuheat/{sdk}/json")
        )
        require(
            metadata["info"]["version"] == sdk
            and any(
                not f.get("yanked", False) and f.get("packagetype") == "bdist_wheel"
                for f in metadata["urls"]
            ),
            "sdk_unavailable",
        )
        passed(check, version=sdk)
        check = "hacs_visibility"
        releases = []
        for page in range(1, 11):
            batch = remote.api(f"repos/{repo}/releases?per_page=100&page={page}")
            releases.extend(batch)
            if any(r["tag_name"] == tag for r in releases) or len(batch) < 100:
                break
        visible = [
            r["tag_name"] for r in releases if not r["draft"] and not r["prerelease"]
        ]
        require(
            any(r["tag_name"] == tag and not r["draft"] for r in releases),
            "release_not_listed",
        )
        default_matches = bool(visible) and visible[0] == tag
        report["hacs"] = {
            "visible_without_beta": tag in visible,
            "beta_visibility_required": release["prerelease"],
            "first_regular_matches": default_matches,
            "explicit_tag_source_verified": True,
            "ui_installation_tested": False,
        }
        require(not require_default or default_matches, "default_selection_mismatch")
        passed(check, default_selection_advisory=not default_matches)
    except Invalid as err:
        report["checks"].append(
            {"check": check, "status": "failed", "category": str(err)}
        )
        return report, 1
    except Incomplete as err:
        report["checks"].append(
            {"check": check, "status": "incomplete", "category": str(err)}
        )
        return report, 2
    except KeyError, TypeError, ValueError, UnicodeError, SyntaxError, RecursionError:
        report["checks"].append(
            {"check": check, "status": "failed", "category": "invalid_evidence"}
        )
        return report, 1
    return report, 0


def main(argv=None):
    """Print JSON only; no reports are written automatically."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--kind", choices=("regular", "prerelease"), default="regular")
    parser.add_argument("--expect-latest", action="store_true")
    parser.add_argument("--require-default", action="store_true")
    parser.add_argument("--workflow", action="append")
    args = parser.parse_args(argv)
    report, code = verify(
        args.repo,
        args.tag,
        args.expected_commit,
        kind=args.kind,
        expect_latest=args.expect_latest,
        require_default=args.require_default,
        workflows=args.workflow or WORKFLOWS,
    )
    print(json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
