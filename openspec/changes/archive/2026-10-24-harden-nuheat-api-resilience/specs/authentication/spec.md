# NuHeat permission and authorization delta

## ADDED Requirements

### Requirement: Permission denial differs from expired authorization
HTTP 403 SHALL be reported as insufficient application permission rather than expired authorization. A required-endpoint permission failure SHALL remain visible without clearing credentials, replacing providers or forcing reauthentication solely for that response. The existing single refresh/retry for HTTP 401 and genuine authorization failure handling SHALL remain intact.

#### Scenario: Required endpoint is forbidden
- **WHEN** the primary thermostat read or a requested Permanent Hold write returns HTTP 403
- **THEN** HA reports a permission failure without retrying the write, selecting another provider or converting the command to Manual.

#### Scenario: Credentials truly expire
- **WHEN** HTTP 401 persists after the existing single forced refresh and retry
- **THEN** the existing reauthentication path remains available without recreating NuHeat entries or entities.

### Requirement: Optional detail permissions preserve authoritative reads
A successful v2 thermostat read SHALL remain usable when optional v1 details return HTTP 403. Missing details SHALL remain unresolved; HA SHALL NOT infer Permanent Hold, Standby or permission to change a possible hold to Manual. Genuine authorization failure on optional requests SHALL NOT be silently treated as a harmless permission limitation.

#### Scenario: v2 succeeds and optional v1 is forbidden
- **WHEN** v2 returns a mode-3 thermostat but the correlated v1 read returns HTTP 403
- **THEN** HA retains the v2 data and entity identity, avoids forced account reauthentication, and leaves the Manual/Permanent Hold distinction unresolved.

#### Scenario: Unresolved mode receives an implicit target write
- **WHEN** optional permissions are missing and safe hold-preserving mode selection is unresolved
- **THEN** the implicit write is rejected without changing the thermostat; explicit supported controls remain explicit user choices.

#### Scenario: Optional read remains unauthorized
- **WHEN** an optional read still returns HTTP 401 after the existing authorization recovery attempt
- **THEN** the account authorization error propagates rather than being hidden by the v2 fallback.

### Requirement: Failure diagnostics preserve configuration privacy
Cooldown, timeout and permission failures SHALL retain config-entry IDs, entity/device registry links, options and provider associations. User-visible messages SHALL identify the failure category without exposing credentials, access tokens, callback URLs, thermostat identifiers or raw vendor response bodies.

#### Scenario: Transient API failure
- **WHEN** a running account encounters a throttle, timeout or permission denial
- **THEN** HA provides actionable sanitized feedback without deleting entries, unlinking entities or changing stored application credentials.
