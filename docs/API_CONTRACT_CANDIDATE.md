# Stage A/B local candidate â€” not a published release

This implements the approved isolated proof following
[Chemelex's clarification](https://github.com/home-assistant/core/issues/175923#issuecomment-6737221965).
A separately approved isolated read-only live Stage B check passed; see
[measured results](../openspec/changes/extend-nuheat-api-capabilities/live-stage-b-validation.md).
It has not been deployed to production or published.
The candidate pins `chemelex-nuheat==0.1.5` and the public beta remains v0.1.0b11.
The new SDK must be available on PyPI before the beta is distributed. The Core
PR independently pins `chemelex-nuheat==0.1.4`.

## Stage A: timed holds and retry certainty

Hold end times are normalized to UTC with fractions of a second removed, matching
the SDK wire format. Accepted pending state retains that same
canonical value; confirmation still requires the actual target, mode and expiry.
We do not accept a different end time using a broad comparison tolerance.

There is no imposed 23- or 24-hour v2 upper duration cap. The HA action still uses
HA's configured timezone for offset-free user input and rejects ambiguous/nonexistent
local times. The SDK requires a timezone-aware expiry. Existing supported target
temperatures, schedule, ordinary Temporary Hold, Permanent Hold and Standby meanings
are unchanged.

NuHeat requires at least two seconds of lead time at server receipt. The SDK checks
the canonical expiry after authorization waits, just before each submission, including
the one allowed retry after a definite HTTP 401. HA also checks after its control
lock. It never silently advances the end time. Network delay or server clock
differences can still cause a 400; that error is surfaced, not automatically retried.
Changing the target during a timed hold explicitly sends its end time again,
including when the previous accepted hold is still awaiting confirmation.

A definite rejected PUT 401 is safe to retry once after refreshing authorization.
A 401 on GET after an accepted PUT retries only that GET. Transport failures,
timeouts, server failures or failed post-write readback never repeat a write.

## Stage B: optional push-triggered refresh

For a future matched installation, the existing NuHeat entry's options contain
**Enable push-triggered updates (experimental)**, off by default. No new thermostat
entry, credentials, helper or dashboard change is needed. This local proof must
not be enabled on production under its current unpublished SDK dependency.

When explicitly enabled in the isolated proof, one listener per account uses the
existing OAuth provider and sends its bearer token in the request header, never
the URL. It connects directly to the SignalR JSON v1 hub without negotiation.
Redirects are rejected. Each connection has a thirty-second opening/handshake/
subscription budget; server silence is bounded at forty-five seconds. Application
pings are sent every fifteen seconds. Reconnection uses cancellable exponential
backoff with jitter, from five seconds up to a five-minute cap, and respects the
shared account cooldown.

The listener subscribes after every connection and asks for a full account refresh.
A recognized newer thermostat timestamp asks HA for a coalesced authoritative
REST read; equal/older timestamps and unknown devices do not create extra reads.
Notifications contain no authoritative state and never confirm an accepted command.
The five-minute polling fallback, two/eight-second command reconciliation and
thirty-second confirmation deadlines remain in place. A cooldown takes priority.
Turning push off reloads the account and returns to polling-only behavior.

Options changes reload the account; OAuth token updates alone do not. Unload
cancels the listener, reconnect/heartbeat work, pending invalidation reads and
existing control timers. Unknown/raw hub payloads and authorization details are
excluded from diagnostics and are not logged by the listener.

## Boundaries and recovery

Synthetic tests use fake OAuth providers, mock clocks and loopback services.
The separately approved live check also verified vendor hub subscription, ordinary
reconnect, push-triggered refresh and polling fallback for one account/device.
Additional models, long-lived sessions and live Stage A writes remain unverified.

Disable push to fall back to existing polling. Do not delete NuHeat entries or
Application Credentials to recover. Entity/device registry associations, account
ownership migration and Core handoff protections are retained. Core has not been
changed. Relative controls and energy reporting remain outside stages A and B.

A separately approved [live Stage A attempt](../openspec/changes/extend-nuheat-api-capabilities/live-stage-a-validation.md)
returned successfully from the hold call but did not confirm the complete state
before timeout. It stopped and verified original-setting restoration. Live expiry
retention across retargeting remains unverified; this is not a hardware pass.

## Observed Signature hold limitations

Isolated readback comparisons found that the tested thermostat's 25-hour request
was subsequently reported with about 23 hours remaining. A separate 22-hour
request initially echoed the exact requested time, then both API readback paths
reported the expiry rounded down by 37 seconds to the whole minute. These are
observations of one setup, not proof of a universal API or firmware limit. The
vendor's statement that v2 imposes no upper cap does not guarantee every device
retains every requested duration or precision.

For predictable holds on the tested setup, choose a whole-minute expiry and avoid
longer-than-23-hour holds until the vendor explains this behavior. Do not rely on
the initial API echo as device confirmation. The candidate does not silently
round, clip or replay requests. A differing expiry remains unconfirmed until the
bounded pending intent expires; the reported expiry is then the retained state
for a later deliberate temperature adjustment. No thermostat entries need removal.
A subsequent isolated hardware test confirmed that a roughly 22-hour, whole-minute
hold retained its exact expiry after a 0.5°C target adjustment. Both API readback
paths confirmed the new target and original expiry, and the original scheduled
settings were restored.
