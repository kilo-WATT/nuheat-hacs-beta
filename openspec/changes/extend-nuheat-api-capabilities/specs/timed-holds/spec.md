# Timed holds delta

## MODIFIED Requirements

### Requirement: Temperature and time validation
The action SHALL use HA's configured temperature unit and validate finiteness and the same inclusive 5–35°C range as ordinary temperature controls. Offset-free times SHALL use HA's timezone. Past, nonexistent, and ambiguous local times SHALL be rejected before a write; an explicit valid UTC offset SHALL disambiguate a repeated hour. Explicit expiry SHALL be canonical whole-second UTC with the documented minimum lead time checked near submission; no v2 upper duration cap SHALL be imposed.

#### Scenario: Fahrenheit target
- **WHEN** HA uses Fahrenheit and a valid Fahrenheit target is supplied
- **THEN** the API receives the equivalent Celsius value.

#### Scenario: Repeated daylight-saving hour
- **WHEN** an offset-free expiry falls in a repeated local hour
- **THEN** no write occurs and the user is asked for an unambiguous expiry.

#### Scenario: Lower-bound timed hold
- **WHEN** a timed-hold action requests 5°C or 41°F with a valid future expiry
- **THEN** range validation accepts it and the requested expiry is retained.

#### Scenario: Invalid numeric target
- **WHEN** the target is nonfinite or outside the supported range
- **THEN** validation rejects it without a write.

#### Scenario: More than an app-length hold
- **WHEN** a valid explicit v2 expiry is more than 23 or 24 hours ahead
- **THEN** the client does not reject or clip it solely because of duration.

#### Scenario: Expiry becomes too close during waits
- **WHEN** the canonical expiry has less than two seconds of local lead time after lock or authorization waits
- **THEN** the write is rejected without advancing expiry; any server-receipt-time 400 is surfaced without automatic retry.

## ADDED Requirements

### Requirement: Canonical expiry confirmation
The wire expiry and accepted pending expiry SHALL use the same UTC value with fractional seconds dropped. Readback SHALL confirm that exact canonical expiry without a broad time tolerance that could confirm another hold. The original pending deadline SHALL remain bounded.

#### Scenario: Fractional expiry returned at second precision
- **WHEN** a request specifies a fractional second and the server returns the same expiry with fractional seconds dropped
- **THEN** matching target, mode and canonical expiry can confirm the hold without remaining assumed solely for precision differences.

### Requirement: Explicit expiry on every timed retarget
A temperature change retaining an existing timed Hold SHALL explicitly resend its canonical expiry, including accepted pending expiry. No request SHALL assume the server retains expiry when it is omitted. Preset changes SHALL retain their deliberate existing control meanings and never acquire an arbitrary new expiry.

#### Scenario: Rapid retarget before readback
- **WHEN** a newly accepted explicit hold is retargeted before its expiry appears in readback
- **THEN** the new target request carries the accepted canonical expiry and does not become Manual or next-schedule Hold.

#### Scenario: Ordinary Temporary Hold preset
- **WHEN** a user deliberately selects the ordinary Temporary Hold preset
- **THEN** the existing next-schedule behavior applies rather than implicitly carrying a superseded timed expiry.

### Requirement: Device-rewritten expiry remains unconfirmed
A successful PUT SHALL NOT prove device expiry retention. A different authoritative expiry SHALL remain unconfirmed until the bounded pending deadline; it SHALL NOT trigger automatic write replay. After timeout, a deliberate retarget SHALL retain the authoritative expiry. Single-device observations SHALL NOT impose a universal v2 cap or silent rounding.

#### Scenario: Seconds removed after initial API echo
- **WHEN** an initial matching expiry is later reported with seconds removed before confirmation
- **THEN** that changed value does not confirm the original expiry, and polling does not replay the write.

#### Scenario: Long hold shortened downstream
- **WHEN** a valid long-hold request is accepted but a shorter expiry is subsequently reported
- **THEN** the client does not silently clip subsequent requests or treat the shorter expiry as exact confirmation.
