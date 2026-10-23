# Migration and identity

## Purpose
Keep existing users' configuration, entity references, and registry relationships through legacy-to-beta migration and a compatible official Core transition.

## Requirements

### Requirement: Stable domain and identity
The integration SHALL retain the nuheat domain and matching thermostat identity so users can keep existing entity IDs, registry associations, dashboards, and automations wherever matching data permits. Upgrades SHALL NOT instruct users to delete and recreate NuHeat entries.

#### Scenario: Matching legacy thermostat
- **WHEN** a legacy thermostat is matched during account migration
- **THEN** the surviving configuration retains its existing registry identity and entity references.

### Requirement: Ownership before cleanup
Legacy consolidation SHALL validate the OAuth account and device ownership before transferring registry associations or removing redundant entries. Unmatched entries SHALL remain available for a later migration attempt.

#### Scenario: Thermostat cannot be matched
- **WHEN** a legacy entry's thermostat is not proven to belong to the linked account
- **THEN** the entry is retained and cleanup does not guess ownership.

### Requirement: Reversible transfer and explicit recovery
Migration SHALL preserve rollback safeguards, retry deferred cleanup, and surface incomplete restoration through existing repair guidance. A validation failure SHALL NOT be worked around by discarding registry or credential associations.

#### Scenario: Registry transfer fails
- **WHEN** migration cannot safely complete ownership transfer
- **THEN** it attempts restoration and reports unrecovered state instead of silently deleting configuration.

### Requirement: Transient device absence
A temporary account read omitting a known device SHALL NOT remove its entity or registry identity. Availability SHALL reflect missing or offline devices without requiring re-creation.

#### Scenario: Device disappears from one response
- **WHEN** a successful account response temporarily omits an existing thermostat
- **THEN** its known entity is retained and marked unavailable as appropriate.
