"""Verify release preparation cannot package placeholders or unexpected files."""

import hashlib
import json
from pathlib import Path
import sys
import zipfile

import pytest

from tools import package


def candidate(tmp_path: Path, monkeypatch) -> Path:
    """Build only a synthetic candidate; never load distributed OAuth values."""
    monkeypatch.setattr(package, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["package.py"])
    component = tmp_path / "custom_components/nuheat"
    for name in package.COMPONENT_FILES:
        path = component / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}" if path.suffix == ".json" else "# synthetic\n")
    source = "CLIENT_ID = 'synthetic-client'\nCLIENT_SECRET = 'synthetic-secret'\n"
    (component / "community_oauth.py").write_text(source)
    manifest = {
        "domain": "nuheat",
        "version": "0.1.0b7",
        "requirements": ["chemelex-nuheat==0.1.2"],
        "issue_tracker": "https://example.invalid/issues",
        "documentation": "https://example.invalid/docs",
        "codeowners": ["@synthetic"],
    }
    (component / "manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "release-status.json").write_text(
        json.dumps(
            {
                "version": "0.1.0b7",
                "tag": "v0.1.0b7",
                "publish_allowed": False,
                "gates": {"synthetic": "passed"},
            }
        )
    )
    (tmp_path / "provenance.json").write_text(
        json.dumps(
            {
                "sha256": {},
                "setpoint_reconciliation_sha256": {},
                "distributed_community_registration": {
                    "sha256": hashlib.sha256(source.encode()).hexdigest()
                },
            }
        )
    )
    for name in (
        "README.md",
        "LICENSE.md",
        "RELEASE_NOTES.md",
        "hacs.json",
        "docs/AUTHENTICATION.md",
        "docs/VALIDATION.md",
        "docs/SETPOINT_RECONCILIATION.md",
        "docs/OAUTH_UNAUTHORIZED_CLIENT.md",
        "docs/PERMANENT_HOLD.md",
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "{}" if path.suffix == ".json" else "Synthetic packaging fixture\n"
        )
    return component


@pytest.mark.parametrize(
    ("client_id", "client_secret"), [("", ""), ("synthetic", ""), ("", "synthetic")]
)
def test_blank_community_credentials_are_rejected(tmp_path, client_id, client_secret):
    """Even an explicitly pinned blank template cannot produce a package."""
    source = f"CLIENT_ID = {client_id!r}\nCLIENT_SECRET = {client_secret!r}\n"
    (tmp_path / "community_oauth.py").write_text(source)
    with pytest.raises(AssertionError, match="placeholders"):
        package.validate_community_registration(
            tmp_path, hashlib.sha256(source.encode()).hexdigest()
        )


def test_registration_drift_is_rejected(tmp_path):
    """A registration must match the independently audited source fingerprint."""
    (tmp_path / "community_oauth.py").write_text(
        "CLIENT_ID = 'synthetic'\nCLIENT_SECRET = 'synthetic'\n"
    )
    with pytest.raises(AssertionError):
        package.validate_community_registration(tmp_path, "0" * 64)


def test_pending_publication_blocks_release_build(tmp_path, monkeypatch):
    """Preparation must not silently clear the maintainer's approval gate."""
    candidate(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "argv", ["package.py", "--release"])
    with pytest.raises(SystemExit, match="RELEASE BLOCKED"):
        package.main()
    assert not (tmp_path / "artifacts").exists()


def test_development_sdk_cannot_be_released_even_with_approval(tmp_path, monkeypatch):
    """A local wheel test must not authorize a publicly unavailable dependency."""
    component = candidate(tmp_path, monkeypatch)
    path = tmp_path / "release-status.json"
    status = json.loads(path.read_text())
    status["publish_allowed"] = True
    path.write_text(json.dumps(status))
    path = component / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["requirements"] = ["chemelex-nuheat==0.1.3.dev0"]
    path.write_text(json.dumps(manifest))
    path = tmp_path / "provenance.json"
    provenance = json.loads(path.read_text())
    provenance["api_resilience"] = {
        "status": "approved",
        "sdk_version": "0.1.3.dev0",
        "sha256": {},
    }
    path.write_text(json.dumps(provenance))
    monkeypatch.setattr(sys, "argv", ["package.py", "--release"])
    with pytest.raises(SystemExit, match="unpublished development SDK"):
        package.main()
    assert not (tmp_path / "artifacts").exists()


def test_unexpected_component_file_is_rejected(tmp_path, monkeypatch):
    """An accidentally copied private JSON file must not enter the ZIP."""
    component = candidate(tmp_path, monkeypatch)
    (component / "unexpected.json").write_text('{"synthetic": true}')
    with pytest.raises(AssertionError, match="Unexpected or missing"):
        package.main()
    assert not (tmp_path / "artifacts").exists()


