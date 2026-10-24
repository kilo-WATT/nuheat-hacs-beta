# Current Core handoff: isolated validation results

2026-10-23. This is not a completed end-to-end transition validation.
The exact candidate and source digests are in `candidate-manifest.json`.

## Revised destination: official Cloud linking

The user clarified that community OAuth is temporary. Official Home Assistant
Cloud linking is the intended destination after merge and separate provider
enablement. The community-provider tests below are historical capability evidence;
their recommendation to preserve community login/My after handoff is superseded.
No new community/My handoff requirement is proposed. Existing entries and entity
identity must survive official-provider relinking; provider association and tokens
may intentionally change on successful authorization of the same account.

The PR was checked once during b9 preparation: it is OPEN at
`9ab210660371eaf6bda2083a518cf15eea29318f`. Its user flow accepts HA-registered
local or cloud providers and its manifest depends on Application Credentials.
That source inspection does not establish an enabled official NuHeat Cloud
provider or deployed linking availability. Task 1.3 remains incomplete. Official
authorization, cancellation, wrong-account protection and same-entry relinking
have not yet been exercised. Automatic handoff stays disabled for this candidate.

## Confirmed gates

Core candidate `9ab210660371eaf6bda2083a518cf15eea29318f` runs on
HA 2026.11.0.dev0 and requires chemelex-nuheat 0.1.2. The beta test framework is
2026.10.2. The shipped handoff guard requires SDK 0.1.1 and five allowlisted
source files differ. Calling the actual `compatible_core()` against the current
Core directory returns false. The override therefore remains active. Merely
updating JSON fingerprints would not satisfy the SDK guard.

The actual guard was exercised by the private command
`/home/codex/.cache/nuheat-permanent-hold/bin/python ../record_followup_validation.py`.
Five existing isolated tests in `tests/nuheat/test_core_handoff.py` also pass,
covering known-source recognition, mismatch rejection, reversible retirement and
failure handling. Those fixtures are older candidates, not proof of a current
Core transition. The shipped allowlist and guard are unchanged.

## OAuth compatibility probe

Private synthetic-only probe, run from the parent directory:

```
PYTHONPATH=/home/codex/core /home/codex/core/.venv-nuheat-3148/bin/python -m pytest -p tests.conftest -c callback-probe.ini test_candidate_callback_probe.py -q
```

Result: six passed, one framework deprecation warning. Four cases construct
Core's actual NuHeat provider and generate authorization URLs for synthetic
community/custom registrations with My enabled/disabled. Two more import
synthetic Application Credentials, resolve the persisted provider key through
HA's real resolver, and complete mocked token refresh. No real credentials,
accounts, vendor requests, or production data were used.

Observed: provider keys and client selection resolve without a resolver mock;
PKCE uses S256. Core uses My's callback when `my` is enabled, and an
instance-specific callback otherwise, for both registration kinds. A registration
restricted to My's callback cannot accept the latter. The beta treats its
community registration specially and requires My before authorization; Core
currently has no corresponding community-specific check. Custom registrations
must retain their own supported callback behavior.

This demonstrates callback selection, not live vendor rejection or a full
browser round trip. My being disabled after beta setup is an unresolved future
reauthentication case. Normal My-enabled setups are not shown to fail. No new
vendor restriction or account-specific problem is claimed.

## Serialized storage and fresh callbacks

Private harness `../run_current_transition.py` builds disposable copies of the
beta and tests, excludes `community_oauth.py`, and writes only synthetic
registration values into the lab. Eight independent pytest processes passed:
seed, beta migration, beta restart, and current-Core startup for each of the
community-labelled and custom-labelled synthetic registrations. The candidate
stage imports the real current Core component, not the old candidate fixture.
It explicitly switches the disposable installation to Core; it does not bypass
the guard and claim automatic retirement worked.

The persistence assertions verify entry ID, entity IDs, unique IDs, device links,
user customizations and options. The real provider resolver is used on restart
and Core startup, not replaced by FakeOAuthImplementation. The migration flow's
authorization itself uses the existing synthetic fake implementation. The
synthetic stored credential is associated with its `test` provider key.
`../check_transition_provider_storage.py` separately verifies that provider key
and synthetic credential remain in beta, restart and candidate serialized stores.
No real OAuth registration or vendor interaction was exercised by those stages.
The same storage checker scanned all 73 non-cache lab files against 18 known
private values: zero matches. It also asserted that the lab's community
registration file contains only the two expected synthetic values. The standard
Git-based privacy scanner alone selected zero files in this ignored lab, so that
empty scan is not counted as fixture privacy evidence.

Additional fresh OAuth round trips used the real Core flow, local token HTTP
server and HA callback handler. The private adapted test
`test_current_roundtrip_probe.py`, run with the same Core pytest command as the
callback probe, passed six cases: successful and denied authorization for
community-labelled credentials with My enabled, and custom credentials with My
enabled/disabled. Successful cases verify PKCE verifier exchange, account subject
and provider association; denial creates no entry. This does not simulate the
hosted My website, verify live vendor acceptance, or cover reauthentication.

## Follow-up: reauthentication and post-storage controls

