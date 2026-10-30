# Tasks

## 1. Preset compatibility

- [x] 1.1 Update beta preset constants and mappings to advertise the six agreed values in preferred-first order; verify mapping tests cover every spelling and reject unknown values without writes.
- [x] 1.2 Add regression tests through HA's actual preset service handler, verifying all six inputs, canonical reported state, and equivalent commands; retain rapid-command, stale-read, failed-write, and bounded-confirmation coverage.
- [x] 1.3 Update preset documentation and upgrade notes with exact action aliases, reported-state mappings, duplicate UI choices, and template/state-trigger migration examples; verify examples match tested values and preserve existing entity references.

## 2. Temperature bounds

- [x] 2.1 Introduce shared beta 5–35°C constants and use them for advertised climate limits and timed-hold validation; verify Celsius and Fahrenheit boundaries through actual HA temperature service validation and the timed-hold action.
- [x] 2.2 Add regression tests for 5°C/41°F acceptance, just-below-minimum rejection, unchanged 35°C/95°F maximum, above-maximum and nonfinite rejection, retained mode/expiry, and vendor rejection without clipping or substitute writes; verify explicit Off retains its existing behavior.
- [x] 2.3 Document the explicit fallback range and its evidence limits, distinguishing a 5°C target from selecting Off; verify ordinary and timed-hold instructions use the same range without claiming vendor-wide validation.

## 3. Account-scoped migration guidance

- [x] 3.1 Update README and authentication guidance to explain authorization from any matching legacy entry for the intended account, account-wide consolidation, ownership checks, and remaining repair prompts/retries; review all instructions for entry-deletion or identity-loss advice.
- [x] 3.2 Run existing multi-entry, unrelated/temporarily omitted device, and wrong-account migration tests; add only necessary coverage for any newly documented uncovered path and verify entity/device associations and rollback remain intact.

## 4. Integration validation

- [x] 4.1 Run the repository's existing full integration tests, lint, formatting, provenance, privacy, and release packaging checks; update only required changed-runtime provenance hashes, and record exact commands/results without private values.
- [x] 4.2 Run `npm run specs:check` and review the final diff/package to confirm no Core, SDK, OAuth, identity, reconciliation, handoff allowlist, or unrelated changes; record any unverified hardware/model assumptions and leave release/version operations for separate authorization.

## Workflow follow-up

- Present implementation evidence for review before any commit, push, release, or live hardware test.
- Sync and archive the change after implementation and review satisfy the project workflow.
