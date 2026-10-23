# Official Core handoff

## Purpose
Retire the custom beta only when an explicitly validated official implementation can safely use the user's existing NuHeat configuration.

## Requirements

### Requirement: Exact-source handoff gate
Automatic handoff SHALL require a match to an explicitly tested Core source allowlist. Unknown, missing, changed, or unreadable Core source SHALL leave the beta active. A PR update or merge SHALL NOT automatically expand that allowlist.

#### Scenario: Updated PR source is not allowlisted
- **WHEN** official Core files differ from the recorded compatible source
- **THEN** the beta continues running and does not retire its override.

### Requirement: Recoverable retirement
A compatible handoff SHALL preserve the beta files outside custom_components, retire the override, and request the restart needed to load Core. Failure SHALL preserve recoverable files and use the existing repair path.

#### Scenario: Compatible Core is found
- **WHEN** the tested source is present and retirement succeeds
- **THEN** the override is backed up outside the import path and a restart is requested.

### Requirement: Existing configuration continuity
The validated handoff SHALL retain entries, entity/device associations, Application Credentials, and account tokens. It SHALL NOT create a second account or new thermostat entities as a shortcut.

#### Scenario: Core starts after retirement
- **WHEN** the validated official implementation loads after restart
- **THEN** it uses the preserved entries and registry associations.
