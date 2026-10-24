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
