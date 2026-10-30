# Spec Delta

## ADDED Requirements

### Requirement: Account-scoped migration guidance
Installation and authentication guidance SHALL explain that users can start authorization from any matching legacy thermostat entry belonging to the account being signed in. Guidance SHALL describe account-scoped consolidation, ownership verification, retained unrelated entries, and retryable repair prompts without recommending deletion or recreation of NuHeat entries.

#### Scenario: Several thermostats on one account
- **WHEN** several legacy entries correspond to thermostats verified on the authorized account
- **THEN** instructions explain that migration can consolidate them while retaining entity identities and that separate authorization per thermostat is unnecessary.

#### Scenario: Remaining repair prompts
- **WHEN** ownership cannot be verified, an unrelated entry remains, or cleanup needs retrying
- **THEN** instructions explain that prompts can remain and direct users to retry or seek help without deleting entries or bypassing ownership checks.
