# Timed holds delta

## MODIFIED Requirements

### Requirement: Temperature and time validation
The action SHALL use HA's configured temperature unit and validate the supported range and finiteness. Offset-free times SHALL use HA's timezone. Past, nonexistent, and ambiguous local times SHALL be rejected before a write; an explicit valid UTC offset SHALL disambiguate a repeated hour. Once verified for v2, the vendor's maximum duration SHALL also be enforced without silent clipping.

#### Scenario: Fahrenheit target
- **WHEN** HA uses Fahrenheit and a valid Fahrenheit target is supplied
- **THEN** the API receives the equivalent Celsius value.

#### Scenario: Repeated daylight-saving hour
- **WHEN** an offset-free expiry falls in a repeated local hour
- **THEN** no write occurs and the user is asked for an unambiguous expiry.

#### Scenario: Expiry exceeds the confirmed maximum
- **WHEN** a new explicit expiry exceeds the maximum verified for the v2 endpoint
- **THEN** the action rejects before a thermostat write, states the supported limit and does not clamp the supplied time.

#### Scenario: Duration crosses a clock change
- **WHEN** a valid offset-aware expiry crosses a daylight-saving transition
- **THEN** duration is evaluated as elapsed UTC time using the verified boundary policy rather than wall-clock hours.

## ADDED Requirements

### Requirement: Evidence before enforcing vendor duration
The duration policy SHALL distinguish the guide's documented 23-hour window from verified v2 behavior. Its endpoint applicability, boundary inclusion and clock basis SHALL be recorded before enabling a new limit. Missing confirmation SHALL remain an explicit blocker, not evidence of a different limit or permission for long live tests.

#### Scenario: Guide and schema differ in detail
- **WHEN** the guide states 23 hours but v2 Swagger supplies no duration bound and no v2 confirmation exists
- **THEN** documentation reports the documented restriction and outstanding confirmation without claiming tested enforcement or changing the current runtime.

### Requirement: Preserve existing holds and next-schedule behavior
The new duration policy SHALL NOT rewrite or shorten existing holds, change next-schedule Temporary hold meaning, alter Permanent Hold or remove existing entity/configuration data. Existing expiry readback SHALL remain visible even if it exceeds a new-command limit. Retargeting such a hold SHALL follow the separately verified vendor policy without clipping expiry or silently changing mode.

#### Scenario: Existing longer hold
- **WHEN** a successful read returns an explicit expiry beyond the newly confirmed new-command window
- **THEN** HA retains the readback and entity identity without issuing a corrective thermostat command.

#### Scenario: Retargeting is disallowed by verified policy
- **WHEN** a target change would retain an expiry that the vendor rejects for new commands
- **THEN** HA explains the unsupported change before writing and preserves the existing hold without silently converting it.

#### Scenario: Ordinary preset and Permanent Hold
- **WHEN** a user selects next-schedule Temporary hold or Permanent hold
- **THEN** the explicit-expiry duration limit is not substituted for those existing control meanings.
