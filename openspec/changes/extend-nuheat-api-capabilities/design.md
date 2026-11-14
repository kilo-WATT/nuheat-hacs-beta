# Design

## Context

See proposal.md and assessment.md. The old vendor gates are superseded by the public Chemelex reply. Beta v0.1.0b11 and SDK 0.1.3 already support the required REST failure classification and basic explicit holds. The local library candidate is 0.1.4; its version must not silently replace the beta pin. Diagnostics is complete. The user approved A and B for isolated implementation; C and D remain subject to separate approval. See stage-ab-validation.md for the local result.

## Goals / Non-Goals

**Goals:** prove expiry correctness and optional push-triggered REST refresh in separately testable stages, preserving identity, provider associations, existing controls and bounded reconciliation.

**Non-Goals for the initial proof:** energy entities/statistics/backfill, relative HA actions, setpoint-increment semantics, user alerts, new OAuth applications, Core changes, live vendor connectivity, production access or publication. No EGM run is needed for this bounded proposal; a broader statistics/action architecture would need its own design approval.

## Decisions

### A. Correct expiry semantics before adding a new transport

Normalize an explicit expiry to UTC and drop fractional seconds before validating, serializing or retaining pending intent. A shared SDK helper can define the canonical value; the beta must use that same value for exact confirmation. Keep explicit timezone-aware SDK inputs; HA continues resolving offset-free input in its configured timezone before calling the SDK. The vendor's offset-free-as-UTC rule does not justify changing HA's documented local-time UI or accepting offset-free API responses silently.

There is no v2 upper hold limit. Do not implement the old proposed 23/24-hour cap. Validate the canonical future expiry with at least the documented two-second lead time near each actual submission, after lock and authorization waits, including a definite-401 retry. Do not add time or move the user's expiry forward. Local validation cannot guarantee server-clock or transit timing; surface a server 400 without retrying or clipping. Use an injectable clock for synthetic tests. An inherited expiry that is too close to send must fail visibly instead of losing its hold mode.

Every timed retarget sends the explicit expiry again, including accepted pending expiry. Selecting the ordinary Temporary Hold preset remains a deliberate next-schedule control; selecting Manual or another preset intentionally supersedes prior expiry. Permanent Hold remains the existing v1 path, with no invented relative v1 support.

Keep one forced refresh and one retry for a definite HTTP 401. That response means the rejected request did not reach the thermostat. A 401 on the GET after an accepted PUT retries only that GET. No retry for uncertain PUT acceptance, disconnect, timeout, 5xx, or failed post-write read. Shared cooldown and total operation budgets still apply.

### B. Small optional SignalR proof with the existing transport dependency

Use one default-off adapter per runtime account, based on existing aiohttp WebSocket support. Implement only the documented ASP.NET Core SignalR JSON v1 subset: record-separator framing, handshake/response, Subscribe completion, Notify invocation, application Ping and Close. Handle split/coalesced records, bounded buffers and unknown messages. Do not add an unreviewed third-party SignalR dependency or general-purpose hub framework.

Use the documented `/v2/notificationsHost` hub path on the configured trusted API origin, distinct from REST's `/api/v2/...` path prefix. Prefer direct WSS; skip negotiation because Chemelex reports intermittent negotiate 404. Validate the synthetic URL construction. Exact deployed routing remains untested until separately authorized live validation. Do not add query-string tokens, cross-origin redirects or fallback transports in the proof.

Obtain authorization through the existing token callback and send only an Authorization Bearer header. An established socket need not be cycled merely at the token's sixty-minute age; obtain a valid token on reconnect. A definite connection 401 permits the existing single forced-refresh attempt. Optional hub failure must leave REST polling usable; persistent REST authorization failure follows the existing account reauthentication path.

Send Subscribe with a connection-local invocation ID and thermostat type 2. UserAccount type 1 is reserved for a later justified use; the initial proof does not need it. Wait for successful completion, resubscribe after reconnect, and request one full account GET after each successful initial connection/reconnect. No subscription persistence or exactly-once delivery is assumed.

Validate recognized Notify messages against devices already known to that account. Parse offset-aware timestamps and track the newest change time per known device; ignore duplicates and older events. Keep deduplication state bounded by the known-device set. Notifications never contain authoritative thermostat values and never confirm an accepted command. The reconnect GET handles missed events and clock/timestamp anomalies independently of deduplication.

