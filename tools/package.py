"""Build an allowlisted local HACS candidate; fail closed for release builds."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
COMPONENT_FILES = {
    "__init__.py",
    "account_identity.py",
    "application_credentials.py",
    "behavior.py",
    "climate.py",
    "community_oauth.py",
    "config_flow.py",
    "const.py",
    "coordinator.py",
    "diagnostics.py",
    "core-handoff.json",
    "core_handoff.py",
    "manifest.json",
    "migration.py",
    "oauth_setup.py",
    "registry_migration.py",
    "strings.json",
    "services.yaml",
    "translations/en.json",
}


def validate_community_registration(component: Path, expected_digest: str) -> None:
    """Reject blank placeholders or drift from the audited public registration."""
    source = (component / "community_oauth.py").read_bytes()
    assert hashlib.sha256(source).hexdigest() == expected_digest
    values = {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in ast.parse(source).body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in {"CLIENT_ID", "CLIENT_SECRET"}
    }
    assert all(
        isinstance(values.get(key), str) and values[key].strip()
        for key in ("CLIENT_ID", "CLIENT_SECRET")
    ), "Community OAuth placeholders cannot be packaged"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()
    status = json.loads((ROOT / "release-status.json").read_text())
    if args.release and (
        not status["publish_allowed"]
        or any(state != "passed" for state in status["gates"].values())
    ):
        raise SystemExit(
            "RELEASE BLOCKED: publication approval or validation gates are pending"
        )
    component = ROOT / "custom_components/nuheat"
    manifest = json.loads((component / "manifest.json").read_text())
    provenance = json.loads((ROOT / "provenance.json").read_text())
    resilience = provenance.get("api_resilience", {})
    sdk_version = resilience.get("sdk_version", "0.1.2")
    assert manifest["version"] == status["version"]
    assert status["tag"] == "v" + manifest["version"]
    assert manifest["domain"] == "nuheat"
    assert manifest["requirements"] == [f"chemelex-nuheat=={sdk_version}"]
    assert all(
        key in manifest
        for key in ("version", "issue_tracker", "documentation", "codeowners")
    )
    if args.release and resilience and resilience.get("status") != "approved":
        raise SystemExit("RELEASE BLOCKED: API resilience has no publication approval")
    if args.release and "dev" in sdk_version:
        raise SystemExit("RELEASE BLOCKED: unpublished development SDK dependency")
    validate_community_registration(
        component, provenance["distributed_community_registration"]["sha256"]
    )
    actual_files = {
        path.relative_to(component).as_posix()
        for path in component.rglob("*")
        if path.is_file() and path.suffix in (".py", ".json", ".yaml")
    }
    assert actual_files == COMPONENT_FILES, "Unexpected or missing component files"
    permanent_candidate = provenance.get("permanent_hold_fix", {})
    if (
        args.release
        and permanent_candidate
        and permanent_candidate.get("status") != "approved"
    ):
        raise SystemExit(
            "RELEASE BLOCKED: Permanent Hold correction has no publication approval"
        )
    mode_candidate = provenance.get("bounded_mode_confirmation", {})
    if args.release and mode_candidate and mode_candidate.get("status") != "approved":
        raise SystemExit(
            "RELEASE BLOCKED: Bounded mode confirmation has no publication approval"
        )
    permanent_fixes = {
        **permanent_candidate.get("sha256", {}),
        **mode_candidate.get("sha256", {}),
        **resilience.get("sha256", {}),
    }
    for relative, expected_digest in permanent_fixes.items():
        assert (
            hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            == expected_digest
        )
    oauth_candidate = provenance.get("oauth_authorization_fix", {})
    if args.release and oauth_candidate and oauth_candidate.get("status") != "approved":
        raise SystemExit(
            "RELEASE BLOCKED: OAuth correction has no publication approval"
        )
    oauth_fixes = {**oauth_candidate.get("sha256", {}), **resilience.get("sha256", {})}
    for relative, expected_digest in oauth_fixes.items():
        assert (
            hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            == expected_digest
        )
    for relative, expected_digest in (
        provenance.get("diagnostics", {}).get("sha256", {}).items()
    ):
        assert (
            hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            == expected_digest
        ), relative
    for relative, digest in provenance["sha256"].items():
        if relative in permanent_fixes:
            original = (
                ROOT / "tests/fixtures/core_candidate/nuheat" / Path(relative).name
            )
            assert hashlib.sha256(original.read_bytes()).hexdigest() == digest
            continue
        if relative in oauth_fixes:
            original = (
                ROOT / "tests/fixtures/core_candidate/nuheat" / Path(relative).name
            )
            assert hashlib.sha256(original.read_bytes()).hexdigest() == digest
            continue
        if relative in provenance["setpoint_reconciliation_sha256"]:
            name = Path(relative).name
            original = (
                ROOT / "tests/fixtures/core_candidate/nuheat" / name
            ).read_bytes()
            assert hashlib.sha256(original).hexdigest() == digest
            expected = (
                ROOT / "tests/fixtures/setpoint_candidate/nuheat" / name
            ).read_bytes()
            assert (
                hashlib.sha256(expected).hexdigest()
                == provenance["setpoint_reconciliation_sha256"][relative]
            )
            if name == "climate.py":
                for old, new in (
                    (b"native_temperature_unit", b"temperature_unit"),
                    (b"native_current_temperature", b"current_temperature"),
                    (b"native_target_temperature", b"target_temperature"),
                ):
                    expected = expected.replace(old, new)
            assert (ROOT / relative).read_text() == expected.decode(), relative
        elif relative == "custom_components/nuheat/__init__.py":
            original = (
                ROOT / "tests/fixtures/core_candidate/nuheat/__init__.py"
            ).read_bytes()
            assert hashlib.sha256(original).hexdigest() == digest
            guard = '    if hass.data.get("nuheat_beta_core_handoff_pending"):\n        raise ConfigEntryNotReady("Switching NuHeat to verified Core")\n'
            actual = (ROOT / relative).read_text().replace(guard, "")
            assert actual.startswith(
                original.decode().rstrip() + "\n\n\nasync def async_setup("
            )
        elif relative == "custom_components/nuheat/config_flow.py":
            original = (
                ROOT / "tests/fixtures/core_candidate/nuheat/config_flow.py"
            ).read_bytes()
            assert hashlib.sha256(original).hexdigest() == digest
            actual = (
                (ROOT / relative)
                .read_text()
                .replace(
                    "from .oauth_setup import async_ensure_community_credentials\n", ""
                )
                .replace(
                    "            await async_ensure_community_credentials(self.hass)\n",
                    "",
                )
            )
            assert actual == original.decode(), relative
        elif relative == "custom_components/nuheat/strings.json":
            original = (
                ROOT / "tests/fixtures/core_candidate/nuheat/strings.json"
            ).read_bytes()
            assert hashlib.sha256(original).hexdigest() == digest
            actual = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            assert actual["issues"].pop("beta_handoff_failed")
            assert actual["config"]["abort"].pop("my_required")
            assert actual == json.loads(original)
        elif relative.startswith("custom_components/") and not relative.endswith(
            "manifest.json"
        ):
            assert (
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
            ), relative
    translations = (component / "translations/en.json").read_text()
    assert "[%key:" not in translations
    json.loads(translations)
    paths = [
        ROOT / name
        for name in (
            "hacs.json",
            "README.md",
            "LICENSE.md",
            "provenance.json",
            "release-status.json",
            "RELEASE_NOTES.md",
        )
    ]
    paths += [component / name for name in COMPONENT_FILES]
    paths += [
        ROOT / "docs/AUTHENTICATION.md",
        ROOT / "docs/VALIDATION.md",
        ROOT / "docs/SETPOINT_RECONCILIATION.md",
        ROOT / "docs/OAUTH_UNAUTHORIZED_CLIENT.md",
        ROOT / "docs/PERMANENT_HOLD.md",
    ]
    suffix = ".zip" if args.release else "-UNRELEASED.zip"
    artifact = ROOT / "artifacts" / ("nuheat-" + manifest["version"] + suffix)
    artifact.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(artifact, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            archive.write(path, path.relative_to(ROOT).as_posix())
    checksum = hashlib.sha256(artifact.read_bytes()).hexdigest()
    artifact.with_suffix(".zip.sha256").write_text(f"{checksum}  {artifact.name}\n")
    print(f"Local artifact: {artifact}\nSHA256: {checksum}")


if __name__ == "__main__":
    main()
