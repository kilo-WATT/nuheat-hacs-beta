# community-support Specification

## Purpose

Help users report actionable NuHeat problems and contributors connect fixes to reviewable design and release evidence without disclosing private account data.

## Requirements

### Requirement: Structured issue intake
The repository SHALL offer bug, feature-request and installation-help forms. Bug reports SHALL collect HA and integration versions, HACS-tracked tag or branch, setup history, reproduction steps, expected behavior and actual behavior. Optional details SHALL permit unknown model or firmware values.

#### Scenario: Existing installation cannot authenticate
- **WHEN** a user reports an authentication failure after updating a legacy installation
- **THEN** the form distinguishes setup history and installed reference without asking the user to delete entries or recreate entities.

#### Scenario: User needs installation help
- **WHEN** a user opens the issue chooser
- **THEN** installation help and links to existing documentation are available without requiring OpenSpec or developer tools.

### Requirement: Public report privacy
All support forms SHALL explain that submissions are public and request removal of tokens, passwords, authorization headers, serial numbers, callback URLs and private configuration storage. Sanitized logs SHALL be optional, and no form SHALL require account identifiers or full configuration exports.

#### Scenario: Logs might contain private data
- **WHEN** a user reaches the optional log field
- **THEN** the form presents redaction instructions before submission and offers reporting without logs.

### Requirement: Contributor traceability
Contributor guidance and the PR template SHALL connect related issues, applicable OpenSpec changes, implementation scope, verification and release impact. Documentation-only contributions SHALL NOT require runtime tests or a new behavior proposal unless behavior actually changes.

#### Scenario: Runtime control fix is proposed
- **WHEN** a contributor prepares a thermostat control PR
- **THEN** the template asks for relevant failure, stale-read, rapid-command and lifecycle coverage plus migration, identity and Core-compatibility impact.

#### Scenario: A typo is corrected
- **WHEN** a contributor changes documentation only
- **THEN** guidance permits proportionate documentation checks without live hardware or a full HA regression run.

### Requirement: Lightweight issue triage
The repository SHALL document a small catalog of issue-type, affected-area and information/vendor-wait labels. Triage SHALL link confirmed fixes to a PR and released version, and SHALL NOT close reports solely because they become inactive.

#### Scenario: A fix is merged but not released
- **WHEN** a maintainer updates a confirmed bug
- **THEN** the issue distinguishes the implementing PR from the published version that users can actually install.

#### Scenario: Vendor confirmation is required
- **WHEN** investigation needs Chemelex input
- **THEN** triage records that dependency without representing a vendor restriction as confirmed evidence.
