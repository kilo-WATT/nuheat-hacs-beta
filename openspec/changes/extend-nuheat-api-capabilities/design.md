# Design

## Context

See proposal.md for the observed gaps and public sources. The existing beta has
one climate platform, a fixed package-file allowlist, explicit timed-hold action,
shared runtime API cooldown and bounded command reconciliation. The SDK candidate
adds permission/rate-limit errors and request/operation budgets. None of the four
optional capabilities is implemented. No vendor answer or push/energy/relative
live observation is available in this proposal.

## Goals / Non-Goals

**Goals:** independently testable stages; a concrete evidence gate before each
vendor-dependent runtime addition; additive entities/actions that preserve the
existing account/device model; reliable fallback and privacy by construction.

**Non-Goals:** user-facing alerts, dashboard changes, schedule editing, price or
load-setting writes, inferred measured power, unverified Energy dashboard totals,
replacing OAuth, expanding handoff eligibility, changing Core in this request,
or treating API documentation as proof of live protocol compatibility.

## Decisions

### 1. Separate evidence gates from implementation

Use four explicit gates, with timestamped public sources or a paraphrased vendor
answer stripped of private correspondence. A gate fails closed if evidence is
missing. Implementation of another independent stage can continue, but its
completion does not complete blocked tasks. Changing a gate's intended behavior
requires revising this plan before coding, not guessing during apply.

| Gate | Required evidence | If unresolved |
| --- | --- | --- |
| H: hold duration | v2 applicability of 23 hours; inclusive/exclusive boundary; server clock basis; retained longer-hold policy | Document restriction and question; no new runtime cap or long hold test |
| P: push | hub/protocol version, token transport, Subscribe contract, account/device filtering, expiration and disconnect behavior | Keep push disabled; retain polling |
| E: energy | timezone/DST, bucket identity, units, revision/reset behavior, configured load and zero validity | Keep sensors unexposed; no energy-statistics import |
| R: relative | 0/1 enum already documented; additionally reference temperature, signed delta scaling, range, mode/expiry behavior | Keep existing SDK rejection and absolute controls |

Draft outreach in vendor-questions.md; do not send it under planning/apply
authority alone. Use synthetic responses for implementation first. Additional
read-only account probes, long holds, reconnect testing on real credentials or
hardware writes require their own explicit live scope. Prior six-command live
approval applied to the completed resilience test, not these new features.

The alternative is shipping all documented fields immediately. It is rejected:
the schemas omit details that affect thermostat state and historical statistics.

### 2. Diagnostics is the first independent implementation

Add the standard entry diagnostics handler in `diagnostics.py`, returning a
constructed schema, not a recursively dumped config entry or SDK dataclass.
Include integration/SDK versions, coarse setup/availability, cooldown-active
status and pending-confirmation categories/counts. Omit temperatures, schedules,
times of user activity, names, paths, serials, IDs, host URLs, entry data/options,
raw messages and all credential material. No opaque serialized exception objects.

Tests seed private markers in keys and values at every nesting depth, verify
only the allowlisted schema appears, and assert no session/token/API methods
were called. No extra dependencies are needed. Register the new file explicitly
in package allowlist/provenance; do not broaden the allowlist to arbitrary files.

### 3. Hold validation is conditional on gate H

After confirmation, put a shared duration policy in the SDK and invoke the same
policy from the HA action after timezone normalization. Compare elapsed UTC time
using an injectable clock. Validate near submission inside the existing command
budget so lock wait cannot make an already expired request valid. Return a
translated error with the supported window; do not clamp or send a trial write.

Do not add a maximum to readback parsing: older holds must remain representable.
Retargeting a longer hold uses the policy confirmed by the vendor; if disallowed,
reject the new command without modifying its existing expiry. Keep preset
next-schedule Hold and Permanent Hold independent from explicit-expiry bounds.
Tests cover limit minus one second, exact limit, plus one second, expired input,
timezone offsets/DST, Celsius/Fahrenheit, queue delay and no-write failures.

### 4. Push invalidates; existing scheduler reads and confirms

After gate P, use an optional transport adapter owned by the SDK, with one
connection per runtime account. Beta owns setup/unload and a default-off option
for initial rollout. Do not start a connection merely to validate config flow.
Choose a maintained async implementation only after protocol, license and
dependency compatibility are verified; aiohttp is already present but does not
by itself prove SignalR framing/subscription compatibility.

