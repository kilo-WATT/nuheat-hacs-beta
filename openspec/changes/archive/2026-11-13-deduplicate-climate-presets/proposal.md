# Proposal

## Why

Issue #13 shows duplicate choices because the published beta advertises both readable labels and snake_case aliases as preset values. HA's entity translation guidance requires snake_case keys for translated attribute states. The approved correction uses stable identifiers and translated UI labels.

## What Changes

- Advertise and accept exactly run_schedule, temporary_hold and permanent_hold.
- Display Run schedule, Temporary hold and Permanent hold through entity translations.
- **BREAKING** Return snake_case preset state and retire title-case action inputs introduced in b11/b12. Document replacements for action calls, state comparisons and templates.
- Verify HA translation lookup as well as actual preset service validation.

## Capabilities

### New Capabilities

### Modified Capabilities

- `thermostat-controls`: Three canonical snake_case preset values with translated labels and upgrade guidance for title-case consumers.

## Impact

Beta const.py, behavior parsing, strings and English translations, preset service tests, documentation and candidate provenance. The temperature migration remains a separate composable change. SDK, identity, OAuth, migration and handoff behavior retain their current contracts.

## Evidence and corrected decision

- https://github.com/kilo-WATT/nuheat-hacs-beta/issues/13
- https://contributors.home-assistant.io/core/integrations/translations/
- The user approved the HA naming convention on 2026-11-13, superseding the earlier title-case-only choice.
- Existing b11/b12 reports remain historical evidence. The initial local implementation and test expectations reflected the earlier decision and require revalidation.
