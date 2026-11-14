# Combined climate compatibility verification

Recorded 2026-11-13 for the local changes addressing beta issues #11 and #13.

## Implementation

The preset list and parser accept exactly run_schedule, temporary_hold and
permanent_hold. HA's translation loader resolves those identifiers to Run schedule,
Temporary hold and Permanent hold, with exactly three advertised values and three
readable labels. Title-case inputs fail before a thermostat write. Upgrade guidance
covers title-case actions and state comparisons adopted in b11/b12. Existing
underscore-based calls continue to work. This supersedes the earlier local
recommendation to standardize on title-case values.

The climate entity reports Celsius through native temperature properties. Its
legacy property definitions are conditional on the minimum framework capability.
Ordinary climate services convert to the entity unit through HA. The custom
hold action independently converts its configured-HA-unit input exactly once.
Pending state, mode selection, limits, expiry and control cleanup are covered.

## Results

- Full suite on installed HA 2026.10.2 and SDK 0.1.5: 482 passed, one existing skip.
- Official native climate API source overlay: 161 passed, covering setup/state
  and deprecation log assertions, standard temperature controls, explicit hold
  input in both units, preset validation, stale readback, errors, rapid commands,
  bounded confirmation and cleanup.
- Supplemental native contract checks are included in the suite and described
  explicitly as probes in tests/nuheat/test_native_temperature.py.
- Ruff lint passed for custom_components, tests and tools. Seven targeted files
  passed format checks. git diff --check passed.
- All 14 OpenSpec specifications and changes passed strict validation.
- Local review ZIP built successfully with the compatibility guide included.
  SHA256 221764722afe3ca6de7be23a1f947957791a0c69616060f58581c5a17d7a7bdf.
- Privacy audit scanned 220 working-tree files and one archive, checked 13 private
  baseline values and returned zero findings.
- OAuth, identity, migrations, manifest, handoff source and allowlist bytes match
  the published baseline. SDK and Core source were not edited.

## Official framework source and scope

The November release package/tag lookup returned 404. The plan's exact-source
alternative was exercised with official home-assistant/core native climate
source obtained through the GitHub connector and verified against these Git blob
identifiers before execution:

| File | Git blob |
| --- | --- |
| climate/__init__.py | d825b339eada0e05d635abb525fc285d9b025104 |
| climate/entity.py | d51c5316faf42a62843d3e9cf21d0caf81b33da5 |
| climate/const.py | 7d497f063646290e0b17137f930cacda60b0c42e |
| climate/services.py | 0a97071932e6e2212844dfc5ef52e00c63f2e62b |
| helpers/deprecation.py | 4f5094a3744b878084b024d420318704b85db607 |

The isolated process loads the exact official native entity, constants and
migration/deprecation helpers. It executes the official temperature service
handler extracted by AST, supplying its installed display conversion dependency.
Unrelated new service schemas require another validation library and are outside
this API overlay. This verifies the affected native API paths on the installed
HA test host, and does not claim a full HA 2026.11.2 installation or UI test.

Reproduce with tools/verify_native_climate.py. It retrieves missing public source
blobs, verifies every expected blob before loading, and confines the API overlay
to its own process. Source downloads and the local ZIP remain ignored artifacts.

## Review status

Implementation and tests are local. Runtime version remains b12 until separately
authorized release preparation. Publication is disabled and candidate provenance
is local-only. Production HA and live thermostats were not accessed. No commit,
push, issue comment, PR merge or release was performed during these changes.

## Naming guidance verification

Checked HA's entity attribute translation guidance before revising this design:
https://contributors.home-assistant.io/core/integrations/translations/
The translation-loader regression checks the raw state identifiers independently
of the readable labels, correcting the earlier tests that mirrored the initial
title-case design assumption. EGM was not run in that earlier planning pass.

## b13 release-preparation follow-up

Versioned candidate 0.1.0b13 passed 485 tests with one existing skip. CI exposed
that the source verifier validated downloads without persisting them on a clean
checkout. The helper now writes only verified bytes, with three regressions for
fresh download, cache reuse and rejected mismatching cached/downloaded source.
Native API verification remains a required candidate CI step. Publication is
pending review of the final preparation commit and its GitHub checks.
