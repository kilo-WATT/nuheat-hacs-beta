"""Historical reference only; import and ordinary invocation have no effects."""


def _historical_reference():
    """Replay beta storage under a matching Core checkout without editing that checkout."""

    import argparse
    import json
    import os
    from pathlib import Path
    import subprocess
    import tempfile

    ROOT = Path(__file__).resolve().parents[1]

    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("--core", type=Path, required=True)
        parser.add_argument("--storage", type=Path)
        args = parser.parse_args()
        core = args.core.resolve()
        if args.storage is None:
            args.storage = max(
                (ROOT / "artifacts").glob("synthetic-transition-*/restart.json"),
                key=lambda p: p.stat().st_mtime,
            ).parent
        source_sha = json.loads((ROOT / "provenance.json").read_text())["sha"]
        assert (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=core, text=True
            ).strip()
            == source_sha
        )
        directory = Path(
            tempfile.mkdtemp(prefix="core-handoff-", dir=ROOT / "artifacts")
        )
        source = (ROOT / "tests/test_persistence.py").read_text()
        source = source.replace(
            "from tests.nuheat.helpers import",
            "from tests.components.nuheat.helpers import",
        )
        (directory / "test_candidate.py").write_text(source)
        (directory / "pytest.ini").write_text(
            "[pytest]\nasyncio_mode = auto\nasyncio_default_fixture_loop_scope = function\n"
        )
        env = dict(
            os.environ,
            PYTHONPATH=str(core),
            NUHEAT_TRANSITION_STAGE="candidate",
            NUHEAT_TRANSITION_DIR=str(args.storage.resolve()),
        )
        result = subprocess.run(
            [
                str(core / ".venv/bin/python"),
                "-m",
                "pytest",
                "-p",
                "tests.conftest",
                "-q",
                "--tb=short",
                str(directory / "test_candidate.py"),
            ],
            cwd=directory,
            env=env,
            text=True,
            capture_output=True,
        )
        (directory / "result.txt").write_text(result.stdout + result.stderr)
        print((result.stdout + result.stderr)[-5000:])
        print(f"Matching Core source: {source_sha}; result: {result.returncode}")
        return result.returncode

    if __name__ == "__main__":
        raise SystemExit(main())


def main():
    """Prevent accidental execution of obsolete reference code."""
    print(
        "Historical reference only. See tools/historical/README.md and docs/DEVELOPMENT.md."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
