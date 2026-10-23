# v0.1.0b7 - Permanent Hold (prerelease)

Opt-in prerelease for initial testing. v0.1.0b6 remains the regular latest release.
Enable **Show beta versions** in HACS, explicitly download **v0.1.0b7**, verify
HACS tracks that tag, and restart HA. Back up first. Keep existing NuHeat entries,
credentials, entities, dashboards, and automations; no re-creation is required.

## Prerelease revision: Run schedule refresh

This existing v0.1.0b7 prerelease was revised before promotion. If you already
installed b7, use HACS **Redownload**, explicitly select **v0.1.0b7**, then restart
HA. The unchanged version number may not produce an update notification.

Run schedule and Auto now schedule a read after two seconds, including uncertain
post-write read failures. This refreshes the scheduled target and mode when the
immediate cloud response is stale. It does not guess the scheduled temperature,
repeat thermostat commands, or guarantee confirmation if the vendor remains stale.
Regression tests cover Manual, Permanent Hold and Standby, target changes,
failed writes, rapid commands, and cancellation on unload.

## Controls and fixes

Run schedule, Temporary hold, and Permanent hold are available as presets.
Off remains frost-protected Standby (5 C / 41 F); Heat remains physical Manual.
Correlated v1 schedule details distinguish Manual and Permanent Hold where v2
returns the same mode. Permanent Hold uses the documented v1 command and retains
its hold when the target changes. Unresolved schedule details block implicit
temperature changes rather than silently changing the hold type.

Failed commands do not report invented success or automatically repeat writes.
Delayed reconciliation, bounded optimistic setpoint updates, OAuth, migration,
entity identity, and the Core handoff allowlist retain their safeguards.
The pinned API client is chemelex-nuheat 0.1.2.

## Validation and limitations

107 client tests and 236 integration/packaging tests passed (one historical
persistence scenario skipped in the standard suite). Lint, formatting, client
type checks, package validation, and scoped private-data audits passed.
An approved isolated Signature comparison verified Manual versus Permanent Hold
and restored the original schedule, target, and hold after five commands.
Full client-to-HA regression tests use synthetic data. Other models/firmware and
Standby-to-Permanent Hold still need community hardware verification.
See [Permanent Hold validation](docs/PERMANENT_HOLD.md) and the README for backup,
upgrade, recovery, authentication, and eventual Core handoff instructions.
No production HA or upstream Core PR changes are included.

---

# v0.1.0b6 - OAuth authorization correction

Published as a regular GitHub release (prerelease disabled), visible by default
in HACS. NuHeat Beta remains unofficial community beta software.

## Fixed

Community sign-in now requires My Home Assistant (`my`) before opening NuHeat's
login page. If it is absent, HA explains how to enable `my:` and retry linking
the existing entry. Nothing is enabled or edited automatically. This avoids the
direct instance callback that the shared registration rejects, and supports the
documented My return/cancellation paths.

The community client is registered alongside existing Application Credentials.
Fresh and legacy migration flows with multiple providers show an explicit picker
with recognizable names. Choose **NuHeat community beta** for the shared client,
or your own application if you have registered one. Existing OAuth entries retain
their associated provider. Stored credentials are neither deleted nor replaced.
Custom applications retain normal callback handling and can work without `my`.

## Upgrade

Back up HA, explicitly select the **v0.1.0b6** tag in HACS, verify HACS tracks that
tag, and restart. Do not install `main` as a substitute. A regular GitHub release
needs no beta-visibility opt-in.
If community sign-in reports missing My Home Assistant and you do not use
`default_config:`, add `my:` to `configuration.yaml` and restart HA. Reconnect the
existing NuHeat entry from a desktop browser. Do not delete entries, thermostats,
entities, or Application Credentials to perform this upgrade.

## Validation and unchanged behavior

Validated on HA 2026.10.2: 208 tests passed, 1 skipped; lint, formatting, packaging,
and the scoped privacy audit passed. A live isolated round trip completed NuHeat
consent, My redirect, PKCE token exchange, account/device reads, and entry creation
with `my` loaded. No production HA access or thermostat writes occurred. Synthetic
HTTP tests cover community/custom success and denial, custom direct callbacks
without My, provider choices, credential associations, and missing-My guidance.
See [the OAuth validation record](docs/OAUTH_UNAUTHORIZED_CLIENT.md).

The domain, account/thermostat identity, migration safeguards, bounded setpoint
reconciliation, shared credential values, scopes, PKCE, and dependency are unchanged.
The Core handoff allowlist is not expanded. Updated/final Core code still needs
separate validation before handoff eligibility changes. No Core PR changes are
included. Affected community testers still need to confirm the fixes on their
installations; their original callback/provider choices remain unconfirmed.

---

# v0.1.0b5 — setpoint reconciliation

Published as a **regular GitHub release** so HACS users can see it without enabling
beta versions. NuHeat Beta remains unofficial community beta software.

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

Back up HA and explicitly select **v0.1.0b5** in HACS. **Show beta versions is not
required** for this regular GitHub release. Verify HACS displays that tag as installed, then
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
See [validation](docs/VALIDATION.md) for the test boundaries. The preparation
commit passed [GitHub Actions](https://github.com/kilo-WATT/nuheat-hacs-beta/actions/runs/39503358029).
Publication requires successful checks on the final main commit as well.

Visual frontend/physical-display latency, forced live failure/timeout behavior,
other thermostat models, and a separate live Core-framework run remain unverified
for this fix. Cloud timing can vary. The temporary shared OAuth registration
remains vendor-controlled. If a command's outcome is uncertain, check the NuHeat
app/device before repeating it. The final merged Core implementation must be
validated before a changed source is allowlisted for automatic handoff.
