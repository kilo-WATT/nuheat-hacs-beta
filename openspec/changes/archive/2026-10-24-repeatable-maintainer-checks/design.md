# Design

## Context

See proposal.md for inspected files and b10 evidence. The package builder is
already an allowlisted local validator. Preserve it as the source of runtime
membership rather than adding a second drifting file list. Existing CI can
collect new pytest tests and Ruff checks without workflow privilege changes.

## Goals / Non-Goals

Goals: maintainers can reproduce checks without private version-specific scripts;
synthetic failures demonstrate trustworthy reports; legacy tools cannot silently
rewrite a current checkout; supported privacy policy matches published software.

Non-goals: automated publication, production installation, live thermostat use,
new SDK or HA runtime dependencies, branch rules, CI matrices, vendor features,
baseline-contract refresh or changes to the completed community archive.

## Decisions

### 1. A standalone read-only verifier

Add `tools/verify_release.py` with explicit `--repo owner/name`, `--tag`,
`--expected-commit`, desired release kind and optional `--expect-latest`.
Use argument arrays for `gh api` read operations and bounded public HTTPS
downloads; never invoke release edits, git checkout, tag writes or pip installs.
Use standard-library parsing/HTTP and existing maintainer `gh`, with no new
runtime dependency. Keep injected adapters for synthetic unit tests.

Resolve annotated/lightweight tags to a commit with bounded traversal. Require
the selected tag/release/version/pin to agree. Inspect SDK release metadata on
official PyPI for the exact nondevelopment pin; availability is separate from
the beta suite proving behavior. Require successful workflow results on that
commit, not the newest run for another revision. Accept explicit required
workflow names; default to this repo's stable and specification workflows.
Distinguish a pending run from a missing or failed check in the report.

Validate the checksum sidecar, GitHub digest when present, package ZIP members
and public tag-source archive in memory or bounded temporary storage. Derive
the runtime allowlist from the selected tag's package-tool data without executing
that source, and compare all expected component bytes. Reject duplicate names,
unsafe paths, encrypted/symlink members, excessive member/expanded/download sizes
and redirects outside approved GitHub/PyPI distribution hosts. Do not extract
arbitrary source or import fetched Python. Clean temporary resources on failure.

Report versioned JSON with check names/statuses and safe public SHA/version
evidence. Use exit 0 for required pass, 1 for confirmed failure, 2 for incomplete
or invalid invocation. Error output must not echo subprocess bodies, tokens,
credential-bearing URLs, remote source text or private local paths. Public
release-list ordering limitations are advisory unless the caller explicitly
requires default discovery. No network behavior runs on module import/help.

### 2. HACS evidence is accurately scoped

Preserve GitHub's raw list order. Report whether the selected regular release
appears with beta visibility disabled and whether the selected tag's component
download matches its commit. Report GitHub latest independently. Do not execute
downloaded HACS source or call metadata verification a production UI install.
The b10 live check can validate these specific public observations after tests;
synthetic fixtures reproduce b9-before-b10 without assuming stable external order.

### 3. Current privacy audit with explicit views

Keep `tools/privacy_check.py` as the supported audit, replacing its historical
policy and documenting that older validation records describe the previous
behavior. Require an external baseline. Support a JSON array of private strings
and the existing Markdown backtick baseline; never read production storage or
discover tokens in unrelated files automatically. Reject missing/empty usable
baselines rather than returning a meaningless pass.

Working-tree mode scans tracked existing files plus nonignored untracked files
and reports deleted tracked paths as skipped. Staged mode reads indexed blobs,
including unchanged indexed files, rather than opening working-tree paths.
Neither mode stages files. Scan selected local ZIPs and filename/member names,
with bounded member expansion and no extraction. Output view, scanned/skipped
counts and finding categories only, not matched values, contents or filenames.

Read audited registration bytes/hash from the selected view's provenance and
expected component path. Permit known public registration values only inside
that exact hash-matching runtime file, including the same ZIP member. Never
subtract them globally from the baseline or ignore credential fields. Scan
unexpected copies elsewhere and all other baseline values everywhere. Do not
load an external credential Python module to obtain the values; parse literals
from the audited selected file without executing it. No change to the actual
registration or packaging approval is authorized by this audit.

### 4. Historical commands fail safely

Move legacy helper implementations into `tools/historical/` with a README
describing their original source/framework assumptions. Preserve their source
as history, while wrapping executable bodies in guarded functions so import
has no effect. Keep original command paths as explanatory stubs: default
invocation exits nonzero with the historical location and supported replacement.
Do not expose an easy force flag that reapplies old transformations to current
runtime files. Tests verify import/help/default invocation cannot spawn network,
process or source writes. Existing synthetic transition tests remain intact.

Classify `package.py`, `privacy_check.py`, `verify_release.py` and `openspec.mjs`
as supported. Treat adaptation and historically pinned transition/Core helpers
as historical until a separately scoped reproducible current transition tool
exists. Document exact commands in MAINTAINING/DEVELOPMENT rather than modifying
old evidence to imply the new commands existed then.

## Risks / Trade-offs

- Strict verification rejects unexpected archives → structured failure and
  synthetic coverage; no weakening published allowlists to make a check pass.
- Network propagation differs by endpoint → independent incomplete/advisory
  evidence, finite retries/budgets and explicit tag selection guidance.
- Privacy scan cannot prove absence of every secret → require baseline, describe
  its limits and keep narrow public-registration provenance validation separate.
- Legacy commands may be referenced externally → explanatory stubs retain paths
  and historical docs, with no silent destructive replacement.

## Rollout and validation

Implement verifier and its tests/docs first, then privacy audit and safe
historical entry points. Run focused tool tests, full beta tests, Ruff and package
checks; assert no component bytes, SDK pins, migration or handoff files change.
Run a public read-only b10 verification only after synthetic tests pass. Runtime
packages must continue to exclude tools, history, baseline and OpenSpec files.
No release or hardware test is needed for developer-only changes. Leave prior
local archive edits separate and do not commit or push without current scope.
