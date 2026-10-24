# Tasks

## 1. Pending mode confirmation

- [x] 1.1 Add per-thermostat expected mode/preset and generation tracking with a thirty-second deadline; verify stale and reordered read cases using synthetic time.
- [x] 1.2 Reconcile pending mode intents through the coalesced two-second read and eight-second retry schedule; parameterize all presets, Heat, Auto, Off, and On tests and document the new bounded window.
- [x] 1.3 Keep failed writes visible without optimistic success or repeated writes; verify transport, post-write read, and authentication failures.

## 2. Standby and superseding commands

- [x] 2.1 Clear Standby assumptions on confirmation and expiry; verify a later externally reported mode can update HA and document unconfirmed outcomes.
- [x] 2.2 Preserve setpoint/expiry intent when controls supersede each other; verify rapid commands and in-flight old responses cannot confirm newer intent.
- [x] 2.3 Cancel all pending deadlines and account callbacks on unload; verify independent devices and absence of reads after shutdown.

## 3. Compatibility and review evidence

- [x] 3.1 Prepare the matching Core port in a separately authorized Core scope; verify normalized behavior parity and its tests/lint/types under Core's framework.
- [x] 3.2 Run the full beta regression, lint, packaging, and privacy checks; record exact results and all remaining hardware limits in the validation record.
- [x] 3.3 Validate spec deltas and documentation against the implementation with npm run specs:check; keep production, publication, and allowlist changes outside this change's implementation scope.

## 4. Accepted-target follow-up release preparation

- [x] 4.1 Prepare v0.1.0b9 manifest, metadata, release notes and validation documentation; keep published b8 and the handoff allowlist unchanged.
- [x] 4.2 Run the full beta suite, lint, formatting, strict OpenSpec validation, package audit and private-data checks for the exact candidate.
- [x] 4.3 Commit and push the reviewed candidate on codex/release-prep-v0.1.0b9 and verify GitHub Actions on that commit; do not update main or publish during preparation.
- [ ] 4.4 After separate publication approval, verify final main CI and publish the tag/release; verify HACS visibility and published contents.

## Workflow follow-up

- Present the implementation and evidence for the user's requested release scope before publishing.
- Beta specs synced for v0.1.0b8. Core port prepared and validated locally; see core-port-validation.md. Review before archiving or submission.
