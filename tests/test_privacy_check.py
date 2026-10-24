"""Private markers remain inside temporary synthetic repositories and memory."""

import hashlib
import importlib
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest

from tools import privacy_check as p
from .test_verify_release import zipped

PRIVATE = "synthetic-account-private-value"
PUBLIC_ID = "synthetic-community-client-id"
PUBLIC_SECRET = "synthetic-public-registration-secret"


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)


@pytest.fixture
def candidate(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    component = root / p.REGISTRATION
    component.parent.mkdir(parents=True)
    component.write_text(
        f"CLIENT_ID = {PUBLIC_ID!r}\nCLIENT_SECRET = {PUBLIC_SECRET!r}\n"
    )
    (root / "provenance.json").write_text(
        json.dumps(
            {
                "distributed_community_registration": {
                    "sha256": hashlib.sha256(component.read_bytes()).hexdigest()
                }
            }
        )
    )
    (root / "tracked.txt").write_text("safe indexed bytes")
    (root / ".gitignore").write_text("ignored/\n")
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps([PRIVATE, PUBLIC_SECRET]))
    git(root, "add", ".")
    return root, baseline


def audit(candidate, **kwargs):
    return p.audit(*candidate, **kwargs)


def test_working_tree_and_index_are_distinct(candidate):
    root, _ = candidate
    (root / "tracked.txt").write_text(PRIVATE)
    before = git(root, "diff", "--cached").stdout
    working, code = audit(candidate)
    assert code == 1 and working["findings"] == {"file_content": 1}
    staged, code = audit(candidate, view="staged")
    assert code == 0 and staged["view"] == "staged"
    assert before == git(root, "diff", "--cached").stdout
    git(root, "add", "tracked.txt")
    assert audit(candidate, view="staged")[1] == 1
    (root / "tracked.txt").write_text("safe working tree")
    assert audit(candidate)[1] == 0
    assert audit(candidate, view="staged")[1] == 1


def test_untracked_deleted_and_ignored_paths(candidate):
    root, _ = candidate
    (root / "tracked.txt").unlink()
    (root / "ignored").mkdir()
    (root / "ignored/private.txt").write_text(PRIVATE)
    report, code = audit(candidate)
    assert code == 0 and report["deleted_paths_skipped"] == 1
    (root / "new.txt").write_text(PRIVATE)
    assert audit(candidate)[1] == 1
    assert audit(candidate, view="staged")[1] == 0


@pytest.mark.parametrize("content", ["[]", "{}", "not json", '[""]', "[1]", "[null]"])
def test_invalid_and_empty_baselines_fail_closed(candidate, content):
    _, baseline = candidate
    baseline.write_text(content)
    report, code = audit(candidate)
    assert code == 2 and report["status"] == "incomplete"


def test_internal_missing_and_markdown_baselines(candidate, tmp_path):
    root, _ = candidate
    inside = root / "private.json"
    inside.write_text(json.dumps([PRIVATE]))
    assert p.audit(root, inside)[0]["category"] == "baseline_inside_repository"
    inside.unlink()
    assert p.audit(root, tmp_path / "missing.json")[1] == 2
    legacy = tmp_path / "baseline.md"
    legacy.write_text(f"Synthetic known value: `{PRIVATE}` and `config_entry`.")
    report, code = p.audit(root, legacy)
    assert code == 0 and report["private_values_checked"] == 1


@pytest.mark.parametrize(
    "mutation", ["missing", "changed", "copied", "private_in_approved"]
)
def test_registration_exemption_is_exact(candidate, mutation):
    root, _ = candidate
    source = root / p.REGISTRATION
    if mutation == "missing":
        (root / "provenance.json").unlink()
    elif mutation == "changed":
        source.write_text(source.read_text() + "# drift\n")
    elif mutation == "copied":
        (root / "unexpected.txt").write_text(PUBLIC_SECRET)
    else:
        source.write_text(source.read_text() + f"# {PRIVATE}\n")
        (root / "provenance.json").write_text(
            json.dumps(
                {
                    "distributed_community_registration": {
                        "sha256": hashlib.sha256(source.read_bytes()).hexdigest()
                    }
                }
            )
        )
    report, code = audit(candidate)
    assert code != 0
    assert PRIVATE not in json.dumps(report) and PUBLIC_SECRET not in json.dumps(report)


def test_zip_private_values_names_and_provenance(candidate, tmp_path):
    root, _ = candidate
    files = {
        p.REGISTRATION: (root / p.REGISTRATION).read_bytes(),
        "provenance.json": (root / "provenance.json").read_bytes(),
    }
    archive = tmp_path / "candidate.zip"
    archive.write_bytes(zipped(files))
    assert audit(candidate, archives=[archive])[1] == 0
    files[PRIVATE + ".txt"] = PRIVATE.encode()
    files["unexpected-copy.txt"] = PUBLIC_SECRET.encode()
    archive.write_bytes(zipped(files))
    report, code = audit(candidate, archives=[archive])
    assert code == 1 and report["findings"]["archive_name"] == 1
    assert report["findings"]["archive_content"] == 2
    assert PRIVATE not in json.dumps(report) and str(tmp_path) not in json.dumps(report)
    files.pop(PRIVATE + ".txt")
    files.pop("unexpected-copy.txt")
    files["provenance.json"] = b"{}"
    archive.write_bytes(zipped(files))
    assert audit(candidate, archives=[archive])[1] == 1
    archive.write_bytes(b"malformed")
    assert audit(candidate, archives=[archive])[1] == 2


def test_private_filename_and_cli_do_not_print_matches(candidate, monkeypatch, capsys):
    root, baseline = candidate
    (root / (PRIVATE + ".txt")).write_text("safe bytes")
    monkeypatch.setattr(p, "ROOT", root)
    assert p.main(["--private-baseline", str(baseline)]) == 1
    out = capsys.readouterr()
    assert PRIVATE not in out.out + out.err
    assert str(root) not in out.out + out.err
    assert json.loads(out.out)["findings"] == {"file_name": 1}


def test_import_help_and_git_errors_are_side_effect_free(candidate, capsys):
    with (
        patch("subprocess.run", side_effect=AssertionError("spawned")),
        patch.object(Path, "write_bytes", side_effect=AssertionError("wrote")),
    ):
        importlib.reload(p)
        with pytest.raises(SystemExit) as exc:
            p.main(["--help"])
        assert exc.value.code == 0
    with patch.object(p.subprocess, "run", side_effect=OSError("private filename")):
        report, code = audit(candidate)
        assert code == 2 and "private filename" not in json.dumps(report)
    assert "Audit" in capsys.readouterr().out
