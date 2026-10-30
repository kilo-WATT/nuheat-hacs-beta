# Local implementation validation — 2026-10-29

Scope: HACS beta only, on the existing worktree branch. No commits, pushes,
version changes, releases, Core edits, production access, or thermostat commands.

## Implemented

- Six advertised preset inputs, preferred names first, with canonical title-case
  readback. Compatibility aliases use the existing command/confirmation paths.
- Shared 5–35°C bounds for climate limits and timed holds. Ordinary temperature
  actions also reject nonfinite input before calling the API: HA's own range
  comparisons alone do not reject NaN.
- Regression coverage uses HA's real preset handler and temperature service
  handler, synthetic accounts/devices, mocked writes, and controlled time.
- Upgrade examples distinguish preserved action aliases from changed preset
  state comparisons. Multi-thermostat guidance describes existing account-scoped
  migration and ownership/cleanup behavior; migration code was not changed.
- Updated only the effective provenance hashes for the five edited runtime files.
  OAuth registration digests, historical source hashes, and handoff maps remain
  unchanged. Manifest/dependency/version pins are unchanged.

## Executed checks

Commands ran from the beta root in the existing isolated Python environment:
`/home/codex/.cache/nuheat-api-resilience/bin/python`. Ruff came from
`/home/codex/.cache/nuheat-permanent-hold/bin/ruff`.

| Check | Result |
| --- | --- |
| `python -m pytest -q tests/nuheat/test_automation_compatibility.py tests/nuheat/test_permanent_hold.py tests/nuheat/test_hold_action.py tests/nuheat/test_integration.py` | 172 passed |
| `python -m pytest -q` | 452 passed, 1 existing skip |
| `ruff check custom_components tests tools` | Passed after removing an unused test import |
| `ruff format --check tests/nuheat/test_automation_compatibility.py` | Passed |
| `python tools/package.py` | Passed, including runtime provenance, registration, dependency and allowlist checks |
| `npm run specs:check` | 13 passed, 0 failed |
| `git diff --check` | Passed |
| `python tools/privacy_check.py --private-baseline ../USER_HA_BASELINE.md --view working-tree --zip artifacts/nuheat-0.1.0b10-UNRELEASED.zip` | Passed: no findings; private values were not printed |

The local ZIP is an unpublished candidate under the unchanged b10 manifest:
`artifacts/nuheat-0.1.0b10-UNRELEASED.zip`, SHA256
`086ddb4e3110c4638333074534484cc7be57712466fd69d347b0b8cf04c2a6a1`.
It is not a replacement for the published b10 release. No release-mode build or
publication approval is claimed.

The complete suite includes existing multi-entry migration, wrong-account
rollback, unrelated/omitted device retention, OAuth, identity, handoff, stale
responses, failed writes, rapid commands, timeout/cooldown and unload coverage.
Those safeguards' implementations remain unchanged.

## Remaining limits

No new live hardware test was performed. Signature lower-bound evidence and the
existing 5°C Standby implementation support the fallback; Swagger does not define
numeric bounds and acceptance across other models is unverified. Backend errors
remain visible, with no clipped target or substitute mode write. UI aliases are
intentionally duplicate choices, and existing snake_case preset state comparisons
need the documented update when this candidate is eventually installed.
