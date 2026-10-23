# v0.1.0b7 - Hold controls and responsive updates

Published as the regular latest GitHub release. Beta visibility is not required
in HACS. The integration remains unofficial community beta software.
Explicitly download **v0.1.0b7**, verify
HACS tracks that tag, and restart HA. Back up first. Keep existing NuHeat entries,
credentials, entities, dashboards, and automations; no re-creation is required.

## Prerelease revision: timed holds and consistent refresh

This existing v0.1.0b7 prerelease was revised before promotion. Already installed
b7? Use HACS **Redownload > v0.1.0b7**, then restart HA; the unchanged version may
not produce an update notification.

All thermostat writes now schedule a read about two seconds after the last
command: setpoints, all presets, Heat/Manual, Off, and On. This prevents a stale
immediate response from being the only post-command read. Mode writes get one
follow-up; setpoint retries retain their existing eight-second interval and
30-second deadline. Commands are never automatically repeated after uncertainty.

New **NuHeat: Set temporary hold** action: select the existing thermostat, target
in HA's temperature unit, and a future end date/time. Local times use HA's timezone;
invalid/past/nonexistent times are rejected, and ambiguous times require an
explicit offset. The ordinary Temporary hold preset remains until next schedule.
Quick target changes preserve a newly requested expiry during confirmation.
See README and [action examples](docs/PERMANENT_HOLD.md).

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

107 client tests and 271 integration/packaging tests passed (one historical
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
