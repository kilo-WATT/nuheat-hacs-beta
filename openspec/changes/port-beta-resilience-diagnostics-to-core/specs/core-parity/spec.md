## Purpose

Keep the Core NuHeat integration's fault handling and private support snapshots equivalent to validated beta behavior while preserving framework-specific lifecycle and authorization contracts.

## ADDED Requirements

### Requirement: Core command resilience parity
Core SHALL preserve the command-reconciliation contract for all target, preset, HVAC, Off/On and explicit timed-hold controls. Server cooldowns SHALL prevent queued writes and override read cadence without extending pending-state deadlines. Uncertain writes SHALL NOT be replayed. Native temperature conversion, rapid-intent supersession and unload cleanup SHALL retain beta-equivalent observable behavior.

#### Scenario: Long cooldown overlaps confirmation
- **WHEN** a synthetic API returns Retry-After 120 during command confirmation
- **THEN** no new request starts during cooldown, pending state expires after thirty seconds, and no rejected or uncertain command is replayed.

#### Scenario: Rapid target and mode changes meet stale reads
- **WHEN** successive target, hold or schedule commands precede authoritative readback
- **THEN** accepted pending targets remain visible, old reads cannot confirm newer intent, and read coalescing preserves the latest command and explicit expiry in Celsius and Fahrenheit.

#### Scenario: Operation stalls or unloads
- **WHEN** authorization, lock wait, request body, write or post-write read stalls or is cancelled
- **THEN** finite budgets bound the operation, failed writes do not invent success, serialization is released, and unloading leaves no request or callback that initiates later network activity.

### Requirement: Core permission and identity parity
Core SHALL distinguish required permission failures and throttling from genuine expired authorization using the authentication contract. Optional forbidden v1 details SHALL preserve usable v2 state without guessing hold classification. Errors and the dependency upgrade SHALL retain entry, entity, device, option and provider associations without importing the beta community registration.

#### Scenario: Required permission failure
- **WHEN** a supported read or command returns HTTP 403
- **THEN** Core reports a sanitized permission error without forced reauthentication, provider replacement, Manual fallback or deletion of existing configuration.

#### Scenario: Optional permission failure versus expired token
- **WHEN** optional details return 403 but v2 succeeds, or a genuine 401 persists after the existing single refresh/retry
- **THEN** the former preserves conservative v2 availability and unresolved mode semantics while the latter retains normal reauthentication on the existing entry.

### Requirement: Core private cached diagnostics
Core diagnostics SHALL expose only allowlisted version, entry-status, availability, cooldown and confirmation-count fields from local state. Credentials, tokens, identifiers, names, locations, URLs, raw models, unknown fields and free-text errors SHALL be excluded. Download SHALL make no cloud, refresh-token or thermostat request and SHALL not alter configuration, including during incomplete setup or outage.

#### Scenario: Nested synthetic private markers
- **WHEN** entry data, options, errors, model fields or dictionary keys contain private markers
- **THEN** none appear in the downloaded diagnostic snapshot and entry/registry associations remain unchanged.

#### Scenario: Core has no custom integration version
- **WHEN** diagnostics are requested from built-in Core, including incomplete setup or cooldown
- **THEN** truthful locally available Core/SDK version metadata and status are returned without inventing a beta version or initiating account traffic.

### Requirement: Parity does not establish handoff eligibility
Successful Core parity tests SHALL NOT enable beta retirement, transfer community tokens to an official provider or broaden source eligibility. Official provider deployment and same-entry relinking SHALL remain independently verified before transition. Failed or unavailable official linking SHALL leave the beta and stored identities recoverable.

#### Scenario: Core resilience tests pass before official linking
- **WHEN** all isolated parity tests pass but official Cloud linking is not verified
- **THEN** the beta's shipped handoff guard and allowlist remain unchanged and no automatic transition readiness is claimed.
