# Change notifications delta

## Purpose

Reduce the time before externally changed thermostat state reaches HA while
preserving safe polling and bounded confirmation when push delivery fails.

## ADDED Requirements

### Requirement: Verified optional push support
Push support SHALL be default-off and use the documented SignalR JSON v1 contract. Enabling it SHALL require isolated transport/lifecycle verification. Unsupported or unavailable push SHALL leave existing entries, OAuth providers and five-minute polling usable. Notifications SHALL NOT send user-facing alerts.

#### Scenario: Unsupported hub
- **WHEN** the vendor rejects a notification connection or the protocol is not proven compatible
- **THEN** push stays disabled or falls back to polling without a reauthentication loop or thermostat write.

### Requirement: Header authentication and connection protocol
The adapter SHALL use a trusted-origin direct WebSocket connection, header-only bearer authorization, record-separated JSON handshake, thermostat Subscribe invocation and matching completion. It SHALL obtain a valid token and resubscribe on reconnect. Tokens SHALL NOT enter query strings or raw transport logs.

#### Scenario: New connection after token expiry
- **WHEN** a disconnected adapter reconnects after the previous token expired
- **THEN** it obtains valid authorization, completes handshake and Subscribe, and requests one full authoritative account refresh.

#### Scenario: Definite connection rejection
- **WHEN** opening the connection returns HTTP 401
- **THEN** at most one forced-refresh retry occurs within the connection budget and failure leaves polling usable.

### Requirement: Notifications invalidate cached state
Account and thermostat notifications SHALL schedule a coalesced authoritative read through the existing cooldown-aware scheduler. Unknown, duplicate or out-of-order events SHALL NOT overwrite thermostat state or resend commands. Events SHALL NOT themselves confirm a pending target, expiry or mode.

#### Scenario: External app changes a thermostat
- **WHEN** a recognized thermostat notification arrives
- **THEN** an account refresh is requested without waiting for the next normal poll, subject to the shared cooldown.

#### Scenario: Push overlaps polling and command readback
- **WHEN** duplicate or out-of-order events arrive during a normal poll or delayed reconciliation
- **THEN** reads coalesce and only compatible API readback can confirm current command intent.

#### Scenario: Throttle during a notification burst
- **WHEN** many notifications arrive during Retry-After cooldown
- **THEN** no immediate API burst occurs and one coalesced refresh remains due after cooldown.

#### Scenario: Periodic repeat of last change
- **WHEN** a known device sends repeated events with the same change timestamp or an older timestamp
- **THEN** those events do not trigger additional reads, while a newer timestamp requests a coalesced refresh.

#### Scenario: Notification arrives during a read
- **WHEN** a newer change notification arrives while an account read is in progress
- **THEN** at most one necessary follow-up read remains due without postponing it indefinitely or resetting pending command deadlines.

### Requirement: Bounded fallback and cleanup
Push connections SHALL use bounded connection attempts and backoff, refresh authorization through the existing provider, retain normal polling and command-confirmation deadlines, and cancel subscriptions, reconnect work and pending callbacks on unload. Credentials and token-bearing connection URLs SHALL NOT appear in logs or diagnostics.

#### Scenario: Disconnection with a pending command
- **WHEN** push disconnects while a command awaits confirmation
- **THEN** ordinary delayed reads and the original confirmation deadline continue without repeating the write or extending assumed success.

#### Scenario: Unload during reconnect
- **WHEN** the entry unloads during subscription or backoff
- **THEN** the connection and tasks close and no additional reads, reconnects or commands occur.

#### Scenario: Connection stays open beyond token lifetime
- **WHEN** a working hub connection continues beyond the access token lifetime
- **THEN** it is not needlessly cycled solely for token age, and normal polling continues.

#### Scenario: Server silence or malformed framing
- **WHEN** hub traffic exceeds framing limits or the server is silent beyond the documented client timeout
- **THEN** the adapter closes safely and reconnects with bounded backoff while polling continues.
