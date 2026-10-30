# Proposal

## Why

[A community report](https://github.com/home-assistant/core/issues/175923#issuecomment-6478874618) identifies rejected title-case preset actions, a 7°C minimum blocking existing 5°C automations, and confusing repair prompts when migrating multiple thermostats. Isolated inspection reproduced the preset rejection and generic temperature floor; existing migration tests support account-scoped consolidation rather than deleting entries.

## What Changes

- Advertise all six preset values: preferred `Run Schedule`, `Temporary Hold`, `Permanent Hold`, plus accepted compatibility aliases `run_schedule`, `temporary_hold`, `permanent_hold`. Equivalent names invoke the same controls; duplicate UI choices are intentional.
- **BREAKING**: Report preferred title-case preset state values. Existing snake_case action calls remain valid, but state comparisons in templates and automation triggers need documented updates.
- Define an explicit beta temperature range of 5–35°C (41–95°F), shared by ordinary temperature controls and timed holds. A 5°C target preserves the requested mode and expiry; explicit Off retains its existing Standby behavior.
- Clarify account-scoped migration: start from a matching legacy entry for the account being authorized; preserve existing entries and explain remaining repair prompts and retries.
- Add service-path regression coverage and migration guidance without changing OAuth, identity, reconciliation, or handoff safeguards.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `thermostat-controls`: Six accepted preset inputs, canonical reported values, and explicit beta temperature bounds.
- `timed-holds`: Shared temperature bounds while retaining timezone, expiry, and finiteness validation.
- `migration-identity`: Account-scoped user guidance that preserves entries and ownership checks.

## Impact

Only the HACS beta is in scope: control constants/mappings, climate bounds, relevant tests, and user documentation. Implementation may require updating existing runtime provenance hashes for changed protected files. Core PR #176586, the SDK, OAuth registrations, handoff allowlists, production HA, and published releases remain untouched.

The lower bound is supported by the reported Signature behavior and existing 5°C Standby behavior; Swagger supplies no numeric range contract. This is an integration fallback, not proof of every model's vendor acceptance. Vendor rejections must remain visible. No hardware commands are authorized by this proposal.
