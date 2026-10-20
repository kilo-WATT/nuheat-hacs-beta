"""Audit candidate files against a private, external baseline without printing it."""

import argparse
import ast
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-baseline", type=Path, required=True)
    args = parser.parse_args()
    baseline = args.private_baseline.resolve()
    if baseline.is_relative_to(ROOT):
        raise SystemExit("Private baseline must remain outside the beta repository")
    private = baseline.read_text()
    values = set(re.findall(r"`([^`]+)`", private))
    # Public schema enums and product model names are not user identifiers.
    values -= {"config_entry", "nVent Signature"}
    values = {v for v in values if len(v) >= 6}
    credential_source = baseline.parent / "approved_shared_client.py"
    if credential_source.exists():
        for node in ast.parse(credential_source.read_text(encoding="utf-8")).body:
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "CLIENT_SECRET"
            ):
                values.add(ast.literal_eval(node.value))
    files = (
        subprocess.check_output(["git", "ls-files", "--cached", "-z"], cwd=ROOT)
        .decode()
        .split("\0")
    )
    findings = []
    for name in filter(None, files):
        content = (ROOT / name).read_text(errors="replace")
        if any(value in content for value in values):
            findings.append(name)
    for artifact in (ROOT / "artifacts").glob("*.zip"):
        with zipfile.ZipFile(artifact) as archive:
            for name in archive.namelist():
                content = archive.read(name).decode(errors="replace")
                if any(value in content for value in values):
                    findings.append(f"ZIP:{name}")
    if findings:
        raise SystemExit("Private-value matches found in: " + ", ".join(findings))
    print(
        f"Privacy audit passed for {len(list(filter(None, files)))} staged files and local ZIPs. No private values printed."
    )


if __name__ == "__main__":
    main()
