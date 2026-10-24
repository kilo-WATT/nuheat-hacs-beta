> Historical validation snapshot. The accepted-target beta correction is now
> included in the b9 preparation; see RELEASE_NOTES.md and docs/VALIDATION.md.

# Accepted-target follow-up validation

Local candidate only, 2026-10-23. Published v0.1.0b8 is unchanged.

## Reproduction and correction

Six new cases first reproduced the defect: an accepted 24 C target followed by
Temporary hold, Permanent hold, or Heat sent the old cloud target of 23 C.
Each control was tested in Celsius and Fahrenheit (75.2 F). All six now pass.
The beta copies Core's existing `_command_temperature()` helper and uses it at
the two mode-write temperature arguments. No coordinator, OAuth, migration,
registry, SDK, or handoff implementation was changed.

## Completed checks

Run from the beta root using `/home/codex/.cache/nuheat-permanent-hold/bin/`:

- `python -m pytest -q`: 303 passed, one existing persistence-stage skip.
- `ruff check custom_components tests tools`: passed.
- Ruff formatting of the two changed Python files: passed.
- `python tools/package.py`: passed; local UNRELEASED archive only.
- `python ../audit_b8_privacy.py .`: 18 private values checked, 126 files checked,
  zero private account or identifier matches; no credential values printed.
- `npm run specs:check`: all ten items passed strict validation.
- `python -m pytest tests/nuheat/test_core_handoff.py -q`: five passed.

`../record_followup_validation.py` confirms the target helper is AST-identical
to Core commit `9ab210660371eaf6bda2083a518cf15eea29318f` and the coordinator is
byte-identical. Core's working tree remains clean. The old port-audit script's
dirty-tree precondition no longer applies after the Core port was committed;
its invocation failed that precondition and is not counted as a new audit pass.

## Limits

No new hardware test, production access, commit, push, version bump, release,
or allowlist change. Existing tests cover failure handling, stale responses,
expiry preservation, generation ordering and cleanup; these six cases add the
previously missing target-then-mode order. The serialized persistence test is
intentionally skipped outside its separate-process transition harness. Current
Core handoff remains unapproved; see the separate handoff investigation report.
