# Hold controls and automation compatibility - v0.1.0b11

Regular latest GitHub release using `chemelex-nuheat==0.1.3`. Beta visibility
is not required in HACS. Explicitly select v0.1.0b11 and keep your existing NuHeat
entries. The integration remains unofficial community beta software.

## Home Assistant controls

### Automation compatibility update

This section describes v0.1.0b11. Earlier v0.1.0b10
reports snake_case states and uses the previous 7°C lower limit.

The update accepts all six exact preset action values below. Preferred names
appear first in the preset list; compatibility aliases also appear, so the menu
contains duplicate choices for the same three operations.

| Preferred action and reported state | Accepted action alias |
| --- | --- |
| `Run Schedule` | `run_schedule` |
| `Temporary Hold` | `temporary_hold` |
| `Permanent Hold` | `permanent_hold` |

Existing snake_case **action calls** keep working. Reported `preset_mode` values
use the preferred title-case strings regardless of which action spelling was
used. Update snake_case **state triggers and template comparisons** after upgrading;
the integration does not rewrite automations. These are exact state values,
not the translated labels displayed by the card. Keep your existing entity ID.

For example, this existing action remains valid:

```yaml
action: climate.set_preset_mode
target:
  entity_id: climate.your_existing_thermostat
data:
  preset_mode: permanent_hold
```

Change a template comparison from
`state_attr('climate.your_existing_thermostat', 'preset_mode') == 'permanent_hold'`
to `state_attr('climate.your_existing_thermostat', 'preset_mode') == 'Permanent Hold'`.
Likewise, a state trigger should use:

```yaml
trigger: state
entity_id: climate.your_existing_thermostat
attribute: preset_mode
to: "Permanent Hold"
```

Ordinary temperature actions and **NuHeat: Set temporary hold** accept the same
inclusive **5–35°C / 41–95°F** range, using HA's configured unit. Setting 5°C
does not select Off: the intended heating mode and active hold expiry are
preserved. Explicit Off still selects the existing frost-protected Standby.
The minimum reflects Signature behavior and existing 5°C Standby support;
Swagger specifies no hardware limits, and other models are not newly verified.
Vendor rejections are reported without clipping the target or sending a fallback
mode command. The 35°C maximum is unchanged.

No entry deletion, new entities, or OAuth setup is needed for this update.
If rolling back, restore any state comparisons to the older snake_case values;
the older version's 7°C minimum also returns.

### Existing control meanings

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
No extra entities are created. The integration automatically provides this action;
users do not need to create it. No dashboard edits, helpers, or custom cards are
required. The action is also available to automations and scripts.

### Why is there no end-time picker on the thermostat card?

The standard thermostat card's **Temporary hold** preset means until the next
scheduled event. Its preset picker has no expiry field. Adding an end-time field
to that standard card would require a Home Assistant frontend change; the NuHeat
integration alone cannot add one. Use **NuHeat: Set temporary hold** when you want
a specific end time. Selecting the preset does not open the action form.

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
