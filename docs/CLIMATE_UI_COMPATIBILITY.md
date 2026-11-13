# Upcoming climate compatibility update

This document describes the v0.1.0b13 release candidate.

## Three translated preset choices

The candidate uses run_schedule, temporary_hold and permanent_hold as its raw
preset values. Home Assistant displays their translated labels as Run schedule,
Temporary hold and Permanent hold. Older snake_case action calls keep working.

If you adopted title-case values in b11/b12, update both action inputs and preset
state comparisons. Check scripts and templates that generate those values too.

| b11/b12 title-case value | Canonical action and state value |
| --- | --- |
| Run Schedule | run_schedule |
| Temporary Hold | temporary_hold |
| Permanent Hold | permanent_hold |

```yaml
action: climate.set_preset_mode
target:
  entity_id: climate.your_existing_thermostat
data:
  preset_mode: permanent_hold
```

For a state comparison, use
`state_attr('climate.your_existing_thermostat', 'preset_mode') == 'permanent_hold'`.
Keep your existing entity reference. The integration rejects retired title-case
inputs before any thermostat write. Published b11/b12 behavior is documented as
historical context in the hold-controls guide.

## Temperature compatibility

The candidate supplies Celsius readings and targets through HA's native climate
temperature interface. HA handles display and ordinary climate action conversion.
The NuHeat Set temporary hold action still accepts the configured HA temperature
unit, converting that custom action input to Celsius once. For example, a request
for 77 Fahrenheit sends 25 Celsius. The expiry is retained explicitly.

The older interface is used only where required by the minimum supported HA
version. Displayed limits remain 5–35 Celsius or 41–95 Fahrenheit. Existing
setpoint, hold-confirmation and failure handling safeguards continue to apply.

## Verification status

The local candidate passed 485 tests with one existing skip on HA 2026.10.2,
and 161 affected-control tests against verified official native climate API
source. Tests cover Celsius/Fahrenheit display and commands, exact hold expiry,
three preset choices, rejected legacy inputs and deprecation log output.

The newer API source was loaded into an isolated test process. A complete
HA 2026.11.2 installation and UI were not tested because that release package
lookup returned 404 here. Full evidence and exact source hashes are recorded
in the two OpenSpec changes. Publication remains disabled pending review.

HA translation lookup verifies one readable label for each raw identifier.
