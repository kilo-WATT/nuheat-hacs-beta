# v0.1.0b5 — setpoint reconciliation

Prepared prerelease; awaiting maintainer approval. No v0.1.0b5 tag or release has
been published by this preparation.

## Fixed

After NuHeat accepts a temperature change, Home Assistant now displays the
requested setpoint immediately instead of retaining an old cloud value until
the five-minute poll. A delayed cloud read reconciles the request after two
seconds. Rapid changes share a delayed refresh and keep the latest successful
target. Unconfirmed targets expire after thirty seconds, returning to the latest
cloud value instead of remaining optimistic indefinitely.

Failed command methods do not display unconfirmed success or automatically repeat
the write. An outcome can be uncertain when the command succeeds but its following
read fails; a delayed read checks the result. Unloading cancels reconciliation
timers. The normal five-minute background polling interval is unchanged.

## Upgrade

Back up HA, enable **Show beta versions** in HACS, and explicitly select
**v0.1.0b5** once published. Verify HACS displays that tag as installed, then
restart HA. Branch users can use **Redownload** to select the tag. Keep all
existing NuHeat entries; do not delete or recreate thermostats or entities.
No credential reset is required for this fix. Reauthenticate the existing entry
only if HA requests it.

The domain, entity identities, migration safeguards, community OAuth registration,
PKCE flow and pinned API dependency are unchanged. Automatic Core handoff still
requires an explicitly verified compatible implementation. This release does not
extend the handoff allowlist to the separately prepared Core patch or unknown
future Core code.

## Validation and limits

The approved isolated Signature hardware run observed HA state updates in
0.24–0.32 seconds and delayed cloud confirmation in about 2.1 seconds. Naturally
stale responses did not revert the displayed target. Rapid commands, original
target/mode/hold restoration, and a forty-second unload check passed without
modifying production HA. Regression coverage includes failed writes, stale and
in-flight reads, rapid/concurrent commands, bounded timeout and timer cleanup.
Final local checks passed: **185 beta tests, 1 skipped**, **164 Core tests**, lint,
Core formatting/type checks, and packaging. The skipped persistence scenario
passed separately through legacy, beta, restart and modified Core processes.
See [validation](docs/VALIDATION.md) for the test boundaries. GitHub Actions must
pass on the selected release-preparation commit before merging, tagging or
publishing. No remote CI pass is claimed in advance by these release notes.

Visual frontend/physical-display latency, forced live failure/timeout behavior,
other thermostat models, and a separate live Core-framework run remain unverified
for this fix. Cloud timing can vary. The temporary shared OAuth registration
remains vendor-controlled. If a command's outcome is uncertain, check the NuHeat
app/device before repeating it. The final merged Core implementation must be
validated before a changed source is allowlisted for automatic handoff.
