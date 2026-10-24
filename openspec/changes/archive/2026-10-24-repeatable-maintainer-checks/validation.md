# Maintainer-check implementation validation

2026-10-24. Local implementation only. No commits, pushes, releases, settings
changes, production access, account probes or thermostat commands were performed.

## Implemented

- `tools/verify_release.py`: parameterized read-only GitHub/PyPI checks with
  structured evidence, exact-commit workflow results, bounded downloads and
  archive inspection, selected-tag byte comparison and HACS ordering distinctions.
  No downloaded code is executed and no files are extracted or installed.
- `tools/privacy_check.py`: explicit working-tree/index views, external baseline,
  selected ZIPs, count-only output, and narrow provenance-pinned recognition of
  the public community registration. It does not read production storage or
  execute credential modules. Unknown private values remain outside its claim.
- Three obsolete command paths now explain their historical status and exit
  nonzero without executing their old implementation. Four original helper
  implementations are preserved inside inert functions under `tools/historical/`.
  Their source/AST fingerprints are recorded against the b10 commit so tests
  do not depend on the current HEAD or a deep Git clone.
- DEVELOPMENT and MAINTAINING document supported commands, Python 3.14/gh
  prerequisites, exit codes, privacy scope and historical-tool limitations.

## Synthetic verification

- Final complete beta suite: **410 passed, one existing skip** in 18.92 seconds.
- Of these, **62 focused maintainer-tool tests** cover release evidence,
  nondefault release ordering, privacy views and historical entry points.
- Ruff lint passed for all components, tests and tools. Formatting checks passed
  for all thirteen changed/new Python files, including historical references.
- `git diff --check` passed. Strict OpenSpec validation: twelve items passed.
- A combined-test run exposed a stale exception-class reference after module
  reload; module-qualified access fixed it and the full suite passed afterward.
- Corrupt DEFLATE, malformed/encrypted/duplicate/unsafe/oversized archives,
  incomplete CI/transport, missing SDK and stale-byte cases are synthetic tests.
  No live failures were induced against GitHub, PyPI or NuHeat.

## Public read-only b10 verification

The new command passed against `kilo-WATT/nuheat-hacs-beta`, tag `v0.1.0b10`,
expected commit `3f77a85f459fb61021ea688d094229f4429fba9c`:

- Regular, nondraft and GitHub latest status matched.
- Both required exact-commit workflows passed; observed run IDs were
  `40066903723` and `40066903702`.
- Public SDK 0.1.3 metadata and wheel availability passed.
- Sidecar/digest and all selected-tag package bytes passed; nineteen runtime
  files were verified. ZIP SHA256:
  `969650b1d29c65677dcb8c7203efdf931208c6bd3b8686ef858f325a03e946d6`.
- b10 appeared with beta visibility disabled. GitHub returned b9 first, so the
  report correctly retained `first_regular_matches: false` and an advisory.
  Explicit-tag source was verified; no production HACS UI install was claimed.

## Privacy and compatibility

The supported audit passed against thirteen known values in an external Markdown
baseline: working tree plus one explicitly selected published ZIP, and the full
154-file index separately. Working-tree scanning initially counted 171 files and
seven skipped deletions from the earlier archive; the final validation record
adds another planning file. No actual values or filenames were printed. An
independent external audit checked eighteen known private values, including its
separate saved-token inputs, with no matches. Those token files are not inputs
the supported audit discovers implicitly.

All nineteen `custom_components/nuheat` files match published b10 byte-for-byte.
Dependency, HACS, provenance and release-status files also match. The local
30-entry package retained exactly the published ZIP digest; tools, history,
tests, private baselines and OpenSpec remain excluded. No SDK/Core port or new
runtime feature is included.

## Review boundary

Prior authorized local community sync/archive edits are still present separately:
`openspec/changes/archive/2026-10-24-organize-community-workflow/`, its new
community-support baseline and the promotion requirement in release-distribution.
They are not implementation changes from this proposal. No unrelated archive or
unimplemented optional API requirement was synced or marked complete.

Implementation files are local and uncommitted. Current GitHub CI was not run for
these unpushed developer-tool changes; the public CI evidence above belongs to
published b10. Review before authorizing commits/pushes or syncing this change.

## Subsequent publication authorization

The user subsequently approved separate commits, push, GitHub CI, merge and final
spec sync/archive for this developer-only change. The community-workflow closure
is commit `4770553899846fe8f71a4af0fdf730c14f7d0d20`; implementation follows as a
separate commit. Fresh implementation CI and closure evidence will be recorded
after they complete. No HA release, production access or runtime update is part
of this authorization.

## Implementation CI and specification closure

Implementation commit `e768f2fab7a8e455d698bcf1d56bd709ff06dbf7` passed both
GitHub workflows for its push and PR #4. Successful runs:

- https://github.com/kilo-WATT/nuheat-hacs-beta/actions/runs/40093611845
- https://github.com/kilo-WATT/nuheat-hacs-beta/actions/runs/40093611870
- https://github.com/kilo-WATT/nuheat-hacs-beta/actions/runs/40093648364
- https://github.com/kilo-WATT/nuheat-hacs-beta/actions/runs/40093648342

After those checks, the completed change's three maintainer-tool requirements
and three release-verification requirements were synced into baseline specs.
Existing release purpose/requirements and the new capability's authored purpose
were preserved; every delta requirement was compared against the main specs.
Strict baseline validation passed for all nine capabilities. All seven tracked
implementation tasks are complete. The change is archived under
`2026-10-24-repeatable-maintainer-checks` in a documentation-only closure commit.
Final closure CI and the main merge are verified separately after publication;
this record does not claim future checks have already run.
