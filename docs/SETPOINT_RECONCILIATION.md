# Setpoint reconciliation in v0.1.0b5

This fix is included in v0.1.0b5 and is not part of the published v0.1.0b4 tag.
Publication was approved by the maintainer. OAuth behavior, migration
format and Core handoff eligibility are unchanged. The matching upstream Core
patch remains separate and unpushed.

After a setpoint command returns successfully, the entity displays the requested
target and reports assumed state. Authoritative thermostat data is kept separate.
The existing immediate refresh remains; stale responses cannot replace the pending
target. A coalesced account refresh runs two seconds after the latest command,
bypassing the normal refresh-request debounce. Unconfirmed targets are checked
again every eight seconds, up to an independent thirty-second deadline per device.
Confirmation cancels the pending target. Expiry restores the latest cloud value
and logs a warning. Cloud failures retain normal availability and reauthentication
handling; authentication failures stop the extra retries.

Setpoint writes are serialized per entity. In-flight reads cannot confirm a newer
request that started after that read. Successful mode/preset commands supersede
the pending setpoint. Unload cancels delayed refreshes and deadlines. A failed
write method schedules one delayed read without displaying success or repeating
the write: the library can raise on its post-PUT GET after the PUT succeeded.

The Core and beta implementation files are aligned, allowing only the existing
stable/Core climate temperature-property naming differences. The original pinned
Core fixtures, provenance hashes, and `core-handoff.json` are preserved. Separate
`setpoint_candidate` fixtures and provenance hashes let packaging verify this
reviewable local deviation without broadening automatic Core handoff eligibility.

Validation uses synthetic credentials, thermostat models, and controlled clocks.
The new suite covers stale readback, Celsius/Fahrenheit conversion, confirmation,
expiry, failed writes, concurrent/rapid commands, in-flight reads, refresh errors,
independent device deadlines, a blocked read at expiry, command supersession,
and timer cleanup.

An approved isolated Signature hardware run passed on 2026-10-20. Observed HA
state changes took 0.239–0.313 seconds from service start. Delayed account reads
started 2.0016 and 2.0008 seconds after service completion and confirmed targets
after 2.1091 and 2.0901 seconds. Naturally stale post-write responses did not
revert the requested display; the rapid sequence used one delayed refresh after
its final successful command. Original target, scheduled mode and no-hold state
were confirmed restored. Six bounded setpoint writes and one schedule-restoration
write were sent; production HA was not accessed or changed. No additional reads
occurred during the forty-second unload observation.

These results measure HA state and cloud readback, not visual frontend or physical
display latency. Live failure/timeout behavior and a separate live Core-framework
run were not exercised. Hardware beyond Signature remains unverified for this
specific fix; synthetic tests cover the remaining failure and timing scenarios.

## Bounded mode confirmation in v0.1.0b8 (pre-release)

All accepted presets, Heat/Manual, Auto, Off and On now share the bounded read
lifecycle: an initial account read about two seconds after completion, then reads
about every eight seconds until confirmation or a thirty-second per-device
deadline. Matching online readback confirms the expected mode; ambiguous Manual /
Permanent Hold details cannot confirm either. No scheduled target is invented.
Mode confirmation uses a distinct generation object for each accepted write, so
an earlier in-flight read cannot confirm a newer intent.

Pending modes report assumed state. Off retains its immediate optimistic display
only until Standby confirms or the deadline expires. On expiry HA uses reported
cloud state and logs a mode-not-confirmed warning. A later external mode change
can update the display normally. API/authentication errors retain their normal
availability and reauthentication behavior; authentication failure stops extra
reads. Failed write methods still raise, receive a delayed read, and never create
new optimistic success or automatic write retries.

All control writes now use the existing per-entity lock. A target adjustment
following an accepted preset preserves that intent while readback remains stale,
including when leaving Standby. Mode-only commands cancel an earlier pending
target/expiry; explicit timed-hold expiry stays intact during target changes.
Selecting ordinary Temporary hold must not restore a previous timed expiry.
Unload cancels account callbacks and both kinds of independent deadlines.

v0.1.0b8 is an opt-in pre-release; it is not automatically installed on production. The Core
port and fresh live hardware validation remain pending; earlier hardware evidence
above does not validate this new mode-confirmation lifecycle. OAuth, migration,
identity, dependency pins, and automatic Core handoff allowlisting are unchanged.