The private `test_current_roundtrip_probe.py` was extended from the initial six
cases above to 16 fresh/reauthentication cases, all passing. Community/custom
registrations are exercised with My enabled/disabled, successful and denied
authorization. My-disabled community cases explicitly model a registration
restricted to My by delivering `unauthorized_client` instead of a code. This
confirms the direct-instance callback mismatch and safe error handling, not a
new live vendor observation. Successful reauthentication retains the original
entry, account subject and provider key; denial leaves existing entry data intact.

Two additional tests load serialized beta storage into actual current Core, one
per provider, and exercise the existing entity via HA service dispatch. All three
presets, Heat, Auto, Off and On send the expected commands and confirm fresh
synthetic readback. Target writes display immediately and then clear pending
state on confirmation. The existing `nuheat.set_temporary_hold` action still
targets the retained entity, preserves explicit expiry and confirms target/expiry.
The real migrated OAuth session also refreshes an expired token through a mocked
endpoint without losing its entry/provider association. Advancing six minutes
after coordinator shutdown produces no additional reads. API writes are mocked;
no thermostat commands are sent.

Reproduction: run `prepare_post_handoff_probe.py`, then run
`test_post_handoff.py` from the generated candidate directory with the Core pytest
command above, `NUHEAT_TRANSITION_STAGE=candidate`, and
`NUHEAT_TRANSITION_DIR` pointing to each provider's synthetic storage directory.
The shared control helper is private `post_handoff_controls.py`.

## Follow-up: failure and recovery

The beta suite now includes `tests/nuheat/test_handoff_recovery.py`. Together with
the original handoff tests, seven tests pass. They use the existing known-source
fixture and exercise actual filesystem retirement, one restart request, rejection,
rename failure, and missing restart service. Rename failure preserves the override
and creates a repair issue. Restart-dispatch failure leaves a complete backup
outside `custom_components`, creates a repair issue, and permits explicit file
restoration. The current candidate is not silently approved by these fixture
tests. An accepted restart request is not proof a real process restart completes.

Private `run_failed_core_recovery.py` exercised failed current-Core setup for both
providers: two tests pass with SETUP_RETRY and unchanged identities. Two attempts
to restore beta on the older HA framework using newer saved storage fail: HTTP
storage version 3 exceeds the older framework's supported version 2. This is an
unsupported HA downgrade, not a NuHeat migration failure. No storage versions
were patched. Two complete pre-upgrade synthetic snapshot restorations on the
matching old framework pass and preserve identities. If recovery includes an HA
downgrade, restore its full pre-upgrade backup; integration files alone are
insufficient. Restoring beta on the newer framework was not tested by this
downgrade exercise.

Final beta suite: 305 passed, one existing persistence-stage skip. Lint and
formatting pass. The recursive fixture scan now checks 95 non-cache files against
18 known private values, with zero matches. The actual unchanged guard still
rejects current Core, and Core's working tree remains clean.

## Outstanding automatic transition and decision

Do not approve an allowlist update yet. Capability, authorization and recovery
checks above were exercised, but automatic retirement and a real restart into
this exact candidate remain unexecuted because the existing source/SDK gate
correctly refuses eligibility. Task 2.1 remains open for that integrated test.
The revised destination requires verified official Cloud linking and same-entry
provider transition rather than continued community authorization. Custom
credentials retain their explicit choice. Review official linking evidence and
exact-source/SDK eligibility separately before the final automatic transition.
Keep the beta active and do not archive this change.

No Core source, production, commit, push, tag, or release change was made. A later
merged Core revision requires another exact comparison.

## Public availability recheck after maintenance archival

2026-10-24: Core PR #176586 remains OPEN and unmerged, with unchanged head
`9ab210660371eaf6bda2083a518cf15eea29318f`. Its application-credentials module
still provides local user-supplied PKCE credentials; that source alone does not
prove deployed official Cloud linking.

Public maintainer guidance explicitly states Account Linking is added when the
integration is merged:
https://github.com/home-assistant/core/pull/176586#issuecomment-5132719796
No later public enablement confirmation was found in the PR conversation. This
supports treating enablement as a separate gate, not assuming merge readiness
from community authorization. The public NuHeat integration page likewise does
not establish that the new official OAuth path is deployed.

Tasks 1.3, 2.1 and 2.2 remain open. No production, account-based provider query,
Core edit, beta allowlist change or new official end-to-end authorization was
performed. The beta remains the active bridge pending verified official linking
and exact-source transition tests.

## New submitted candidate after the resilience port

2026-10-24: The separately reviewed resilience/diagnostics port was committed and
pushed to the existing Core PR as `d70d43b22ae84d0e2d3f33705162ee0efc9f25b9`,
using published SDK 0.1.3. Its isolated NuHeat suite passed 305 tests, the SDK suite
passed 133, and scoped/commit-time hooks passed; repository-wide pylint remained
incomplete as documented in the parity change.

This is a newer submitted candidate, not a transition-tested replacement for the
older candidate manifest. Prior migration/retirement results retain their original
source scope. The shipped beta handoff allowlist is unchanged. Re-resolve and
validate this or the eventual merged source, official provider enablement and
same-entry relinking before making it eligible for retirement. No final automatic
transition or deployed official OAuth success is claimed by the port.
