# Tasks

## 1. Reproducible Core baseline and dependency

- [x] 1.1 Resolve the current PR head and beta b10 source, read applicable Core instructions/AI policy, inspect working-tree state and run required Core setup in an isolated environment; record exact source/framework/dependency versions and any baseline conflicts before edits.
- [x] 1.2 Upgrade Core to published SDK 0.1.3 and regenerate dependency metadata through its current generator; verify public package availability, all generated NuHeat pins, absence of development/Git dependencies and unrelated generated changes, and document the dependency/classification change in the port evidence.

## 2. Runtime resilience and identity preservation

- [x] 2.1 Port coordinator cooldown, coalesced reads and lifecycle handling; adapt regression tests for Retry-After variants, long cooldown versus pending deadlines, normal/reconcile overlap, two devices, stale/out-of-order reads and unload, then document verified framework adapters and results in the parity matrix.
- [x] 2.2 Port operation budgets and sanitized errors across all preset/HVAC/Off/On, target and timed-hold controls; test lock/token/body/write/post-write-read stalls, failed versus uncertain writes, rapid controls, inherited accepted targets, C/F conversion and explicit expiry without write replay, and document resulting user-visible failure behavior.
- [x] 2.3 Port startup/config-flow/poll/service permission versus throttle/auth classification while preserving Core provider/schema behavior; run required/optional 403 and persistent/transient 401 tests plus migration/registry/provider retention regressions, and record unchanged identity contracts.
- [x] 2.4 Update Core strings and regenerate English translations for tests using its prescribed command; verify translated permission/retry-later/timeout feedback through regression assertions without copying beta community OAuth setup or changing provider discovery, and document wording/translation differences.

## 3. Private Core diagnostics

- [x] 3.1 Add allowlisted cached diagnostics with truthful built-in Core/SDK metadata; adapt Core diagnostics tests for nested private keys/values, unknown fields, absent runtime/package metadata, cooldown and outage while asserting zero API/token/session calls and unchanged entry data.
- [x] 3.2 Document diagnostics fields, Core-versus-beta version metadata and private-data exclusions in the parity report; verify downloaded synthetic snapshots expose only approved health/count fields and no identifiers, URLs, raw models or free-text exceptions.

## 4. Complete isolated validation and review evidence

- [x] 4.1 Run the complete Core NuHeat suite on the matching framework with published SDK, including existing controls, auth, migration and diagnostics tests; record exact counts/skips and map each beta resilience/diagnostics case to its Core result, explicitly separating synthetic evidence from unperformed live/official-provider tests.
- [ ] 4.2 Run Core Ruff lint/format, scoped mypy and pylint, hassfest, dependency/translation consistency and required full-file prek checks; record exact commands/results and diagnose baseline failures without weakening checks or claiming unexecuted validation passed.
- [x] 4.3 Review the final Core patch and beta planning changes for unintended scope and private markers; verify beta runtime/provenance/handoff files and the SDK checkout are unchanged, no community registration was copied, and deliver an explicit human-reviewable diff/file summary before any upstream submission.

## Workflow follow-up

- Implementation starts only on a new apply request. Keep every task unchecked until its evidence exists.
- Human review and separate commit/push approval precede updating the existing Core PR; preserve all previously pushed commits without amendment, squash or rebase. Check approved submission CI without repetitive polling.
- Refresh the separate handoff proposal's candidate evidence after any actual Core source update, without expanding the shipped allowlist or claiming official linking is enabled.
- Sync/archive this parity change after implementation and verification; retain the optional-capabilities proposal's unresolved vendor gates and unfinished official handoff independently.
