# NuHeat Beta for Home Assistant

Restore NuHeat after the Chemelex API migration, keeping the existing `nuheat`
domain, thermostat entities, devices, dashboard and automation references.
Based on [Core PR #176586](https://github.com/home-assistant/core/pull/176586).

Requires **Home Assistant 2026.10.2 or later**. Testing covers stable 2026.10.2
and the pinned Core candidate on its matching framework. Live hardware testing
used a Signature thermostat; broader hardware coverage is not claimed.

## Install

[![Open your Home Assistant and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kilo-WATT&repository=nuheat-hacs-beta&category=integration)

HACS must already be installed. The button opens the repository in your own
Home Assistant; confirm the download there, then restart and reconnect NuHeat.

1. Create and retain a complete Home Assistant backup.
2. In HACS > Custom repositories, add
   `https://github.com/kilo-WATT/nuheat-hacs-beta` as **Integration**.
3. Download **NuHeat Beta**. Keep your existing NuHeat entry and enable it if
   disabled, then restart Home Assistant.
4. In a **desktop browser**, open Settings > Devices & services > NuHeat and
   follow the existing entry's **Reauthenticate / Reconnect NuHeat** prompt.
   Sign in to your own NuHeat account and complete the return to Home Assistant.
   Do not delete and re-add the integration. New users can add NuHeat from
   Devices & services instead.
5. Verify your existing entity IDs, dashboards and automations. Restart HA once
   more and confirm the thermostat remains available without another login.

The beta registers its community OAuth client automatically; users do not need
to enter a Client ID or Client secret in Application Credentials.

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

Back up, download the HACS update, restart HA, and verify your existing entities.
If prompted, reauthenticate the existing account. Keep its config entry.

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
