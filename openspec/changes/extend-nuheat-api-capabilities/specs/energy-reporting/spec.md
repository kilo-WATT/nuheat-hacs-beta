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
Consumption SHALL be parsed as floating-point vendor-estimated Wh, never measured power; any kWh display SHALL convert explicitly. A returned zero SHALL retain unknown quality because no heating, missing load and offline reporting are indistinguishable. Missing/invalid estimates SHALL remain unavailable. Cost and HA statistics import SHALL be excluded from the initial model proof.

#### Scenario: Missing estimate
- **WHEN** runtime exists but consumption is absent or invalid
- **THEN** runtime remains usable and consumption reports unavailable instead of invented zero usage.

#### Scenario: Ambiguous zero consumption
- **WHEN** the vendor returns zero estimated Wh
- **THEN** the raw estimate can be retained with unknown quality without claiming verified no-heating, configured load or complete reporting.

### Requirement: UTC hourly identity and revision
The model proof SHALL use hourly UTC buckets as its single accounting granularity. Day queries SHALL represent 24 buckets labelled 0–23, regardless of DST, and accept newest-first input. Buckets SHALL be keyed by UTC period and device, replaced on revision, and never accumulated across overlapping Day/Week/Month responses. Historical estimates SHALL NOT be treated as immutable or total_increasing.

#### Scenario: DST change day
- **WHEN** a day response spans a local daylight-saving clock change
- **THEN** it still represents 24 UTC buckets, with local-time conversion confined to presentation.

#### Scenario: Floor load changes later
- **WHEN** a previously stored bucket is fetched again with a lower or higher estimated value
- **THEN** its prior estimate is replaced without double counting; a bounded recent refresh window is not represented as correcting all historical data.

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
