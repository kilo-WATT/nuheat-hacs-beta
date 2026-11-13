# Thermostat controls

## Purpose
Define the mode and preset behavior users can rely on while retaining their existing NuHeat thermostat entities.

## Requirements

### Requirement: Distinct modes and presets
The integration SHALL expose Run schedule, Temporary hold, and Permanent hold as presets. Scheduled and held operation SHALL use Auto; physical Manual SHALL use Heat. Off SHALL retain NuHeat's frost-protected Standby behavior, not claim hard power off.

#### Scenario: Permanent Hold is confirmed
- **WHEN** compatible API details confirm Auto-family Permanent Hold
- **THEN** HA reports Auto with the Permanent hold preset rather than an unknown preset.

#### Scenario: Physical Manual is confirmed
- **WHEN** compatible API details confirm physical Manual
- **THEN** HA reports Heat without labeling it Permanent hold.

#### Scenario: Standby is selected
- **WHEN** a user selects Off
- **THEN** the existing frost-protected 5 C / 41 F command is retained.

### Requirement: Conservative state classification
The integration SHALL correlate available v1/v2 details before distinguishing overlapping Manual and Permanent Hold states. Missing or conflicting details SHALL NOT justify guessing Permanent Hold or changing a possible hold implicitly to Manual.

#### Scenario: Details are missing
- **WHEN** a mode-3 response needs supplementary details but they are unavailable
- **THEN** no Permanent hold preset is invented and an implicit target change requiring that distinction is rejected.

### Requirement: Preset command meaning
Run schedule SHALL request scheduled operation. Temporary hold selected as a preset SHALL hold until the next scheduled event. Permanent hold SHALL preserve an explicit target indefinitely until superseded.

#### Scenario: Returning to schedule
- **WHEN** Run schedule is selected during a hold
- **THEN** HA sends the schedule command and displays the scheduled target when readback confirms it.

#### Scenario: Selecting ordinary Temporary hold
- **WHEN** the standard-card Temporary hold preset is selected
- **THEN** no arbitrary expiry is invented; the command uses the next-schedule behavior.

### Requirement: Bounded Standby display assumptions
An accepted Off command's optimistic display SHALL stop being assumed when Standby is confirmed and SHALL expire when its confirmation deadline passes. A later confirmed external mode change SHALL be able to update HA's displayed mode.

#### Scenario: Standby confirms on a delayed read
- **WHEN** the API confirms Standby after an initially stale response
- **THEN** HA reports authoritative Off and does not retain an indefinite assumed-state flag.

#### Scenario: Standby never confirms
- **WHEN** the confirmation deadline expires without Standby readback
- **THEN** HA stops treating the requested Off as confirmed and reports current readback plus the unconfirmed outcome.

#### Scenario: Thermostat resumes externally
- **WHEN** a later successful poll reports scheduled or held operation
- **THEN** an obsolete Standby assumption does not keep HA displaying Off.

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

### Requirement: Explicit beta temperature bounds
The beta SHALL advertise and accept targets from 5°C through 35°C inclusive, equivalently 41°F through 95°F. Temperature actions SHALL preserve their intended mode and active hold expiry. A 5°C target SHALL NOT itself select Off. Existing explicit Off behavior SHALL remain unchanged, and vendor rejection SHALL surface without clipping or fallback writes.

#### Scenario: Lower boundary with a hold
- **WHEN** a user sets 5°C or its Fahrenheit equivalent during an active timed hold
- **THEN** the command passes HA range validation and retains the hold expiry and intended mode.

#### Scenario: Out-of-range target
- **WHEN** a requested target is below 5°C or above 35°C
- **THEN** it is rejected before a write.

#### Scenario: Device rejects an in-range target
- **WHEN** the vendor rejects an otherwise valid target
- **THEN** existing failure handling reports the failure without claiming successful confirmation or issuing a substitute mode command.

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

### Requirement: Current climate temperature compatibility
The beta SHALL use the supported native temperature interface on current HA without emitting temperature deprecation warnings during setup, state reporting or controls. The advertised minimum HA version SHALL retain working temperature display and services through its supported interface.

#### Scenario: Current-framework setup
- **WHEN** the NuHeat climate entity is set up on HA with the native temperature interface
- **THEN** setup and normal temperature controls produce no integration temperature deprecation warnings.

#### Scenario: Minimum-supported framework
- **WHEN** the entity loads on HA 2026.10.2
- **THEN** display and controls remain functional in both Celsius and Fahrenheit.

### Requirement: Single temperature conversion boundary
Displayed temperatures and limits SHALL match the configured units. Ordinary climate actions and the custom timed-hold action SHALL each convert their user input to the SDK Celsius value exactly once, retaining intended mode, pending intent and explicit expiry.

#### Scenario: Fahrenheit ordinary temperature command
- **WHEN** an ordinary climate action requests 77 Fahrenheit
- **THEN** the SDK receives 25 Celsius with the existing mode and hold selection.

#### Scenario: Fahrenheit explicit hold action
- **WHEN** the NuHeat hold action requests 77 Fahrenheit with a valid explicit expiry
- **THEN** the SDK receives 25 Celsius and that exact canonical expiry.

#### Scenario: Pending target after successful write
- **WHEN** a Fahrenheit command succeeds and the cloud still returns the earlier target
- **THEN** HA displays the accepted requested target while existing bounded confirmation is pending.

#### Scenario: Write failure and shutdown
- **WHEN** a write fails or the entity unloads during temperature control
- **THEN** existing failure handling, no-replay behavior and timer cleanup remain effective.

#### Scenario: Limits and Standby
- **WHEN** HA advertises bounds or a user sets 5 Celsius or 41 Fahrenheit
- **THEN** bounds remain 5 through 35 Celsius or 41 through 95 Fahrenheit and an ordinary target request retains its intended mode.
