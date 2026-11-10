# Relative temperature controls delta

## Purpose

Provide an explicit temperature adjustment action after vendor delta semantics
are verified, preserving existing absolute controls and thermostat hold intent.

## ADDED Requirements

### Requirement: Explicit verified adjustment
Relative SHALL mean the last cloud-reported measured room temperature plus a signed hundredths-Celsius delta, not an increment to the target setpoint. Ordinary set-temperature SHALL remain absolute. The initial proof SHALL expose no relative HA action. A later action SHALL require explicit supported endpoint/mode and range policy rather than guessing resulting targets.

#### Scenario: Target differs from room temperature
- **WHEN** room temperature is 23°C, target is 18°C or 26°C, and Relative +100 is submitted in a supported later-stage SDK test
- **THEN** the expected resulting target is 24°C in both cases, with no promise that stale cached room data is authoritative.

### Requirement: Correct delta units and mode intent
Adjustment SHALL convert finite temperature differences without absolute-temperature offsets. The selected endpoint SHALL determine mode. A timed Hold SHALL resend its exact explicit expiry, including accepted pending expiry, to retain it. Manual and Hold without expiry SHALL NOT be described as expiry-preserving. Unknown, Standby and unsupported v1 Permanent Hold combinations SHALL be rejected without implicit mode conversion.

#### Scenario: Fahrenheit adjustment
- **WHEN** a supported thermostat receives a +1.8°F adjustment
- **THEN** the delta is encoded as +1°C without adding or subtracting 32.

#### Scenario: Pending timed hold
- **WHEN** a relative adjustment follows an accepted timed-hold command before cloud confirmation
- **THEN** the accepted expiry is preserved and the command does not silently become next-schedule hold or physical Manual.

#### Scenario: Manual or Hold without expiry
- **WHEN** the caller explicitly chooses Manual or Hold without an expiry
- **THEN** the documented endpoint semantics apply and no existing timed expiry is claimed to survive automatically.

### Requirement: Nonreplayed bounded adjustment
Relative writes SHALL obey the existing per-entity serialization, cooldown, operation timeout and confirmation deadline. They SHALL NOT retry after uncertain acceptance, invent a resulting target from stale state, or let an older read confirm newer intent. Unload SHALL cancel pending work.

#### Scenario: Rapid adjustments and stale reads
- **WHEN** two relative actions arrive rapidly and the first readback is stale
- **THEN** the accepted actions remain ordered, no delta is replayed or added to a stale local base, and only a compatible later read confirms the latest target.

#### Scenario: Accepted write with failed readback
- **WHEN** a relative PUT may have succeeded but subsequent GET fails
- **THEN** HA surfaces an unconfirmed outcome and schedules bounded reads without reapplying the delta.

#### Scenario: Definite unauthorized write versus readback
- **WHEN** a relative PUT returns a definite HTTP 401
- **THEN** one forced-refresh retry of that rejected PUT is permitted, while a 401 on GET after a successful PUT can retry only the GET.

#### Scenario: Cooldown, timeout or unload
- **WHEN** adjustment is attempted during cooldown, exceeds its operation budget or is unloaded
- **THEN** it rejects or cancels under the existing safeguards without queued writes or leaked timers.

### Requirement: Action UI boundary
Adjustment SHALL be usable through an integration action targeting the existing entity. It SHALL NOT require helpers, entity replacement or dashboard customization, and SHALL NOT claim to add relative controls or an expiry picker to the standard thermostat card.

#### Scenario: Automation requests an adjustment
- **WHEN** a user selects the supported adjustment action
- **THEN** it targets their existing thermostat entity with a delta in HA units.
