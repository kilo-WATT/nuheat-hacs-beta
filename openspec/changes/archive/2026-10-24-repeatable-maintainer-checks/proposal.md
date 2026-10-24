# Proposal

## Why

Releasing b10 required version-specific private scripts and manual corrections
to stale assertions. Contributors need repeatable, read-only release checks and
an unambiguous set of supported maintainer commands.

## Observed evidence

- `tools/package.py` checks local allowlisted packaging, but no repository tool
  verifies a published tag, release flags, downloaded assets and SDK availability.
- The b10 publication verified GitHub latest=b10 while its release list returned
  b9 first. HACS 2.0.5 could explicitly download/update b10 with beta visibility
  disabled; automatic default selection was not b10. These are separate facts.
- `tools/privacy_check.py` still implements the earlier secret-free policy,
  scans tracked files only, reads working-tree content, and assumes tracked paths
  exist. Historical validation acknowledges its intentional shared-client rejection.
- `tools/adapt_stable.py` rewrites files at import time. Transition/Core helpers
  preserve historical source/framework assumptions, not a current general workflow.

## What Changes

- Add a parameterized read-only verifier for repository/tag/expected commit,
  release flags/latest, complete CI evidence, package and source bytes, the pinned
  public SDK and release-list visibility. Report HACS default-order limitations
  separately from explicit-tag availability; do not assume list[0] is latest.
- Make checks testable with synthetic metadata, HTTP and Git responses; provide
  structured bounded output and nonzero failure/unfinished status.
- Establish a supported maintainer-command index. Retire historical rewrite and
  transition entry points from normal use without deleting historical evidence
  or pretending their old framework fixtures validate current Core handoff.
- Replace the obsolete privacy entry point with a supported external-baseline
  audit that checks the chosen Git view and ZIPs without printing private values.
  Recognize the public registration only by its audited provenance, without
  blanket exclusions for account credentials or unexpected copies.
- Test and document each tool. Keep tools out of HA packages and preserve
  runtime, dependency pins, provider selection, migrations and handoff allowlist.

## Capabilities

### New Capabilities

- `maintainer-tools`: supported command discovery, side-effect-free historical
  entry points and private-data audit contracts.

### Modified Capabilities

- `release-distribution`: repeatable read-only verification that distinguishes
  publication, installable bytes, exact CI and explicit HACS tag visibility.

## Impact

Beta `tools/`, focused tests, `docs/MAINTAINING.md`, `docs/DEVELOPMENT.md` and
historical-tool documentation. No SDK/Core/production changes, thermostat
commands, release publication, privilege changes or automatic publishing.
Existing published b10 files/tags remain immutable. The prior local community
archive remains separate from this implementation diff.

## Scope boundary

These artifacts capture recommendations 1 and 2 only. CI matrix expansion,
branch protection, baseline/traceability refresh, vendor-dependent features and
official Cloud handoff remain separate. Implementation begins through the apply
workflow after this newly created proposal is reviewed.
