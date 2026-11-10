# Vendor clarification assessment — 2026-11-10

Planning only. No implementation, production access, live NuHeat connection,
thermostat command, deployment, commit, push or publication was performed.
Public GitHub metadata/docs were read; all behavioral probes used fake sessions.

## Sources and inspected revisions

- [Chemelex's public reply](https://github.com/home-assistant/core/issues/175923#issuecomment-6737221965).
- [Microsoft SignalR JSON protocol](https://github.com/dotnet/aspnetcore/blob/main/src/SignalR/docs/specs/HubProtocol.md)
  and [configuration](https://learn.microsoft.com/en-us/aspnet/core/signalr/configuration).
- Beta release v0.1.0b11, inspected preparation commit
  `d804cc3652d11b840f9f6794962ff5b3af5673c1` (published merge has the same tree).
  Public current `climate.py` blob matched the inspected file.
- SDK candidate 0.1.4 at `47e9dc5004c5415f0d917d147ab9f22ef58b2c2f`.
  Public current `client.py` blob matched the inspected local file. The beta
  continues pinning 0.1.3; its tagged `client.py` blob also matches. No version
  change is proposed in this planning pass.
- Context7 lookup failed with npm registry DNS resolution failure. Official
  Microsoft documentation was used instead; no documentation client was installed.

## Findings

| Topic | Confirmed vendor contract | Existing behavior / mismatch |
| --- | --- | --- |
| Push | SignalR JSON v1; direct WebSocket preferred because negotiate can return 404; bearer header only; subscription repeated after reconnect; Notify invalidates state | No SDK adapter or beta connection lifecycle exists. Existing five-minute polling is correct fallback. The write reconciliation rescheduler resets its delay on every call and must not be reused blindly for repeated notifications. |
| Push deduplication | Timestamp is last state change, including repeated periodic events; reconnect needs a full GET | No timestamp tracking yet. Plan per-known-device/account tracking, ignore equal/older timestamps, one due coalesced read, and an unconditional reconnect GET. Events never confirm targets/modes. |
| Holds: upper limit | v2 imposes no 23/24-hour cap; app restriction is separate | Runtime has no upper cap and is correct here. Old proposal's future cap and vendor-duration blocker are stale. |
| Holds: lower limit | Server checks receipt time; past or less-than-two-seconds-ahead values return 400 | HA only tests expiry greater than local now; SDK has no minimum-lead check. A locally future value can still be rejected after waits/transit. Add submission-time validation and preserve server error handling; local time cannot guarantee server acceptance. |
| Holds: precision | Offsets convert to UTC, fractional seconds are dropped, readback is UTC | SDK sends microseconds, beta retains the original requested expiry, coordinator compares exact datetimes. A fake vendor-style truncated readback reproduced inequality. Canonicalize payload and pending intent together rather than adding a broad confirmation tolerance. |
| Holds: retention | A timed retarget must send holdUntil again | Existing ordinary/pending timed-target paths explicitly carry expiry and are correct. Keep that behavior; an intentional preset/mode change is separate. |
| Relative | Last cloud-reported measured room temperature plus signed hundredths-Celsius delta; endpoint determines mode and only explicitly resent expiry survives | SDK rejects temperature_type; no wrong setpoint-delta implementation is shipped. Its unverified-enum explanation and proposed generic mode-preserving adjustment need correction. A room-relative action is distinct from incrementing the target, and resulting-limit/clamping policy remains unspecified. |
| Energy | UTC buckets; day has 24 hours; newest first; float Wh estimates; both models supported; load edits can revise history | No energy API/models/sensors are shipped, so there is no existing incorrect accounting. The plan must use explicit Wh, replace UTC-keyed buckets, avoid overlapping granularities and total_increasing, and avoid claims of immutable totals. |
| Energy zero | Zero cannot distinguish no heating, missing floor load or offline reporting | Old plan's verified-genuine-zero gate cannot be satisfied from this API. Preserve estimated raw zero with unknown quality, not a claim of verified no consumption; missing/invalid data stays unavailable. |
| HTTP 401 | Rejected before thermostat acceptance | SDK already retries only that request once after forced refresh. A post-PUT GET 401 retries the GET, not the write. Transport/timeouts/5xx/readback uncertainty do not replay writes. Add explicit write-path regressions, not a new retry policy. |

HA's offset-free action input uses its configured timezone. That is intentional UI
behavior, distinct from the vendor API's offset-free-as-UTC convention. Do not
change this existing user contract or weaken strict response parsing accidentally.

## Synthetic checks executed

Existing library tests, without cache/bytecode writes:
`python -m pytest -q -p no:cacheprovider tests/test_client.py -k "401 or rejected_authorization or temperature_type or schedule_mode"`:
**3 passed, 69 deselected**. This is selected baseline coverage, not validation
of unimplemented features.

Additional in-memory probes reused `tests/test_client.py` FakeSession/FakeResponse:

| Probe | Observed methods | Result |
| --- | --- | --- |
| Rejected PUT 401, then success | PUT, PUT, GET | One forced refresh; rejected request retried once |
| Accepted PUT, readback 401 | PUT, GET, GET | One forced refresh; no repeated PUT |
| PUT transport failure | PUT | Error surfaced; no retry |
| Accepted PUT, readback transport failure | PUT, GET | Error surfaced; no repeated PUT |
| Fractional explicit hold, whole-second readback | PUT, GET | Wire retained fractional seconds; readback did not equal requested expiry |

No test read credentials, used an actual account/device identifier, or opened a
network connection. Probe payloads were synthetic and are not copied from vendor
sample identifiers. No new tests or runtime files were written.

## Smallest proposed implementation and affected files

**A — expiry and retry contract:** library `src/chemelex_nuheat/client.py`,
`tests/test_client.py`, `tests/test_resilience.py`, library documentation;
beta `custom_components/nuheat/climate.py`, existing hold-action/reconciliation
tests and user docs. Preserve exact coordinator confirmation; canonicalize its
input rather than changing matching tolerance. Test long holds, fractional
seconds, offsets/DST, near expiry after lock/token waits, explicit retention,
definite PUT/GET 401, uncertain writes and cancellation.

**B — default-off push proof:** a proposed library
`src/chemelex_nuheat/notifications.py` and fake-hub tests, minimal public export
if required; beta runtime setup/unload in `__init__.py`, coordinator invalidation
queue, options flow/translations for opt-in, synthetic lifecycle tests, docs and
exact packaging/provenance updates as needed. Retain REST polling. Use aiohttp's
existing transport with the documented limited JSON protocol; no broad SignalR
dependency or new thermostat entities. Existing OAuth/token callback is reused.

The proof is local and opt-in, not a beta deployment. Do A first and review its
evidence before B. C (estimated-energy models) and D (room-relative controls)
remain separately approved later tasks; no energy entities/statistics or relative
HA action belongs in the initial proof. The user's approval is required before
implementing any stage.

## Remaining evidence limits

Vendor statements resolve protocol semantics but do not prove this client's live
reachability, precise deployed WebSocket routing, reconnect/session limits or
device-limit behavior for relative results. Synthetic protocol/clock tests come
first. A future live push-only connection would need separate explicit approval;
it must not be bundled with thermostat-write approval. A recent energy refresh
window cannot guarantee repairing arbitrarily old load-driven revisions.

Do not send new vendor questions automatically. Historical vendor request and
validation files remain evidence of their original date, not current blockers.
