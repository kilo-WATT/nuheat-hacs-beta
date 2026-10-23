# Updated handoff validation delta

## ADDED Requirements

### Requirement: Capability-compatible source validation
A newly allowlisted Core candidate SHALL have isolated matching-framework evidence for configuration identity, OAuth provider continuity, refresh and reauthentication, all hold controls, and the explicit timed-hold action. Candidate failures or absent evidence SHALL leave the current allowlist unchanged and the beta active.

#### Scenario: Candidate provides all required capabilities
- **WHEN** exact candidate source passes the isolated transition and capability matrix
- **THEN** that source is eligible for a separately authorized allowlist update with recorded evidence.

#### Scenario: Timed-hold action is absent
- **WHEN** a candidate preserves entities but lacks the beta's timed-hold action contract
- **THEN** it is not declared compatible for a seamless handoff of automations using that action.

#### Scenario: Existing provider cannot reauthenticate
- **WHEN** a migrated community or custom provider cannot complete its expected authorization path
- **THEN** the candidate remains unapproved and the blocker is recorded without deleting credentials or entries.

### Requirement: Reproducible handoff recovery
The transition validation SHALL exercise unknown-source rejection, preservation of override files outside custom_components, restart into Core, and recovery after failed retirement or reload. Validation SHALL use isolated synthetic installations and SHALL NOT count production or live hardware checks as completed without explicit evidence.

#### Scenario: Retirement is interrupted
- **WHEN** the isolated transition cannot finish retirement or restart
- **THEN** the test proves recoverable configuration and override files and records any failure before allowlisting.
