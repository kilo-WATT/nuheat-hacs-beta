# v0.1.0b7 Permanent Hold validation

107 SDK tests passed; 236 beta tests passed, 1 historical persistence case skipped.
Validated on HA 2026.10.2 with lint, packaging, and private-data checks.
The revised b7 adds 12 regression cases for stale schedule targets/modes, failed
Auto writes, rapid commands, and timer cleanup. Original failing cases reproduced
the stale display; all pass with delayed reconciliation.
See [Permanent Hold evidence and limits](PERMANENT_HOLD.md). Protected OAuth,
migration, identity, coordinator, and Core handoff source is unchanged from b6.
The Core PR and production HA are unchanged. GitHub CI is verified before publication.

# Validation record: v0.1.0b6 and published-release history

Validated 2026-10-19 and 2026-10-20, America/New_York. This record distinguishes
v0.1.0b5 from published v0.1.0b4 and the older v0.1.0b3
audit. No published tag is rewritten. Final merged Core remains a future target.

## v0.1.0b6

Validated on 2026-10-20, America/New_York, from published v0.1.0b5. The maintainer
approved publication as a regular latest GitHub release. Preparation commit
`d860313925cee4279d5a95f3d9f624bfc315c64a` passed
[GitHub Actions](https://github.com/kilo-WATT/nuheat-hacs-beta/actions/runs/39522439116).
Final approval/documentation metadata is checked again on the exact release commit
before tagging. Existing tags are not rewritten.

Local validation passed 208 tests with 1 skip, lint, changed-file formatting,
allowlisted packaging, and the known-private-value source/archive scan. The
historically separate persistence scenario remains skipped in the routine suite;
this version does not change migration, registry, setpoint, or handoff code.
Live read-only OAuth passed with My genuinely loaded in an isolated HA instance.
Synthetic full HTTP round trips cover custom clients with/without My, successful
community authorization and denial, plus preserved provider associations. See
[the detailed evidence and boundaries](OAUTH_UNAUTHORIZED_CLIENT.md).

The proposed runtime differences are confined to OAuth registration/provider
selection, callback requirements, and explanatory translations. Community secrets,
API dependency, scopes, PKCE, entity identity, migration code, setpoint behavior,
and handoff allowlist remain byte-for-byte unchanged from v0.1.0b5. No production
HA or Core PR changes are included. Community-user confirmation remains pending.

## v0.1.0b5

The manifest is 0.1.0b5, containing bounded optimistic targets and delayed cloud
reconciliation beyond published v0.1.0b4. The maintainer approved publication as
a regular GitHub release, with prerelease disabled, so HACS beta opt-in is not
required. The beta product name and version suffix do not change that GitHub flag.
The validated preparation commit is `da1d3a5042e5814af6f6edd482ba5d8f570a236c`;
[its GitHub Actions run passed](https://github.com/kilo-WATT/nuheat-hacs-beta/actions/runs/39503358029).
Final publication metadata changes are limited to documentation and approval
status, followed by CI on the final main commit before tagging and publishing.
OAuth, migration, registry identity, and Core handoff eligibility remain unchanged.
Thirteen unchanged runtime/configuration files, including the community OAuth
registration and handoff guards, match the saved v0.1.0b4 source. The community
registration also matches the public v0.1.0b4 file byte-for-byte. Packaging now
rejects blank OAuth placeholders, registration drift, inconsistent version/tag
metadata and unexpected component source/JSON files. See
[the implementation record](SETPOINT_RECONCILIATION.md).

Validation on 2026-10-20: **185 beta tests passed, 1 skipped**, **164 Core tests
passed**, beta/Core lint passed, Core changed-file formatting passed, and targeted
Core type checks passed. The extracted review ZIP also passed all 185 beta tests
and lint. Its 26 allowlisted files matched the selected source bytes. An offline
audit found no matches against known private account tokens and identifiers in
source or ZIP contents; this is a scoped check, not a universal secret detector.
Local packaging and archive-content checks passed;
the publication-gated build is enabled by the recorded approval. The domain,
minimum HA version and API dependency remain unchanged.
The normally skipped persistence test was run separately:
synthetic legacy seed, beta migration, beta restart, and modified Core each passed
in independent processes with preserved registry identities and options. These
checks used isolated runtimes. No production HA installation was accessed or
changed during these tests or the hardware run below. The configured CI commands
pass locally. Verify the GitHub Actions checks on the selected release-preparation
commit before merging, tagging or publishing; this record does not claim a remote
CI result in advance.

The approved isolated Signature hardware run passed. HA state changes took
0.239–0.313 seconds from service start. Two delayed account reads started
2.0016/2.0008 seconds after service completion and confirmed the requested targets
after 2.1091/2.0901 seconds. Naturally stale readbacks did not revert the displayed
target. Rapid changes used one delayed read after the final success. Six setpoint
writes stayed within the approved 0.5 C bound; one Auto write restored the original
scheduled mode. Cloud readback confirmed the original target and no-hold state.
No further reads occurred during the forty-second unload observation. The lab
was stopped. A private-observer JSON snapshot race affected only the final unload
event, which was recovered from a complete independently decodable record; command
and readback measurements were intact. The observer was corrected without another
hardware run. Private logs, tokens and device identities are excluded from source
and release artifacts.

Live frontend/physical-display latency, deliberately failed writes/timeouts, other
thermostat models, and a separate live Core-framework test remain unverified for
this fix. Failure and timeout handling has synthetic coverage; no universal cloud
propagation timing is promised.

## Published v0.1.0b4 release

The published tag's manifest version is `0.1.0b4`. Compared with audited commit
`90842666ccf03ea9450b9ad13f065ddd8dac8ae5`, preparation changes only that version
and version-specific documentation. Integration logic, client registration,
OAuth behavior, migration safeguards, config-entry version and Core handoff
are unchanged. The maintainer subsequently published v0.1.0b4 as a prerelease,
tagging `a813aac8735c6f0ac00c4c9be2c458146eba9b5b`.

The existing suite passes **161 tests, 1 skipped**; the persistence scenario was
exercised separately in the audit. Lint and the gated `tools/package.py --release`
validation also pass. The generated audit package is local only.
[GitHub Actions passed on the release commit](https://github.com/kilo-WATT/nuheat-hacs-beta/actions/runs/39427903599).
This documentation update does not change either published release or tag.

## Published release and readiness audit

`v0.1.0b3` points to `7173b6a62da2c3667ea6b87539a79e870524dd48`.
That tag's manifest version is `0.1.0b3`, domain is `nuheat`, minimum HA is 2026.10.2,
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

The corrections are included in the published v0.1.0b4 release. The v0.1.0b3
tag and release are untouched. New installations should use v0.1.0b4 or a newer
tagged beta release.

## Source and changes

Core PR #176586 is pinned to `c45837c18b59ebddf4a2ce40a1732f5beec360fd`.
The remote upstream branch, PR text and comments were not modified. Original
fixtures and hashes remain in `provenance.json`. A separate uncommitted Core
patch contains the aligned setpoint fix; it is not included in the beta ZIP.
Config entry version remains **3**.

Migration, registry transfer and account identity are the PR implementation.
Beta changes are HACS metadata, English translations, stable climate property
names, community-client import into standard Application Credentials and guarded
automatic Core handoff. The v0.1.0b4 release also imports the same client
before a setup flow needs it. v0.1.0b5 adds the documented setpoint reconciliation
deviation while retaining the exact Core handoff allowlist.
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

Those earlier transition checks sent no thermostat writes; the later v0.1.0b5
Signature run is recorded above. No backup data, actual serials, account IDs,
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

The subsequent read-only production audit found HACS 2.0.5 recording a branch
installation at `a813aac`, with no selected tag and beta visibility effectively
disabled. Its update entity reported both installed and latest versions as that
commit hash, despite HACS knowing about prerelease v0.1.0b4. All 17 installed
NuHeat source/configuration files nevertheless matched the v0.1.0b4 tag's Git
blob hashes exactly, including the client and startup helper. Matching manifest
versions or file contents therefore do not prove tagged-release tracking.

The README now requires enabling beta visibility, explicitly selecting the
latest release tag rather than `main`, and verifying the installed tag in HACS.
It includes Redownload instructions for existing branch users, retaining their
NuHeat entries and registry associations. The repository button alone does not
pin a release. No production download, settings change or restart was performed
during that audit, so a completed live branch-to-tag switch is not claimed.

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
python tools/package.py
```

This produces a local `-UNRELEASED.zip` review artifact. `--release` produces the
local release ZIP only when approval and validation gates are satisfied. Neither
mode uploads, tags, pushes or publishes anything.

`tools/transition.py` retains the expected failure of development climate code
on stable. `tools/core_handoff.py --core /path/to/matching/core` verifies the
matching runtime using its existing Core fixtures without editing the checkout.
Private live-storage scripts and tokens are intentionally excluded.

References: [Core PR](https://github.com/home-assistant/core/pull/176586),
[stable feed](https://raw.githubusercontent.com/home-assistant/version/master/stable.json),
[HACS requirements](https://www.hacs.dev/docs/publish/integration/).