def test_prepared_archive_has_only_allowlisted_files(tmp_path, monkeypatch):
    """A local review artifact includes the selected runtime and release notes."""
    candidate(tmp_path, monkeypatch)
    package.main()
    artifact = tmp_path / "artifacts/nuheat-0.1.0b7-UNRELEASED.zip"
    with zipfile.ZipFile(artifact) as archive:
        names = set(archive.namelist())
        assert len(names) == len(archive.namelist())
        assert {name for name in names if name.startswith("custom_components/")} == {
            "custom_components/nuheat/" + name for name in package.COMPONENT_FILES
        }
        assert "RELEASE_NOTES.md" in names
        assert (
            json.loads(archive.read("custom_components/nuheat/manifest.json"))[
                "version"
            ]
            == "0.1.0b7"
        )


def test_diagnostics_source_drift_is_rejected(tmp_path, monkeypatch):
    """The explicit new diagnostics file must retain its audited source bytes."""
    component = candidate(tmp_path, monkeypatch)
    path = tmp_path / "provenance.json"
    provenance = json.loads(path.read_text())
    provenance["diagnostics"] = {
        "sha256": {
            "custom_components/nuheat/diagnostics.py": hashlib.sha256(
                (component / "diagnostics.py").read_bytes()
            ).hexdigest()
        }
    }
    path.write_text(json.dumps(provenance))
    (component / "diagnostics.py").write_text("# unexpected diagnostics drift\n")
    with pytest.raises(AssertionError, match="diagnostics.py"):
        package.main()
    assert not (tmp_path / "artifacts").exists()


def test_manifest_and_candidate_version_must_match(tmp_path, monkeypatch):
    """Version metadata cannot silently describe a different candidate."""
    component = candidate(tmp_path, monkeypatch)
    path = component / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["version"] = "0.1.0b4"
    path.write_text(json.dumps(manifest))
    with pytest.raises(AssertionError):
        package.main()


def test_unapproved_oauth_candidate_cannot_build_release(tmp_path, monkeypatch):
    """Historical v5 approval cannot authorize publishing this local fix."""
    candidate(tmp_path, monkeypatch)
    status_path = tmp_path / "release-status.json"
    status = json.loads(status_path.read_text())
    status["publish_allowed"] = True
    status_path.write_text(json.dumps(status))
    provenance_path = tmp_path / "provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance["oauth_authorization_fix"] = {
        "status": "local review candidate; not released",
        "sha256": {},
    }
    provenance_path.write_text(json.dumps(provenance))
    monkeypatch.setattr(sys, "argv", ["package.py", "--release"])
    with pytest.raises(
        SystemExit, match="OAuth correction has no publication approval"
    ):
        package.main()
    assert not (tmp_path / "artifacts").exists()


def test_pending_permanent_hold_cannot_build_release(tmp_path, monkeypatch):
    candidate(tmp_path, monkeypatch)
    status_path = tmp_path / "release-status.json"
    status = json.loads(status_path.read_text())
    status["publish_allowed"] = True
    status_path.write_text(json.dumps(status))
    provenance_path = tmp_path / "provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance["permanent_hold_fix"] = {
        "status": "local review candidate",
        "sha256": {},
    }
    provenance_path.write_text(json.dumps(provenance))
    monkeypatch.setattr(sys, "argv", ["package.py", "--release"])
    with pytest.raises(
        SystemExit, match="Permanent Hold correction has no publication approval"
    ):
        package.main()


def test_pending_mode_candidate_blocks_release_build(tmp_path, monkeypatch):
    """A new local behavior cannot inherit an older release's approval."""
    candidate(tmp_path, monkeypatch)
    status_path = tmp_path / "release-status.json"
    status = json.loads(status_path.read_text())
    status["publish_allowed"] = True
    status_path.write_text(json.dumps(status))
    provenance_path = tmp_path / "provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance["bounded_mode_confirmation"] = {"status": "pending", "sha256": {}}
    provenance_path.write_text(json.dumps(provenance))
    monkeypatch.setattr(sys, "argv", ["package.py", "--release"])
    with pytest.raises(SystemExit, match="Bounded mode confirmation"):
        package.main()


def test_mode_candidate_source_drift_is_rejected(tmp_path, monkeypatch):
    """Candidate packaging retains exact source fingerprint enforcement."""
    candidate(tmp_path, monkeypatch)
    provenance_path = tmp_path / "provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance["bounded_mode_confirmation"] = {
        "status": "pending",
        "sha256": {"custom_components/nuheat/climate.py": "0" * 64},
    }
    provenance_path.write_text(json.dumps(provenance))
    with pytest.raises(AssertionError):
        package.main()