Use a separate coalesced invalidation request path into the coordinator's shared read lock and account cooldown. Do not repeatedly call the existing write-reconciliation rescheduler from push: it resets its initial delay and could starve reads under bursts. A burst must retain one due read and a notification arriving during a read must cause at most one necessary follow-up. Neither push nor reconnect extends the original thirty-second confirmation deadline or resends a thermostat command.

Retain five-minute polling regardless of connection status. Bound connection/handshake/Subscribe attempts; use cancellable exponential backoff with jitter (initial 5 seconds, cap 300 seconds), respect server cooldown/Retry-After, and avoid concurrent account connections. Handle SignalR application pings separately from WebSocket control pings; document finite server-silence detection (proposed 45 seconds, allowing margin over reported 15-second pings). SDK lifetime is not one thirty-second REST operation: only each connection attempt has a finite budget. Unload cancels the socket, listener, backoff, heartbeat, subscription wait and deferred callbacks.

No raw frames, identifiers, timestamps, access tokens or vendor errors go into logs/diagnostics. New runtime modules require explicit package allowlist and provenance changes. Keep the current iot_class until actual implemented behavior and HA validation justify updating it. Disable push to roll back; all climate and polling behavior remains available.

Send SignalR application Ping on an otherwise idle connection at a bounded interval (proposed 15 seconds), independently of WebSocket control pings, and cancel that task on unload. Pings never schedule REST reads or extend command confirmation deadlines.

### C. Later energy model proof, not HA statistics

Vendor contracts are now known: day queries cover UTC midnight to midnight with 24 hourly buckets, newest first; values are floating-point estimated Wh, derived from heating time and current configured load. Conductor and Signature share the v1 endpoints. Historical values may change after load edits, not just while an hour is active.

Choose hourly UTC intervals as one storage granularity. Identify a bucket by device and UTC period start; replace revised values, allow decreases, and sum distinct buckets only. Do not add overlapping Day/Week/Month results or mark period estimates total_increasing. Convert Wh to kWh explicitly if a later display needs it. Refresh recent periods but disclose that a bounded window cannot repair arbitrarily old load-driven revisions; no automatic historical import is proposed.

A returned zero cannot distinguish no heating, unconfigured load or offline reporting. Preserve raw estimated zero with unknown quality; do not call it verified no-consumption or fabricate a way to distinguish those cases. Missing/invalid consumption remains unavailable. No cost, floor-load writes, measured power or Energy dashboard statistics in the initial proof. Later optional sensors/cache need separate approval and preserve existing device links.

### D. Later room-relative controls, not setpoint increments

Relative means last cloud-reported measured room temperature plus a signed delta in hundredths Celsius. It does not add to the target. Represent that contract explicitly in SDK types/names and docs; absolute calls stay unchanged. Temperature differences convert 1.8°F to 1°C without a 32-degree offset.

The endpoint selects mode. Manual removes expiry; Hold without holdUntil does not retain an existing timed expiry; Hold with holdUntil uses exactly the sent expiry. Resend the prior explicit expiry to retain it. No Relative support is established for the separate v1 Permanent Hold path. Do not silently map Schedule, Standby or Permanent Hold into another mode.

If a later user feature means increment-the-target, that is a separate read/absolute-write operation with race semantics, not temperatureType=Relative. It is not part of this proof. Do not invent optimistic absolute results from cached room readings. Preserve one definite-401 retry but never replay a relative operation after uncertain acceptance. Remaining resulting-target clamp/validation behavior at device limits is not specified by the reply and needs synthetic policy plus separately approved evidence before exposing a relative HA action.

## Risks / Trade-offs

- Local expiry checks versus server time/transit → validate at submission, retain exact expiry, surface 400; no guaranteed arrival margin.
- Small in-house protocol subset → bound and exhaustively exercise the documented framing; polling remains independent.
- Push storms/read starvation → separate due-read coalescing, bounded deduplication, shared cooldown, no deadline resets.
- Optional hub authentication failure → REST remains authoritative for working account availability; no provider replacement.
- Revised energy history → replace buckets, no cumulative/statistics claim or silent historical finality.
- Room-relative confusion → explicit naming, no setpoint-increment alias or guessed result.

## Migration Plan

No domain, config-entry migration, credentials, entities or registry changes. Initial push is opt-in/default-off and owned by the existing runtime account. Keep accepted intent, cooldown, cleanup and handoff safeguards. Core is excluded. Implement and review A before B; C and D require separate approval. A fake local hub proves client behavior, not Chemelex reachability. Any future live connection, write, SDK release, pin change, beta deployment, commit or push needs explicit authorization.
