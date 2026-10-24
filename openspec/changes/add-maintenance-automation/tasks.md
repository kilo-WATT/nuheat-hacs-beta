# Tasks

## 1. Bounded dependency proposals

- [x] 1.1 Add weekly Actions/npm/pip Dependabot configuration with per-ecosystem grouping, two-open-PR limits and a Ruff-only pip allowlist; verify parsed configuration excludes coordinated HA/frontend/plugin/SDK version updates.
- [x] 1.2 Add focused configuration-contract tests for scope, schedules, limits and absence of automerge/publication; run those tests using synthetic local configuration only.
- [x] 1.3 Document manual review, coordinated compatibility updates, npm lockfile/generated-skill review and the distinction between version-update limits and security updates in maintainer/development guidance; verify instructions match the configuration.

## 2. Independent HACS validation

- [x] 2.1 Review the current official action inputs and reference-selection code, then add a source-pinned integration-validation workflow for PR/push/manual/weekly events with comments disabled, read-only permissions and a bounded timeout; verify the selected action and its mutable container boundary are recorded without introducing secrets or privileged triggers.
- [x] 2.2 Add focused checks for workflow events, permissions, comment suppression, timeout and no publish operations; validate YAML/workflow syntax with appropriate tooling and run the configuration-contract tests.
- [x] 2.3 Document HACS failure triage, custom-repository scope, upstream mutability, checked-reference evidence and limits versus release/UI/migration checks; verify no catalog submission, blanket ignored checks or production steps are introduced.
- [x] 2.4 Update maintainer release-verification examples to require the new HACS workflow for post-adoption releases via repeated `--workflow` arguments while retaining historical two-workflow expectations; verify workflow names against YAML and existing verifier tests without changing verifier defaults.

## 3. Integration validation and evidence

- [x] 3.1 Update specification traceability and record CodeQL default-setup assessment as a deferred follow-up without enabling it; verify every new requirement maps to a configuration check or explicitly pending hosted observation.
- [x] 3.2 Run `npm run specs:check`, `python -m pytest -q`, `ruff check custom_components tests tools` and `python tools/package.py` in the supported isolated environment; record results and confirm runtime source, SDK/test-stack pins and ZIP runtime membership are unchanged.
- [ ] 3.3 When separately authorized to push/run GitHub CI, verify exact-commit existing checks and the new HACS check, record the actual reference checked and assess fork/Dependabot compatibility; leave this task pending if remote validation is not authorized or unavailable.

## Workflow follow-up

- After separate merge approval, observe Dependabot's first default-branch update check and resulting eligible PR or no-update result; local schema checks alone do not prove hosted bot operation.
- Sync and archive only after implementation and required evidence are complete; retain explicit pending evidence rather than marking unobserved behavior passed.
- Propose CodeQL enablement separately after reviewing the first phase; prefer default setup initially and avoid duplicate advanced/default scans.
- No runtime release is needed for these maintainer-only changes. GitHub settings, production access, commits, pushes, merges and publication remain governed by the user's current authorization.
