# Tasks

## 1. Repeatable read-only release verification

- [x] 1.1 Add parameterized CLI/report and injected read-only GitHub/HTTP adapters; verify help/import cause no network or writes, invalid inputs fail safely, annotated/lightweight tags resolve correctly, and subprocess/network errors produce bounded sanitized failure/incomplete reports. Document required inputs and exit codes with synthetic CLI tests.
- [x] 1.2 Verify release flags/latest, exact-commit required workflows, selected manifest/SDK availability and asset/tag byte identity; test wrong commit/version, missing or pending CI, unpublished SDK, bad checksums/digests, duplicate/traversal/symlink/oversized archives, timeouts and unexpected redirects without executing or extracting fetched source. Document each independent evidence check and its limits.
- [x] 1.3 Add explicit-tag/HACS metadata observations preserving raw release order; reproduce b9-first/latest-b10 and prerelease cases, show explicit-tag success separately from default selection, and verify downloaded component bytes match the chosen tag. Document that this is not a production UI installation or default-update guarantee.

## 2. Supported privacy audit

- [x] 2.1 Replace historical privacy semantics with explicit working-tree/index views and external JSON/Markdown baseline input; verify index-versus-unstaged differences, nonignored untracked files, deleted paths, invalid/empty/in-repo baselines and safe count-only output using temporary synthetic Git repositories. Document exact supported invocations without requiring real credentials.
- [x] 2.2 Add bounded ZIP/member-name scanning and narrowly hash-verified public-registration recognition; test approved registration, changed/missing provenance, private tokens in the expected file, unexpected registration copies, private filenames, ZIP values and malformed archives. Assert no marker/content/path disclosure or writes; document that no automated audit proves all unknown secrets absent.

## 3. Historical-tool boundary

- [x] 3.1 Preserve old adaptation/transition/Core helpers under clearly documented history and keep explanatory safe original-path stubs; test imports, help and ordinary invocation cannot rewrite source, spawn runtime processes or contact HA. Update supported-command index and pinned historical limitations in DEVELOPMENT/MAINTAINING without rewriting old evidence or synthetic transition tests.

## 4. Combined verification

- [x] 4.1 Run focused tool tests, full beta suite, Ruff lint/changed-file format, `python tools/package.py`, `git diff --check` and `npm run specs:check`; verify runtime/dependency/migration/handoff and published b10 bytes remain unchanged, tools/history/baseline stay outside the package, then run the new verifier read-only against public b10. Deliver exact results, known ordering limitations and an auditable diff separated from the prior local archive edits.

## Workflow follow-up

- Start apply through a new request after reviewing these newly created artifacts.
- No production access, thermostat commands, publication, commits, pushes or
  repository-permission changes are part of this maintainer-tool implementation.
- Sync/archive only after all implementation and verification tasks pass.
