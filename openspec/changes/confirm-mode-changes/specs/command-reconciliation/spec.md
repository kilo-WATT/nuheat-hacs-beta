# Mode confirmation delta

## MODIFIED Requirements

### Requirement: Mode-only confirmation boundary
A mode or preset write without a pending setpoint SHALL receive delayed read confirmation beginning about two seconds after completion and retrying about every eight seconds within a thirty-second deadline. The integration SHALL confirm only compatible current intent, never retry writes automatically, and expose unconfirmed outcomes without guessing a scheduled target.

#### Scenario: Mode read remains stale after two seconds
- **WHEN** a mode-only command's delayed read still contains old mode data
- **THEN** reads retry within the bounded window instead of waiting only for normal polling.

#### Scenario: New command supersedes old intent
- **WHEN** a user selects a newer control while an earlier read is in flight
- **THEN** that read cannot incorrectly confirm the newer command and reconciliation targets the current intent.

#### Scenario: Mode never confirms
- **WHEN** the deadline expires without compatible readback
- **THEN** pending confirmation ends, the unconfirmed outcome is surfaced, and normal polling continues without another write.
