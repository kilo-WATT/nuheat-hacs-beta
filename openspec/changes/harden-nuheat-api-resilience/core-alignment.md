# Core alignment report

2026-10-24. Core remains clean at
`9ab210660371eaf6bda2083a518cf15eea29318f`, using SDK 0.1.2 and its matching
HA 2026.11.0.dev0 framework. This change implements only the local SDK/beta;
no Core patch was applied, committed, pushed or tested as an implementation.

## Compatibility boundary

The candidate SDK 0.1.3.dev0 preserves existing public method arguments and
thermostat models, adds optional constructor timeout budgets, and exports typed
permission/rate-limit errors under the existing API-error base. Persistent 401
still uses the existing refresh/retry contract. HTTP 403 intentionally changes
from authentication failure to API permission failure; this must be documented
when the eventual SDK version is released. No registration values belong in Core.

The local wheel is not a distributable public dependency. A future Core port
must use an authorized published SDK version, not point upstream at a local wheel
or claim 0.1.3.dev0 is available from a package index.

## Corresponding files

| Beta responsibility | Core port target | Adaptation |
| --- | --- | --- |
| Shared cooldown, coalesced refresh, permission errors and cleanup | `homeassistant/components/nuheat/coordinator.py` | Preserve deadline/generation behavior; test poll and reconciliation overlap on Core's coordinator framework. |
| Bounded controls and cancellation, translated errors | `homeassistant/components/nuheat/climate.py` | Keep Core's native temperature properties, unit conversion, existing Off dispatch inside its lock and None-return lifecycle APIs. |
| Bounded initial token validation and first-refresh cleanup | `homeassistant/components/nuheat/__init__.py` | Preserve typed runtime data and `async_unload_platforms_or_raise`; no provider or migration redesign. |
| Setup permission/throttle feedback | `homeassistant/components/nuheat/config_flow.py` and `strings.json` | Preserve Core's Probatio schema, account checks and provider selection. Do not copy beta community setup or translations into upstream files. |
| SDK dependency | Integration `manifest.json` and generated `requirements_all.txt` | Both currently pin 0.1.2; regenerate required dependency metadata through Core tooling after publication is authorized. |
| Regressions | `tests/components/nuheat/test_api_resilience.py`, existing integration/hold/migration tests | Adapt helper imports to pytest_homeassistant and Core's native/lifecycle contracts; preserve synthetic data. |

The current stable and Core frameworks were inspected: `async_refresh()` and
`_handle_refresh_interval()` use the debounced refresh lock and the same scheduled
refresh arguments. The beta's coalescing adapter deliberately checks generation
before that lock. These private framework hooks require fresh verification when
porting or when HA changes; source inspection is not a completed Core test run.

## Verification commands for the separately authorized port

After satisfying Core's AGENTS/setup instructions and installing the authorized
SDK in its isolated framework environment, run from the Core checkout:

```
UV_PROJECT_ENVIRONMENT=/home/codex/core/.venv-nuheat-3148 uv run --no-sync pytest -q tests/components/nuheat
UV_PROJECT_ENVIRONMENT=/home/codex/core/.venv-nuheat-3148 uv run --no-sync ruff check homeassistant/components/nuheat tests/components/nuheat
UV_PROJECT_ENVIRONMENT=/home/codex/core/.venv-nuheat-3148 uv run --no-sync ruff format --check homeassistant/components/nuheat tests/components/nuheat
UV_PROJECT_ENVIRONMENT=/home/codex/core/.venv-nuheat-3148 uv run --no-sync mypy homeassistant/components/nuheat
UV_PROJECT_ENVIRONMENT=/home/codex/core/.venv-nuheat-3148 uv run --no-sync pylint homeassistant/components/nuheat
UV_PROJECT_ENVIRONMENT=/home/codex/core/.venv-nuheat-3148 uv run --no-sync python -m script.hassfest --integration-path homeassistant/components/nuheat
UV_PROJECT_ENVIRONMENT=/home/codex/core/.venv-nuheat-3148 uv run --no-sync prek run --all-files
```

These are proposed port-validation commands, not runs claimed by this task.
Include SDK 401/403 distinction, optional v1 fallback, 429 header forms and shared
cooldown, simultaneous normal/reconciliation reads, all controls, token/lock/body
timeouts, shutdown cancellation, two devices, units/expiry and registry identity.
Recheck exact commands if Core tooling changes before authorization.

## Remaining authorization and eligibility

Actual Core edits/submission, SDK publication, beta release/version promotion and
official Cloud relinking need their own user-authorized scope. The beta's
`core_handoff.py` and `core-handoff.json` are unchanged. Neither this report nor
the SDK compatibility tests make the current PR source eligible for retirement.
