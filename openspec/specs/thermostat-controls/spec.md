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
