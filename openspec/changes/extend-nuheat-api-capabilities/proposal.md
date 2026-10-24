# Proposal

## Why

The Swagger review identified useful API capabilities that the integration does
not expose and a documented temporary-hold limit it does not enforce. Resolve
the vendor-specific uncertainties before expanding working thermostat controls.

## Observed behavior and evidence

Checked public vendor guide and v1/v2 Swagger on 2026-10-24; no account access:

- The guide describes explicit hold expiry within the following 23 hours. The
  v2 `ModeHold.holdUntil` schema has no maximum-duration constraint. Current
  `async_set_temporary_hold` checks future/timezone validity but no upper bound.
- v2 `eTemperatureType` explicitly documents 0 = Absolute and 1 = Relative,
  adding to the current thermostat temperature. The SDK still rejects explicit
  `temperature_type`; the exact reference temperature, scaling and mode effects
  for safe relative controls remain unverified. Earlier wording that enum
  meanings are wholly undocumented is outdated.
- The guide documents SignalR thermostat/account change notifications. The
  beta currently polls every five minutes and reconciles its own commands; it
  has no notification client. Notifications here mean API push invalidations,
  not mobile alerts or messages to users.
- v1 energy logs expose relay-on minutes, estimated kWh and estimated charge
  per period. Timezone, DST, reset/correction rules, load configuration and the
  meaning of zero estimates need confirmation before HA energy statistics.
- There is no NuHeat diagnostics module, sensor platform, or relative action
  in the reviewed beta. This is an opportunity, not a proven outage.

## What Changes

- Establish a vendor-confirmation record and draft questions for v2 hold
  duration, boundary semantics and existing longer holds. Enforce a confirmed
  limit locally, with actionable errors and no silent expiry clipping.
- Add locally generated, allowlisted and redacted HA diagnostics with no cloud
  request, thermostat command, token or account/device identifiers.
- Investigate and, after its compatibility gate passes, add bounded SignalR
  push-triggered refresh with polling fallback and shared cooldown/coalescing.
- After energy-data semantics are verified, add optional, disabled-by-default
  runtime/estimated-energy sensors on existing devices. Do not claim measured
  power, cost or Energy dashboard compatibility without the required contract.
- After relative-command semantics are verified, add an explicit temperature
  adjustment action in HA's configured units, preserving mode and timed expiry.
  Do not repurpose standard set-temperature or change standard-card controls.
- Deliver in independent stages. Vendor-dependent stages remain blocked when
  their evidence is absent; diagnostics need not wait on those stages.

## Capabilities

### New Capabilities

- `diagnostics`: redacted local support snapshots without extra API traffic.
- `change-notifications`: account-scoped push invalidations with safe fallback.
- `energy-reporting`: optional period-based runtime and estimated-energy data.
- `relative-temperature-controls`: explicit relative adjustment with safe units,
  mode/expiry preservation and bounded confirmation.

### Modified Capabilities

- `timed-holds`: confirmed vendor-duration validation, boundaries and preservation
  of existing hold readback without clipping or modifying existing configuration.

## Impact

SDK: typed energy models, optional notification transport and verified relative
commands; preserve existing public calls. Beta: diagnostics, optional sensor and
notification lifecycle, climate action/time validation, strings/services,
packaging allowlist/provenance and regression tests. Core: alignment plan only;
any port is separately authorized and excludes beta registration values.

Build on `harden-nuheat-api-resilience`, whose SDK dependency is still unpublished.
Do not combine this feature plan with that dependency's publication or rewrite
its validated controls. Keep domain, entries, OAuth provider association,
migration, entity/device identities and Core handoff guard/allowlist unchanged.

This request authorizes planning only: no runtime changes, vendor messages,
credentials, production/hardware access, commits, pushes or publication.
No unsupported SignalR library or new runtime dependency is selected yet.

## Sources

- https://api.nam.mynuheat.com/ — Validation / Mode: Hold; Energy log; Change Notifications.
- https://api.nam.mynuheat.com/swagger/v1/swagger.json — EnergyUsageModel and EnergyUsageEntryModel.
- https://api.nam.mynuheat.com/swagger/v2/swagger.json — ModeHold, ModeManual and eTemperatureType.
- Beta source `d72bb6066158dd5b0eb006561afd02244a2b6145`; local SDK 0.1.3.dev0.
