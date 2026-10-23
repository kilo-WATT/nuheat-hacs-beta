# Design

## Context

See proposal.md for the observed gap. Setpoint confirmation already has independent
per-thermostat deadlines and coalesced account reads. Mode commands currently
schedule one read; Standby uses an entity-local optimistic flag. Neither a valid
OpenSpec file nor an accepted write proves that the vendor applied the mode.

## Goals / Non-Goals

Extend bounded confirmation to mode controls without changing their payloads or
replacing stable identity, OAuth, or migration code. Retain actual readback as the
mode source of truth. Do not add a standard-card expiry field, retries of writes,
new hardware commands, or a handoff allowlist change.

## Decisions

- Extend the coordinator's pending-intent lifecycle with the expected observable
  mode/preset and a generation marker for each thermostat. Use separate deadlines
  so an unrelated thermostat cannot extend another's pending state.
- Reuse coalesced two-second initial reads and eight-second retries with a
  thirty-second deadline. A single account read can reconcile multiple intents.
- Confirm only complete, compatible readback. Unknown supplementary details remain
  unresolved. An old in-flight response must not confirm a later intent.
- Replace or clear the entity-local Standby assumption through the bounded
  lifecycle. Do not optimistically invent a schedule target or Permanent Hold state.
- Surface uncertainty through assumed state while pending and a concise diagnostic
  at expiry; preserve any original action error. Retain reported cloud state.
- Preserve bounded target/expiry confirmation when mode-only and setpoint requests
  supersede each other. No token refresh or migration behavior is redesigned.
- Implement/test beta first. Prepare the equivalent Core port in a separately
  authorized Core scope, following its native temperature and service APIs.

## Risks / Trade-offs

- More reads during slow propagation: coalesce account reads and stop at the deadline.
- Reordered responses: generation-aware confirmation tests must cover in-flight reads.
- Manual/Permanent Hold ambiguity: incomplete details cannot confirm either by guess.
- Divergence between beta and Core: compare normalized behavior and run each framework's tests.

## Migration Plan

No entry or registry migration. Keep the existing dependency pin and public
control names. Validate with synthetic clocks, run packaging, document the new
mode confirmation window, and obtain the user's requested release/deployment scope
before any publication or production installation. Hardware validation remains a
separate optional authorized activity, not a prerequisite silently marked passed.
