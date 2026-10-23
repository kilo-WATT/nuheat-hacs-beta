# Proposal

## Why

The beta has tested runtime behavior but no structured issue intake or contributor templates, so reports omit information needed to reproduce OAuth, migration and thermostat problems. Release promotion also left the README and release notes describing b8 as a prerelease after GitHub marked it regular/latest.

## What Changes

- Add bug, feature-request and installation-help forms plus a chooser linking existing installation and troubleshooting documentation.
- Collect HA/integration/HACS versions, the tracked tag, installation history, expected/actual behavior and optional sanitized logs; never request credentials, serial numbers or configuration storage.
- Add CONTRIBUTING.md and a PR template explaining setup, relevant checks, beta/Core boundaries and issue-to-OpenSpec-to-PR-to-release traceability.
- Define a small label catalog and triage guide, preserving existing labels and avoiding automatic stale closure or retroactive edits to user reports.
- Add a release/promotion checklist and correct current main-branch documentation for b8's regular/latest status, while retaining historical evidence and immutable published tags/assets.
- Prepare local files for review. GitHub label application, publishing documentation/release-note edits and settings changes remain explicit operations at the implementation/publication stage.

## Capabilities

### New Capabilities

- `community-support`: useful public issue intake, private-data minimization, contributor guidance and consistent triage.

### Modified Capabilities

- `release-distribution`: explicit promotion consistency across current documentation and release metadata without rewriting published source or assets.

## Impact

Only kilo-WATT/nuheat-hacs-beta: .github issue/PR templates and label catalog, CONTRIBUTING.md, maintainer documentation and current release guidance. Existing integration code, dependency pins, migrations, identity guarantees, OAuth, handoff eligibility and upstream Core remain unchanged.

Observed on 2026-10-23: no issue/PR/contribution templates, two closed issues with no labels/milestones, default labels only, no rulesets and unprotected main. GitHub reports b8 regular/latest; repository text still says prerelease. These observations motivate the scope; they do not imply authorization to change branch protection.

Deferred: branch protection, Discussions, project boards, security-reporting settings, CI expansion, legacy-script relocation and restructuring historical validation files. No production access, hardware commands, automatic release publishing or runtime changes are proposed.
