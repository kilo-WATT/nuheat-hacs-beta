# Tasks

## 1. Native properties and conversion paths

- [x] 1.1 Implement native Celsius readings, bounds, step handling and pending targets, with a narrow minimum-framework compatibility path. Add setup/state tests for both framework capabilities and document supported versions.
- [x] 1.2 Separate ordinary climate service input from the custom timed-hold action conversion. Verify Celsius/Fahrenheit requests through actual service handlers, boundary values, explicit expiry, Standby, pending state and registry identity. Document the action input unit.

## 2. Framework and regression verification

- [x] 2.1 Obtain an official current HA framework artifact or exact framework source and record its version/hash. Run setup, state reporting and every affected control with deprecation warnings checked, alongside HA 2026.10.2. Record an unavailable framework as incomplete verification.
- [x] 2.2 Run temperature, preset, hold, stale-read, failed-write, rapid-command, timeout and unload regressions. Verify mode/expiry preservation, no write replay and timer cleanup on both supported paths.
- [x] 2.3 Run the complete isolated beta suite, lint/format, strict OpenSpec, packaging and privacy checks. Update exact candidate provenance without rewriting historical evidence or allowing publication. Record local modifications and verification results.

## Workflow follow-up

- Review implementation before commit, push or release preparation.
- Sync and archive after approved implementation verification. Preserve any unverified current-framework task as open.
