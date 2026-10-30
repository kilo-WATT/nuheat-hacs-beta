# Spec Delta

## MODIFIED Requirements

### Requirement: Temperature and time validation
The action SHALL use HA's configured temperature unit and validate finiteness and the same inclusive 5–35°C range as ordinary temperature controls. Offset-free times SHALL use HA's timezone. Past, nonexistent, and ambiguous local times SHALL be rejected before a write; an explicit valid UTC offset SHALL disambiguate a repeated hour.

#### Scenario: Fahrenheit target
- **WHEN** HA uses Fahrenheit and a valid Fahrenheit target is supplied
- **THEN** the API receives the equivalent Celsius value.

#### Scenario: Repeated daylight-saving hour
- **WHEN** an offset-free expiry falls in a repeated local hour
- **THEN** no write occurs and the user is asked for an unambiguous expiry.

#### Scenario: Lower-bound timed hold
- **WHEN** a timed-hold action requests 5°C or 41°F with a valid future expiry
- **THEN** range validation accepts it and the requested expiry is retained.

#### Scenario: Invalid numeric target
- **WHEN** the target is nonfinite or outside the supported range
- **THEN** validation rejects it without a write.
