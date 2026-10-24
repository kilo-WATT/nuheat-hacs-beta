# Diagnostics-stage validation and Core alignment

2026-10-24. The user authorized apply and a separate proposal commit on the same
preparation branch as the previous resilience commit. Main, releases and Core
remain outside scope. Live validation was separately requested and performed
read-only in throwaway HA; production was never accessed.

## Implemented stage

`custom_components/nuheat/diagnostics.py` constructs a fixed local health schema:
integration/SDK versions, entry state, availability counts, cooldown-active
boolean and counts of pending target/mode/expiry confirmations. It does not dump
entry data/options, thermostat models or exceptions. Missing SDK metadata and
incomplete setup produce a minimal snapshot. No existing runtime file changed.

`tests/nuheat/test_diagnostics.py` covers nested synthetic private values in keys,
entry data/options and unknown fields; pending hold status; failed/offline data;
missing metadata and setup; and zero API/token calls or entry changes.
Packaging explicitly adds the single module and checks its provenance hash.
The packaging drift regression rejects changed diagnostic source bytes.
Authentication guidance documents local-only behavior and warns that HA's own
download wrapper/filename may contain metadata beyond this handler's snapshot.

## Validation results

- Beta complete suite: 348 passed, one existing skip, using the installed
  candidate SDK wheel in isolated HA 2026.10.2.
- SDK complete suite: 133 passed; no SDK implementation changed in this stage.
- Ruff lint and scoped formatting checks passed; SDK strict mypy passed.
- Diagnostics plus packaging subset: 18 passed.
- Strict OpenSpec: 11 items passed, zero failures.
- Package: 30 entries, including the new diagnostics file; every ZIP member
  matches its source, and no OpenSpec files enter the runtime artifact.
- Candidate ZIP SHA256:
  `348e197649d19cf5165b87edd1a0226c380b49d5aee8c65443b31806ec5b31d0`.
- All pre-existing integration runtime files match resilience commit
  `d72bb6066158dd5b0eb006561afd02244a2b6145`, including OAuth, migration,
  identity, hold/control behavior, handoff guard and allowlist. Core is clean.

SDK wheel provenance remains the resilience validation's 0.1.3.dev0 artifact,
SHA256 `2211a95b54612d839ca175a8b2e655a9624cbb927ea2e30f527159436224dbea`.
This is an unpublished local dependency. Release publication stays blocked;
ordinary remote integration CI cannot install it from the package index yet.

## Final read-only live check

Passed against the linked thermostat using isolated HA with the exact runtime
files and candidate SDK. Account data loaded and device availability was true.
The actual diagnostics handler returned its fixed schema, with zero additional
API requests, zero thermostat commands, no config-entry change and no tested
private account/device/token values exported. Private evidence remains outside
Git under `nuheat-beta-private/setpoint-hardware-validation/`.

No new heating/mode/hold command was needed to validate this additive handler.
The earlier resilience hardware test remains distinct evidence; it does not
verify the four proposed optional API capabilities.

## Outstanding gates and merge readiness

[evidence.md](evidence.md) records unresolved H/P/E/R gates. Their twelve tasks
remain unchecked; no hold cap, notification transport, energy sensors or relative
action was shipped or claimed. No vendor message was sent. Diagnostics can be
reviewed together with resilience without enabling these unfinished features.

This stage merges additively with the preceding commit on the same branch.
No release/tag/version promotion is implied. An installable beta still requires
authorized SDK publication and release validation. The full capabilities change
must remain active rather than sync/archive unimplemented requirements.

## Core alignment

Future separately authorized port targets:

- `homeassistant/components/nuheat/diagnostics.py`: same fixed local schema,
  Core's diagnostics type conventions and integration-version representation.
  Core is bundled rather than a custom integration; do not assume a custom
  manifest version is always present. Native temperature/lifecycle behavior is
  irrelevant to this read-only module and must not be changed.
- `tests/components/nuheat/test_diagnostics.py`: adapt fixtures and use Core's
  diagnostics download helpers to verify handler discovery and the complete
  response, in addition to zero network calls and private-marker assertions.
- SDK version metadata may be absent; preserve the tested null fallback rather
  than making diagnosis dependent on a package-index call.

Run Core's NuHeat and diagnostics tests, Ruff, mypy/pylint and hassfest in its
matching environment after port authorization. None of those Core implementation
checks were run here. No community registration was copied and no handoff source
was made newly eligible. Optional future features need their own Core scope and
evidence gates; they are not implied updates to the current PR.
