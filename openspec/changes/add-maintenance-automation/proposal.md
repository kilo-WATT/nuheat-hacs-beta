# Proposal

## Why

The beta already validates runtime tests, lint, packaging and OpenSpec structure, but dependency updates remain manual and CI does not exercise the official HACS repository validator. Add bounded maintenance automation without changing the working integration or publication process.

## What Changes

- Add weekly Dependabot PRs for GitHub Actions, npm development tooling and Ruff, with grouped updates and small per-ecosystem PR limits. Preserve coordinated HA/frontend/test-plugin and runtime SDK pins for manual updates.
- Add an independent HACS integration validation check on PRs, pushes, manual dispatch and a weekly schedule, with PR comments disabled and no automatic catalog submission.
- Document failure triage, upstream validator mutability, manual review and evidence limits.
- Defer CodeQL enablement to a separate reviewed follow-up using GitHub default setup initially; do not introduce duplicate scanning configurations now.
- Keep automatic merging, release publication, issue closure and branch-protection changes out of scope.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `maintainer-tools`: Bounded dependency update proposals and unprivileged validation automation.
- `release-distribution`: Independent HACS repository validation with explicit limits on compatibility claims.

## Impact

Observed evidence: `.github/workflows/validate.yml` runs pytest, Ruff and the package builder; `specs.yml` validates pinned OpenSpec tooling. No Dependabot or HACS workflow exists. `requirements-test.txt` pins a coordinated HA stack and SDK; the runtime SDK also appears in the integration manifest and package provenance checks.

Proposed implementation affects this beta repository only: `.github/dependabot.yml`, a new HACS workflow, maintainer/development documentation, relevant workflow checks and specification traceability. No Core, SDK, runtime, OAuth, migration, entity identity, thermostat control or handoff changes. HACS remains a custom repository; developer automation stays outside the release ZIP. Community users see no thermostat behavior change.
