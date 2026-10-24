# Relative temperature controls delta

## Purpose

Provide an explicit temperature adjustment action after vendor delta semantics
are verified, preserving existing absolute controls and thermostat hold intent.

## ADDED Requirements

### Requirement: Explicit verified adjustment
A relative-temperature action SHALL be exposed only after the vendor reference temperature, signed scaling, supported modes, expiry behavior and range validation are verified. Ordinary set-temperature SHALL remain absolute. Unverified combinations SHALL be rejected before writing rather than silently converted to Manual or guessed absolute targets.

#### Scenario: Unknown reference temperature
- **WHEN** the API's relative base or mode preservation is unverified
- **THEN** no relative control is exposed as supported and the existing absolute controls remain unchanged.

### Requirement: Correct delta units and mode intent
Adjustment SHALL accept finite deltas in HA's configured units and convert temperature differences without absolute-temperature offsets. It SHALL preserve verified mode/preset and explicit hold expiry, including accepted pending expiry. Standby, unknown states and unsupported Permanent Hold combinations SHALL be rejected without writes.

#### Scenario: Fahrenheit adjustment
- **WHEN** a supported thermostat receives a +1.8°F adjustment
- **THEN** the delta is encoded as +1°C without adding or subtracting 32.

#### Scenario: Pending timed hold
- **WHEN** a relative adjustment follows an accepted timed-hold command before cloud confirmation
- **THEN** the accepted expiry is preserved and the command does not silently become next-schedule hold or physical Manual.

### Requirement: Nonreplayed bounded adjustment
Relative writes SHALL obey the existing per-entity serialization, cooldown, operation timeout and confirmation deadline. They SHALL NOT retry after uncertain acceptance, invent a resulting target from stale state, or let an older read confirm newer intent. Unload SHALL cancel pending work.

#### Scenario: Rapid adjustments and stale reads
- **WHEN** two relative actions arrive rapidly and the first readback is stale
- **THEN** the accepted actions remain ordered, no delta is replayed or added to a stale local base, and only a compatible later read confirms the latest target.

#### Scenario: Accepted write with failed readback
- **WHEN** a relative PUT may have succeeded but subsequent GET fails
- **THEN** HA surfaces an unconfirmed outcome and schedules bounded reads without reapplying the delta.

#### Scenario: Cooldown, timeout or unload
- **WHEN** adjustment is attempted during cooldown, exceeds its operation budget or is unloaded
- **THEN** it rejects or cancels under the existing safeguards without queued writes or leaked timers.

### Requirement: Action UI boundary
Adjustment SHALL be usable through an integration action targeting the existing entity. It SHALL NOT require helpers, entity replacement or dashboard customization, and SHALL NOT claim to add relative controls or an expiry picker to the standard thermostat card.

#### Scenario: Automation requests an adjustment
- **WHEN** a user selects the supported adjustment action
- **THEN** it targets their existing thermostat entity with a delta in HA units.
