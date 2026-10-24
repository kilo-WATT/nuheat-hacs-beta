"""Historical helper; see tools/historical/README.md for its pinned scope."""

import argparse


def main(argv=None):
    """Explain supported usage without invoking the obsolete implementation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    print(
        "Historical helper: tools/historical/core_handoff.py is reference only. "
        "Use docs/DEVELOPMENT.md and the current OpenSpec transition plan; "
        "this command does not validate the current Core handoff."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
