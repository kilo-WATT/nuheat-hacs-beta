# Tasks

## 1. Public support intake

- [x] 1.1 Add bug_report.yml, feature_request.yml, installation_help.yml and chooser config.yml; verify YAML parses, required GitHub form keys and unique field IDs are present, links resolve, and only existing type labels are referenced.
- [x] 1.2 Add public-submission/redaction guidance to every form and optional log field; review synthetic filled examples to confirm no credentials, serials, callbacks, storage exports or logs are required and existing entries are preserved in help instructions.

## 2. Contribution and triage guidance

- [x] 2.1 Add CONTRIBUTING.md and PULL_REQUEST_TEMPLATE.md linked to existing development instructions; verify links and review both a hypothetical runtime fix and documentation-only PR for proportionate requirements and beta/Core boundaries.
- [x] 2.2 Add a non-destructive labels.yml catalog and docs/MAINTAINING.md triage guide; validate unique names/colors/descriptions, document explicit provisioning, and show issue-to-OpenSpec-to-PR-to-release traceability without auto-closure or rewriting reports.

## 3. Release documentation consistency

- [x] 3.1 Correct current README, release summary and release-status.json for b8 regular/latest; verify against read-only GitHub metadata, retain explicit tag selection, and remove obsolete beta-visibility requirements without editing historical releases or runtime files.
- [x] 3.2 Add a dated current-status validation note and release/promotion checklist in MAINTAINING.md; verify qualitative user hardware feedback is distinct from measured evidence and published tag/asset checksums remain unchanged.

## 4. Combined verification and review

- [x] 4.1 Run strict OpenSpec validation, YAML/content/link checks and existing packaging tests plus a local candidate package check; verify runtime, dependencies, provenance source pins and handoff allowlist bytes are unchanged and new community tooling is excluded from runtime packaging.
- [x] 4.2 Review the final diff and record local checks, pending GitHub rendering/provisioning verification, and the exact future publication operations; verify no unauthorized commit, push, issue message, release mutation, Core or production change occurred.

## Workflow follow-up

- Present the local result for review before publishing the templates/docs or applying the label catalog to GitHub.
- After authorized default-branch publication, verify rendered issue forms and existing type-label assignment without posting synthetic public issues. Verify any authorized label provisioning read-only.
- If editing GitHub release notes is authorized, make the current summary agree with regular/latest status while retaining original tag and asset bytes.
- Sync specifications and archive after implementation and review; artifact completeness is not implementation completion.
