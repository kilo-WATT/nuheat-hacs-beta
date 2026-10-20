# Validation record: beta 0.1.0b2

Validated 2026-10-19 and 2026-10-20, America/New_York. Current beta-release gates passed.
The final merged Core release is a future verification target.

## Source and changes

Core PR #176586 is pinned to `c45837c18b59ebddf4a2ce40a1732f5beec360fd`.
No upstream source, branch, PR text or comment was modified. Original hashes
are in `provenance.json`. Config entry version remains **3**.

Migration, registry transfer and account identity are the PR implementation.
Beta changes are HACS metadata, English translations, stable climate property
names, standard Application Credentials and guarded automatic Core handoff.
Packaging checks the original integration code except these documented changes.

## Stable tests

Ubuntu 24.04 / WSL, CPython 3.14.2, HA **2026.10.2**,
pytest-homeassistant-custom-component 0.13.373, chemelex-nuheat 0.1.1.

**157 passed, 1 skipped.** The skipped persistence scenario is run separately.
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

The exact secret-free package repeated migration, restart, automatic retirement
and the following Core startup successfully. Reusing the upgraded clone initially
exposed a newer HTTP storage schema; its disposable HTTP settings were archived
before repeating stable validation. NuHeat credentials and registries were retained.

No thermostat writes were sent. No backup data, actual serials, account IDs,
private addresses, real registry IDs or raw logs are published.

## Recovery, privacy and future Core

The requested PBS backup completed and its restore archive was independently
listed before any production change. Private locations stay outside this repo.
Staged files and package contents are audited against an external private
baseline before publication. HACS metadata and English translations are checked;
release packaging requires current beta gates to pass and never uploads itself.

Publication of an embedded shared secret was rejected by automatic approval
review. The released package instead uses one-time local Application Credentials.
The secret and the unpublished commit containing it are excluded from the public
branch. The privacy audit also checks the actual approved secret value, without
printing it, and refuses any file or package containing it.

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

