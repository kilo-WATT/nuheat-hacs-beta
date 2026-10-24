# Proposal

## Why

The updated Core candidate includes hold controls, the timed-hold action, and
reconciliation behavior that the beta's old exact-source allowlist does not
recognize. A compatible handoff needs evidence for those capabilities as well as
entry and registry continuity, not just a newer commit hash.

## What Changes

- Propose isolated legacy-to-beta-to-updated-Core transition validation.
- Make official Home Assistant Cloud linking the destination for beta community
  OAuth users. Verify its actual availability separately from PR merge; do not
  require the beta's community registration to remain usable after handoff.
- Test relinking the same existing entry to the official provider, including
  refresh, cancellation, failed authorization, hold controls and recovery.
  Preserve entity/device identity and automations; a user authorization step may
  be needed. Legitimate custom credentials retain their explicit provider choice.
- Allowlist exact tested source only after matching-framework checks pass and
  the user authorizes that beta implementation change.
- Retain the current safe outcome for unknown source: keep the beta active.
- No current allowlist change, Core edit, production access, or publication occurs
  when this plan is created.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `core-handoff`: require capability and authorization continuity evidence for a
  newly allowlisted Core candidate.

## Impact

Beta handoff fixtures/tests and validation documentation first; a later approved
allowlist update only if the candidate passes. The recorded candidate is Core PR
#176586 at `59749ee3512fa56265fae085cae0c7db68f9b26c`; resolve the intended actual
candidate again before running the transition. No shared OAuth registration is
copied into Core or the client library.

The user's clarified destination supersedes the earlier requirement to preserve
the community provider after transition. Existing community/My callback tests
remain historical evidence, not proof of official Cloud linking or its readiness.
