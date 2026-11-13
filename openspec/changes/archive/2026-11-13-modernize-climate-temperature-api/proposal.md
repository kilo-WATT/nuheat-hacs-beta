# Proposal

## Why

Issue #11 reports deprecated climate temperature properties on Home Assistant 2026.11. The beta currently exposes those properties and performs its own display-unit conversions, so the migration must preserve service conversion and timed-hold behavior.

## What Changes

- Use the native climate temperature API where the framework supports it, with an isolated compatibility path for the advertised minimum HA version.
- Preserve Celsius/Fahrenheit display, command values, bounds, step sizes, pending targets, and explicit hold expiry.
- Add matching-framework tests that fail on deprecated integration access.

## Capabilities

### New Capabilities

### Modified Capabilities

- `thermostat-controls`: Require native temperature support on current HA and consistent display/service units across supported frameworks.

## Impact

Beta climate entity, temperature service tests, custom hold-action tests, and isolated framework test configuration. SDK 0.1.5 remains the dependency. Core PR, runtime credentials, registry identity, production HA, and live hardware are outside this change.

## Evidence

- https://github.com/kilo-WATT/nuheat-hacs-beta/issues/11
- https://github.com/home-assistant/developers.home-assistant/blob/master/blog/2026-10-08-climate-native-temperature.md
- Existing beta `climate.py` implements deprecated temperature properties and selects HA display units as its entity temperature unit.
- Installed minimum framework is HA 2026.10.2. An attempted PyPI lookup for 2026.11.2 returned HTTP 404. Matching-current-framework execution remains required before declaring the migration verified.
