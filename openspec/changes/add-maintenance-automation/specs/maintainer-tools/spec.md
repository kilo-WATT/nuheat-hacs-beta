## ADDED Requirements

### Requirement: Bounded dependency update proposals
Automated version updates SHALL propose reviewed PRs on a weekly schedule with per-ecosystem grouping and finite open-PR limits. Initial coverage SHALL include Actions, npm development tooling and Ruff only; coordinated HA, frontend, test-plugin and runtime SDK updates SHALL remain manual. Automation SHALL NOT merge or publish changes.

#### Scenario: Development tooling update is available
- **WHEN** the weekly update check finds an eligible dependency update
- **THEN** it proposes a reviewable PR subject to existing validation and the configured open-PR limit, without merging or publishing.

#### Scenario: Coordinated runtime or test-stack update is available
- **WHEN** an update affects the HA compatibility set or runtime SDK
- **THEN** the version-update configuration does not propose an isolated bump and documentation explains the coordinated manual process.

### Requirement: Unprivileged maintenance validation
Maintenance checks SHALL operate without production access, NuHeat account credentials or a private audit baseline. They SHALL use read-only repository permissions, run untrusted PR content without privileged triggers, and report failures without changing runtime configuration or publishing. Additional scanning or repository-setting changes SHALL require separate reviewed scope.

#### Scenario: Fork or dependency-bot pull request runs validation
- **WHEN** a fork or Dependabot PR triggers maintenance checks
- **THEN** checks require no private secrets or write permissions and do not contact HA or issue thermostat commands.

#### Scenario: External validator is unavailable
- **WHEN** an upstream request or validator fails
- **THEN** the check reports unsuccessful validation without silently passing, changing settings or publishing.
