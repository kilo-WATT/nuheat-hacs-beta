# NuHeat Beta for Home Assistant

Restore NuHeat after the Chemelex API migration, keeping the existing `nuheat`
domain, thermostat entities, devices, dashboard and automation references.
Based on [Core PR #176586](https://github.com/home-assistant/core/pull/176586).

This is an **unofficial community beta**, installed as a HACS custom repository.
It is not listed in the official HACS catalog and is not an official Core release.

Requires **Home Assistant 2026.10.2 or later**. Testing covers stable 2026.10.2
and the pinned Core candidate on its matching framework. Live hardware testing
used a Signature thermostat; broader hardware coverage is not claimed.

## Install

[![Open your Home Assistant and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kilo-WATT&repository=nuheat-hacs-beta&category=integration)

HACS must already be installed. The button opens the repository in your own
Home Assistant; it does **not** select a release for you. Follow the version
selection and verification steps below before restarting or reconnecting NuHeat.

1. Create and retain a complete Home Assistant backup.
2. In HACS > Custom repositories, add
   `https://github.com/kilo-WATT/nuheat-hacs-beta` as **Integration**.
3. Open **NuHeat Beta** and **enable Show beta versions**. This is required
   because the beta releases are GitHub prereleases.
4. In the download/version dialog, explicitly select the **latest tagged beta
   release**, currently **v0.1.0b4**, then download it. **Do not select `main`.**
   If the tag is missing, refresh the repository information and check beta
   visibility rather than downloading the branch.
5. Verify that **HACS's installed version** shows the selected release tag,
   such as **v0.1.0b4**, rather than `main` or a short commit hash such as
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

No manual pip installation is needed. The beta uses HA's standard Application
Credentials store and Authorization Code + S256 PKCE. Enter your password only
on Chemelex's login page. Each user authorizes their own NuHeat account; account
tokens remain in their HA installation. Existing application credentials are
retained through upgrades and handoff.
HA installs the pinned `chemelex-nuheat==0.1.1` dependency automatically.
The shared client registration is not added to Core or the API library.

## Upgrade

Back up, keep **Show beta versions enabled**, and select the latest tagged beta
release in HACS. After downloading, verify HACS shows that release tag as the
installed version, restart HA, and verify your existing entities. If prompted,
reauthenticate the existing account. Keep its config entry.

## Switch from a branch install

If HACS shows `main` or a short commit hash as the installed version:

1. Create a complete HA backup and open **NuHeat Beta** in HACS.
2. Enable **Show beta versions**, then open **Redownload**.
3. Explicitly select the latest tagged release, currently **v0.1.0b4**, and
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
repository. Thermostat commands have mocked coverage; these live tests sent no
thermostat writes. Shared-client availability remains controlled by Chemelex.
The final merged release still needs verification before extending the allowlist.

Apache-2.0. [License](LICENSE.md).

Derived from Home Assistant Core's NuHeat integration; source commit and changes
are recorded in `provenance.json` and the validation record. Thanks to
[SmilesGalore](https://github.com/SmilesGalore/HA-Nuheat-Conductor) for the community
OAuth registration. Vendor permission is maintainer-reported; see
[authentication details](docs/AUTHENTICATION.md).
