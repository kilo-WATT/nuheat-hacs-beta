# Tasks

## 1. SDK transport and permission contracts

- [x] 1.1 Add compatible typed rate-limit and permission errors; verify required-endpoint 403 does not force token refresh, persistent 401 retains the single-refresh contract, and existing generic API-error catches still work.
- [x] 1.2 Preserve usable v2 data when optional list/get v1 details return 403, without trusting stale details; verify unresolved mode/identity invariants and persistent optional 401 propagation in client tests.
- [x] 1.3 Add runtime-client cooldown state covering required/optional requests; test delta-seconds, HTTP-date, zero, expired, malformed, absent and very long Retry-After, concurrent requests, two devices and independent clients with synthetic clocks.
- [x] 1.4 Implement explicit per-request and whole-operation budgets; verify stalled authorization, response headers/body, PUT and nested post-write GET time out, responses are released, cancellation propagates and uncertain writes are never replayed.
- [x] 1.5 Document SDK exception mapping, cooldown ownership, proposed 15-second request/30-second operation budgets and 60-second fallback; verify examples and successful-path request contracts against client tests and the referenced vendor schemas.

## 2. Beta integration behavior and user feedback

- [x] 2.1 Make normal polls and all command reconciliation reads honor the SDK cooldown; verify no eight-second request during Retry-After 120, optional throttling retains v2 availability, pending state expires at thirty seconds, and cooldown exit coalesces reads without a burst.
- [x] 2.2 Bound all seven mode/preset/Off/On controls, target writes and the timed-hold action including lock wait; verify cooldown rejects without queuing/optimism, timeout releases serialization, rapid commands and explicit expiry remain correct, and unload leaves no callbacks or orphan requests.
- [x] 2.3 Map startup, config-flow, polling and service permission failures distinctly from genuine auth expiry; verify actionable sanitized feedback, no automatic Manual fallback, and unchanged entry/entity/device/provider/option associations for community and custom setups.
- [x] 2.4 Update API-reconciliation and authentication guidance for retry-later, permission and uncertain-timeout outcomes; verify documented messages against regression assertions and avoid implying that relinking or repeating a command fixes every failure.

## 3. Cross-layer validation and Core alignment

- [x] 3.1 Consume a locally built candidate SDK in an isolated beta environment; run complete client/beta suites, lint, formatting, migration/identity and Celsius/Fahrenheit regressions, and record measured synthetic results separately from unperformed hardware checks.
- [x] 3.2 Validate candidate dependency/provenance packaging, private-data exclusion and strict OpenSpec structure; verify only intended files/dependencies change and the shipped Core handoff guard/allowlist remain untouched.
- [x] 3.3 Deliver a Core alignment report naming the corresponding source/tests, framework-specific adaptations and exact verification commands; verify SDK API compatibility and explicitly leave actual Core edits/submission pending separate authorization.

## Workflow follow-up

- The subsequent `opsx:apply` request authorized local SDK/beta implementation
  and isolated validation. Production/hardware access, commits, pushes, SDK
  publication, beta releases and upstream Core updates remain outside this scope.
- Review the proposed timeout/fallback defaults with the implementation results;
  revise artifacts explicitly if evidence requires materially different behavior.
- SDK publishing and beta/Core
  dependency-pin publication follow their own validated, authorized release steps.
- Sync and archive only after implementation and the applicable verification pass;
  leave official Cloud handoff and the 23-hour hold-limit question separate.
