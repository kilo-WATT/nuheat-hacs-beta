# Permanent Hold - v0.1.0b7 prerelease

Opt-in HACS prerelease using `chemelex-nuheat==0.1.2`. Enable Show beta versions
and explicitly select v0.1.0b7. Keep your existing NuHeat entries.

## Home Assistant controls

* Off / Standby: existing frost-protected 5 C / 41 F behavior, not hard power off.
* Run schedule: follow the thermostat schedule.
* Temporary hold: hold until the next scheduled event. Existing explicit hold
  expiration is preserved when changing the temperature of a timed hold.
* Permanent hold: hold the selected target indefinitely until changed/canceled.

The three schedule/hold options are presets. Physical Manual remains the separate
Heat HVAC mode. Permanent Hold is an Auto-family state, not physical Manual.
Physical Manual and Standby are not labeled as Permanent Hold.

## API implementation and evidence

An approved isolated comparison on 2026-10-22 sent five thermostat commands,
kept the same requested temperature, and verified restoration of the original
scheduled mode, target, and null hold. Production HA was not accessed.

V2 returned mode 3 with the same target and null expiration for both commanded
Manual and Permanent Hold. V1 distinguished operatingMode 2 (Manual) from 1
(Auto with scheduleMode 3). Reads after 2 and 10 seconds agreed. The documented
v1 Permanent Hold command succeeded from both Manual and scheduled Auto.
No further thermostat commands were sent for this implementation.

The client optionally supplements v2 mode-3 reads with v1 schedule details. Other
v2 states use the existing path. Details are joined by serial, require matching
setpoint/mode/expiration, and never replace entity identifiers. Missing, invalid,
or conflicting details leave the v2 state unresolved; a 5 C target alone does
not prove Standby on this path. Implicit setpoint writes are rejected while
schedule details are unresolved, rather than converting a possible hold to Manual.
An explicit Heat/Manual command remains available. Optional transport
or schema failures retain available v2 data; authorization failures propagate.

Permanent Hold writes use PUT /api/v1/Thermostat with serialNumber, setPointTemp,
and scheduleMode 3. An explicit target is required to avoid unknown defaults.
No expiration, name, unrelated field, or temperatureType is sent. A temperature
change while Permanent Hold is active uses the same command, preserving the hold.
No command is automatically repeated after transport/server/readback failure.
The existing single authentication refresh/retry contract remains unchanged.

A delayed read follows a new Permanent Hold command, including an uncertain
post-write read failure. Success is not invented on a failed command. Existing
bounded optimistic setpoint reconciliation remains unchanged. Unload cancels
reconciliation timers. OAuth credentials/flow, migration, entity IDs, config entry
identity, registry associations, and the Core handoff allowlist are unchanged.

## Validation boundaries

The raw endpoint comparison above was live. Full client and HA tests use synthetic
identifiers, responses, and controlled time. They cover the preset menu, app-driven
Permanent Hold, request payloads, preserved setpoints, Manual/Standby handling,
conflicting metadata, failures, delayed reconciliation, timer cleanup, OAuth,
migration, registry identity, and handoff. Standby-to-Permanent Hold is covered
synthetically; the live comparison covered Manual and scheduled Auto transitions.
Other thermostat models and firmware need community verification.

The upstream Core PR and production HA are unchanged by this release.
The historical persistence scenario remains a separately run baseline check.
