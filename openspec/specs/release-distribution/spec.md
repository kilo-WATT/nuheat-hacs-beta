# Distribution and release readiness

## Purpose
Make custom-repository installation, upgrades, and release claims match the exact validated NuHeat build while protecting private information.

## Requirements

### Requirement: Tagged HACS installation
The beta SHALL be installable as a HACS custom repository using an explicit published tag. Instructions SHALL require verifying HACS's tracked tag rather than relying only on the manifest version or installing main. Prereleases SHALL require beta visibility; regular releases SHALL be discoverable without it.

#### Scenario: User installed a branch
- **WHEN** HACS tracks main or a commit instead of the release tag
- **THEN** instructions switch the download reference without deleting NuHeat configuration.

### Requirement: Release consistency
Published code SHALL match its tag, manifest, dependency pins, and audited package contents. Revisions retaining a prerelease version SHALL explain redownload requirements. Publication status SHALL distinguish unofficial community beta software from GitHub's prerelease flag.

#### Scenario: Earlier b7 prerelease is installed
- **WHEN** a user needs the final same-version b7 files
- **THEN** instructions explicitly require redownloading the tag and restarting HA.

### Requirement: Evidence-based readiness
Release claims SHALL separate synthetic tests, live authorization, approved hardware tests, and unverified models or firmware. Changes affecting controls SHALL cover stale responses, failures, rapid commands, and cleanup across every affected interaction.

#### Scenario: Validation is incomplete
- **WHEN** a model, transition, or behavior has not been exercised
- **THEN** the record marks that limit instead of claiming it passed.

### Requirement: Development-only tooling
OpenSpec, agent workflows, Node tooling, planning files, and dependency caches SHALL remain outside the Home Assistant runtime dependency set and allowlisted HACS release ZIP.

#### Scenario: A release package is built
- **WHEN** developer specification tooling is present in the checkout
- **THEN** the integration's runtime files and Python dependency contract are unchanged and development-only files are excluded.

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
