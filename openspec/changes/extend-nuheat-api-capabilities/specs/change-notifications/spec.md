# Change notifications delta

## Purpose

Reduce the time before externally changed thermostat state reaches HA while
preserving safe polling and bounded confirmation when push delivery fails.

## ADDED Requirements

### Requirement: Verified optional push support
Push support SHALL be enabled only after its protocol, authorization, subscription and transport lifecycle have been verified. Unsupported or unavailable push SHALL leave the existing thermostat entries, OAuth providers and polling behavior usable. Notifications SHALL NOT send user-facing alerts.

#### Scenario: Unsupported hub
- **WHEN** the vendor rejects a notification connection or the protocol is not proven compatible
- **THEN** push stays disabled or falls back to polling without a reauthentication loop or thermostat write.

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

### Requirement: Bounded fallback and cleanup
Push connections SHALL use bounded connection attempts and backoff, refresh authorization through the existing provider, retain normal polling and command-confirmation deadlines, and cancel subscriptions, reconnect work and pending callbacks on unload. Credentials and token-bearing connection URLs SHALL NOT appear in logs or diagnostics.

#### Scenario: Disconnection with a pending command
- **WHEN** push disconnects while a command awaits confirmation
- **THEN** ordinary delayed reads and the original confirmation deadline continue without repeating the write or extending assumed success.

#### Scenario: Unload during reconnect
- **WHEN** the entry unloads during subscription or backoff
- **THEN** the connection and tasks close and no additional reads, reconnects or commands occur.
