# Spec Delta

## ADDED Requirements

### Requirement: Compatible preset inputs and canonical output
The beta SHALL advertise and accept `Run Schedule`, `Temporary Hold`, `Permanent Hold`, `run_schedule`, `temporary_hold`, and `permanent_hold`, with title-case choices first. Each alias SHALL invoke the same control as its title-case equivalent. Reported preset state SHALL use the title-case value independently of the input spelling.

#### Scenario: Framework accepts every supported spelling
- **WHEN** an HA preset action supplies any of the six advertised values
- **THEN** framework validation accepts it and the corresponding schedule or hold control is invoked.

#### Scenario: Confirmed state after an alias
- **WHEN** an alias command is accepted and subsequent API data confirms the requested preset
- **THEN** reported preset state uses its title-case equivalent and existing bounded confirmation behavior remains in effect before confirmation.

#### Scenario: Unsupported spelling
- **WHEN** an action supplies an unadvertised preset
- **THEN** it fails validation without a thermostat write.

### Requirement: Preset state transition guidance
Upgrade instructions SHALL explain that snake_case action calls remain accepted while state-trigger and template comparisons must use the reported title-case values. The integration SHALL NOT rewrite user automations or create replacement entities for this transition.

#### Scenario: Existing state comparison
- **WHEN** an automation compares preset state with `permanent_hold`
- **THEN** documentation directs the user to compare with `Permanent Hold` while preserving the existing entity reference.

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
