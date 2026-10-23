# Design

## Context

See proposal.md for the observed gaps. Existing .github/workflows/validate.yml runs the HA suite, Ruff and the package builder; specs.yml validates OpenSpec. Neither workflow needs runtime changes for this first batch. The allowlisted ZIP excludes .github, contributor tooling and OpenSpec, but includes README, release notes, validation and publication metadata. Therefore current-doc corrections must not be confused with replacement release assets.

A design is included because the work crosses public support intake, contributor workflow, release guidance and GitHub label provisioning, with privacy and immutable-release constraints.

## Goals / Non-Goals

Goals: make reports useful for nontechnical users, give contributors proportionate checks, and make release promotion repeatable. Preserve the existing custom_components/tests/docs/tools layout and the established codex/release-prep-vVERSION naming for release work. Use a purpose-named codex branch for non-release community setup when implementation is authorized.

Non-goals: runtime or dependency changes, production access, Core edits, new releases, tag/asset rewrites, issue comments/closures, branch rules, Discussions, boards, automated stale management or new privileged CI.

## Decisions

1. Use three YAML issue forms: .github/ISSUE_TEMPLATE/bug_report.yml, feature_request.yml and installation_help.yml, with config.yml linking README and troubleshooting. Keep public intake on GitHub Issues until support volume warrants Discussions. Allow an escape route for reports that do not fit rather than forcing users to misclassify them.
2. Keep bug fields concise: HA version, integration version, exact HACS reference, fresh/legacy/reauth history, steps, expected and actual state. Optional context includes model/firmware, desktop/mobile auth, Celsius/Fahrenheit and sanitized logs. Do not make credentials, serials, callbacks, configuration exports or logs required. Use generic examples rather than real account data.
3. Add CONTRIBUTING.md and .github/PULL_REQUEST_TEMPLATE.md, linking docs/DEVELOPMENT.md rather than duplicating installation commands. Runtime changes reference relevant OpenSpec contracts and tests; documentation-only work uses link/content checks. Tests do not require access to the maintainer's HA.
4. Add .github/labels.yml as a reviewable catalog, not a claimed automatic sync. Retain default labels; define area:oauth, area:controls, area:migration, area:handoff, needs-info and waiting-on-vendor. Forms apply existing type labels immediately. No destructive pruning, bulk reclassification or automatic issue closure. Document an idempotent, explicitly executed label-provisioning step after review; no workflow token gains write permission.
5. Add docs/MAINTAINING.md for triage and release/promotion checklists. Link issue -> applicable OpenSpec change -> PR -> release. Use release milestones only for committed release scope; do not invent a release date or create a board for two reports.
6. Correct current README, current RELEASE_NOTES.md summary and release-status.json for b8 regular/latest. Add a dated current-status note to docs/VALIDATION.md instead of rewriting historic evidence. Record qualitative user feedback separately from measured hardware results. Verify the current Core PR commit when describing its status, without repeatedly polling its CI.
7. Publishing these corrections means a later reviewed docs commit and, if authorized, a matching edit of GitHub release notes. Existing tag v0.1.0b8 and uploaded ZIP/checksum remain immutable. No packaging behavior is weakened to accommodate changed documentation.

## Risks / Trade-offs

- Long forms discourage reports -> use short required fields and optional technical context.
- GitHub rendering cannot be proven by a YAML parser -> validate syntax locally and record UI availability as pending until templates reach the default branch; do not submit synthetic public issues.
- Labels do not exist merely because a catalog is committed -> keep provisioning explicit and verify the actual names after an authorized apply operation.
- Current and historical release records differ -> clearly date current promotion notes and preserve original evidence and immutable assets.
- CI private-value audit requires local evidence -> never upload the private baseline to GitHub or add a privileged workflow as a shortcut.

## Migration Plan

No HA migration. Prepare files locally, inspect forms and links, validate the label catalog and OpenSpec, verify runtime/dependency/allowlist bytes are unchanged, and run existing packaging tests/checks as appropriate. After review, publish the docs/templates to main through the user's approved workflow. GitHub forms become available on default-branch publication. Apply labels only within explicit authorization and verify them read-only afterward. Roll back repository docs/templates with a normal revert if necessary; do not rewrite release tags or remove reports.
