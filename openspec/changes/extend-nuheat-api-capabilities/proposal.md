# Proposal

## Why

The [Chemelex clarification](https://github.com/home-assistant/core/issues/175923#issuecomment-6737221965) resolves the main API contract questions. Update the earlier plan to those facts and prove the smallest useful additions with synthetic transports before implementation or live testing is approved.

## Observed behavior and evidence

Reviewed 2026-11-10: beta v0.1.0b11 pins SDK 0.1.3; the separate local SDK checkout is 0.1.4. Current source and fake-session probes are recorded in assessment.md. No vendor/account connection was opened.

- Five-minute polling, delayed reconciliation, expiry retention, one forced refresh on definite HTTP 401, and no replay after transport/readback uncertainty already exist.
- No hold upper cap exists, which matches v2. A real mismatch is fractional expiry: SDK sends microseconds, vendor drops them, and the coordinator compares exact datetimes. The local guard also lacks the vendor's two-second server-receipt lead-time rule.
- There is no SignalR adapter, energy-log API/model, or exposed relative action. Rejecting relative input is currently safe, but the SDK's explanation that the meanings are unverified is now stale.
- Diagnostics already shipped. Earlier statements that it was absent or SDK 0.1.3 was unpublished are historical, not current blockers.

## What Changes

- **Stage A, proposed first:** normalize explicit expiry once to whole-second UTC for payload and pending confirmation; retain no v2 upper cap; validate near submission and preserve the exact expiry during target changes. Add explicit PUT-401, GET-401, uncertain-write and deadline regressions without broadening retry behavior.
- **Stage B, proposed second:** build a default-off SignalR JSON/WebSocket proof using the existing aiohttp dependency. Header-only bearer authorization, bounded handshake/subscription/reconnect, timestamp deduplication, and REST invalidation flow must work against a local fake hub before any opt-in integration use. Retain five-minute polling and command deadlines.
- **Later stage C:** typed UTC hourly estimated-Wh energy models and replaceable historical buckets, initially with synthetic fixtures only. No HA energy sensors, statistics import or Energy dashboard claim in the initial proof.
- **Later stage D:** explicit measured-room-relative SDK controls and tests. Do not present them as setpoint increments or expose an HA action in the initial proof. Endpoint mode and explicit expiry must be deliberate.
- Retain completed diagnostics and earlier verification as historical evidence; new runtime validation remains unchecked.

## Capabilities

### New Capabilities

- `diagnostics`: already implemented local private snapshots; retained delta is unchanged.
- `change-notifications`: optional timestamp-deduplicated invalidations and polling fallback.
- `energy-reporting`: later UTC bucket models and optional reporting; outside initial proof approval.
- `relative-temperature-controls`: later explicit room-relative adjustment; outside initial proof approval.

### Modified Capabilities

- `timed-holds`: whole-second UTC expiry, minimum lead-time handling, no upper cap, and explicit retention. Existing temperature range and HA timezone interpretation remain.

## Impact

Initial implementation, if approved, affects only the SDK's expiry handling/notification adapter and related tests, plus beta climate/coordinator lifecycle, opt-in configuration, documentation and exact packaging/provenance as required. Detailed candidate files and findings are in assessment.md. Core source, OAuth registrations/providers, migration, entity identity and handoff eligibility are outside scope.

The user approved stages A and B for isolated implementation and synthetic tests. The local result and exact validation are recorded in stage-ab-validation.md. Stages C and D remain deferred. No production access, live API/hardware testing, deployment, messages, commits, pushes or publishing are authorized. Vendor statements are protocol evidence, not a completed live compatibility test.
