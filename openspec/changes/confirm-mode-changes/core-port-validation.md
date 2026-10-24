> Historical validation snapshot. The accepted-target beta correction is now
> included in the b9 preparation; see RELEASE_NOTES.md and docs/VALIDATION.md.

# Core port validation

Local port based on Core PR #176586 commit
`094a11a1c251aac5d749d2133fe0852d9093ed17`, compared with beta v0.1.0b8
(`804343b755df8a381e52eba8d2746ac9a5224fd6`). No commit, push, production
access, thermostat command, release update, or beta runtime modification.

## Implementation and compatibility

- Core coordinator matches b8 exactly: per-device mode generations, online and
  unambiguous confirmation, independent thirty-second deadlines, coalesced
  two-second initial reads and eight-second retries, authentication stop, and
  unload cleanup. Writes are never retried automatically.
- Core climate retains its native temperature properties, current lifecycle and
  service APIs, and existing shared control lock. Only climate.py/coordinator.py
  change at runtime; thirteen other tracked integration files are byte-identical
  to the Core base, including OAuth, identity, migration, services and dependencies.
- Preserve Core's `_command_temperature()` helper in preset/HVAC writes. This
  intentionally improves on b8's rapid target-then-preset edge: an accepted 24 C
  target is passed onward instead of stale 23 C readback. Existing Core regression
  cases for Temporary hold, Permanent hold and Heat all pass. The inverse order
  (preset then target) receives b8's accepted-mode and expiry-preservation logic.
- Twenty-three climate methods match b8 after native-property normalization.
  Intentional differences are Core's existing Off dispatch inside the lock and
  its accepted-target helper in mode/preset writes. Nothing is copied from beta
  OAuth registration or developer tooling into Core.

## Executed validation

- Required `script/setup` completed in the isolated Python 3.14.8 Core environment.
- Full NuHeat Core suite: **263 passed**, including all 24 new mode regression
  cases and the existing target-preservation, timed hold, OAuth and migration tests.
- Ruff integration/tests check and formatting of changed files: passed.
- Mypy: passed, no issues in eleven integration source files.
- Pylint integration: passed.
- Hassfest integration validation: passed, zero invalid integrations.
- All applicable pre-commit hooks on the five changed files: passed (Ruff check,
  Ruff format, codespell, prettier, mypy, pylint and branch guard; unrelated hooks
  skipped by their configured file filters). Direct hassfest validation passed
  separately.
- Required repository-wide `uv run --no-sync prek run --all-files` was attempted
  with a 240-second bound but produced no completed hook result. No repository-wide
  pass is claimed; only the completed relevant checks above are treated as passed.

The user reported successful b8 hardware testing. This port was tested with
synthetic clocks and mocked APIs; no measured Core hardware latency or new
live Core OAuth validation is claimed.

## Remaining work

Core remains outside the beta's exact-source handoff allowlist. Differences are
__init__.py, behavior.py, climate.py, const.py and coordinator.py. The allowlist is
unchanged and therefore keeps the beta active. Execute the separate
`validate-updated-core-handoff` change before considering eligibility changes.

The beta rapid target-then-preset correction remains a separate follow-up; b8 has
not been modified. Review this local Core patch before authorizing submission.
