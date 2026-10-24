# maintainer-tools Specification

## Purpose

Give contributors documented maintainer commands with explicit input views,
privacy boundaries and no hidden changes to thermostat or publication state.

## Requirements

### Requirement: Supported and historical command boundaries
Maintainer documentation SHALL distinguish supported commands from historical migration/adaptation helpers. Importing a tool or asking for help SHALL NOT rewrite source, contact HA, run tests or publish. Historical commands SHALL explain their pinned scope and fail safely on ordinary invocation instead of silently applying old transformations.

#### Scenario: Contributor imports a historical helper
- **WHEN** an old adaptation or transition module is imported
- **THEN** no source, storage, process or network operation occurs.

#### Scenario: Old command is run normally
- **WHEN** a contributor invokes an obsolete entry point
- **THEN** it explains its historical status and supported replacement without rewriting files or suggesting its result proves current Core compatibility.

### Requirement: Explicit privacy audit views
The audit SHALL require a private baseline outside the repository and distinguish working-tree content from index content. Working-tree mode SHALL include nonignored untracked files and account for deleted paths; staged mode SHALL inspect indexed bytes. Selected ZIP contents SHALL also be scanned. Output SHALL contain counts and safe finding categories, never matched private values or content.

#### Scenario: Safe index and private unstaged edit
- **WHEN** a private marker exists only in the working tree
- **THEN** working-tree mode fails and staged mode reports its separate index result without claiming the working tree is clean.

#### Scenario: Private untracked file or ZIP member
- **WHEN** a nonignored untracked file or selected ZIP contains a baseline marker
- **THEN** the audit fails without printing that marker, its containing content or potentially private filenames.

### Requirement: Narrow public registration recognition
The approved shared registration SHALL be recognized only at its expected runtime path with matching audited source bytes. Other private values and unexpected registration copies SHALL remain findings. Missing or changed registration provenance SHALL fail closed; the audit SHALL NOT blanket-ignore credential keys, files or archive members.

#### Scenario: Approved registration and private account token
- **WHEN** the expected registration matches provenance but a separate account token appears
- **THEN** registration recognition does not suppress the token finding.

#### Scenario: Copied or changed registration
- **WHEN** registration values appear at an unexpected location or the expected file differs from its approved hash
- **THEN** the audit fails without exposing those values.
