"""Audit explicit Git views and selected ZIPs against an external private baseline."""

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

try:
    from tools import verify_release as release_checks
except ModuleNotFoundError:
    import verify_release as release_checks

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = "custom_components/nuheat/community_oauth.py"
MAX_FILE = 32 * 1024 * 1024


class AuditError(Exception):
    """A fixed safe error category, never a filename or private value."""


def git(root, *args):
    """Read Git without shell interpolation or printing stderr."""
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, timeout=30, check=False
        )
    except OSError, subprocess.TimeoutExpired:
        raise AuditError("git_unavailable") from None
    if result.returncode or len(result.stdout) > MAX_FILE:
        raise AuditError("git_read_failed")
    return result.stdout


def bounded_file(path):
    """Do not load unbounded local input."""
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_FILE + 1)
    except OSError:
        raise AuditError("file_unavailable") from None
    if len(data) > MAX_FILE:
        raise AuditError("file_too_large")
    return data


def baseline_values(path, root):
    """Support explicit JSON strings or the original Markdown baseline."""
    path = path.resolve()
    if path.is_relative_to(root):
        raise AuditError("baseline_inside_repository")
    try:
        text = bounded_file(path).decode("utf-8")
        if path.suffix.lower() == ".json":
            values = json.loads(text)
            if not isinstance(values, list) or not all(
                isinstance(v, str) and v.strip() for v in values
            ):
                raise AuditError("baseline_format")
            values = set(values)
        else:
            values = {
                v
                for v in re.findall(r"`([^`]+)`", text)
                if len(v) >= 6 and v not in {"config_entry", "nVent Signature"}
            }
    except ValueError, UnicodeError:
        raise AuditError("baseline_format") from None
    if not values:
        raise AuditError("baseline_empty")
    return {v.encode("utf-8") for v in values}


def selected_files(root, view):
    """Return selected bytes and skipped working-tree deletion count."""
    args = ["ls-files", "--cached", "-z"]
    if view == "working-tree":
        args.extend(["--others", "--exclude-standard"])
    names = sorted(set(git(root, *args).decode("utf-8").split("\0")) - {""})
    if len(names) > 10000:
        raise AuditError("file_count_limit")
    files = {}
    skipped = 0
    for name in names:
        if view == "staged":
            files[name] = git(root, "show", ":" + name)
            continue
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise AuditError("unsafe_working_tree_path")
        if not path.exists():
            skipped += 1
        elif path.is_file():
            files[name] = bounded_file(path)
    return files, skipped


def registration_policy(files):
    """Parse only the provenance-pinned registration; never execute it."""
    try:
        data = files[REGISTRATION]
        digest = json.loads(files["provenance.json"])[
            "distributed_community_registration"
        ]["sha256"]
        if hashlib.sha256(data).hexdigest() != digest:
            raise AuditError("registration_provenance")
        tree = ast.parse(data)
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {
                        "CLIENT_ID",
                        "CLIENT_SECRET",
                    }:
                        if target.id in values:
                            raise AuditError("registration_provenance")
                        values[target.id] = ast.literal_eval(node.value)
        if set(values) != {"CLIENT_ID", "CLIENT_SECRET"} or not all(
            isinstance(v, str) and v.strip() for v in values.values()
        ):
            raise AuditError("registration_provenance")
        return data, {v.encode("utf-8") for v in values.values()}
    except KeyError, ValueError, TypeError, SyntaxError, UnicodeError, RecursionError:
        raise AuditError("registration_provenance") from None


def audit(root, baseline, *, view="working-tree", archives=()):
    """Return counts only; no private matches or names leave this function."""
    report = {
        "schema_version": 1,
        "view": view,
        "files_scanned": 0,
        "deleted_paths_skipped": 0,
        "archives_scanned": 0,
        "findings": {},
    }
    try:
        if view not in {"working-tree", "staged"}:
            raise AuditError("view_invalid")
        root = root.resolve()
        private = baseline_values(baseline, root)
        files, skipped = selected_files(root, view)
        expected, public = registration_policy(files)
        report.update(
            private_values_checked=len(private), deleted_paths_skipped=skipped
        )
        findings = Counter()

        def scan(name, data, *, in_archive=False):
            category = "archive" if in_archive else "file"
            if any(v in name.encode("utf-8") for v in private | public):
                findings[category + "_name"] += 1
            needles = private | public
            if name == REGISTRATION and data == expected:
                needles = private - public
            elif name == REGISTRATION:
                findings["registration_provenance"] += 1
            if any(v in data for v in needles):
                findings[category + "_content"] += 1

        for name, data in files.items():
            scan(name, data)
            report["files_scanned"] += 1
        for path in archives:
            try:
                members = release_checks.archive_members(bounded_file(path))
            except release_checks.Invalid:
                raise AuditError("archive_invalid") from None
            if REGISTRATION not in members:
                findings["archive_registration_missing"] += 1
            try:
                archive_expected, _ = registration_policy(members)
                if archive_expected != expected:
                    findings["archive_provenance"] += 1
            except AuditError:
                findings["archive_provenance"] += 1
            for name, data in members.items():
                scan(name, data, in_archive=True)
            report["archives_scanned"] += 1
        report["findings"] = dict(sorted(findings.items()))
        report["status"] = "failed" if findings else "passed"
        return report, int(bool(findings))
    except (AuditError, OSError, UnicodeError) as err:
        report.update(
            status="incomplete",
            category=str(err) if isinstance(err, AuditError) else "input_unavailable",
        )
        return report, 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-baseline", type=Path, required=True)
    parser.add_argument(
        "--view", choices=("working-tree", "staged"), default="working-tree"
    )
    parser.add_argument(
        "--zip", type=Path, action="append", default=[], dest="archives"
    )
    args = parser.parse_args(argv)
    report, code = audit(
        ROOT, args.private_baseline, view=args.view, archives=args.archives
    )
    print(json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
