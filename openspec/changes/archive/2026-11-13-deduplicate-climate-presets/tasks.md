# Tasks

## 1. Canonical advertised and accepted presets

- [x] 1.1 Advertise exactly three snake_case preset identifiers and matching translated labels. Add ordinary HA service and parser tests proving one choice per control, canonical state output, preserved command payloads and zero API writes for retired title-case or invalid inputs, plus real HA translation lookup.
- [x] 1.2 Add upgrade mapping and a climate.set_preset_mode YAML example to user-facing upgrade guidance and candidate release notes. Check action-generating template guidance, title-case state comparisons and existing entity references against the tests.

## 2. Regression and combined-candidate verification

- [x] 2.1 Run preset, mode-confirmation, hold, Standby, stale-read, failed-write, rapid-command and unload tests. Verify source changes preserve domain, identity, provider associations, registry migration and exact-source handoff behavior.
- [x] 2.2 Run the full isolated suite, lint/format, strict OpenSpec, packaging and privacy checks with modernize-climate-temperature-api applied. Record exact framework and SDK versions and leave unavailable matching-framework verification open.
- [x] 2.3 Update candidate provenance and document the breaking title-case input and state change without rewriting shipped-release evidence. Keep release gates consistent with actual approval and verification state.

## Workflow follow-up

- Review code and results before commit, push or release preparation.
- Sync and archive the completed change after implementation verification. Compose with the temperature fix for a later approved beta release.
