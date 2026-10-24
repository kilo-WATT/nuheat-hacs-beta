# Tasks

## 1. Independent local diagnostics

- [x] 1.1 Add an allowlisted cached-state diagnostics handler; verify synthetic nested private markers, unknown keys, URLs and errors are excluded and no API/token/session call occurs, including incomplete setup and cooldown.
- [x] 1.2 Document the diagnostic fields, local-only behavior and safe support-sharing guidance; add the exact file to packaging/provenance and verify diagnostics tests plus `python -m pytest -q tests/test_packaging.py` and `python tools/package.py` pass without changing protected OAuth/migration/handoff bytes.

## 2. Hold-duration evidence and policy

- [ ] 2.1 Resolve gate H from applicable public vendor guidance or a separately authorized vendor answer; deliver a dated evidence record for v2 applicability, boundary/clock rules and existing longer holds, with no private correspondence. Keep 2.2 and 2.3 blocked if unresolved; the unsent question draft is not confirmation.
- [ ] 2.2 Implement the verified SDK duration policy and HA action validation without changing readback parsing or preset meanings; verify synthetic limit-minus-one-second, exact-limit, plus-one-second, expired-after-lock-wait, UTC/DST, C/F and inherited-expiry cases with no rejected writes or silent clipping.
- [ ] 2.3 Document the confirmed limit and translated error with an existing-hold recovery example; verify action/service metadata, unchanged ordinary hold/Permanent Hold controls and identity retention using `python -m pytest -q tests/nuheat/test_hold_action.py tests/nuheat/test_migration.py` plus SDK policy tests.

## 3. Push invalidations with polling fallback

- [ ] 3.1 Resolve gate P's protocol, token, subscription and lifecycle contracts using applicable vendor evidence; record an async transport/dependency/license choice and synthetic handshake expectations. Do not treat an unperformed live connection as success; leave 3.2 and 3.3 blocked if compatibility is unresolved.
- [ ] 3.2 Add a bounded SDK notification adapter and beta default-off option/lifecycle; verify synthetic subscribe/disconnect/token-refresh, reconnect backoff, malformed/unknown events, two-account isolation, disabled zero-connections and unload cleanup with no token URLs in logs.
- [ ] 3.3 Route notifications through shared cooldown-aware coalesced reads while retaining five-minute fallback and existing command deadlines; test duplicate/out-of-order events, quota bursts, simultaneous poll/reconcile/push, missed events, stale readback, failed writes and unload without write replay. Document opt-in/fallback, audit any dependency and exact package additions, and run notification, resilience and packaging tests.

## 4. Optional period energy reporting

- [ ] 4.1 Resolve gate E's units, zero/load validity, timezone/DST, bucket identity and correction/reset/retention rules; record synthetic day/week/month fixtures and explicit statistics exclusions. Leave 4.2 and 4.3 blocked if runtime/consumption semantics cannot be verified.
- [ ] 4.2 Add typed SDK energy GET models and bounded cached reporting separate from climate but sharing its runtime client; test missing/invalid/genuine-zero data, partial/corrected/repeated and DST buckets, nonoverlapping period accounting, 401/403/404/405/429 and request cancellation; document the SDK contract alongside tests.
- [ ] 4.3 Add disabled-by-default runtime/estimated-energy sensors to existing devices and document units/estimates, fifteen-minute caching and lack of unverified Energy dashboard/cost support; verify enabled/disabled transitions, zero disabled requests, stable climate and sensor registry associations, optional failure isolation, command responsiveness and unload. Validate exact packaging additions and sensor metadata in isolated HA.

## 5. Explicit relative adjustment

- [ ] 5.1 Resolve gate R's reference temperature, signed scale/range and mode/expiry behavior; record confirmed enum values separately from unresolved semantics and supported endpoint/mode combinations. Leave 5.2 and 5.3 blocked while the safe resulting-state contract remains unverified.
- [ ] 5.2 Add typed SDK interpretation and the existing-entity adjustment action while retaining absolute defaults; test signed finite deltas, +1.8°F to +1°C conversion, quantization/ranges, every supported mode, pending expiry and no-write rejection of unknown/Standby/unsupported combinations. Document the SDK/action contract and standard-card boundary.
- [ ] 5.3 Integrate nonreplayed relative intent with existing locks/cooldown/deadlines; verify rapid deltas, stale/out-of-order reads, failed PUT and accepted-PUT/failed-GET, genuine 401 contract, timeout/lock wait, supersession and unload without invented absolute optimism. Document unconfirmed outcomes and verify existing absolute controls remain unchanged.

## 6. Cross-feature verification and Core alignment

- [x] 6.1 Run complete SDK and beta suites against an isolated installed SDK wheel; run SDK mypy and both repositories' Ruff lint/format checks, `git diff --check`, `python tools/package.py` and `npm run specs:check`. Record exact counts, SDK provenance and synthetic-versus-live scope; audit private markers and protected OAuth, migration, identity and handoff files. Keep blocked feature tasks unchecked rather than claiming the whole proposal complete.
- [x] 6.2 Deliver a Core alignment and staged-readiness report mapping each implemented capability to source/tests and Core-specific APIs; verify no community registration copied, no upstream edits and no allowlist expansion. Identify unresolved gates, dependency publication needs and optional-feature rollback before any separately authorized release.

## Workflow follow-up

- Planning only. Start implementation through a new apply request; independent
  diagnostics may proceed while external gates remain unresolved.
- Vendor messages, account/protocol probes, hardware commands, production
  changes, commits, pushes, SDK publication and releases need their own scope.
- Review and revise this plan if gate evidence contradicts the proposed behavior;
  do not weaken requirements or call a deferred feature completed.
- Sync/archive only implemented and verified requirements. Split a reviewed
  completed stage into its own change before partial publication/archival rather
  than claiming all five capabilities shipped.
