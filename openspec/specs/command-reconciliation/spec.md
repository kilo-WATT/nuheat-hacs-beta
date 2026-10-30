# Command reconciliation

## Purpose
Specify how accepted thermostat writes become visible in HA without treating stale cloud responses as confirmation.

## Requirements

### Requirement: Immediate command submission
HA SHALL submit an authorized thermostat command when the interaction occurs rather than wait for normal polling, unless an active server cooldown prevents submission. A prevented command SHALL fail promptly without being queued. Confirmation reads SHALL NOT automatically repeat thermostat writes after uncertain failures.

#### Scenario: User changes a control
- **WHEN** a user selects a valid setpoint, preset, HVAC mode, Off, or On
- **THEN** the write is sent immediately unless throttled, and subsequent refresh work consists of reads.

#### Scenario: Command arrives during cooldown
- **WHEN** a user changes a control before the account client's cooldown expires
- **THEN** HA reports a retry-later error without sending or queuing the write and without inventing an accepted target or mode.

### Requirement: Delayed read after every write control
Setpoint changes, all three presets, Heat, Auto, Off, and On SHALL schedule a follow-up account read about two seconds after command completion. Rapid commands SHALL coalesce delayed reads. Normal five-minute polling SHALL continue. Active server cooldowns SHALL override nominal read intervals.

#### Scenario: Immediate response is stale
- **WHEN** the immediate post-command response still contains the old target or mode
- **THEN** a delayed read is scheduled for the affected write control instead of relying only on normal polling, subject to server cooldown.

#### Scenario: Several rapid commands
- **WHEN** multiple commands complete before the delayed callback runs
- **THEN** the callback is rescheduled and reads the latest account state without duplicating writes.

### Requirement: Bounded setpoint confirmation
A successful setpoint write SHALL display its accepted target while confirmation is pending. Reads SHALL begin after about two seconds and retry about every eight seconds when not throttled, with pending state expiring after thirty seconds. A requested explicit expiry SHALL also match before confirmation. Cooldown SHALL NOT extend optimistic state beyond its deadline.

#### Scenario: Target and expiry are stale
- **WHEN** an explicit timed hold has a matching target but its expiry has not been confirmed
- **THEN** pending state remains within its deadline and HA does not claim full confirmation.

#### Scenario: Confirmation never arrives
- **WHEN** thirty seconds pass without confirming readback, including while throttled
- **THEN** pending target and expiry state expires and write retries are not introduced.

### Requirement: Mode-only confirmation boundary
A mode or preset write without a pending setpoint SHALL receive delayed read confirmation beginning about two seconds after completion and retrying about every eight seconds within a thirty-second deadline. The integration SHALL confirm only compatible current intent, never retry writes automatically, and expose unconfirmed outcomes without guessing a scheduled target. Active server cooldowns SHALL override read intervals without extending the deadline.

#### Scenario: Mode read remains stale after two seconds
- **WHEN** a mode-only command's delayed read still contains old mode data
- **THEN** reads retry within the bounded window instead of waiting only for normal polling, subject to server cooldown.

#### Scenario: New command supersedes old intent
- **WHEN** a user selects a newer control while an earlier read is in flight
- **THEN** that read cannot incorrectly confirm the newer command and reconciliation targets the current intent.

#### Scenario: Mode never confirms
- **WHEN** the deadline expires without compatible readback
- **THEN** pending confirmation ends, the unconfirmed outcome is surfaced, and normal polling continues without another write.

### Requirement: Accepted target during follow-up mode writes
Temporary hold, Permanent hold and Heat commands SHALL carry an accepted pending target rather than stale cloud readback. Without a pending target they SHALL use the reported target. Values SHALL be converted correctly for Celsius and Fahrenheit. Existing failed-write and confirmation deadlines SHALL remain unchanged.

#### Scenario: Target then hold before cloud readback
- **WHEN** a target write succeeds and a hold or Heat command follows before the API reports it
- **THEN** the mode write carries the accepted target without resending the setpoint write.

#### Scenario: No pending target remains
- **WHEN** a mode command follows confirmation or expiry of pending target state
- **THEN** its temperature comes from current reported thermostat data.

### Requirement: Failure and lifecycle handling
A failed or uncertain write SHALL surface its error and schedule reconciliation without inventing success. Unloading the integration SHALL cancel its reconciliation and pending-confirmation timers.

#### Scenario: Readback fails after a write
- **WHEN** the API raises after a potentially accepted write
- **THEN** the error remains visible and later reconciliation does not resend the command.

#### Scenario: Integration unloads
- **WHEN** the integration unloads with delayed work pending
- **THEN** its timers are cancelled and they issue no further reads.

### Requirement: Account-client server cooldown
HTTP 429 SHALL establish a cooldown shared by the runtime account client's required and optional requests. A valid Retry-After value SHALL prevent new requests until its deadline; missing or invalid values SHALL use a documented bounded fallback. Polling and reconciliation SHALL avoid repeatedly calling a throttled endpoint. Already in-flight requests SHALL NOT be replayed.

#### Scenario: Cooldown exceeds confirmation window
- **WHEN** a read returns Retry-After 120 while command confirmation is pending
- **THEN** no new API request starts during those 120 seconds, and the thirty-second pending state still expires independently.

#### Scenario: Optional v1 read is throttled
- **WHEN** v2 data is usable but optional v1 details return HTTP 429
- **THEN** available v2 data is retained conservatively and the shared cooldown remains effective for later requests.

#### Scenario: Header is malformed or absent
- **WHEN** HTTP 429 supplies no usable Retry-After
- **THEN** a finite documented fallback avoids a tight retry loop without creating a thermostat write retry.

#### Scenario: Cooldown ends
- **WHEN** the cooldown expires and HA is still loaded
- **THEN** eligible reads resume in a coalesced manner, and previously rejected commands are not sent automatically.

### Requirement: Bounded request and control operations
Network requests and the complete submitted control operation SHALL have explicit finite deadlines, including authorization waits and post-write reads. Timeouts SHALL surface as communication failures without repeating uncertain writes. A failed or cancelled operation SHALL release control serialization and retain timer cleanup and generation safeguards.

#### Scenario: Submission hangs
- **WHEN** a thermostat write stalls before a response
- **THEN** the operation times out within its documented budget, releases serialization and does not publish optimistic success or repeat the write.

#### Scenario: Readback hangs after successful write
- **WHEN** a write succeeds but its follow-up read stalls
- **THEN** HA reports the uncertain operation, performs only bounded cooldown-aware reconciliation reads and never repeats the write automatically.

#### Scenario: Unload or caller cancellation
- **WHEN** HA unloads or cancels a pending control operation
- **THEN** cancellation propagates, locks and responses are released, and no orphan callback initiates later network activity.
