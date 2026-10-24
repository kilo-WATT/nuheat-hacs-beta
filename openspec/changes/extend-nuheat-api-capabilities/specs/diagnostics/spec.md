# Diagnostics delta

## Purpose

Provide useful support snapshots from local integration state without exposing
account information or causing additional thermostat or cloud traffic.

## ADDED Requirements

### Requirement: Private local support snapshot
Diagnostics SHALL contain only allowlisted version, availability, cooldown and confirmation-status fields. They SHALL exclude credentials, registration values, tokens, identifiers, names, locations, URLs, raw payloads and free-text errors. Unknown fields SHALL be excluded by default.

#### Scenario: Nested private data
- **WHEN** entry data, options or errors contain synthetic private values at any nesting depth
- **THEN** none of those values appear in diagnostics, including as dictionary keys.

#### Scenario: New vendor field
- **WHEN** a later response introduces an unrecognized field
- **THEN** diagnostics exclude it until it is explicitly reviewed and allowlisted.

### Requirement: Side-effect-free download
Downloading diagnostics SHALL use cached integration state only. It SHALL NOT refresh credentials, issue cloud requests, send commands, alter options or change entity/registry associations. Incomplete setup and cooldown SHALL still permit a sanitized snapshot.

#### Scenario: Diagnostics during outage
- **WHEN** the account is throttled or setup is incomplete and diagnostics are requested
- **THEN** the snapshot describes the locally known status without network access or exposing the underlying exception text.
