# Updated handoff validation delta

## MODIFIED Requirements

### Requirement: Existing configuration continuity
The validated handoff SHALL retain entries, entity/device associations and user configuration. Official relinking MAY replace the existing entry's community provider association and tokens only after authorizing the same account successfully. Failed or cancelled relinking SHALL preserve recoverable credentials. The handoff SHALL NOT create a second account or new thermostat entities as a shortcut.

#### Scenario: Core starts after retirement
- **WHEN** the verified official implementation loads after successful same-account relinking
- **THEN** it uses the preserved entry and registry associations with the official provider's tokens.

## ADDED Requirements

### Requirement: Capability-compatible source validation
A newly allowlisted Core candidate SHALL have isolated evidence for identity preservation, relinking from community credentials to official Cloud linking, refresh, reauthentication, hold controls and the timed-hold action. Official linking SHALL be verified separately from PR merge. Continued community OAuth SHALL NOT be required after handoff. Failures or missing evidence SHALL keep the beta active and the allowlist unchanged.

#### Scenario: Candidate provides all required capabilities
- **WHEN** exact candidate source passes the isolated transition and capability matrix
- **THEN** that source is eligible for a separately authorized allowlist update with recorded evidence.

#### Scenario: Timed-hold action is absent
- **WHEN** a candidate preserves entities but lacks the beta's timed-hold action contract
- **THEN** it is not declared compatible for a seamless handoff of automations using that action.

#### Scenario: Official linking is unavailable after merge
- **WHEN** the PR has merged but the official provider is not enabled or verified
- **THEN** the beta stays active and automatic retirement is not enabled.

#### Scenario: Community user relinks through official provider
- **WHEN** the user authorizes the same NuHeat account through official Cloud linking
- **THEN** the existing entry receives the official provider association and its tokens while entry IDs, entity IDs, unique IDs, device associations, dashboards and automations are preserved without recreating thermostats.

#### Scenario: Relinking fails or is cancelled
- **WHEN** official authorization is denied, cancelled, unavailable, or returns a different account
- **THEN** the existing entry and recoverable credentials remain intact and beta retirement does not proceed.

#### Scenario: Legitimate custom credentials exist
- **WHEN** an entry uses a legitimate custom OAuth registration
- **THEN** its provider choice is preserved unless the user explicitly chooses official relinking, and community credentials are never forced onto it.

### Requirement: Reproducible handoff recovery
The transition validation SHALL exercise unknown-source rejection, preservation of override files outside custom_components, restart into Core, and recovery after failed retirement or reload. Validation SHALL use isolated synthetic installations and SHALL NOT count production or live hardware checks as completed without explicit evidence.

#### Scenario: Retirement is interrupted
- **WHEN** the isolated transition cannot finish retirement or restart
- **THEN** the test proves recoverable configuration and override files and records any failure before allowlisting.
