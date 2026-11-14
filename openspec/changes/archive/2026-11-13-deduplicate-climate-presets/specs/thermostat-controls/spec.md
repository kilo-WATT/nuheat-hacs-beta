# Thermostat controls delta

## REMOVED Requirements

### Requirement: Compatible preset inputs and canonical output
**Reason**: The approved three-choice interface retires the six-spelling input contract.
**Migration**: Replace Run Schedule, Temporary Hold and Permanent Hold action values and state comparisons with run_schedule, temporary_hold and permanent_hold respectively. Keep the same entity references.

## ADDED Requirements

### Requirement: Canonical preset choices
The beta SHALL advertise and accept exactly run_schedule, temporary_hold and permanent_hold and report those values as preset state. Entity translations SHALL display Run schedule, Temporary hold and Permanent hold. Each value SHALL retain its control meaning. Retired title-case action values SHALL fail validation before a thermostat write.

#### Scenario: Three visible choices
- **WHEN** HA obtains preset_modes for a NuHeat climate entity
- **THEN** exactly the three canonical values are advertised, once each.

#### Scenario: Framework accepts canonical values
- **WHEN** an HA preset action supplies any of the three canonical values
- **THEN** framework validation accepts it and invokes the existing schedule or hold command.

#### Scenario: Confirmed state after a command
- **WHEN** a canonical command is accepted and subsequent API data confirms its preset
- **THEN** the reported state is its canonical snake_case identifier and existing bounded confirmation applies before confirmation.

#### Scenario: Unsupported or retired spelling
- **WHEN** an action supplies an unadvertised value including a retired title-case input
- **THEN** framework validation rejects it before any thermostat write.

## MODIFIED Requirements

### Requirement: Preset state transition guidance
Upgrade instructions SHALL provide exact snake_case replacements for title-case action inputs, preset state comparisons and templates introduced by b11/b12. Existing snake_case inputs SHALL remain valid. The integration SHALL preserve entity references and SHALL NOT rewrite user automations automatically.

#### Scenario: Existing state comparison
- **WHEN** an automation compares preset state with Permanent Hold
- **THEN** documentation directs the user to compare with permanent_hold while preserving the existing entity reference.

#### Scenario: Existing action call
- **WHEN** an automation calls climate.set_preset_mode with Run Schedule, Temporary Hold or Permanent Hold
- **THEN** upgrade guidance maps the value to run_schedule, temporary_hold or permanent_hold respectively.

#### Scenario: Readable labels through HA translations
- **WHEN** HA resolves English translations for the three advertised preset identifiers
- **THEN** it finds exactly Run schedule, Temporary hold and Permanent hold, while stored preset_mode and preset_modes use snake_case identifiers.
