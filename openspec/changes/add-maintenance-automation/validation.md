# Local validation evidence

Date: 2026-10-24. Local branch: `codex/add-maintenance-automation`.
No commit, push, hosted workflow run, repository-setting change, release or
production/hardware access was performed.

## Executed

- Focused maintenance/release-verifier tests: 40 passed.
- Full isolated Python 3.14.2 / HA 2026.10.2 suite: 414 passed, one existing skip.
- Ruff 0.17.1: `python -m ruff check custom_components tests tools` passed.
- Official actionlint 1.7.12: all three workflow files passed, shellcheck disabled
  (no shell code was added). Official Linux amd64 asset SHA256 verified against
  the release checksum file before use; binary kept in an isolated temporary path.
- `npm run specs:check`: strict validation passed, 13 items and zero failures.
- `python tools/package.py`: allowlisted local candidate passed. ZIP SHA256:
  `969650b1d29c65677dcb8c7203efdf931208c6bd3b8686ef858f325a03e946d6`.
  This matches the previously recorded b10 ZIP: no runtime or packaged member
  bytes changed and maintenance/development files remain excluded.
- `git diff --exit-code -- custom_components requirements-test.txt provenance.json`
  passed; runtime source, HA/SDK test pins and provenance remain unchanged.
- `git diff --check` passed.

## Upstream source reviewed

- HACS action source pinned at `1ebf01c408f29afcb6406bd431bc98fd8cbb15aa`.
- Official `hacs/integration` `action/action.py` was inspected: ordinary PR events
  choose the head repository; `REPOSITORY_REF` overrides the selected revision.
  This workflow supplies head SHA for PRs and event SHA otherwise, without setting
  the repository input that would bypass automatic fork selection.
- Its source-pinned action definition uses `docker://ghcr.io/hacs/action:main`;
  the validator container remains mutable and is not claimed reproducible.

## Pending hosted evidence

Task 3.3 stays unchecked. Exact-commit hosted CI, actual HACS validation logs and
fork/Dependabot execution need an authorized push/run. No HACS compatibility pass
is claimed from actionlint or configuration tests alone. No ignored checks have
been introduced; any hosted failure needs investigation before exceptions.

Dependabot's first default-branch update check/PR remains a post-adoption
observation. CodeQL stays deferred; no catalog submission, automerge, automatic
publication, issue closure or branch-protection setting was added.
