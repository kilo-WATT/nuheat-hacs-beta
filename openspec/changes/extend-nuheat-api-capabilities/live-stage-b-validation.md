# Isolated live Stage B validation — 2026-11-10

Separately approved read-only validation of the local candidate, using fresh lab
OAuth and one linked thermostat. Production Home Assistant was not accessed.
No agent thermostat commands were sent. The user made and restored the app change.

## Observations

- Header-authenticated direct WebSocket connection, SignalR handshake and Subscribe
  succeeded against the vendor hub.
- Six notifications were received across two connections. Two observed coordinator
  state changes followed notification receipt by 0.42 and 0.36 seconds. These are
  notification-to-state measurements, not app-tap-to-state latency.
- Read-only verification agreed with the app's rounded 75°F target display;
  exact Fahrenheit equality was not established because of API/display rounding.
- Controlled disconnect recovered: resubscription occurred after 5.686 seconds,
  followed by an authoritative REST read after another 0.484 seconds.
- After explicitly stopping push, the user reported restoring the original
  scheduled setting. The unchanged automatic five-minute poll detected a state
  change 300.180 seconds after the preceding read, with no forced refresh.
  This was 217.866 seconds after the user's restoration marker, not a measured
  app-tap timestamp. Push count stayed unchanged during fallback.
- The harness recorded 13 REST GETs and zero thermostat writes. Two additional
  standalone read-only GETs checked target display rounding.
- Listener, coordinator, sessions and isolated HA were stopped cleanly; the local
  authorization server was confirmed unavailable after cleanup.

## Limits

The user confirmed restoration; exact original target/mode/hold equality was not
independently measured against a retained baseline. This single-account check
proves deployed routing, ordinary reconnect, push-triggered authoritative reads
and polling fallback for this setup. It does not establish all device/account
coverage, long-lived token expiry, outages, rate limits or live Stage A writes.
Those failure paths retain synthetic coverage. No production deployment, commit,
push, SDK publication or beta release occurred or is authorized by this test.

The current manifest still pins the public SDK without these candidate APIs.
A matching newly versioned SDK, dependency update and release approval are still
required before distributing the candidate.
