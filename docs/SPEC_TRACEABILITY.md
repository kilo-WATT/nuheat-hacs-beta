# Specification evidence and refinement map

Snapshot: 2026-10-23. Baselines describe the v0.1.0b9 beta contract, including
bounded mode confirmation and accepted-target preservation. The completed change
is archived; official Cloud linking and final Core handoff remain unfinished.
Proposals do not strengthen shipped guarantees by themselves.

The b9 suite passed 305 tests with one existing skip. The maintainer is testing b9;
no new b9 hardware result is claimed. Historical sources remain pinned for provenance.

## Recorded sources

- Published beta `v0.1.0b9`: `60b38fe9a04d1b51bb30632c1d4a054b5dcd9488`.

- Beta runtime tag `v0.1.0b7`: `1d1d73b0be76faa73c4783291114afcf6570c535`.
- Beta documentation/promotion baseline: `1a19cae8602ef77a5f70eea695d905900baab43f`.
- Published client: `chemelex-nuheat==0.1.2`.
- Recorded Core candidate: PR #176586, `9ab210660371eaf6bda2083a518cf15eea29318f`.
  Re-resolve the intended candidate before transition testing; the final merge
  is not assumed to have these exact files.

The existing records report 271 beta tests passed with one skipped historical
persistence case, 107 client tests passed, and 227 Core tests passed. Those are
recorded prior runs, not new hardware or transition evidence produced by adding
OpenSpec. Older sections of VALIDATION.md are historical and must not be treated
as a current claim that every source file or Core revision is unchanged.

## Contract-to-evidence map

| Capability | Current implementation | Main existing evidence | Known boundary |
| --- | --- | --- | --- |
| Thermostat controls | `behavior.py`, `climate.py`; optional client schedule details | `tests/nuheat/test_permanent_hold.py`, `test_integration.py`; approved Signature mode comparison in `PERMANENT_HOLD.md` | Other models/firmware and Standby-to-Permanent Hold lack equivalent live coverage. |
| Command reconciliation | `coordinator.py`, `climate.py` | `test_setpoint_reconciliation.py`, `test_hold_action.py`, `test_mode_reconciliation.py` | Bounded confirmation and rapid target-then-mode preservation have synthetic coverage. Core port parity is recorded; no new b9 hardware measurements are claimed. |
| Timed holds | Integration-provided action, HA units/timezone, pending expiry | `test_hold_action.py`; client request-contract tests | End-to-end action tests use synthetic responses. No new live timed-expiry test is claimed; the standard card has no expiry field. |
| Authentication | Named beta/custom provider choice, community My prerequisite, PKCE | `test_beta_oauth.py`, `test_community_setup.py`, `test_oauth_roundtrip.py`, `test_oauth_routing.py`; `OAUTH_UNAUTHORIZED_CLIENT.md` | Official-provider relinking is planned. Existing community-provider tests do not prove official Cloud linking readiness. |
| Migration/identity | Existing ownership checks, registry transfer/rollback, account setup | `test_migration.py`, `test_integration.py`, `test_edge_cases.py` | Do not replace unmatched entries or weaken cleanup safeguards. |
| Core handoff | `core_handoff.py`, exact `core-handoff.json` source map | `test_core_handoff.py`, `test_handoff_recovery.py`; active change investigation | Current Core `9ab210660371` is not recognized. Isolated capabilities and recovery were exercised; official-provider relinking and final automatic transition remain pending. |
| Release distribution | Manifest, pins, allowlisted package builder, HACS instructions | `tests/test_packaging.py`, `tools/package.py`; recorded public download/HACS checks | OpenSpec is developer-only. Structural spec CI is not a runtime, vendor, or hardware test. |

Paths in the implementation column are under `custom_components/nuheat` unless
otherwise stated. Test links and code are the evidence source; this table is an
index, not a substitute for their assertions or results.

## Completed and proposed refinements

### Completed maintenance automation

`add-maintenance-automation` adds requirements to maintainer-tools and release
distribution. `.github/dependabot.yml` and `tests/test_maintenance_automation.py`
cover weekly grouped proposals, finite limits and the Ruff-only pip scope.
`.github/workflows/hacs.yml` and the same contract tests cover read-only PR/push/
manual/weekly checks, comment suppression, bounded execution and candidate SHA
selection. `docs/MAINTAINING.md` documents failure triage, mutable upstream image,
manual release verification and limits on installation/migration claims.

Hosted push/PR HACS logs verified the correction's exact SHA and nine enabled
checks. The approved brands exception preserves the Core domain; topics are set.
Main validation passed after PR #5 merged. Initial Dependabot update checks ran
successfully and opened PR #6; its bot-authored push/PR checks passed, it was
reviewed and merged, and all three main workflows passed again. Actual fork-user
execution remains unobserved. CodeQL setup is deferred and no scanner is enabled.
Evidence is retained in the archived change; runtime guarantees are unchanged.

| Change | Proposed acceptance | Current status |
| --- | --- | --- |
| [Archived control change](../openspec/changes/archive/2026-10-23-confirm-mode-changes/tasks.md) | Bounded confirmation, accepted-target preservation, failures, rapid commands and cleanup. | 13/13 tasks complete; shipped in b8/b9; baseline specs synced. |
| [Archived maintenance automation](../openspec/changes/archive/2026-10-24-add-maintenance-automation/tasks.md) | Bounded dependency proposals and independent HACS validation. | 10/10 tasks complete; merged; baseline specs synced. First actual bot PR reviewed and merged. |
| [Archived API resilience](../openspec/changes/archive/2026-10-24-harden-nuheat-api-resilience/tasks.md) | Cooldown-aware reconciliation, bounded operations and permission classification. | 12/12 tasks complete; shipped in b10; baseline specs synced. Optional capabilities and official handoff remain separate. |
| [Updated Core handoff](../openspec/changes/validate-updated-core-handoff/tasks.md) | Stable identities while moving community users to verified official Cloud linking, plus action continuity and recovery. | 7/10 tasks complete. Official-provider checks remain open; allowlist unchanged. |
