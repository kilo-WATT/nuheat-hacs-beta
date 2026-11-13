# Design

## Context

See proposal.md for the correction. HA validates incoming preset values against the same list it advertises. The entity already has translation key thermostat. Its translations previously listed both title-case and snake_case state keys.

## Goals / Non-Goals

Present three readable choices using HA's translated-state convention. Preserve the existing thermostat command meanings and entity references. User-authored automations receive upgrade guidance for the approved value change.

## Decisions

### Canonical identifiers and translated labels

Set the three preset constants to run_schedule, temporary_hold and permanent_hold. Advertise only those three values and return them as reported preset state. Keep the direct mode lookup and standard HA service validation. Translation keys match the raw identifiers exactly, mapping them to Run schedule, Temporary hold and Permanent hold.

Remove title-case keys from strings.json and translations/en.json. Tests must exercise HA's translation loader and prove that each advertised raw value has exactly one readable label. The raw preset state remains a machine identifier regardless of display language.

### Compatibility and migration

Snake_case calls from older installations keep working. Users who adopted title-case action values or state comparisons in b11/b12 need the inverse mapping in the upgrade guide. Include automations, scripts, action-generating templates and preset state comparisons. The implementation does not rewrite user automation files.

### Release composition

Run combined preset and native-temperature suites. Record the revised source hashes as local candidate evidence and preserve published-release history.

## Risks / Trade-offs

- Title-case action inputs will fail validation. Provide exact replacements and zero-write rejection tests.
- A readable label can hide an incorrect raw state contract. Test stored state attributes, HA translation resolution and service inputs independently.

## Migration Plan

Replace Run Schedule with run_schedule, Temporary Hold with temporary_hold and Permanent Hold with permanent_hold in action data and state comparisons. Retain entity IDs. Distribute through a later approved tagged release.
