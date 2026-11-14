# Design

## Context

See proposal.md for issue #11 and the developer migration reference. The SDK represents temperatures in Celsius. The entity currently declares HA's configured unit and converts both readings and input values itself. Ordinary climate service handling and the custom NuHeat action have different conversion boundaries.

## Goals / Non-Goals

Preserve the advertised minimum HA version, all user-visible temperature values and thermostat intent while adopting current climate properties. The beta owns this compatibility adaptation. SDK releases, Core edits and hardware commands are outside the implementation scope.

## Decisions

### Native Celsius throughout the entity

Use Celsius for the entity's native unit, native current temperature, native target, min/max, and pending setpoints. Let the climate framework convert display temperatures and ordinary climate service input. Ordinary async_set_temperature receives Celsius. The custom nuheat.set_temporary_hold action continues to interpret its temperature in HA's configured unit and explicitly converts that input to Celsius once.

Preserve 0.5 Celsius and 1 Fahrenheit user-facing step behavior using the supported framework contract for native step size. Inspect actual framework state and service behavior when testing. The direct result of a deprecated property is insufficient evidence of the displayed temperature.

Renaming alone while leaving conversion paths ambiguous was rejected because two conversions can alter Fahrenheit commands.

### Narrow minimum-framework compatibility

Detect the framework native property capability once. Expose old temperature properties and old shorthand attributes only on the older framework that requires them. Current HA uses the native properties exclusively. Share Celsius state computation and control logic. Preserve the minimum HA 2026.10.2 requirement.

### Existing command semantics

Retain locks, operation deadlines, API calls, pending targets and exact hold expiry. Standby remains an explicit control. An ordinary 5 Celsius target keeps its intended mode. Registries, account ownership, providers and migration behavior retain their existing source and fixtures.

## Risks / Trade-offs

- Conversion errors can affect physical commands. Validate display and submitted Celsius values through ordinary service handlers and the custom hold action in both unit systems.
- Compatibility properties can cause current-HA startup warnings. Assert log output for entity setup, display and services on a real matching framework.
- Current-framework package retrieval returned 404 during planning. Obtain a supported official wheel or exact framework source for integration tests before claiming issue #11 is fixed. Synthetic shims can supplement that test, and cannot fulfill it.

## Migration Plan

Deploy through a later approved beta release with existing entries retained. Reverting that release uses the normal HACS tagged-version rollback. Record exact framework versions and dependency pins with verification.
