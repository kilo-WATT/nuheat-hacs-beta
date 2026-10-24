## ADDED Requirements

### Requirement: Independent HACS repository validation
The custom repository SHALL run HACS integration validation on PRs, pushes, manual requests and a weekly schedule without catalog submission or PR comments. Failures SHALL be investigated before narrowly documented exceptions are introduced. Reports SHALL identify the checked reference and distinguish repository validation from release-byte, installation, migration and hardware evidence.

#### Scenario: Candidate pull request is validated
- **WHEN** HACS validation runs for a pull request
- **THEN** evidence identifies the candidate branch or revision checked and does not claim that a previously published tag was validated instead.

#### Scenario: Upstream HACS behavior changes
- **WHEN** a scheduled validation fails after an upstream validator change
- **THEN** maintainers receive a failed check for triage without catalog submission, publication or automatic suppression.

#### Scenario: Repository validation passes
- **WHEN** HACS accepts the checked repository structure
- **THEN** documentation does not infer correct default release selection, successful UI installation, retained entities or live thermostat behavior from that result alone.

#### Scenario: Retained Core domain fails custom brands lookup
- **WHEN** the action rejects the existing Core domain because its lookup accepts only custom brand registration or local assets
- **THEN** only the investigated brands check is excluded with documented owner approval, repository topics and other checks remain validated, and runtime identity and package contents stay unchanged.
