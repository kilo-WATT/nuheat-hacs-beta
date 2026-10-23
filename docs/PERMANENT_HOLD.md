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

A delayed read follows Permanent Hold and Run schedule/Auto commands, including an uncertain
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

## Explicit temporary hold expiry

Use **Developer tools > Actions > NuHeat: Set temporary hold**. Select your
existing climate entity, target temperature, and future end date/time. The target
uses HA's temperature unit. The date/time picker uses HA's configured timezone.
No extra entities are created. **Temporary hold** in the thermostat preset picker
still means until the next scheduled event; that picker has no expiry field.

For an automation/script, this action holds a Fahrenheit-configured thermostat
at 75.2 F for two hours (use 24 for Celsius). Replace the example entity ID:

```yaml
action: nuheat.set_temporary_hold
target:
  entity_id: climate.your_existing_thermostat
data:
  temperature: 75.2
  hold_until: "{{ (now() + timedelta(hours=2)).isoformat() }}"
```

The template is for automations/scripts. In Developer tools, use the date/time
picker or a literal future ISO date/time instead. For repeated daylight-saving
hours, include an explicit offset such as `-04:00` or `-05:00`. Ambiguous and
nonexistent local times, past times, and invalid temperatures fail before a write.

The existing v2 Hold command receives the explicit expiry in UTC. Successful
commands use the existing optimistic setpoint and bounded reconciliation. A quick
setpoint change preserves a newly requested expiry while readback is pending.
Readback must confirm both target and expiry; pending state expires after 30
seconds. Failed writes are surfaced without inventing success or repeating the
command. Run schedule, Manual/Heat, Off, or a different preset supersedes the
pending request. The regular five-minute poll continues after confirmation or
timeout. The new action is covered by isolated HA service dispatch and synthetic
API tests; no new live timed-hold hardware test is claimed.

All thermostat writes now schedule a read after two seconds: setpoint changes,
Run schedule, Temporary hold, Permanent hold, Heat/Manual, Off, and On. Multiple
writes coalesce into one delayed read. Setpoint read retries remain bounded;
mode-only writes get one delayed read without optimistic mode guesses.

The timed-hold action is currently beta-specific and has not been added to the
upstream Core PR. Existing Core handoff safeguards are unchanged. Final Core
handoff validation must check action compatibility; scripts using this new action
will need equivalent official support when transitioning to Core.
