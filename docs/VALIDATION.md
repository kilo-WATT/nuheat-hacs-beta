# Validation record: beta 0.1.0b3 and unreleased audit corrections

Validated 2026-10-19 and 2026-10-20, America/New_York. This record distinguishes
the immutable published tag from corrections on `main`. The final merged Core
release remains a future verification target.

## Published release and readiness audit

`v0.1.0b3` points to `7173b6a62da2c3667ea6b87539a79e870524dd48`.
The manifest version is `0.1.0b3`, domain is `nuheat`, minimum HA is 2026.10.2,
and runtime dependency is `chemelex-nuheat==0.1.1`. The stable version feed still
reported HA 2026.10.2 at audit time. Both the version-commit and tag CI runs
passed. No release assets were attached; the source archive is sufficient for
the HACS configuration in this repository.

The actual tagged archive passed **155 tests, 1 skipped** and packaging locally.
Its OAuth setup test file was empty: an earlier test-only API update accidentally
uploaded empty content. Earlier references to 157 passing tests describe the
pre-publication candidate, not this published tag. This audit restores synthetic
bootstrap coverage and adds a regression for a setup flow before domain startup.

That regression reproduced a real v0.1.0b3 limitation: a fresh setup flow, or one
opened while the existing integration is disabled, can abort with
`missing_oauth_credentials`. The correction shares the existing credential-import
helper between component startup and flow startup, preserving existing providers.
It does not change OAuth grants, callback, PKCE, migration, registry transfers,
cleanup or Core handoff. The original config-flow source comparison allows only
this helper import and call. **Corrected suite: 161 passed, 1 skipped.**
Separate synthetic processes also passed legacy seed, corrected beta migration,
restart and matching-Core replay after this correction. Both tagged and corrected
source passed local packaging. No package was uploaded.

The corrections have not been released. The v0.1.0b3 tag and release are untouched;
publish a separately versioned v0.1.0b4 after its final CI passes before broad
community sharing, particularly to new installations.

## Source and changes

Core PR #176586 is pinned to `c45837c18b59ebddf4a2ce40a1732f5beec360fd`.
No upstream source, branch, PR text or comment was modified. Original hashes
are in `provenance.json`. Config entry version remains **3**.

Migration, registry transfer and account identity are the PR implementation.
Beta changes are HACS metadata, English translations, stable climate property
names, community-client import into standard Application Credentials and guarded
automatic Core handoff. The unreleased correction also imports the same client
before a setup flow needs it.
Packaging checks the original integration code except these documented changes.

## Stable tests

Ubuntu 24.04 / WSL, CPython 3.14.2, HA **2026.10.2**,
pytest-homeassistant-custom-component 0.13.373, chemelex-nuheat 0.1.1.

Earlier candidate: **157 passed, 1 skipped**. Tagged release and corrected-suite
counts are recorded above. The skipped persistence scenario is run separately.
Coverage includes account mismatch, climate units/commands, consolidation,
registry preservation, rollback, cleanup, refresh rotation, missing-credential
handling and retention of user-supplied credentials. Automatic-handoff tests cover
exact-source recognition, changed/missing Core rejection, atomic retirement,
retained backup, a single restart and refusal to move another config's files.

## Live OAuth

The user's report of vendor permission is accepted as authorization to reuse
and distribute the specific SmilesGalore registration. The private message was
not independently inspected and is not published. The lab client was compared
to that approved registration without displaying either credential.

- Fresh Authorization Code + S256 PKCE succeeded with a 128-character verifier.
- Scopes: `openid openapi offline_access`; a refresh token was issued.
- Refresh rotated the token, and its replacement was persisted.
- A second fresh code with a deliberately incorrect verifier was rejected with
  HTTP 400 / `invalid_grant`.
- OAuth state validation remained enabled. Passwords, codes, account tokens
  and raw vendor responses are excluded from this repository.

## Independent-process and real-storage transitions

Synthetic storage tests passed legacy seed, beta migration and beta restart,
retaining entry/entity/device IDs, names, icon, areas, labels, user-disabled
state, options and registry ownership, with legacy credentials removed.

The development component initially failed on stable's older climate framework.
The correct target, CPython 3.14.5 / HA 2026.11.0.dev0 at the pinned PR commit,
passed the independent-process Core handoff. No Core source was changed and no
dependency or API stubs were added.

A retained pre-migration HA backup was copied and stripped to NuHeat entries
and related registries, with area/floor/label metadata. No other integration,
automation, add-on or cloud agent could start. The disposable local installation
used real on-disk storage and normal HA bootstrap, configuration manager,
credential provider and climate platform, without pytest storage mocks.

