# Release promotion delta

## ADDED Requirements

### Requirement: Release promotion consistency
When a prerelease is promoted, current default-branch installation instructions, current release summary and publication metadata SHALL describe the resulting GitHub status and HACS visibility. A promotion checklist SHALL verify these surfaces without changing runtime source, rewriting tags or replacing published assets.

#### Scenario: b8 becomes a regular latest release
- **WHEN** GitHub marks v0.1.0b8 regular and latest
- **THEN** current guidance names b8 as regular/latest and explains that beta visibility is unnecessary while retaining explicit tag verification and existing entries.

#### Scenario: Promotion follows user hardware feedback
- **WHEN** the maintainer records successful user testing
- **THEN** the evidence describes that feedback without inventing measured latency or treating it as exhaustive model coverage.

#### Scenario: Documentation changes after publication
- **WHEN** current documentation is corrected after promotion
- **THEN** historical packaged documentation remains associated with its original release and published tag and asset bytes stay unchanged.
