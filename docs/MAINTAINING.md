# Maintaining NuHeat Beta

## Read-only release verification

Use the supported verifier after a release is published; it does not publish,
install dependencies, change Git refs, or access HA:

```sh
python tools/verify_release.py --repo kilo-WATT/nuheat-hacs-beta --tag v0.1.0b10 --expected-commit 3f77a85f459fb61021ea688d094229f4429fba9c --kind regular --expect-latest
```

Requires Python 3.14 (the project test environment) and authenticated `gh` read access plus public HTTPS access to
GitHub and PyPI. Output is versioned JSON on stdout; redirect it only to an
appropriate review file if wanted. Exit 0 means all required checks passed,
1 means invalid/mismatched evidence, and 2 means unavailable/incomplete evidence.
CLI argument errors also exit 2. Raw response bodies and credentials are not
printed. No account or thermostat data is needed.

The checks independently cover the resolved tag, flags/latest status, newest
exact-commit results for both validation workflows, manifest/SDK publication,
checksum sidecar and asset digest, and all package bytes against the tag source.
Archives are inspected without executing their code or extracting their paths.
Downloads and expanded archives have finite size and time limits.

`--workflow NAME` overrides the required workflow list; repeat it for each
workflow. `--kind prerelease` verifies prerelease flags. The default expectation
is a regular release. `--expect-latest` is optional because historical releases
need not remain latest.

HACS evidence distinguishes regular-only visibility, explicit-tag source bytes
and the first regular item in GitHub's raw release list. b10 was marked latest
while b9 appeared first. That ordering is advisory by default; `--require-default`
turns it into a required check. The verifier never sorts it away or claims a
production UI install. Continue to select and verify the explicit tag in HACS.

Run synthetic verifier tests with `python -m pytest -q tests/test_verify_release.py`.
They require no credentials or network. A successful public verification is
publication evidence, not a replacement for runtime, migration or hardware tests.

## Maintenance automation

Dependabot proposes grouped version updates weekly for GitHub Actions, npm
development tooling and Ruff, with at most two open version-update PRs per
ecosystem. Review and merge manually after CI passes; nothing merges or publishes
automatically. These limits do not govern separately enabled security updates or
alerts. This configuration does not enable or change those repository settings.

HA, frontend, the HA pytest plugin and the runtime SDK remain coordinated manual
updates. Check compatible versions together; SDK updates also require the runtime
manifest, test pin and provenance/package checks. Actions updates do not maintain
Python/Node version inputs. For OpenSpec updates, review package.json and lockfile
together and assess whether generated skills need deliberate regeneration. Do not
run generated-skill updates blindly as part of accepting a bot PR.

The **Validate HACS custom repository** workflow checks PRs, pushes, manual runs
and Mondays at 07:23 UTC. It uses the ordinary read-only GitHub token, disables PR
comments and has a ten-minute timeout. PRs validate the source repository at the
head SHA; other events use the triggering SHA via `REPOSITORY_REF`. The HACS log
records its repository/reference. No checkout, PAT, NuHeat login, private audit
baseline, production access or catalog submission is required.

The action source is pinned to `1ebf01c408f29afcb6406bd431bc98fd8cbb15aa`.
Its definition still uses the mutable `ghcr.io/hacs/action:main` container, so the
source pin does not freeze the validator image. Preserve run logs/image evidence
when investigating upstream changes. Only `brands` is ignored: the beta retains
Core's existing `nuheat` domain, while this action checks the custom brands list
or local icon assets. The first hosted run confirmed this mismatch. The approved
exception avoids changing runtime identity or the ZIP solely for that check.
All other checks remain active, including topics. Repository topics are
`home-assistant`, `hacs`, `nuheat` and `custom-integration`. Investigate failures
before adding a narrowly explained exception; never grant a PAT or suppress all
checks to hide fork/bot failures. Failed/unavailable validation remains a failure.

A pass establishes repository validation for the logged reference, not successful
UI installation, correct default release ordering, retained entities or hardware
behavior. Continue explicit-tag installation and independent release verification.
For releases made after adopting this workflow, append all three options to the
selected release-verification command (replace tag/commit with the intended release):

```sh
python tools/verify_release.py --repo kilo-WATT/nuheat-hacs-beta --tag vVERSION --expected-commit COMMIT --kind regular --expect-latest --workflow "Validate unpublished NuHeat candidate" --workflow "Validate NuHeat specifications" --workflow "Validate HACS custom repository"
```

Repeated `--workflow` options replace the verifier's defaults, so include all three.
Historical releases retain their original two-workflow expectation; the verifier's
defaults have not changed. Hosted HACS/fork/bot behavior and actual Dependabot PR
creation remain unverified until observed after authorized push/default-branch
adoption. Local configuration tests do not establish those results.

CodeQL is deferred: assess GitHub default setup with Python in a separate reviewed
change, inspect initial findings, and avoid enabling default and advanced workflows
together. No scanning, branch protection, automatic issue closure or release setting
is enabled by these files. These maintainer changes require no runtime release.

## Issue intake and triage

Before publishing maintainer changes, use the current privacy audit with an
external private baseline. JSON baselines are nonempty arrays of known private
strings; the original Markdown backtick baseline is also supported. Keep it
outside the checkout, backups, issues and CI. The tool never discovers tokens
from production storage or executes a credential module.

```sh
python tools/privacy_check.py --private-baseline /outside/repository/private-values.json --view working-tree --zip artifacts/nuheat-0.1.0b10.zip
python tools/privacy_check.py --private-baseline /outside/repository/private-values.json --view staged
```

Working-tree mode reads tracked existing and nonignored untracked files, with
deleted tracked paths counted as skipped. Staged mode reads the complete index,
not unstaged edits, and never stages anything. Repeat `--zip PATH` for explicit
archives; no archive scan is claimed when none are selected. Each ZIP is read
without extraction and must retain the expected registration and provenance.

Reports contain view/counts/finding categories, never matched strings, content
or filenames. Exit 0 means the selected evidence passed, 1 means findings and
2 means incomplete/invalid inputs. Missing or empty baselines and invalid
registration provenance cannot produce a pass. The known shared registration
is recognized only at the exact audited runtime path/bytes; account tokens and
unexpected copies are still checked. Older validation records refer to the
previous secret-free audit policy and are historical, not the current command.

This targets known baseline values; it does not prove absence of all possible
secrets or make public sharing automatically safe. Use synthetic baselines for
tests: `python -m pytest -q tests/test_privacy_check.py`.

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
settings remain separate follow-ups. Legacy adaptation and transition entry
points are now explanatory stubs; see [historical tools](../tools/historical/README.md)
and the supported-command table in [development](DEVELOPMENT.md#verification).
