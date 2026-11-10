# Isolated live Stage A validation â€” 2026-11-10

Outcome: stopped safely; acceptance observed, complete timed-hold confirmation
not established. This is not a Stage A pass or release-readiness claim.

The user approved at most six commands on the same linked thermostat within
Â±0.5Â°C of its starting target, including restoration. The isolated beta entity
used the local installed candidate SDK. Production HA was not accessed.

## Measured observations

- Confirmed a single online device in scheduled mode with no hold; retained its
  original target, raw mode and schedule/operating-mode fields privately in an
  ignored lab artifact, never in this report or Git.
- Submitted one 25-hour timed hold at the original target. The API call returned
  successfully in approximately 0.309 seconds and the entity's displayed target
  matched the request. This alone does not prove the cloud applied the hold.
- The expected authoritative target, timed-hold state and exact expiry tuple was
  not observed within the 32-second confirmation window. The harness did not
  retain per-field readback comparisons, so the mismatch cannot yet be assigned
  to expiry, mode, target, stale data or test instrumentation.
- Aborted before the planned temperature adjustment. Expiry retention across a
  retarget therefore remains unverified live.
- Submitted one restoration command. Within approximately 4.193 seconds, readback
  matched the original scheduled target, null expiry, mode, operating mode and
  schedule mode. Restoration was verified before shutting down the lab.
- Total: two thermostat commands, zero target deviation requested, no retries of
  the unconfirmed hold, no production access, commits, pushes or publication.
- Listener-free lab, coordinator, entity and HTTP session were stopped cleanly.

## Next step

Retain the synthetic regression evidence, but do not label Stage A hardware
validation complete. Add synthetic-verified, privacy-safe per-field readback
comparisons and request/read counters to the ignored harness before requesting
approval for another bounded attempt. An aggregate mismatch is insufficient to
claim a vendor duration cap or an integration defect. Do not weaken exact-expiry
confirmation or replay uncertain writes to make the test pass.

## Instrumentation follow-up (local only)

Added a pure allowlisted comparator with nine passing synthetic tests: exact
match; target mismatch; missing/invalid targets; mode mismatch; exact one-second
expiry mismatch; timezone-equivalent expiry; missing expiry; offline state; and
boolean-only output excluding private markers. Instrumented the ignored harness
with GET attempt/completion/failure counts, per-field booleans, coordinator success
and read-generation advancement. Confirmation requires a successful new read
since the check began; it cannot pass solely on matching cached data.

Inspected installed HA refresh scheduling: async_request_refresh delegates to a
debouncer whose async_call can return while a refresh remains queued. This is a
confirmed measurement pitfall, not a proven cause of the earlier timeout. The
32-second limit and exact expiry comparison remain unchanged. There is no
integration logic change. The repeat harness requires an explicit approval flag,
limits this second attempt to four HTTP writes (keeping the combined budget at
six), and preserves the first attempt's result. No further live calls occurred
while preparing these measurements. Another hardware attempt awaits approval.

## Separately approved bounded retest

The improved harness used two additional commands: create the hold and restore
schedule. Both attempts together used four commands with no requested target
deviation. The planned temperature retarget was not attempted.

The initial observation matched the requested target, timed-hold mode and exact
expiry. Later successful authoritative reads advanced the coordinator read
generation and still matched target and timed-hold mode, but their non-null
expiry differed from the request. No HTTP read failures were reported. The
confirmation failure is now isolated to expiry mismatch; debouncing alone does
not explain it. Expiry deltas were not retained, so rounding, device rewriting,
duration clipping and vendor defects remain unproven hypotheses.

The test stopped at its confirmation deadline and restored Auto. A fresh read
matched the original target, null expiry, raw mode, operating mode and schedule
mode. The isolated lab stopped cleanly. Production, Core and release state were
untouched. Task 6.5 remains unchecked because retarget expiry retention is still
unverified. This is not a Stage A pass.

Before further hardware testing, add signed expiry differences in seconds and
precision booleans without absolute timestamps, and distinguish list versus
single-device readback. Obtain fresh approval for additional commands. Do not
assume a 24-hour cap, widen expiry tolerance or replay an unconfirmed write.

## Expiry-delta and endpoint investigation (renewed approval)

A further bounded batch used four commands total: 25-hour hold and restoration,
then 22-hour hold and restoration. Both held the original target, with no target
deviation requested. Both restorations matched the original scheduled target,
null expiry, mode, operating mode and schedule mode after fresh successful reads.
All isolated resources stopped cleanly. No production access or publication.

For the 25-hour request, both single-device and account-list GETs consistently
reported an expiry 7,194 seconds earlier than requested. An additional standalone
read-only GET measured 82,772.548 seconds remaining (approximately 23 hours minus
test elapsed time). For the 22-hour request with explicit nonzero seconds, both
GET paths initially echoed the exact expiry, then reported it 37 seconds earlier
at whole-minute precision. All other confirmation fields still matched, with no
HTTP read errors. This rules out a general fixed timezone offset and identifies
both long-duration shortening and delayed minute truncation on the tested setup.
It does not establish whether cloud processing or firmware performs the changes,
or a universal cross-device duration limit. No live temperature retarget occurred.

Fourteen pure instrumentation tests passed. Added synthetic integration regressions
for minute-truncated and shortened expiry: no false confirmation, bounded pending
cleanup, no replay, preserved identity, and deliberate retarget retaining actual
reported expiry; also exact minute-aligned expiry confirmation and retarget.
Existing runtime behavior already handles the mismatch safely, so no runtime
workaround, global duration cap or broadened time tolerance was implemented.

Next hardware validation should use a whole-minute expiry comfortably below the
observed long-duration boundary, then change the target and verify exact expiry
retention. That requires a separately approved command budget; this batch is
finished. Stage A remains incompletely live-validated. C/D remain deferred.

Verification after investigation: 90 targeted hold/action/mode-reconciliation and
packaging tests passed; Ruff lint and formatting passed; all 12 OpenSpec items
passed strict validation. Local review packaging passed with ZIP SHA256
231609327bef534019dd9db1bcefc6641aada7736f08a173bac30d2391606fb2.
Privacy audit: 205 working-tree files plus one archive scanned, 13 private baseline
values checked, zero findings. The hardware harness and raw baseline remain
ignored. Task 6.6 is complete for investigation and regressions; task 6.5 remains
open for a successfully confirmed live retarget. No runtime code changed in this
follow-up. Historical artifact hashes above describe earlier packages.

## Whole-minute hold and retarget (final approved test)

A roughly 22-hour hold with an explicit whole-minute expiry confirmed on fresh
readback. The isolated HA entity changed the target by 0.5°C. The single-device
and account-list responses both confirmed the new target, timed-hold mode and
the exact original expiry (zero seconds difference). A fresh coordinator read
also confirmed all three fields.

The third and final command resumed the schedule. A fresh read matched the
baseline target, mode, null expiry, operating mode and schedule mode. The lab
shut down cleanly. Production HA was not accessed.

Task 6.5 passed for this supported input on the tested thermostat. The earlier
observations of seconds truncation and long-hold shortening still apply.
