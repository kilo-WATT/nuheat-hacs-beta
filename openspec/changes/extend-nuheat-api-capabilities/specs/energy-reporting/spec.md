# Energy reporting delta

## Purpose

Expose optional thermostat relay runtime and vendor-estimated consumption with
accurate period semantics and without weakening existing climate availability.

## ADDED Requirements

### Requirement: Optional existing-device reporting
Energy reporting SHALL be disabled by default and SHALL attach to existing thermostat devices without changing climate entity IDs or config-entry associations. Enabling reporting SHALL NOT write vendor load, price or thermostat settings. Disabled reporting SHALL issue no energy-log requests.

#### Scenario: User upgrades without enabling sensors
- **WHEN** the integration gains energy-reporting support
- **THEN** existing thermostats continue working with their prior IDs and no extra energy polling.

### Requirement: Explicit units and data provenance
Relay-on duration SHALL be labeled runtime. Consumption SHALL be labeled vendor-estimated kWh, never measured power. Unknown or unconfigured estimates SHALL NOT be converted to zero consumption. Cost and HA energy-statistics eligibility SHALL remain unavailable until their required units, period and reset/correction contracts are verified.

#### Scenario: Missing estimate
- **WHEN** runtime exists but consumption is absent, invalid or an unverified zero sentinel
- **THEN** runtime remains usable and consumption reports unavailable instead of invented zero usage.

#### Scenario: Genuine zero consumption
- **WHEN** the validated vendor contract distinguishes a genuine zero from missing data
- **THEN** a valid zero is retained without extrapolating a power or cost value.

### Requirement: Stable periods and optional failure isolation
Energy reads SHALL use verified timezone, DST, bucket, reset and correction semantics and an independently bounded cache schedule sharing the account cooldown. They SHALL NOT block climate commands, replace climate data or double-count overlapping day/week/month periods. Optional permission or transport failures SHALL affect reporting rather than invalidate working climate data.

#### Scenario: Corrected or repeated bucket
- **WHEN** the API repeats or corrects a previously fetched period
- **THEN** the same bucket is updated once and does not accumulate duplicate consumption.

#### Scenario: Energy permission denied
- **WHEN** an optional energy endpoint returns 403 while thermostat reads work
- **THEN** energy becomes unavailable without relinking the account or losing thermostat entities.

#### Scenario: Quota shared with climate
- **WHEN** an energy read receives 429
- **THEN** the shared cooldown suppresses subsequent account traffic and climate data is retained under its existing availability rules.

#### Scenario: Energy request stalls or unloads
- **WHEN** a reporting read times out or its entry unloads
- **THEN** the request and reporting callbacks finish or cancel within their budgets and no thermostat write occurs.
