# Thermostat controls delta

## ADDED Requirements

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
