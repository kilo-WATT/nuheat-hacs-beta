# Specification evidence and refinement map

Snapshot: 2026-10-23. Baselines describe the v0.1.0b8 beta contract, with bounded mode confirmation
synced after synthetic validation. The active change retains a pending Core port;
other proposals do not strengthen current guarantees by themselves.

The b8 suite passed 297 tests with one existing skip. Historical sources below
remain pinned for provenance; they are not the new b8 release commit.

## Recorded sources

- Beta runtime tag `v0.1.0b7`: `1d1d73b0be76faa73c4783291114afcf6570c535`.
- Beta documentation/promotion baseline: `1a19cae8602ef77a5f70eea695d905900baab43f`.
- Published client: `chemelex-nuheat==0.1.2`.
- Recorded Core candidate: PR #176586, `59749ee3512fa56265fae085cae0c7db68f9b26c`.
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
| Command reconciliation | `coordinator.py`, `climate.py` | `test_setpoint_reconciliation.py`, `test_hold_action.py` | Mode and setpoint/expiry confirmation are bounded. New mode lifecycle has synthetic coverage in `test_mode_reconciliation.py`; hardware and Core parity remain pending. |
| Timed holds | Integration-provided action, HA units/timezone, pending expiry | `test_hold_action.py`; client request-contract tests | End-to-end action tests use synthetic responses. No new live timed-expiry test is claimed; the standard card has no expiry field. |
| Authentication | Named beta/custom provider choice, community My prerequisite, PKCE | `test_beta_oauth.py`, `test_community_setup.py`, `test_oauth_roundtrip.py`, `test_oauth_routing.py`; `OAUTH_UNAUTHORIZED_CLIENT.md` | Core intentionally does not embed the beta community registration. Cross-implementation reauthentication needs transition evidence. |
| Migration/identity | Existing ownership checks, registry transfer/rollback, account setup | `test_migration.py`, `test_integration.py`, `test_edge_cases.py` | Do not replace unmatched entries or weaken cleanup safeguards. |
| Core handoff | `core_handoff.py`, exact `core-handoff.json` source map | `test_core_handoff.py`; historical isolated transition record | Updated Core `59749ee3512` is not recognized by the shipped allowlist. Beta remains active. New action compatibility needs verification before allowlisting. |
| Release distribution | Manifest, pins, allowlisted package builder, HACS instructions | `tests/test_packaging.py`, `tools/package.py`; recorded public download/HACS checks | OpenSpec is developer-only. Structural spec CI is not a runtime, vendor, or hardware test. |

Paths in the implementation column are under `custom_components/nuheat` unless
otherwise stated. Test links and code are the evidence source; this table is an
index, not a substitute for their assertions or results.

## Proposed refinements

| Change | Proposed acceptance | Current status |
| --- | --- | --- |
| `confirm-mode-changes` | Bounded read confirmation across every mode control; no stale indefinite Standby assumption; failures/rapid commands/unload covered. | Design and tasks only; no runtime edits. |
| `validate-updated-core-handoff` | Isolated matching-framework transition with stable identities, provider refresh/reauthentication, timed-hold action continuity, and recovery. | Plan only; allowlist unchanged. |
