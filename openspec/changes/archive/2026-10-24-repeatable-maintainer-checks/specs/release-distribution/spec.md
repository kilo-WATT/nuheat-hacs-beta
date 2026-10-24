# Release verification delta

## ADDED Requirements

### Requirement: Read-only reproducible release verification
A parameterized verifier SHALL check the requested repository, tag and expected commit without publishing, editing releases, changing branches, installing into HA or issuing thermostat commands. It SHALL report structured pass, fail or incomplete evidence with a nonzero exit for required failed or incomplete checks. Remote failures SHALL NOT become success.

#### Scenario: Tag points to another commit
- **WHEN** the requested published tag resolves to a commit other than the supplied expected commit
- **THEN** verification fails before claiming matching release contents.

#### Scenario: Network or CI result is unavailable
- **WHEN** a required request times out or an exact-commit CI run is incomplete
- **THEN** the report marks that check incomplete and exits nonzero without remote mutation.

### Requirement: Independent publication and package evidence
Verification SHALL compare release flags/latest status, the resolved tag, manifest version, public SDK version, required exact-commit CI, asset checksums and runtime bytes from the selected tag. It SHALL validate archive paths, duplicates and bounded downloads without executing downloaded source. A matching version string alone SHALL NOT establish byte identity.

#### Scenario: Correct version with stale files
- **WHEN** a downloaded package reports the requested version but its runtime source differs from the tag
- **THEN** verification fails and reports a byte-mismatch category without dumping source or credentials.

#### Scenario: Unsafe archive
- **WHEN** an asset contains duplicate, traversal or unexpected runtime members
- **THEN** verification rejects it without extracting files outside isolated temporary storage or executing code.

#### Scenario: SDK unavailable
- **WHEN** the manifest pins a development or unpublished SDK
- **THEN** the dependency check fails even if local tests used an installed wheel.

### Requirement: Explicit HACS visibility and ordering evidence
Verification SHALL distinguish regular-release visibility with beta versions disabled, explicit-tag download availability and the first/default release-list selection. It SHALL NOT infer that the first returned item equals GitHub latest, or silently sort metadata to claim observed HACS behavior. UI installation SHALL not be claimed from metadata or archive checks alone.

#### Scenario: b9 precedes latest b10
- **WHEN** GitHub latest is b10 but the release list returns regular b9 first
- **THEN** the report preserves that order, checks b10 visibility and explicit-tag contents, and records default-selection uncertainty or mismatch separately.

#### Scenario: Prerelease visibility
- **WHEN** the selected release is a prerelease
- **THEN** the report states beta visibility is required and does not call it visible in the regular-only list.
