# Design

## Context

See proposal.md for source baselines. The archived resilience alignment report identifies the port targets. Core uses typed runtime data, native temperature properties, Probatio configuration schemas and `async_unload_platforms_or_raise`; blindly copying stable-beta modules would regress these interfaces. Core's AGENTS.md requires setup/tooling, typed tests, generated English translations and human review before submission.

## Goals / Non-Goals

**Goals:** Equivalent fault handling and diagnostics on the current PR framework with a published dependency and attributable synthetic evidence.

**Non-Goals:** New beta behavior, SDK development/publication, community OAuth registration in Core, optional vendor-gated features, a new hold cap, live hardware tests, official Cloud deployment or automatic handoff eligibility. Do not copy HACS/OpenSpec/GitHub bot tooling upstream.

## Decisions

### 1. Reconcile against the exact Core head and published SDK

At apply start, resolve PR #176586 and inspect local modifications before editing; preserve unrelated work and stop for a material source conflict. Use published `chemelex-nuheat==0.1.3`, verifying wheel metadata/public availability, rather than the archived report's historical development wheel. Change the Core manifest and regenerate every affected dependency file through Core's current generator (including requirements_all.txt and any generated test requirements). Scope review catches unrelated generator drift. No SDK source change is required.

### 2. Port behavior through Core adapters

| Source responsibility | Core files | Required adaptation |
| --- | --- | --- |
| Account cooldown, read coalescing, confirmation lifecycle | coordinator.py | Verify current coordinator/debouncer hooks; retain generation checks, independent thirty-second expiry and cleanup. |
| Control budgets, lock wait and error mapping | climate.py, services.py where needed | Preserve Core native Celsius properties, conversion, seven mode/preset/Off/On controls, target and timed-hold semantics; do not nest Off locks or replay writes. |
| Startup/first-refresh cleanup | __init__.py | Keep typed runtime data, existing service setup and raising unload API; map permission versus transient/auth failures distinctly. |
| Setup/reauth feedback | config_flow.py, strings.json | Preserve Probatio, identity ownership checks and Core provider discovery; regenerate English test translations with Core tooling. |
| Cached support snapshot | new diagnostics.py | Use Core diagnostics conventions and locally available framework/SDK metadata without assuming manifest.version exists. |
| Public dependency | manifest.json and generated requirements | Exact released SDK pin; no Git, local wheel path or developer dependency. |

Retain 15-second per-request and 30-second whole-operation budgets, the SDK's 60-second missing/invalid Retry-After fallback, two-second initial/eight-second retry reads and thirty-second pending state. Valid longer cooldowns must not be clipped to that fallback or extend pending optimism. Preserve the single genuine-401 recovery contract; required 403 must not become reauth, and optional v1 403/429 must conservatively retain v2 information. Verify these values against published b10 source while porting.

Prefer focused changes within Core modules over wholesale source replacement. Existing beta OAuth selection and community setup are deliberately not port sources. Core's official-provider path is not redesigned here; the handoff proposal owns relinking.

### 3. Diagnostics use positive selection

Port the b10 allowlist rather than serializing config entries/models and redacting after the fact. Count devices and pending states without outputting dictionary keys. Test unknown nested private data and free-text exceptions, outage/incomplete setup, missing package metadata and no network/token/session calls. Core lacks a custom integration version; report truthful local Core/SDK metadata or a documented null, never a fabricated beta version. Do not introduce exposed identifiers for test convenience.

### 4. Independent regression suites and evidence

Adapt beta resilience/diagnostics tests into Core's `tests/components/nuheat` with typed parameters, native fixture imports and snapshots where useful. Preserve existing OAuth/migration/registry/service tests. A parity matrix maps each beta case to a Core case and records any framework-specific difference. Run Core tests against its own pinned framework; retain beta's existing isolated environment only for comparison, without modifying its runtime.

Cover rate-limit headers/cooldown, concurrent devices/reads, required/optional permissions, genuine versus transient OAuth failures, all controls and unit/expiry combinations, stale/out-of-order reads, failed PUT versus accepted-PUT/failed-GET, rapid changes, authorization/lock/body timeouts, cancellation and unload. Synthetic clocks and endpoints establish these failure cases; do not induce vendor errors or command hardware.

### 5. Validation and review boundary

After Core's required setup, run the complete NuHeat suite, Ruff lint/format, scoped mypy/pylint, hassfest, dependency/translation generation checks and prescribed `uv run --no-sync prek run --all-files`. Record exact environment, source revision, dependency and results. Broad baseline failures are reported with cause/scope, not hidden by skips. No commits/pushes occur merely because tests pass. Present source/test diffs for human review before a separately authorized incremental update to the existing PR; never amend/squash/rebase pushed Core commits.

## Risks / Trade-offs

- Private coordinator hooks differ -> inspect the current framework and test poll/reconcile overlap rather than treating a byte copy as parity.
- Permission classification changes with SDK -> regression tests across startup, flows, polls and services keep identity and provider behavior intact.
- Diagnostics leak through keys/errors -> positive allowlist plus nested synthetic marker/no-side-effect tests.
- Core framework version metadata differs -> use local Core conventions and test built-in metadata behavior explicitly.
- Passing isolated tests is mistaken for deployed Cloud readiness -> keep handoff guard/allowlist and unfinished transition tasks unchanged.

## Migration Plan

No entry-version bump, provider conversion or registry rewrite. Update the dependency and Core implementation together in a reviewable patch, then run isolated validation. Rollback reverts that patch without changing stored entries. A later approved PR update preserves history. The final merged Core revision and official provider must be retested under the separate handoff proposal before any beta retirement is eligible.
