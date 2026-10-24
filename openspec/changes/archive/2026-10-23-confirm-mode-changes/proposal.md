# Proposal

## Why

The current release schedules one delayed read for mode-only writes. If the API
is still stale then, HA can retain old state until the five-minute poll. Off also
uses an optimistic flag that is only cleared by particular paths. These observed
limits deserve bounded confirmation rather than another control-specific fix.

## What Changes

- Propose bounded read confirmation for every mode/preset/Off/On command.
- Clear Standby assumptions on confirmation or deadline; do not invent success.
- Keep write payloads, two-second initial read, eight-second read retry, thirty-second
  deadline, identity, OAuth, and migration contracts unchanged.
- Exercise every control and rapid superseding commands before mirroring the
  behavior into Core through its separate contribution workflow.
- No runtime code, hardware commands, production changes, or releases are part of
  this proposal's creation. Implementation requires a subsequent apply request.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `command-reconciliation`: extend mode-only read confirmation to a bounded window.
- `thermostat-controls`: bound optimistic Standby display assumptions.

## Impact

Beta coordinator/climate behavior, regression tests, and user documentation;
corresponding Core behavior and tests would require a separately scoped port.
The client API and dependency pins need no proposed change. Registry identity,
OAuth providers, and handoff allowlisting remain outside this change.
