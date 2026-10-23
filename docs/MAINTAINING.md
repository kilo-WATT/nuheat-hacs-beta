# Maintaining NuHeat Beta

## Issue intake and triage

Use the [issue chooser](https://github.com/kilo-WATT/nuheat-hacs-beta/issues/new/choose)
for bugs, feature requests and installation help. Forms become available when
merged into the default branch. Keep a blank-issue escape route for reports that
do not fit. Use [CONTRIBUTING.md](../CONTRIBUTING.md) for development expectations.

1. Confirm the HA/integration versions and the exact reference HACS tracks. A
   manifest version can also appear in a branch build; do not infer a tag from it.
2. Separate fresh setup, legacy migration, existing OAuth upgrade and reauthentication.
   For OAuth, distinguish community/custom provider and desktop/mobile without
   requesting client secrets, tokens, account identifiers or callback URLs.
3. Ask for a minimal reproduction and expected/actual behavior. For controls,
   compare HA with the NuHeat app and note timing. Do not send hardware commands
   or ask for repeated uncertain writes as an automatic diagnostic step.
4. Keep entry/entity/device identity and credentials intact. Do not suggest
   deleting/recreating NuHeat entries or hand-editing `.storage` to collect evidence.
5. Apply a type label and useful area/wait labels. State which explanation is
   confirmed, which is a hypothesis and what specific information is missing.
6. Link the issue -> applicable OpenSpec change -> implementation PR -> released
   tag. A fix on main is not necessarily available in a published release. Record
   the installable version when resolving an issue; do not close it for inactivity
   alone. Issue comments, label changes and closures are explicit maintainer actions.

The existing labels `bug`, `enhancement`, `documentation` and `question` describe
issue type. Retain other default labels such as `duplicate` and `help wanted`.
The reviewed [label catalog](../.github/labels.yml) adds:

| Label | Use |
| --- | --- |
| `area:oauth` | Login, provider, callback and refresh issues |
| `area:controls` | Modes, targets, holds and reconciliation |
| `area:migration` | Legacy entries and registry identity |
| `area:handoff` | Validated beta-to-Core transition |
| `needs-info` | Specific non-sensitive evidence is needed |
| `waiting-on-vendor` | A stated dependency on Chemelex clarification/action |

`waiting-on-vendor` does not prove a vendor restriction. Document the evidence
and open question. Use release milestones only when work is committed to that
release; do not promise dates or create a board solely to mirror these labels.

## Provisioning labels

Committing `labels.yml` does not synchronize GitHub. Issue forms intentionally
use existing type labels, so they do not depend on new labels being provisioned.
After the maintainer authorizes label provisioning, the following GitHub CLI
commands create/update only these six labels. `--force` makes repeated application
idempotent; it does not delete other labels, reclassify issues or post comments.
Review the [catalog](../.github/labels.yml) first. No workflow token needs write access.

```sh
gh label create "area:oauth" --color "0969DA" --description "Login, provider selection, callbacks and token refresh" --force --repo kilo-WATT/nuheat-hacs-beta
gh label create "area:controls" --color "0969DA" --description "Thermostat targets, modes, holds and reconciliation" --force --repo kilo-WATT/nuheat-hacs-beta
gh label create "area:migration" --color "0969DA" --description "Legacy migration, config entries and entity retention" --force --repo kilo-WATT/nuheat-hacs-beta
gh label create "area:handoff" --color "0969DA" --description "Validated transition from the beta to official Core" --force --repo kilo-WATT/nuheat-hacs-beta
gh label create "needs-info" --color "D4C5F9" --description "Specific non-sensitive information is needed to investigate" --force --repo kilo-WATT/nuheat-hacs-beta
gh label create "waiting-on-vendor" --color "FBCA04" --description "Progress depends on a stated Chemelex clarification or action" --force --repo kilo-WATT/nuheat-hacs-beta
gh label list --repo kilo-WATT/nuheat-hacs-beta
```

## Preparing a release

- Use `codex/release-prep-vVERSION`; match tag, manifest version and release-status
  version. Do not rewrite already published tags or substitute new files silently.
- Follow the applicable OpenSpec change and inspect both the runtime diff and
  [provenance](../provenance.json). Keep source pins and the exact Core allowlist.
- Update current release notes, installation/recovery guidance and dated evidence.
  Separate synthetic tests, measured hardware results, qualitative user feedback
  and remaining models/firmware/transition limits. Do not treat a GitHub prerelease
  flag as a statement that the software is official Core.
- Run relevant tests, lint, packaging and the private local privacy audit. Keep
  the private baseline outside Git and CI; do not copy account data into artifacts.
- Verify exact-commit CI and the allowlisted ZIP contents/dependencies. New forms,
  contributor tooling and OpenSpec do not belong in the HA runtime package.
- Obtain release publication authorization. Explicitly choose prerelease or
  regular/latest; verify those flags, the tag commit, uploaded asset digests and
  isolated HACS visibility/downloads after publishing. Production installation
  and hardware commands remain separate authorized actions.

## Promoting a prerelease

1. Verify the authorized release/tag, its asset digests and test feedback. Retain
   measured results as measurements and user reports as qualitative observations.
2. With promotion authorization, clear the GitHub prerelease flag and explicitly
   decide whether this release becomes latest. Do not rewrite its tag or assets.
3. Correct current README installation/upgrade/branch-switch instructions,
   current RELEASE_NOTES.md summary and release-status.json to match the live
   status. Regular releases do not require HACS beta visibility. Prereleases do.
   Always retain explicit tag selection and verification; do not recommend main.
4. Add a dated current-status note to VALIDATION.md. Preserve older preparation
   records under their historical headings. Update current Core-port references
   only from verified evidence; never expand handoff eligibility because a PR moved.
5. Publish the reviewed documentation commit through the approved workflow. If
   authorized, update the GitHub release summary too. Re-read its flags/notes and
   verify the original tag and assets stayed unchanged. Historical README/notes
   inside an already published ZIP remain a snapshot of its original publication.
6. Verify HACS discovery with beta visibility disabled for a regular release,
   and keep rollback instructions usable without deleting NuHeat entries.

For read-only release verification:

```sh
gh release view v0.1.0b8 --repo kilo-WATT/nuheat-hacs-beta --json url,tagName,isPrerelease,isDraft,assets
gh api repos/kilo-WATT/nuheat-hacs-beta/releases/latest --jq .tag_name
gh api repos/kilo-WATT/nuheat-hacs-beta/releases/tags/v0.1.0b8 --jq '.assets[] | {name,digest}'
```

## Checks proportionate to the change

For documentation/forms, check YAML and required form fields, unique field IDs,
existing type labels, redaction instructions, Markdown links and release wording.
Review a hypothetical bug, feature request, help report and docs-only PR without
posting synthetic public issues. Use the existing packaging tests and a local
candidate build to verify packaging boundaries when release documentation changes.
Do not regenerate or upload the published archive to correct current prose.

For runtime changes, use [DEVELOPMENT.md](DEVELOPMENT.md#verification) and the
relevant regression suites. Keep the [validation index](VALIDATION.md), applicable
[OpenSpec changes](../openspec/changes) and [release notes](../RELEASE_NOTES.md)
linked. Branch rules, Discussions, projects, privileged CI, security-reporting
settings and legacy bootstrap cleanup are separate follow-ups.
