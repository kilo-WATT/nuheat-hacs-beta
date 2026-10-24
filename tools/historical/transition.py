"""Historical reference only; import and ordinary invocation have no effects."""


def _historical_reference():
    """Run independent HA test processes; all persisted data is synthetic."""

    import json
    import os
    from pathlib import Path
    import subprocess
    import sys
    import tempfile

    ROOT = Path(__file__).resolve().parents[1]

    def main():
        (ROOT / "artifacts").mkdir(exist_ok=True)
        directory = Path(
            tempfile.mkdtemp(prefix="synthetic-transition-", dir=ROOT / "artifacts")
        )
        results = {}
        for stage in ("seed", "beta", "restart", "candidate"):
            env = dict(
                os.environ,
                NUHEAT_TRANSITION_STAGE=stage,
                NUHEAT_TRANSITION_DIR=str(directory),
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "--tb=short",
                    "tests/test_persistence.py",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            (directory / f"{stage}.txt").write_text(result.stdout + result.stderr)
            results[stage] = {"returncode": result.returncode}
            print(
                f"{stage}: {'passed' if result.returncode == 0 else 'FAILED'}",
                flush=True,
            )
            if result.returncode:
                print((result.stdout + result.stderr)[-6000:])
                break
        (ROOT / "artifacts").mkdir(exist_ok=True)
        (ROOT / "artifacts/transition-results.json").write_text(
            json.dumps(results, indent=2)
        )
        print(f"Synthetic storage and logs: {directory}")
        return int(any(r["returncode"] for r in results.values()))

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
