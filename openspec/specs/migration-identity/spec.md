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

### Requirement: Account-scoped migration guidance
Installation and authentication guidance SHALL explain that users can start authorization from any matching legacy thermostat entry belonging to the account being signed in. Guidance SHALL describe account-scoped consolidation, ownership verification, retained unrelated entries, and retryable repair prompts without recommending deletion or recreation of NuHeat entries.

#### Scenario: Several thermostats on one account
- **WHEN** several legacy entries correspond to thermostats verified on the authorized account
- **THEN** instructions explain that migration can consolidate them while retaining entity identities and that separate authorization per thermostat is unnecessary.

#### Scenario: Remaining repair prompts
- **WHEN** ownership cannot be verified, an unrelated entry remains, or cleanup needs retrying
- **THEN** instructions explain that prompts can remain and direct users to retry or seek help without deleting entries or bypassing ownership checks.
