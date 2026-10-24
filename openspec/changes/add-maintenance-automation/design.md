# Design

## Context

See proposal.md for motivation and observed workflow coverage. Development tooling is excluded from the allowlisted ZIP. Existing release verification requires both current workflow names, so adding a third independent workflow does not automatically extend its default required-check list.

## Goals / Non-Goals

**Goals:** Reviewable maintenance proposals, independently visible HACS failures, low notification volume, and explicit evidence boundaries.

**Non-Goals:** Runtime changes, newer minimum HA versions, production/hardware access, Core or SDK edits, catalog submission, required-check settings, automatic merges/releases, or CodeQL activation in this change.

## Decisions

### Dependabot with an explicit initial allowlist

Add `.github/dependabot.yml` entries for `github-actions`, `npm` and `pip` at the repository root. Run weekly, group updates within each ecosystem and limit each ecosystem to two open version-update PRs. Pip allows only Ruff. HA, frontend, pytest plugin and chemelex SDK pins stay manual because compatibility and manifest/provenance changes must be coordinated. npm proposals update package.json and its lockfile together; generated OpenSpec skills require explicit review/regeneration when appropriate. Actions updates do not automatically maintain Python/Node version inputs.

Use existing repository labels only if verified; no new labels/settings are required. Keep major updates visible in PR content and review changelogs. Version-update limits and schedules must not be advertised as limits on separately enabled Dependabot security alerts/updates. Broad pip updates and cross-ecosystem groups are rejected initially because they obscure coordinated compatibility work.

### Separate HACS check with minimum permissions

Add `.github/workflows/hacs.yml` using `category: integration`, `comment: false`, `contents: read`, a bounded job timeout, standard `pull_request` (never `pull_request_target`), push, weekly schedule and workflow_dispatch. Use the ordinary ephemeral GitHub token; no PAT, account credentials or private baseline. Verify exact supported inputs and event/reference selection against the current action before implementation. Start with no ignored checks. Diagnose any failure before documenting a narrowly necessary custom-repository exception; do not change runtime files merely to satisfy catalog-only rules.

Pin action source to a reviewed commit with a version comment where useful. The currently inspected HACS action delegates to `docker://ghcr.io/hacs/action:main`; a source SHA alone does not freeze that image. Record this mutability in maintainer docs and run evidence. The weekly check intentionally detects validator drift. A digest-pinned replacement or self-maintained validator would introduce upkeep outside this phase.

### Keep evidence and permissions separate

Existing pytest/Ruff/package/OpenSpec workflows remain intact. The HACS workflow validates repository eligibility, while the release verifier independently checks tagged bytes and release ordering. Document its new workflow name and use the verifier's existing repeated `--workflow` options for post-adoption releases when requiring all three checks; historical releases keep their original two-check expectations. Do not silently make historical releases fail or alter verifier defaults in this change.

No HA access or thermostat tests are necessary for workflow-only changes. Add focused configuration-contract checks for allowlists, prohibited permissions/triggers, events and publication absence, rather than snapshots of whole YAML files. Validate actual hosted execution only when pushing/running CI is separately authorized; mark remote evidence pending otherwise.

### CodeQL follow-up

Record a separate future task to assess GitHub default CodeQL setup, initially Python, and review its first findings. Do not add an advanced workflow alongside default setup. Any enablement, alert triage policy or required-check setting needs its own reviewed scope. CodeQL cannot establish API correctness or replace private-value auditing.

## Risks / Trade-offs

### Approved hosted-validation adjustment

The first push and PR runs at `5228a6493460ebdc457bc4e59711c6770e91e9ea`
failed only topics and brands. The owner approved adding repository topics
`home-assistant`, `hacs`, `nuheat`, `custom-integration` and the narrow
`ignore: brands` exception. The action's brands validator checks local icon
assets or the custom brands list; retaining the existing Core domain does not
satisfy that lookup. Do not change the domain or runtime files to satisfy it.
All other checks remain active. This supersedes the initial no-exception/no-new-
settings starting point above; no branch protection or security settings change.

- Upstream mutable HACS image -> document the resolved evidence available and investigate scheduled failures; do not claim byte-reproducible validation.
- Bot PR churn -> weekly grouped proposals, finite limits and manual merges; no stale-issue automation.
- Matched HA dependencies drift -> keep coordinated pins manual and describe the update process.
- Fork/bot token restrictions -> no comments or write permissions; verify hosted behavior rather than adding a PAT to bypass a failure.
- Passing static configuration checks can miss hosted behavior -> distinguish local checks from observed CI and actual HACS installation.

## Migration Plan

Implement configurations and documentation on a reviewed branch. Run configuration checks, strict OpenSpec validation, existing tests/lint and package validation; confirm runtime members and dependency pins are unchanged. Once separately authorized, push and inspect the candidate HACS run, existing workflows and bot-compatible execution. After approval, merge without a runtime release. Dependabot starts from default-branch configuration; observe its first scheduled/manual update check before claiming PR creation works. Rollback removes the new configurations without touching HA entries or releases.

## References

- https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference
- https://www.hacs.dev/docs/publish/action/
- https://github.com/hacs/action/blob/main/action.yml
- https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/configure-code-scanning/configure-code-scanning
