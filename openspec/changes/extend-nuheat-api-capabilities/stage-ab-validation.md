# Stage A/B isolated implementation â€” 2026-11-10

The user approved stages A and B only. Implemented locally in the existing beta
and SDK checkouts. No commits, pushes, tags, releases, deployment, production
access, real NuHeat API connection, account login or thermostat commands occurred.
Core, credential values/provider associations, migration, registry identity and
handoff allowlists remain untouched. C and D are deferred, not completed.

## Stage A result

- SDK helpers canonicalize aware expiry to whole-second UTC, with no upper cap.
  Local lead-time validation occurs after token waits and before every submission,
  including a retry after definite 401. HA uses that same canonical expiry for
  pending intent and retains its existing local-time UI and target range.
- Timed retargets resend the explicit canonical expiry. Exact readback matching
  remains; different expiries do not falsely confirm. Near-expiry failures map
  to a translated HA validation error without shifting expiry or changing mode.
- Explicit fake-session tests cover rejected PUT 401, repeated 401, GET-only
  retry after accepted PUT, transport/timeout/5xx/readback failures and server 400.
  Existing bounded-operation, serialization and unload tests remain in the suite.
- A test fixture's default hold expiry was moved to a future synthetic date so
  the suite no longer treats an already expired hold as a valid new timed command.

## Stage B result

- SDK implements the limited direct-WebSocket SignalR JSON v1 contract using
  existing aiohttp. Header-only tokens, same configured origin, redirect rejection,
  isolated cookies, bounded records/handshake/Subscribe, application Ping/Close,
  reconnect token handling/resubscription, jittered bounded backoff and shared
  REST cooldown. No new runtime dependency was added.
- Known-device change timestamps deduplicate within each account; notifications
  request coalesced authoritative reads and never provide thermostat state.
- HA options default off. Setup starts one explicitly enabled listener; only a
  push-option change reloads the entry, not routine OAuth token data updates.
  Cleanup closes the owned listener/session without closing HA's shared session.
- A separate due-read path avoids postponing reads during bursts and retains
  one necessary follow-up for events during an in-flight read. Five-minute polling
  and original command deadlines remain. Unload cancels callbacks and tasks.
- An end-to-end loopback hub test performs a real SDK REST GET and updates the
  coordinator's target after Notify; it records zero PUTs. Other fake-hub tests
  exercise authentication, errors, framing, silence, pings, redirects and cleanup.

## Final checks

The isolated environment was created with Rust `uv`, reusing the existing HA test
dependencies. A locally built candidate wheel was installed with `uv pip install
--no-deps --reinstall` into that environment only. Beta was tested on stable HA
2026.10.2; no claim of testing a newer HA version is made.

| Check | Result |
| --- | --- |
| SDK installed-wheel suite: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_asyncio.plugin -q` | 196 passed |
| SDK `mypy src` | Passed, strict typing |
| SDK `ruff check src tests` and `ruff format --check src tests` | Passed |
| Beta installed-wheel suite: `python -m pytest -q` | 469 passed, 1 existing skip |
| Beta `ruff check custom_components tests tools` | Passed |
| New HA regression test formatting | Passed |
| Both repository `git diff --check` | Passed |
| `npm run specs:check` | 12 passed, 0 failed |
| `python tools/package.py` | Local candidate allowlist/provenance validation passed |
| Beta working-tree + local ZIP privacy audit | Passed, no findings |
| SDK source + wheel count-only privacy audit | 22 files / 9 wheel members, no private or copied registration findings |
| `python tools/package.py --release` | Correctly refused; release approval/matching SDK gates pending |

The SDK tests disable unrelated HA plugin autoload because that plugin blocks
all sockets. SDK servers bind only to loopback TestServer origins; HA's equivalent
end-to-end test explicitly enables its local socket fixture. No test contacts
the vendor. Fake identities, tokens and payloads are synthetic.

Local SDK wheel: `chemelex_nuheat-0.1.4-py3-none-any.whl`, SHA256
`8329e90b1ffd7dc800e7375b099fafe160339e74b377fdc8a46f07332ff1a1a1`.
That project version is retained only for local testing and must not replace a
public artifact or be published under an existing version.

Local beta review ZIP: `nuheat-0.1.0b11-UNRELEASED.zip`, SHA256
`22d6eda31e8a274526c6ad9247218091bd308aaeea2348764cb137fa7625f26d`.
This is not the published b11 asset. Its public manifest pin stays at SDK 0.1.3
and does not supply the candidate APIs. Release status and provenance explicitly
block publication until a matching SDK version, pin and final approval are supplied.

## Remaining limits and next decision

The subsequent separately approved [live Stage B check](live-stage-b-validation.md)
verified vendor routing, ordinary reconnect, push-triggered authoritative refresh
and automatic polling fallback for one account/device. That follow-up does not
change the synthetic results or artifact hashes recorded above. Broader account
and device coverage, long-lived token expiry and live Stage A writes remain
unverified. Server clock/transit differences can still reject near-expiry holds;
those errors remain visible without retries or shifted expiry.

SDK/beta release preparation requires a separate request. This multi-stage change
stays active while C/D are deferred; completed A/B tasks do not claim that energy
or relative controls shipped. Production and Core remain untouched.

A subsequent [live Stage A attempt](live-stage-a-validation.md) stopped on an
authoritative confirmation timeout and verified restoration. Retarget/expiry
retention is not yet live-validated; no release readiness is implied.
