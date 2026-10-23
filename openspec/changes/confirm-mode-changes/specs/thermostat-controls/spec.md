# Standby assumption delta

## ADDED Requirements

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
