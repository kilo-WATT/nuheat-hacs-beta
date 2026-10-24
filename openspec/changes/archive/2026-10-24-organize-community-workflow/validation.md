# Local community-workflow validation

Prepared on branch `codex/community-workflow`, based on beta commit
`804343b755df8a381e52eba8d2746ac9a5224fd6`. No commit, push or GitHub mutation
was performed. Earlier uncommitted Core-port OpenSpec records were preserved.

## Delivered files

- Three issue forms and chooser configuration in .github/ISSUE_TEMPLATE.
- CONTRIBUTING.md and .github/PULL_REQUEST_TEMPLATE.md.
- Six-label catalog in .github/labels.yml and docs/MAINTAINING.md with explicit
  provisioning commands, triage and release/promotion checklists.
- Current README, release summary and publication metadata corrected for b8
  regular/latest; a dated note precedes unchanged historical validation records.
- Contributor/development links and the confirmed beta rapid target-then-preset
  limitation documented. No thermostat fix is included in this change.

## Completed checks

- YAML parsed for all forms, chooser and labels. Required form keys, unique field
  IDs, dropdown options and existing GitHub type labels verified.
- Synthetic bug/feature/help report examples can satisfy required fields without
  logs, credentials, identifiers or storage exports. Optional context accepts
  unknown model/firmware. Public redaction guidance is present in every form
  and optional log field. No synthetic reports were submitted to GitHub.
- Runtime-fix and docs-only PR walkthroughs reviewed: relevant behavior tests and
  compatibility evidence apply to runtime work; docs-only work can use proportionate
  content/link checks without hardware or a new behavior proposal.
- Six unique label names/colors/descriptions validated. Documented provisioning
  commands exactly match the catalog and do not delete other labels or edit issues.
- Forty-two local Markdown paths/anchors checked. Twelve external URL targets
  checked for HTTPS syntax and repository-path existence where applicable; this
  is not a claim of rendered GitHub forms or exhaustive external-site availability.
- Strict OpenSpec: **10 items passed, 0 failed**.
- Existing packaging suite: **12 tests passed**. No new tests mirroring prose
  were added, and the full HA suite was not repeated for unchanged runtime code.
- Local candidate ZIP: 29 files; all 18 runtime files match the existing commit.
  New community files, OpenSpec and Node tooling are excluded from runtime packaging.
- Twenty-seven protected files match HEAD, including runtime, dependency pins,
  provenance source pins, packaging code and existing CI workflows.
- Private local audit checked 18 known private values: zero matches in publishable
  files and candidate/release archives. Private baselines remain outside Git.
- Git diff whitespace check passed.

## Read-only external verification

GitHub reports v0.1.0b8 regular/latest, not a draft. Its tag still points to
`804343b755df8a381e52eba8d2746ac9a5224fd6`. Original asset digests remain:

- nuheat-0.1.0b8.zip: `530a2b8d758098876d329eb44f319d216451eab80df3618dbcbbd1834b9cc6ba`
- nuheat-0.1.0b8.zip.sha256: `0a890864e3ffd5d7032312312cfac678ee720004cebbcb03cf9b8f8d1292c9e4`

Core PR #176586 head was verified read-only as
`9ab210660371eaf6bda2083a518cf15eea29318f`. No Core or production files were
accessed for modification. Beta runtime and handoff eligibility are unchanged.

## Pending publication operations

The implementation is local and ready for review. It does not yet change the
public issue chooser, repository labels or GitHub release body.

1. When authorized, commit only the reviewed community-workflow scope, push this
   branch, run its GitHub CI and publish to the default branch through the approved
   workflow. Do not accidentally bundle unrelated earlier OpenSpec edits.
2. Verify the issue forms render after default-branch publication, without posting
   synthetic public issues. Verify PR template availability with an unsubmitted
   draft/preview, not an unsolicited PR.
3. When authorized, provision the six catalog labels and verify their actual
   names/descriptions read-only. Existing labels and reports remain intact.
4. When authorized, update the current GitHub b8 release summary to agree with
   regular/latest status and the new current notes. Keep tag and asset bytes
   unchanged; do not rebuild/upload a replacement published archive.
5. Review before syncing the community-support/release-promotion specs and
   archiving this OpenSpec change. Branch rules, Discussions, projects, security
   reporting settings and legacy-script cleanup remain separate follow-ups.
