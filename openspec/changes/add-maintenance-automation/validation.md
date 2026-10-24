# Local validation evidence

Date: 2026-10-24. Local branch: `codex/add-maintenance-automation`.
Initial local evidence preceded the approved commit/push and PR #5. Later hosted
findings and the separately approved correction are recorded below. No release,
merge or production/hardware access was performed.

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

Task 3.3 is complete with corrected-commit CI and the compatibility assessment below. Initial
push/PR HACS runs failed on empty repository topics and the custom-only brands
lookup. The owner approved adding topics and excluding only `brands` after source
inspection. Repository topics were set and read back successfully. All other
validators remain active; no runtime file or identity change was made.

Initial commit: `5228a6493460ebdc457bc4e59711c6770e91e9ea`. Push runtime and
spec checks passed; HACS selected that exact SHA and failed the two checks above.
Container digest observed in that run:
`sha256:187499a09c5d41f9f0d42ff80d203ed87b974c028290140913b61e005fb0aab2`.
Actual fork/Dependabot actor execution remains unobserved; the compatibility
assessment is read-only token permissions, no secrets and source-repository/head
SHA selection. No real fork or bot execution is claimed from ordinary PR CI.

Dependabot's first default-branch update check/PR remains a post-adoption
observation. CodeQL stays deferred; no catalog submission, automerge, automatic
publication, issue closure or branch-protection setting was added.

## Corrected hosted validation

Correction commit: `f8c0c28083ede5116f628d6dc5942060dd6732fe`.
All three workflows passed for both push and pull_request events:

| Workflow | Push run | PR run |
| --- | --- | --- |
| Runtime tests/lint/package | 40096895713 | 40096898895 |
| OpenSpec | 40096895663 | 40096898885 |
| HACS | 40096895703 | 40096898883 |

HACS PR logs identify that exact head SHA and report all nine enabled checks
passed, including topics. Only the approved brands check is excluded. The image
digest matched the initial run's recorded digest. A nonblocking missing-category
warning remains; no runtime manifest change was made for this maintainer scope.

Hosted pytest: 414 passed, one existing skip. Lint and packaging passed. Hosted
ZIP digest was `ac4bd3a658c12f8413580091117179df2f7e10f24b4fc883a69d88e030adb29e`;
the builder embeds checkout file metadata, so ZIP hashes across fresh checkouts
are not expected to match. Runtime and packaged source files are unchanged by
this branch; the local build retains the previously recorded digest. No release
asset was replaced. Existing Actions emit Node 20 deprecation warnings; reviewing
Actions upgrades is a subsequent Dependabot maintenance task.

Fork/Dependabot compatibility assessment: the action chooses the PR source
repository and exact head SHA, requires only the ordinary read-only token, and
uses no private secrets, write APIs or privileged trigger. Hosted ordinary PR
execution passed under these permissions. Actual fork/bot actor execution and
the first default-branch Dependabot update remain unobserved post-adoption work.
