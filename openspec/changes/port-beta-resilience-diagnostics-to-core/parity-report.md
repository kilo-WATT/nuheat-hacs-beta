# Core resilience and diagnostics port evidence

2026-10-24. Local implementation only; no commit, push, PR update, merge, release,
production access or thermostat command was performed for this port.

## Baselines and setup

- Core PR #176586/local HEAD: `9ab210660371eaf6bda2083a518cf15eea29318f`.
  Working tree was clean before this port; the remote PR head was checked.
- Validated beta source: b10 `3f77a85f459fb61021ea688d094229f4429fba9c`.
  Current beta runtime matches that implementation; subsequent work is maintainer
  tooling/specifications. The beta runtime and handoff allowlist were not edited.
- Core framework: 2026.11.0.dev0; Python 3.14.8 in the existing isolated Core
  environment. `script/setup` completed, including development bootstrap,
  translation generation, hook installation and disposable local config setup.
- Core dependency changed from published SDK 0.1.2 to published 0.1.3, installed
  from the package index. Public wheel SHA256:
  `73140f56c062fdcd6fc9aefb289a071eb9646e433b6553bcdeaa76af74b36e2d`.
- Core's requirements generator changed only `requirements_all.txt` in addition
  to the manifest pin. `python3 -m script.gen_requirements_all validate` passed.
  Existing ignored remnants of three unrelated integration directories produce
  generator warnings; they did not change output or invalidate the NuHeat pin.

## Implementation and observable parity

| Concern | Core source and tests | Evidence / framework adaptation |
| --- | --- | --- |
| Account cooldown and overlap | coordinator.py; test_api_resilience.py; SDK test_resilience.py | Four timer-driven poll/reconcile orderings coalesce one in-flight read. Retry-After 120 suppresses reads while thirty-second pending state expires. Zero/very-long cooldown cleanup and optional-throttle data retention pass. SDK header/date/concurrency tests cover parsing; two devices share one account cooldown while another account remains usable. |
| All controls and deadlines | climate.py; test_api_resilience.py, test_hold_action.py | Seven mode/preset/Off/On controls plus target/timed actions reject cooldown without writing; stalled controls and lock wait time out without replay. Cancellation releases locks/tasks; unload leaves no later reconciliation request. |
| Accepted intent versus confirmation | coordinator.py/climate.py; test_setpoint_reconciliation.py, test_mode_reconciliation.py, test_hold_action.py | Existing stale-read, supersession, explicit-expiry, rapid target-then-mode and Celsius/Fahrenheit tests remain intact. Optimism is accepted intent, not API confirmation. |
| 403 versus 401 and transient failures | __init__.py/config_flow.py/coordinator.py; test_api_resilience.py, test_integration.py; SDK tests | Required 403 stays permission failure; optional v1 403 retains conservative v2 data. Genuine persistent 401 preserves refresh/reauth behavior. Permission failure through synthetic reauth retains data, options and customized registry links for both synthetic provider keys. |
| Startup/first refresh | __init__.py; test_api_resilience.py | Token validation budget is thirty seconds; failed initial refresh shuts down coordinator timers. Setup retries retain existing entries and provider association. |
| Service feedback | strings.json; translated exception assertions | Added permission_denied, rate_limited, request_timeout and write_unconfirmed exception strings plus flow abort descriptions. Generated English test translations using `python3 -m script.translations develop --integration nuheat`. |
| Private cached snapshot | new diagnostics.py; new test_diagnostics.py | Allowlisted Core/SDK versions, entry state, availability counts, cooldown flag and confirmation counts only. Nested private keys/values, unknown fields/errors and failed/incomplete runtime data are excluded without API/token/session calls. The standard admin diagnostics HTTP download is tested. |
| Identity and provider preservation | existing migration/auth tests plus reauth error tests | No entry-version bump, provider replacement or registry migration change. Existing migration/rollback/ownership tests pass. No beta community provider implementation or registration was copied. |

Core keeps native temperature properties/conversion, Probatio flow schema,
independent service registration, typed runtime data and raising unload APIs.
Off's internal dispatch stays inside a single bounded lock, avoiding nested locks.
Coordinator public status/count accessors replace cross-module private access for
Core lint compliance without exposing identifiers or changing pending semantics.

The request budget remains SDK-default fifteen seconds and total operation budget
thirty seconds, including lock/authorization wait. The missing/invalid Retry-After
fallback is sixty seconds; a valid longer cooldown is not shortened. Initial
reconciliation remains about two seconds, subsequent reads about eight seconds,
and pending state expires after thirty seconds independently of cooldown.

## Diagnostics metadata and exclusions

The beta reports its custom integration version; built-in Core has no such
manifest version. Core diagnostics therefore report locally available Core and
SDK versions, with SDK metadata absent represented as null. No beta version is
invented. No credentials, tokens, account/device identifiers, names, locations,
URLs, raw payloads or exception text are serialized. No device/entry names or
config dictionaries are copied to the support snapshot.

