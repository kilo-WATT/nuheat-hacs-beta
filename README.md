# NuHeat Beta for Home Assistant

Restore NuHeat after the Chemelex API migration, keeping the existing `nuheat`
domain, thermostat entities, devices, dashboard and automation references.
Based on [Core PR #176586](https://github.com/home-assistant/core/pull/176586).

This is an **unofficial community beta**, installed as a HACS custom repository.
It is not listed in the official HACS catalog and is not an official Core release.

Requires **Home Assistant 2026.10.2 or later**. Testing covers stable 2026.10.2
and the pinned Core candidate on its matching framework. Live hardware testing
used a Signature thermostat; broader hardware coverage is not claimed.

## v0.1.0b11 regular release - automation compatibility

Accepts title-case and snake_case preset actions, reports title-case preset states,
and supports targets down to 5°C / 41°F. Existing controls, OAuth
providers, migrations and Core handoff safeguards are preserved. See
[release notes](RELEASE_NOTES.md).

**Current regular/latest release:** select **v0.1.0b11**
and verify HACS tracks that tag before restarting HA. **Show beta versions is not required.** Keep existing entries, credentials, entities and automations.
Signature hardware reconciliation and read-only diagnostics checks passed;
additional thermostat models and vendor-dependent optional features are unverified.

## Install

**Automation compatibility in b11:** this update accepts
both title-case and snake_case preset actions, reports title-case preset states,
and lowers the supported target minimum to 5°C / 41°F. See the
[upgrade guidance](docs/PERMANENT_HOLD.md#automation-compatibility-update)
when updating templates or state triggers. Snake_case action calls remain valid.

[![Open your Home Assistant and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kilo-WATT&repository=nuheat-hacs-beta&category=integration)

HACS must already be installed. The button opens the repository in your own
Home Assistant; it does **not** select a release for you. Follow the version
selection and verification steps below before restarting or reconnecting NuHeat.

1. Create and retain a complete Home Assistant backup.
2. In HACS > Custom repositories, add
   `https://github.com/kilo-WATT/nuheat-hacs-beta` as **Integration**.
3. Open **NuHeat Beta**. **Show beta versions is not required** for v0.1.0b11.
4. In the download/version dialog, explicitly select **v0.1.0b11**, then download.
   **Do not select `main`.** If the tag is missing, refresh the repository
   information before retrying.
5. Verify that **HACS's installed version** shows the selected release tag,
   such as **v0.1.0b11**, rather than `main` or a short commit hash such as
   `a813aac`. The integration's own version number alone is not sufficient:
   a branch download can contain the same version. If HACS still shows a hash,
   follow [Switch from a branch install](#switch-from-a-branch-install).
6. Keep your existing NuHeat entry, enable it if disabled, and restart Home
   Assistant. In a **desktop browser**, open Settings > Devices & services > NuHeat and
   follow the existing entry's **Reauthenticate / Reconnect NuHeat** prompt.
   Sign in to your own NuHeat account and complete the return to Home Assistant.
   Do not delete and re-add the integration. New users can add NuHeat from
   Devices & services instead.
7. Verify your existing entity IDs, dashboards and automations. Restart HA once
   more and confirm the thermostat remains available without another login.

The beta registers its community OAuth client automatically; users do not need
to enter a Client ID or Client secret in Application Credentials.
The temporary registration is shared by beta users and remains controlled by
Chemelex. It does not grant access to anyone's account without authorization.

**Authorize from a desktop browser.** On phones, both the Home Assistant app
and a mobile browser may hand the authorization link to the installed NuHeat
app, interrupting the return to HA. Desktop authorization succeeded in testing.
After setup, normal thermostat use through the HA mobile app is supported.

Matching legacy thermostats may consolidate into one account entry while
retaining registry identities. Unmatched entries remain for a later attempt.
If you have several thermostats on the same account, start reconnecting from
**any matching legacy entry belonging to the account you will sign in to**.
After ownership verification, migration covers the matching entries on that
account; you do not need a separate login for each thermostat. An existing account
entry may be reused. Other accounts and unverified entries remain untouched.
Repair prompts can remain if a device was not returned or cleanup needs a retry.
Keep those entries and retry; see [migration help](docs/AUTHENTICATION.md#multiple-legacy-thermostats).

No manual pip installation is needed. The beta uses HA's standard Application
Credentials store and Authorization Code + S256 PKCE. Enter your password only
on Chemelex's login page. Each user authorizes their own NuHeat account; account
tokens remain in their HA installation. Existing application credentials are
retained through upgrades and handoff.
HA installs the pinned `chemelex-nuheat==0.1.3` dependency automatically.
The shared client registration is not added to Core or the API library.

## Set a temporary hold expiry

The standard thermostat card's **Temporary hold** preset holds until the next
scheduled event. It does not offer an end-time picker. The integration cannot
add that field to the standard card; that would require a Home Assistant frontend
change.

For a specific end time, open **Developer tools > Actions**, select **NuHeat: Set
temporary hold**, choose your existing thermostat, enter a target in your HA
temperature unit, and pick a future date/time. Click **Perform action**. This action
is provided automatically by the integration: you do not need to create a custom
action, edit your dashboard, add helpers, or install a custom card. It is also
available to automations and scripts.

Local times use HA's configured timezone. During the repeated hour at the end of
daylight-saving time, use YAML with an explicit UTC offset. Invalid, past, or
nonexistent local times are rejected. Adjusting the target preserves the timed
expiry; selecting Run schedule cancels the hold. No new thermostat entities or
helpers are required. See [hold controls and action examples](docs/PERMANENT_HOLD.md).

Commands are sent immediately. Setpoints, all three presets, Heat/Manual, Off,
and On schedule a follow-up account read about two seconds after the last write.
Rapid commands coalesce. In v0.1.0b9, setpoints
and mode commands retry reads every eight seconds within a 30-second confirmation
window. HA marks accepted but unconfirmed commands as assumed state. Off's
optimistic display clears when Standby confirms or the deadline expires; other
modes and scheduled targets come from API readback. An unconfirmed outcome logs a
warning and returns to reported cloud state. Writes are never automatically
repeated. Rate-limit cooldowns defer API reads without extending assumed state. Normal five-minute polling continues. The previous v0.1.0b7 release gives mode-only commands one delayed read.

## Upgrade

For v0.1.0b11, keep your existing NuHeat entries and credentials. Update preset state comparisons to the title-case values in the upgrade guide; existing snake_case action calls and OAuth provider selection are preserved. Community sign-in requires
My Home Assistant: if you do not use `default_config:`, add `my:` to
`configuration.yaml` and restart HA. If multiple providers are offered, choose
**NuHeat community beta** or your own registered application. Existing OAuth
entries retain their associated provider. Reconnect the existing entry only if
needed; do not delete entries or Application Credentials. See
[release notes](RELEASE_NOTES.md) and [authentication](docs/AUTHENTICATION.md).

Back up and select **v0.1.0b11** in HACS; **Show beta versions is not required** for this regular release. After downloading, verify HACS shows that release tag as the
installed version, restart HA, and verify your existing entities. If prompted,
reauthenticate the existing account. Keep its config entry.

## Switch from a branch install

If HACS shows `main` or a short commit hash as the installed version:

1. Create a complete HA backup and open **NuHeat Beta** in HACS.
2. Open **Redownload**. **Show beta versions is not required** for v0.1.0b11.
3. Explicitly select the regular release (**v0.1.0b11**), and
   download it. Do not select `main`, uninstall the repository, or delete any
   NuHeat integration entries.
4. Confirm HACS now shows the release tag as the installed version, restart HA,
   and verify the original thermostat entities. Reconnect the existing entry
   only if prompted.

This changes the HACS download reference while keeping your NuHeat entries,
credentials and registry associations. Even when the branch files already match
the release, selecting the tag makes the installed release explicit in HACS.

## Automatic transition to Core

When a Core upgrade installs a **verified compatible official implementation**,
the beta backs up its files under `<config>/.storage/nuheat_beta_backups/`,
retires the custom override and requests one additional HA restart. Core loads
the same entries and registries. The tested handoff retains standard Application
Credentials and tokens without creating a second account or new entities.

The allowlist recognizes the exact source tested from PR commit
`c45837c18b59ebddf4a2ce40a1732f5beec360fd`. **The PR is not merged yet.**
If review changes that implementation, a beta update must test and allowlist
the final code before automatic handoff activates. Older or unknown Core code
leaves the beta active, including today's broken built-in integration.

After handoff, remove the downloaded beta entry from HACS if it still appears
installed. The retained backup is outside `custom_components` and cannot shadow
Core. Do not reinstall the beta over the verified Core replacement.

## Recovery

If authorization fails before migration, keep existing entries and retry after
fixing the login. For migration rollback or incomplete cleanup, retain sanitized
logs and follow Settings > Repairs. Cleanup retries when the account loads.
Removing redundant entries is an irreversible boundary.

**Known v0.1.0b3 issue:** opening setup before NuHeat starts can report missing
application credentials. Existing users should enable their original entry and
restart HA before reconnecting. The v0.1.0b4 release registers the client when
the setup flow opens too; it is not included in the unchanged v0.1.0b3 tag.
Fresh installs should use v0.1.0b4 or a newer tagged beta release. Do not
delete an existing entry to work around this message.

To undo completed migration, restore the **complete pre-migration backup** with
the matching HA/custom component version. Removing beta files does not convert
OAuth entries back to legacy credentials or revive the retired API. Do not
hand-edit storage, serials or registry IDs, or delete the NuHeat config entry.

If automatic handoff fails, check Repairs and the installed version before
restarting. The override is moved atomically and preserved, never deleted.
Restore the complete working beta backup if Core cannot load.

## Validation and limits

[Validation record](docs/VALIDATION.md) and [OAuth details](docs/AUTHENTICATION.md).
Testing includes stable HA, live PKCE success and wrong-verifier rejection,
refresh rotation, real-storage legacy migration, restart, pinned Core handoff
and automatic retirement. No private backup contents or identifiers are in this
repository. The v0.1.0b5 setpoint fix also passed an approved isolated Signature
hardware test: HA state updated in 0.24â€“0.32 seconds, stale cloud responses did
not revert it, and delayed reads confirmed changes in about 2.1 seconds. Rapid
changes coalesced correctly and the original target, schedule mode and hold
settings were restored. These timings are observations, not vendor guarantees.
Visual frontend/device timing and live failure/timeout cases were not measured;
failure and timeout handling has synthetic regression coverage.
Shared-client availability remains controlled by Chemelex.
The final merged release still needs verification before extending the allowlist.

After a successful temperature command, HA temporarily shows the requested
setpoint while waiting for cloud confirmation. If confirmation does not arrive
within thirty seconds, HA returns to the latest cloud value and logs a warning.
Check the NuHeat app/device before repeating a command whose outcome is uncertain.

Apache-2.0. [License](LICENSE.md).

Derived from Home Assistant Core's NuHeat integration; source commit and changes
are recorded in `provenance.json` and the validation record. Thanks to
[SmilesGalore](https://github.com/SmilesGalore/HA-Nuheat-Conductor) for the community
OAuth registration. Vendor permission is maintainer-reported; see
[authentication details](docs/AUTHENTICATION.md).

## Support

Use the [issue chooser](https://github.com/kilo-WATT/nuheat-hacs-beta/issues/new/choose)
for bugs, feature requests or installation help. Reports and attachments are public:
remove credentials, tokens, authorization headers, serial numbers, callback URLs,
account identifiers and private storage/backup contents. Sanitized logs are optional.
Keep your existing NuHeat entries while troubleshooting.

## Development

See [the OpenSpec development workflow](docs/DEVELOPMENT.md) for behavior
specifications, regression coverage, and proposed refinements. This tooling is
for contributors; Home Assistant users do not need Node.js or OpenSpec.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contributions and
[MAINTAINING.md](docs/MAINTAINING.md) for triage and release/promotion checklists.