Separate processes passed against the live vendor API:

1. Version-1 legacy to stable beta: account/serial validation, retained IDs and
   customizations/options, removed legacy credentials, completed cleanup and
   an available climate entity.
2. Beta restart: persisted state, live reads and refresh-token rotation.
3. Override removal followed by unmodified pinned Core on its matching framework:
   existing credentials/tokens worked, identities and options survived, climate
   was available and refresh rotated again.
4. Reinstalling beta only in the clone and booting with the matching framework
   triggered automatic backup/retirement. The next Core process loaded the
   same live account and identities.

The earlier secret-free candidate also repeated migration, restart, automatic
retirement and the following Core startup successfully. Reusing the upgraded clone initially
exposed a newer HTTP storage schema; its disposable HTTP settings were archived
before repeating stable validation. NuHeat credentials and registries were retained.

No thermostat writes were sent. No backup data, actual serials, account IDs,
private addresses, real registry IDs or raw logs are published.

Production testing subsequently completed desktop OAuth with the distributed
community client. The original climate entity became available and remained
available after a full HA restart; entity registry ID, config-entry ID, unique ID,
device association and area matched the private baseline. This production check
used an earlier `main` download, not the subsequently published tag. The audit
does not represent it as a second tagged-release production installation.

## HACS custom-repository verification

Only custom-repository installation is in scope; no official catalog submission
was made. The single `custom_components/nuheat` directory, manifest, `hacs.json`,
English translations, source archive and minimum HA requirement conform to that
installation path. HACS on the user's HA reports this custom repository installed
from commit `05394e2`; this confirms actual installation, not a tagged upgrade.

The audit executed HACS 2.0.5's unmodified `get_releases`, `version_to_download`
and `download_repository_zip` methods in a private I/O harness against actual
GitHub release metadata and archives. Without beta opt-in the prerelease is
filtered; with opt-in the v0.1.0b3 tag is selectable. Fresh extraction matched all
released integration files byte-for-byte. A repeat download replaced an older
manifest while leaving separate synthetic registry storage intact. No uploaded
ZIP asset was needed. This is a method-level integration check, not a complete
HACS UI upgrade in another live HA installation. Production was not modified.

The README explains beta visibility, tagged download, moving from a branch
install to a release, restart, reconnect, desktop authorization and complete
backup recovery. HACS updates require a newer release/version; future delivery
cannot be empirically tested until another release exists.

## Recovery, privacy and future Core

The requested PBS backup completed and its restore archive was independently
listed before any production change. Private locations stay outside this repo.
Staged files and package contents are audited against an external private
baseline before publication. HACS metadata and English translations are checked;
release packaging requires current beta gates to pass and never uploads itself.

The published v0.1.0b3 intentionally includes the shared community client. Its
values matched the approved private reference during this audit without printing
them. Individual passwords, access/refresh tokens and private identifiers are
not intentionally distributed. The tagged archive was scanned against the saved
private identifier baseline and retained account/password/token values with no
matches (18 private values checked, without displaying them). This is a targeted privacy check,
not proof that every possible sensitive string can be detected.

The older `tools/privacy_check.py` deliberately also rejects the known shared
secret. That check reflects the earlier secret-free candidate policy; it is not
evidence of a private account-token leak in the intentional community-client
release. The audit does not disable that guard. Independent private audit output
distinguishes that registration from actual user data.

Home Assistant Core and the referenced SmilesGalore project identify their
licenses as Apache-2.0. The Core license is retained; README attribution and
`provenance.json` identify the source and adaptations. No additional SmilesGalore
implementation code was copied. Vendor permission remains maintainer-reported;
see AUTHENTICATION.md for confirmed properties and potential service risks.

The PR remains unmerged. The tested candidate is not represented as a final
release. Automatic handoff recognizes the tested hashes and dependency contract
in `core-handoff.json`. Changed final code requires a validating beta update.
Unknown/older built-in code leaves beta active. Cloud Linking may eventually
require relinking the existing account; never recreate it.

## Reproduce

On Linux/Python 3.14:

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q
ruff check custom_components tests tools
python tools/package.py --release
```

`tools/transition.py` retains the expected failure of development climate code
on stable. `tools/core_handoff.py --core /path/to/matching/core` verifies the
matching runtime using its existing Core fixtures without editing the checkout.
Private live-storage scripts and tokens are intentionally excluded.

References: [Core PR](https://github.com/home-assistant/core/pull/176586),
[stable feed](https://raw.githubusercontent.com/home-assistant/version/master/stable.json),
[HACS requirements](https://www.hacs.dev/docs/publish/integration/).

