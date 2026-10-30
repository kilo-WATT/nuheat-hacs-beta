# v0.1.0b11 - regular/latest - automation compatibility

- Accept `Run Schedule`, `Temporary Hold`, and `Permanent Hold` alongside the
  existing snake_case action aliases. All six appear in the preset list.
- **State comparison change:** reported preset values use the title-case names.
  Snake_case action calls remain valid; update template and state-trigger
  comparisons using the [upgrade guide](docs/PERMANENT_HOLD.md#automation-compatibility-update).
- Use a shared 5–35°C / 41–95°F target range for normal controls and timed holds.
  A 5°C target preserves mode/expiry; explicit Off retains Standby behavior.
- Clarify account-scoped multi-thermostat migration and retry guidance without
  changing ownership checks, entity identity, OAuth, or Core handoff behavior.

Select **v0.1.0b11** in HACS and verify the installed tag before restarting HA.
Beta visibility is not required. Keep existing entries and credentials. Validation:
452 tests passed with one existing skip; lint, packaging, privacy and specs passed.
No new live hardware test was performed for this update; other models remain unverified.

# v0.1.0b10 - historical release - API resilience and private diagnostics

In HACS, explicitly select **v0.1.0b10**, verify
HACS tracks the tag, and restart HA. **Show beta versions is not required.**
This is the regular/latest GitHub release. Back up first and keep existing NuHeat entries,
Application Credentials, entity/device IDs, dashboards and automations.

## Changed

- SDK 0.1.3 honors Retry-After across one runtime account client. Commands during
  cooldown fail promptly rather than queue or replay; pending confirmation still
  expires after thirty seconds.
- HTTP 403 is permission denial rather than expired login. Optional v1 denial
  preserves usable conservative v2 state; required operations report errors.
- Requests have a fifteen-second budget; SDK operations and HA controls have a
  thirty-second budget including token/lock waits and post-write reads. Uncertain
  writes are not automatically repeated. Unload cancels pending work.
- Download diagnostics from the existing entry's menu. NuHeat contributes only
  allowlisted cached health/version counts, without API requests or credentials,
  thermostat identifiers, temperatures, schedules or raw errors. Review HA's own
  wrapper and filename before sharing publicly.

## Validation and limits

348 beta tests passed with one existing skip; 133 SDK tests passed. Lint,
formatting, SDK typing, packaging, private-data and strict OpenSpec checks pass.
A Signature hardware test used five commands within the approved bounds:
entity updates took 0.26-0.71 seconds despite stale immediate cloud readbacks;
rapid changes confirmed and original target, schedule and hold were restored.
A separate read-only live diagnostics check added zero API requests or commands.
Failure injection remains synthetic, not live vendor throttling or stalled writes.
Final package-index dependency and GitHub CI checks are recorded before publication.

Existing OAuth flow/provider associations, modes, expiry handling, migration,
entity identity and exact-source Core handoff safeguards are preserved. Core PR
#176586 and production HA are unchanged. Official Cloud transition validation
remains separate. New hold-duration enforcement, push updates, energy reporting
and relative adjustments are not included; vendor questions remain outstanding.

## Recovery

If needed, redownload **v0.1.0b9** in HACS and restart without deleting NuHeat
entries. Restore the matching full HA backup if the HA framework/storage was
also upgraded. For an uncertain command, check the NuHeat app before repeating
it; relinking or repeated writes do not resolve every API error.

---

# v0.1.0b9 - Preserve accepted targets during rapid control changes

Regular/latest GitHub release. In HACS select **v0.1.0b9**, verify it tracks
that tag, and restart Home Assistant. **Show beta versions is not required.**
Back up before updating. Keep existing NuHeat entries, entities, Application
Credentials, dashboards and automations. This remains unofficial community beta
software. Production HA and the upstream Core PR are not changed by publishing.

## Fixed

- A temperature change immediately followed by Temporary hold, Permanent hold
  or Heat now carries the accepted target rather than an older cloud target.
  The helper and two write sites match the validated Core implementation.
- Six regressions cover all three interactions in Celsius and Fahrenheit.
  Two additional recovery regressions verify rename failure and restoring the
  preserved beta files after restart-dispatch failure.

## Validation and limits

The local suite passes 305 tests with one existing persistence-stage skip.
Lint, formatting, strict OpenSpec validation, package and privacy audits pass.
GitHub CI is verified on the final release commit before publication. No new hardware
test was performed for this follow-up; prior b8 hardware feedback is historical.

OAuth, migration, entity identity, SDK dependencies and runtime handoff safeguards
are unchanged. The revised OpenSpec plan targets official Home Assistant Cloud
linking after it is available and verified, with relinking of existing entries.
It does not require continued community OAuth after handoff. That transition is
not implemented or approved here, and the exact-source allowlist is unchanged.

---

# v0.1.0b8 - Bounded mode confirmation

Promoted to the regular latest GitHub release after maintainer-reported
successful b8 hardware testing. HACS beta visibility is not required. Select
**v0.1.0b8**, verify HACS tracks that tag, and restart Home Assistant. Keep all
existing NuHeat entries, credentials, entities, dashboards and automations.
Back up before updating. The integration remains unofficial community beta software.

## Changed

- Run schedule, Temporary hold, Permanent hold, Heat, Auto, Off and On now
  reconcile with API readback after about two seconds, then about every eight
  seconds within a 30-second per-thermostat deadline.
- Accepted but unconfirmed modes report assumed state. Off's optimistic display
  clears when Standby confirms or the deadline expires; a later external mode
  change can update HA normally. Other modes and schedule targets use API state.
- Rapid and concurrent controls preserve the newest accepted mode, target and
  explicit hold expiry. Selecting ordinary Temporary hold does not resurrect an
  earlier timed expiry. Old in-flight reads cannot confirm a newer command.
- Timeout logs an unconfirmed outcome and resumes reported cloud state. Failed
  writes remain errors; writes are never automatically retried. Timers stop on unload.

OAuth, migration, entity identity, API client 0.1.2, and the exact-source Core
handoff allowlist are unchanged. OpenSpec development tooling is excluded from
Home Assistant runtime packages. The matching Core port was pushed to PR #176586 as `9ab210660371eaf6bda2083a518cf15eea29318f`; final Core handoff validation remains separate.

## Validation and limitations

297 isolated integration/packaging tests passed; one existing historical
persistence case is skipped. Lint, formatting, packaging, privacy and strict
OpenSpec checks passed. GitHub CI is checked on the final release commit before
publication. The maintainer subsequently reported that b8's tested controls
worked well on hardware. This is qualitative feedback; no new b8 timings or
exhaustive model/firmware coverage are claimed. Earlier measured Signature
results cover prior behavior.
No production Home Assistant changes are included.

## Known limitation

A rapid target change followed by a preset change before cloud readback can
reuse the earlier cloud target in b8. A synthetic comparison confirmed that
Core's accepted-target helper avoids this edge; the beta correction is a separate
follow-up. Check the resulting target in HA and the NuHeat app when changing
controls rapidly. No runtime correction is included in this documentation update.

Current repository notes describe the promoted status. Original documentation
inside the published b8 ZIP remains its publication snapshot; its tag and assets
have not been rewritten.

## Recovery

If testing fails, select **v0.1.0b7** in HACS, verify the selected tag, download
and restart HA. Keep existing NuHeat entries and credentials; do not delete or
recreate thermostats. Retain your backup and report the control used and observed
HA/NuHeat state without posting account credentials or thermostat identifiers.

---

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

# v0.1.0b5 â€” setpoint reconciliation

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
0.24â€“0.32 seconds and delayed cloud confirmation in about 2.1 seconds. Naturally
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
