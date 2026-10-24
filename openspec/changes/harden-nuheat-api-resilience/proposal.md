# Proposal

## Why

The b9 API review found that documented rate-limit delays do not reach the HA
retry scheduler, HTTP requests inherit a long session timeout, and optional v1
permission failures can turn successful v2 reads into account reauthentication.
These exceptional paths need explicit contracts without changing working controls.

## Observed behavior and evidence

- In-memory synthetic probes on SDK 0.1.2 and the beta coordinator showed a
  `Retry-After: 120` error receiving an eight-second retry. Optional v1 `429`
  falls back to v2 data without retaining a usable cooldown for later requests.
- SDK requests set no timeout. The reviewed HA session inherits aiohttp's
  300-second total timeout; command serialization can wait behind that request.
  The thirty-second confirmation deadline is separate and starts after command
  completion, so it does not bound a stalled submission/post-write read.
- A synthetic successful v2 list followed by optional v1 `403` raises
  `NuHeatAuthError`. The SDK currently tests this behavior intentionally;
  changing it requires permission-versus-expiry regression coverage.
- NuHeat's public guide documents `429`/`Retry-After`, `401` authorization and
  `403` insufficient scope. The v1/v2 Swagger documents were read without account
  access. These observations do not establish a new live user failure.

## What Changes

- Honor server cooldowns across one runtime account client's requests, including
  optional detail reads, normal polls and command-triggered reconciliation.
- Fail new user commands promptly during cooldown with a useful retry-later error;
  do not queue or replay thermostat writes automatically.
- Bound network requests and complete control operations, including post-write
  reads, and release per-entity serialization after timeout or cancellation.
- Distinguish permission denial from expired authorization. Retain usable v2 data
  when optional v1 details are forbidden; keep unresolved mode classification
  conservative. Required-endpoint permission failures remain visible errors.
- Preserve existing mode payloads, successful-path timing, units, explicit expiry,
  migration, entity identity, provider selection and handoff safeguards.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `command-reconciliation`: cooldown-aware read scheduling, nonqueued commands
  during throttling, and bounded transport/operation time distinct from optimism.
- `authentication`: permission-versus-expiry classification and safe optional
  v1-detail fallback without weakening genuine authorization failure handling.

## Impact

The client repository owns typed errors, cooldown state and HTTP timeout handling
in `src/chemelex_nuheat/client.py` with client regression tests. The beta owns
`coordinator.py`, `climate.py`, `__init__.py`, config-flow error mapping and their
tests/documentation. A separately authorized Core port must retain the same
behavior while adapting Core's framework APIs; do not copy beta credentials there.
Any SDK release and dependency pin update require validation and separate
publication authorization. Existing public SDK consumers retain compatible
exception bases; observable throttling and `403` handling intentionally improve.

This proposal does not modify runtime code, tests, production, Core, versions,
release assets, or the allowlist, and does not authorize commits or publication.
Hold-duration limits, relative-temperature controls, notifications, energy,
diagnostics features and official Cloud handoff remain separate work.

## Sources

Public documentation and source observations checked on 2026-10-24. Deployment
behavior beyond the synthetic probes remains unverified.

- https://api.nam.mynuheat.com/ (error handling, burst/rate limits).
- https://api.nam.mynuheat.com/swagger/v1/swagger.json
- https://api.nam.mynuheat.com/swagger/v2/swagger.json
- Reviewed beta: `299253707fae6cca63c6dddd71692baad7ba6f22`; released runtime b9
  at `60b38fe9a04d1b51bb30632c1d4a054b5dcd9488` and SDK 0.1.2.