## Executed checks

- Complete Core NuHeat suite: **305 passed**, no skips. This includes all new
  resilience and diagnostics cases plus existing controls/auth/migration tests.
- Unchanged SDK synthetic suite: **133 passed**; SDK working tree remains clean.
- Core Ruff lint and formatting: passed on NuHeat source and tests.
- Core scoped mypy: passed, twelve source files, no issues.
- Core scoped pylint: passed on the integration source.
- NuHeat hassfest: passed, one integration and zero invalid integrations.
- Requirements generator validation: passed. English translations regenerated.
- Full-file and final scoped hook results are recorded below after completion;
  the scoped run includes new untracked diagnostics/tests omitted by tracked-only
  file enumeration. Initial scoped test-lint failures were fixed with Core
  registry fixtures, clock-driven refresh callbacks and UTC helpers, not skipped.

The first adapted suite exposed a missing numeric cooldown on an old AsyncMock;
the fixture now models the SDK property explicitly. An old migration test's
custom entity ID overlapped a private baseline marker. Its three fixture/expected
literals now use `climate.synthetic_customized_heater`; migration runtime is
unchanged. The final full suite validates those preserved identity assertions.

## Audit and review boundary

A count-only audit scans NuHeat source/tests against thirteen external private
markers and both distributed community registration values without printing them.
Final audit evidence is retained outside Git; the report records only counts.
OAuth application implementation, account identity, migration/registry code,
behavior mapping, services and constants remain unchanged. Beta runtime,
dependency/provenance/handoff files and the SDK checkout remain unchanged.

No fault was induced against NuHeat, no hardware was commanded and no production
installation was accessed. These results are isolated synthetic evidence, not a
new live thermostat test or deployed official OAuth validation. The Core source
has changed locally, so its final submitted/merged revision needs independent
handoff assessment. This port does not broaden beta eligibility or make official
Cloud linking available. Human review and separate commit/push approval precede
upstream submission under Core's AI policy.

## Final hook outcome and remaining limitation

Final `prek run --files` on all twelve changed/new paths passed every applicable
hook: Ruff lint/format, codespell, JSON, branch guard, prettier, mypy, Core-custom
pylint (including tests), requirements generation and hassfest. Hooks reporting
no applicable files (for example workflow lint on this Python-only patch) are
normal applicability skips, not suppressed failures. New diagnostics/tests were
included explicitly without staging or committing them.

The prescribed `prek run --all-files` was also executed. Its repository-wide
pylint process stalled for over twelve minutes without output; observed parent
and workers were waiting in futex/pipe/event-loop states. It was interrupted and
all associated processes exited. This broad run is **incomplete**, not passed.
No unrelated source or lint configuration was changed to hide that limitation.
Task 4.2 remains unchecked for the unfinished broad hook run despite successful
scoped validation. A later full-repository run needs a suitable environment or
separate investigation before claiming that gate passed.

Final count-only audit: 28 NuHeat source/test files, thirteen private baseline
markers, zero private-marker matches, zero community-registration copies, zero
protected Core source changes, zero protected beta changes; SDK tree clean.
The Core Git index is unchanged. The complete local patch, including new files,
is available outside Git as `nuheat-beta-private/core-parity-review.patch` for
human review; no upstream content was submitted.

Core patch scope:

- Existing source: __init__.py, climate.py, config_flow.py, coordinator.py,
  manifest.json, strings.json; generated requirements_all.txt.
- New source: diagnostics.py.
- Tests: new test_api_resilience.py and test_diagnostics.py; numeric cooldown
  defaults in two existing test_integration.py mocks; synthetic registry-ID
  literals in test_migration.py. Migration code and assertions retain semantics.

No new Core candidate is approved for beta retirement. The separate handoff
proposal remains at its last submitted head until a separately reviewed Core
update, official provider verification and complete transition evidence exist.

## Reviewed submission

2026-10-24: After the patch summary and validation limitation were presented, the
user explicitly approved committing and pushing. Core commit
`d70d43b22ae84d0e2d3f33705162ee0efc9f25b9` was added incrementally to the existing
`chemelex-nuheat` branch of `kilo-WATT/core`, updating Core PR #176586 without
rewriting earlier commits. All applicable commit-time hooks passed, including
Core-custom pylint, mypy, requirements generation and hassfest. The Core working
tree and index are clean after that push.

The earlier local-only descriptions above record the pre-submission evidence
stage. No new live test, production operation or beta release occurred during
submission. The repository-wide all-files pylint limitation remains documented;
successful scoped/commit-time hooks do not convert that incomplete run to a pass.
GitHub CI is a separate post-push result, not claimed by these local checks.
