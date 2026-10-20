"""Build an allowlisted local HACS candidate; fail closed for release builds."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


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
            "RELEASE BLOCKED: authentication/migration/transition gates have not all passed"
        )
    component = ROOT / "custom_components/nuheat"
    manifest = json.loads((component / "manifest.json").read_text())
    assert manifest["domain"] == "nuheat"
    assert manifest["requirements"] == ["chemelex-nuheat==0.1.1"]
    assert all(
        key in manifest
        for key in ("version", "issue_tracker", "documentation", "codeowners")
    )
    provenance = json.loads((ROOT / "provenance.json").read_text())
    for relative, digest in provenance["sha256"].items():
        if relative == "custom_components/nuheat/climate.py":
            expected = (
                ROOT / "tests/fixtures/core_candidate/nuheat/climate.py"
            ).read_bytes()
            assert hashlib.sha256(expected).hexdigest() == digest
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
            actual = (ROOT / relative).read_text().replace(
                "from .oauth_setup import async_ensure_community_credentials\n", ""
            ).replace(
                "            await async_ensure_community_credentials(self.hass)\n", ""
            )
            assert actual == original.decode(), relative
        elif relative == "custom_components/nuheat/strings.json":
            original = (
                ROOT / "tests/fixtures/core_candidate/nuheat/strings.json"
            ).read_bytes()
            assert hashlib.sha256(original).hexdigest() == digest
            actual = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            assert actual["issues"].pop("beta_handoff_failed")
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
        )
    ]
    paths += [
        p for p in component.rglob("*") if p.is_file() and p.suffix in (".py", ".json")
    ]
    paths += [ROOT / "docs/AUTHENTICATION.md", ROOT / "docs/VALIDATION.md"]
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
