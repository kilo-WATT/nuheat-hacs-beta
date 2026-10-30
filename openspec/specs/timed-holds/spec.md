# Explicit timed holds

## Purpose
Allow a specific hold end time through an integration-provided action without adding thermostat entities or requiring dashboard customization.

## Requirements

### Requirement: Integration-provided hold action
The beta SHALL provide a Set temporary hold action targeting an existing NuHeat climate entity with a temperature and future expiry. Users SHALL NOT need to create the action, add helpers, or edit their dashboard to use it from HA Actions or automations.

#### Scenario: User sets a specific end time
- **WHEN** the user selects an existing NuHeat entity, valid target, and future expiry in the action form
- **THEN** the integration sends an explicit timed-hold command using that entity.

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

### Requirement: Preserve an accepted timed expiry
Changing the target SHALL retain an active explicit expiry, including while a newly accepted timed hold awaits cloud confirmation. A different explicit control SHALL supersede pending hold intent. Pending intent SHALL use the existing bounded confirmation deadline.

#### Scenario: Rapid target change
- **WHEN** the user changes temperature before the new timed expiry appears in API readback
- **THEN** the next target command retains the requested expiry instead of converting it to Permanent Hold or Manual.

### Requirement: Standard-card boundary
The standard thermostat card SHALL retain the Temporary hold preset's next-schedule meaning. The integration SHALL NOT claim that selecting it opens an expiry picker. A specific expiry SHALL be offered through the integration action; adding a field inside the standard card requires a separate frontend change.

#### Scenario: User asks for an end-time field
- **WHEN** the user looks for an expiry on the standard thermostat card
- **THEN** documentation explains the card limitation and points to the existing action without requiring dashboard edits.
