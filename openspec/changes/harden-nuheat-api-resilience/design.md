# Design

## Context

See proposal.md for the observed b9/SDK behavior and public API sources. This is
cross-cutting work: the SDK must preserve transport semantics and shared quota
state, while HA owns timers, availability, user feedback and account lifecycle.
Both beta and current Core pin SDK 0.1.2. The beta owns planning; Core keeps its
framework-specific source and contribution workflow.

## Goals / Non-Goals

**Goals:** limit exceptional-path latency, honor quota delays consistently, and
keep optional permissions from discarding authoritative data. Preserve successful
command semantics and existing identities with explicit error categories.

**Non-Goals:** vendor load testing, production or hardware access, changing OAuth
registration/PKCE, credential migration, mode payload redesign, new UI controls,
or official Cloud handoff eligibility. No new third-party runtime dependency.

## Decisions

### 1. SDK-owned typed failures and runtime cooldown

Introduce a permission failure that remains compatible with the public
`NuHeatApiError` catch contract, and a rate-limit failure carrying remaining
cooldown information. Keep genuine `NuHeatAuthError` behavior for persistent 401.
Do not turn a 403 into an OAuth refresh attempt. HA must map permission failures
before generic API failures in setup, config validation, polling and control
paths, with clear sanitized messages and no automatic credential changes.

Keep a monotonic cooldown deadline on the runtime account's shared SDK client,
covering required/optional v1/v2 calls for every thermostat. Check it before
network submission; refresh the check after awaited authorization so another
request's new cooldown is not missed. Existing in-flight calls may finish; do
not claim global serialization of all HA instances sharing the registration.
When optional v1 receives 429, retain conservative v2 data but preserve the
client cooldown for later requests and expose its remaining delay to HA.

Parse Retry-After delta-seconds and HTTP-date forms; convert an absolute date to
a remaining delay once, then use monotonic scheduling. Missing/invalid headers
use a documented 60-second fallback. A new response must not shorten an existing
deadline. Expired dates/zero delay allow normal cadence; no tight-loop retries.
Use finite validated values and safe chunked scheduling for very long deadlines
rather than shortening a valid vendor cooldown or overflowing a timer.

Alternative rejected: coordinator-only backoff loses optional-endpoint cooldowns
and lets other calls from the same client continue hammering the quota.

### 2. Defer reads; reject new writes without queuing

HA reconciliation and normal refresh paths consult the shared cooldown. Schedule
at most one eligible account reconciliation callback, never an eight-second
network attempt during a longer cooldown. Pending mode/target deadlines remain
thirty seconds and expire even when no read is currently allowed. Coalesce with
normal polling so expiry cannot produce a request burst. Only reads may resume
automatically; previously rejected commands never execute later.

New user commands during cooldown raise a retry-later service error before a PUT
or optimistic state. Check cooldown before waiting for the entity lock and again
before network submission so an already-throttled command fails promptly.
A write that already succeeded before a throttled readback
remains uncertain: report that distinction, reconcile later and never repeat it.
The existing single 401 refresh/retry is preserved because it follows an explicit
authorization rejection, not an uncertain transport outcome.

Alternative rejected: sleeping with the entity lock held delays controls, makes
expired intent execute late, and interferes with shutdown.

### 3. Explicit transport and complete-operation budgets

Proposed defaults for isolated validation: 15 seconds total per SDK HTTP request
including body consumption, and 30 seconds for a complete public SDK operation
including its token-provider wait and nested v2/v1 readbacks. Nested calls must
not reset or extend the outer deadline. Use asyncio/aiohttp's existing timeout
facilities; never alter HA's shared session configuration globally.

HA control operations also have a 30-second total budget including lock wait,
write and coordinator readback. A command that expires while waiting for an
earlier command is cancelled before transmission, not queued for later. Bound
integration-owned initial token-validation waits consistently, while retaining
HA's existing OAuth token storage, rotation and refresh serialization. Do not
replace framework-owned interactive authorization timeout handling.

Timeouts map to communication failures, not expired credentials. Release HTTP
responses and per-entity locks; propagate cancellation rather than swallowing
it. Preserve generation guards and shutdown cancellation so a late read cannot
confirm newer intent or schedule work after unload. The operation budget is
separate from the existing thirty-second post-command confirmation window.
If a timed-out operation may have submitted a write, schedule only reconciliation
reads while the integration remains loaded; do not fabricate accepted state.
Unload cancellation must not create that follow-up work or suppress cancellation.

Alternative rejected: bounding only background reconciliation leaves stalled
PUTs and SDK post-write GETs holding the command lock for the session default.

### 4. Endpoint-aware permission fallback

Required reads and all writes treat 403 as a visible permission error; a forbidden
Permanent Hold PUT must never fall back to physical Manual. Optional v1-detail
403 retains the successful v2 sample with `schedule_details_requested` and no
trusted v1 enrichment. Do not recycle previous details into the new sample.
Keep implicit target changes blocked when mode preservation is unresolved.
Persistent optional 401 still propagates the genuine authorization failure.

Alternative rejected: catching every authorization error in optional enrichment
could conceal revoked credentials. Conversely, treating every 403 as an expired
login needlessly interrupts working v2 access and suggests ineffective relinking.

## Verification and compatibility

Use synthetic clocks, sessions, endpoints and credentials. Cover both SDK list
and individual-get enrichment; all controls; malformed/delta/date headers; two
devices sharing cooldown; startup/auth waits; stalled write, body and readback;
lock-wait cancellation; unload; no duplicate writes; and unknown mode details.
Retain Celsius/Fahrenheit, timed expiry, entity identity and migration suites.

Client tests include backward-compatible exception bases and exact unchanged
successful request payloads. Beta tests assert retry timing and visible error
classification rather than just exception construction. Mirror behavior in a
separately authorized Core port and test on each framework's matching environment.
Any runtime changes keep current-Core handoff eligibility unchanged.

## Risks / Trade-offs

- Shorter request budgets may expose slow vendor responses: exercise delayed
  success/failure boundaries and report uncertainty without write retries.
- Quota is vendor-wide per account/client while state here is runtime-local:
  respect returned headers, make no promise to coordinate separate HA processes,
  and never use production to generate real 429 responses.
- Optional permission fallback reduces classification precision: preserve v2
  availability while refusing implicit writes that require missing details.
- An SDK pin bump is required to distribute client fixes: validate a local wheel
  first and obtain separate authorization for SDK/beta release or Core submission.

## Migration Plan

No config-entry schema, domain, registry or provider migration. Implement SDK
changes and tests locally, consume the local candidate in an isolated beta
environment, then prepare the separately authorized Core alignment. Run full
regressions, packaging and privacy checks before any commit/release request.
If checks fail, keep the released SDK/beta pins and allowlist unchanged. Runtime
rollback uses the previous compatible release without recreating entities.
