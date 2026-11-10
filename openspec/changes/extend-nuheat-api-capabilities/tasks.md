# Tasks

Scope revision 2026-11-10: stages A and B are approved for isolated implementation and synthetic tests only. C and D remain later work needing separate approval. Previously completed diagnostics and baseline verification retain their original evidence; they do not validate these additions.

## 1. Independent local diagnostics â€” completed historical scope

- [x] 1.1 Add an allowlisted cached-state diagnostics handler; verify synthetic nested private markers, unknown keys, URLs and errors are excluded and no API/token/session call occurs, including incomplete setup and cooldown.
- [x] 1.2 Document the diagnostic fields, local-only behavior and safe support-sharing guidance; add the exact file to packaging/provenance and verify diagnostics tests plus `python -m pytest -q tests/test_packaging.py` and `python tools/package.py` pass without changing protected OAuth/migration/handoff bytes.

## 2. Stage A â€” hold and authorization contract proof

- [x] 2.1 Record the public Chemelex reply and inspect current beta/library behavior; verify the assessment distinguishes no upper v2 cap, server two-second lead time, whole-second UTC, explicit expiry retention, and definite 401 versus uncertain acceptance. Evidence: assessment.md and existing fake-session probes, with no live calls.
- [x] 2.2 Implement shared canonical expiry and submission-time validation in SDK and beta pending intent; verify synthetic 23/24-hour-plus acceptance, sub-second precision, UTC/DST, server-400 handling, inherited/pending expiry, expiry after lock/token wait and definite-401 retry, with no clipping, extra mode writes or changed existing temperature range.
- [x] 2.3 Document no API upper cap, server lead-time limits, explicit retention and unchanged HA local-time input; verify hold-action/migration tests, identical entity/device/provider associations, and normal preset/Permanent Hold controls.
- [x] 2.4 Add explicit SDK write-path regressions: PUT 401 â†’ one refresh/retry; repeated 401 â†’ auth failure; successful PUT followed by GET 401 â†’ GET-only retry; disconnect/timeout/5xx or failed readback â†’ no write replay. Verify request counts/payload equality, response cleanup and operation deadlines, and update SDK retry documentation.

## 3. Stage B â€” opt-in push invalidations with polling fallback

- [x] 3.1 Prove the documented direct-WebSocket SignalR JSON v1 subset against an isolated fake hub using existing aiohttp; test record separators, split/combined/oversized frames, handshake, Subscribe completion, pings/Close and header-only authorization. Document protocol subset and bounds; no new dependency or live hub access.
- [x] 3.2 Add SDK adapter and beta default-off option/setup/unload lifecycle; verify valid-token reconnect, one definite-401 refresh attempt, resubscription plus full GET, cancellable jitter/backoff, account isolation, zero connections when disabled, no token/frame leakage, and cleanup during every wait. Document opt-in and polling-only rollback.
- [x] 3.3 Route validated notifications through a nonstarving coalesced refresh path retaining five-minute polling; test repeated timestamps, older/unknown/malformed events, one follow-up after an in-flight read, storms during 429 cooldown, polling/write reconciliation overlap, stale reads, failed writes, unchanged confirmation deadlines and unload. Update exact package/provenance entries only if needed and verify runtime/privacy packaging checks.

## 4. Stage C â€” later optional energy reporting, not initial proof approval

- [ ] 4.1 Capture confirmed UTC 24-hour/newest-first estimated-Wh semantics and create synthetic models/fixtures; verify zero remains quality-unknown, both thermostat model contracts are documented, and historical revisions are not treated as immutable. No new vendor clarification needed for these confirmed facts.
- [ ] 4.2 Add typed SDK GET models for one canonical hourly granularity; verify newest-first parsing, UTC/DST, Wh conversion, corrected/decreasing/duplicate/partial buckets, no overlap summation, optional failures, shared cooldown and cancellation. Document bounded refresh and historical-revision limits; no statistics import or sensor yet.
- [ ] 4.3 Only after separate approval, add disabled-by-default reporting/cache/entities; verify zero disabled requests, stable registries, optional failure isolation, responsiveness and unload, and document estimated-data quality without measured-power, cost, total_increasing or Energy dashboard claims.

## 5. Stage D â€” later measured-room-relative controls, not initial proof approval

- [ ] 5.1 Capture confirmed measured-room base, signed hundredths-Celsius scale and endpoint-selected mode/expiry behavior in synthetic fixtures; document that device-limit/clamping policy and any setpoint-increment feature remain separate unresolved scope before HA exposure.
- [ ] 5.2 Add explicit SDK relative interpretation only after approval; verify differing room/setpoint values, positive/negative deltas, Fahrenheit differences, explicit endpoint choices, resend retained expiry, and reject unsupported v1 Permanent Hold/Standby/unknown combinations. Document that ordinary absolute APIs remain unchanged; no HA action in this SDK proof.
- [ ] 5.3 Only after separate user-facing policy approval, implement HA relative action and bounded confirmation; verify ordered rapid operations, stale room readings, pending expiry, definite-401-only retry, uncertain writes/readbacks, cooldown/timeout/supersession/unload, no invented absolute optimism and standard-card limitations.

## 6. Cross-feature verification

- [x] 6.1 Run complete SDK and beta suites against an isolated installed SDK wheel; run SDK mypy and both repositories' Ruff lint/format checks, `git diff --check`, `python tools/package.py` and `npm run specs:check`. Record exact counts, SDK provenance and synthetic-versus-live scope; audit private markers and protected OAuth, migration, identity and handoff files. Historical evidence in validation.md applies to the diagnostics/resilience baseline, not newly proposed stages.
- [x] 6.2 Deliver a Core alignment and staged-readiness report mapping each implemented capability to source/tests and Core-specific APIs; verify no community registration copied, no upstream edits and no allowlist expansion. This is historical work; the current request explicitly excludes all new Core work.
- [x] 6.3 For each approved new stage, run relevant SDK/beta suites, SDK typing, lint/format, exact packaging/provenance/privacy and OpenSpec checks against an isolated installed candidate wheel; record exact versions, results and unverified live assumptions. Verify no Core, production, OAuth/migration/identity or handoff changes. Stop for review before any commit, push, dependency publication or deployment.

- [x] 6.4 Execute the separately approved isolated live Stage B check: fresh lab OAuth, header-authenticated hub subscription, user-made app change followed by authoritative HA refresh, controlled reconnect and unchanged five-minute polling fallback. Enforce zero agent thermostat writes and zero production access; record only sanitized counts/timings and clean up the listener/lab. This approval does not authorize publishing, pushing, deployment or live Stage A write tests.

- [x] 6.5 Execute separately approved isolated live Stage A timed-hold validation on the same linked thermostat: at most six commands including restoration, within ±0.5°C of the original target, preserve explicit expiry during retargeting, retain a private baseline and verify restoration. Abort on unexpected behavior; no production access, deliberate failure injection, commits, pushes or publication.

- [x] 6.6 Following renewed approval, investigate expiry rewrite with signed differences and paired list/single-device readbacks; run synthetic instrumentation checks first, use a bounded isolated test with restoration and no production access. Implement a correction only if supported by evidence, preserving exact expiry and uncertain-write safeguards.

## Workflow follow-up

- Obtain approval for A and B before apply; do not implement C or D under that approval.
- No production, live API/hardware testing, deployment, publishing, pushes or vendor messages without explicit authorization.
- Keep vendor-confirmed contracts distinct from fake-hub correctness and unperformed live compatibility tests.
- Split an approved completed stage into a reviewable change before partial archival; do not mark this entire multi-stage plan complete because one proof passes.