Push carries invalidations rather than trusted climate values. Account events
refresh the account; known thermostat events also use the account refresh path.
Unknown devices never create identity associations from a notification alone.
Coalesce with normal polls and command reconciliation before their shared lock;
use existing cooldowns and do not extend thirty-second confirmation deadlines.
Keep five-minute polling as a safety net even when push is connected. Bound
connect/subscription to the SDK operation budget; exponential reconnect backoff
from 5 to 300 seconds with jitter, cancellable on unload. Authentication uses
the existing token callback and failure classification, with no provider switch.

Never log token-bearing transport URLs or raw frames. Tests cover duplicate,
out-of-order/malformed and unknown events, two accounts, missed-event fallback,
refresh overlap, disconnect during a command, quota, auth refresh and shutdown.
Update `iot_class` only after implemented behavior supports the change and HA
validation passes; it is not changed by this proposal.

### 5. Period energy models precede optional sensors

After gate E, add SDK models and GET methods for the documented day/week/month
endpoints. Use stable period keys and replace corrected values, never sum
overlapping day/week/month datasets. Parse explicit units and missing/invalid
values strictly. Do not derive power by sampling relay state or use price fields
without a verified currency contract.

Use a separate reporting coordinator/cache sharing the same runtime client and
cooldown. Requests run only when reporting entities are enabled, never on the
climate command path. Start with a bounded fifteen-minute cache for enabled
current-period reports and no automatic historical backfill; increase cadence
only from documented need. Optional 403/404/405 or malformed reporting data
affects sensors, not climate availability; genuine 401 retains the existing
account authorization rules. Respect common 429 and operation budgets.

Add disabled-by-default runtime and estimated-energy sensor descriptions with
deterministic unique IDs derived from the existing device identity plus metric.
Periods must be explicit in names/attributes. Do not declare a cumulative
`total_increasing` sensor for a resetting or corrected period series. Initial
Energy dashboard eligibility remains off until reset/correction semantics and
HA statistics tests justify a separately reviewed representation. All data is
vendor-estimated; there is no measured-power or cost sensor in this stage.

### 6. Relative is an explicit action, never an implicit fallback

After gate R, add typed temperature interpretation to the SDK, preserve existing
absolute method defaults, and expose `nuheat.adjust_temperature` on existing
climate entities with a signed finite delta. For differences, 1.8°F maps to 1°C;
never apply the absolute Fahrenheit offset. Do not invent a client-side
read/modify/write substitute that races against cloud changes.

Support only verified endpoint/mode combinations. Physical Manual, explicit
timed hold and next-schedule hold must preserve their confirmed contract;
reject Standby, unresolved classification and unsupported Permanent Hold or
scheduled combinations. Reuse the entity lock, operation budget and pending
expiry rules. Relative PUTs are non-idempotent: persistent authorization handling
must not replay a request whose acceptance is uncertain. Preserve SDK's known
401-before-acceptance contract; no retry on transport/readback uncertainty.

Do not optimistically fabricate an absolute target from stale local data. Keep
an operation generation/deadline for relative intent and use only verified
post-command readback for a resulting target. If read ordering cannot establish
compatible confirmation, expire as unconfirmed. Tests cover positive/negative
deltas, quantization, ranges, pending expiry, rapid commands, stale API data,
failure after accepted PUT, quota/lock waits and unload.

## Risks / Trade-offs

- Legacy guide versus v2 behavior → gate H and explicit boundary evidence.
- More cloud requests and reconnect storms → disabled optional reporting/push,
  bounded caches/backoff, account cooldown and read coalescing.
- Energy-history corruption → no unverified statistics or overlapping summation.
- Delta applied twice → never retry uncertain writes; generation-based readback.
- Token leakage through websocket URLs → URL/frame log suppression and marker tests.
- Extra SDK dependency and unpublished current candidate → validate/publish each
  SDK independently with authorization before selecting a releasable beta pin.
- Optional features enlarge a pending Core PR → provide a port map, not an
  upstream change; Core maintainers can review independent follow-up work.

## Migration Plan

No config-entry version bump or migration rewrite is planned. Options are
additive with disabled defaults; reporting sensors share existing devices and
do not replace climate entities. Rollback disables optional features and keeps
thermostat/account identities and credentials. No conversion of an existing
hold or deletion of entries is permitted. Runtime file additions require exact
packaging/provenance updates and separate publication authorization.

Implement in order: diagnostics, hold evidence/policy, push gate/adapter, energy
gate/models/sensors, relative gate/action. Synthetic validation comes first;
hardware or production tests stay separately authorized. Verify Core native
temperature properties, lifecycle APIs and official OAuth separately when a
port is approved. The handoff guard and shipped allowlist stay unchanged.
