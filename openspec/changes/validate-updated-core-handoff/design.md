# Design

## Context

The current allowlist intentionally pins older tested source. Core PR #176586 has
since received the beta's hold and timing features with framework-specific service
registration and native temperature properties. Equal feature names alone do not
prove that persisted authentication and registry storage survive that change.

## Goals / Non-Goals

Produce a reproducible isolated transition report before any allowlist edit.
Do not merge Core, copy the shared registration into upstream files, use live
account data, retire a production override, or broaden a source allowlist by pattern.

## Decisions

- Re-resolve and record the exact candidate commit and matching HA framework before
  testing. The recorded starting candidate is `59749ee3512fa56265fae085cae0c7db68f9b26c`,
  not an assertion that a later merged source is identical.
- Build disposable installations from synthetic legacy storage, migrate to beta,
  restart, then install the exact Core candidate on its matching framework. Use
  test-local candidate fingerprints rather than altering the shipped allowlist.
- Assert preserved entry IDs, entity IDs, unique IDs, device links, provider keys,
  and token-store associations. Verify refresh and authorization callbacks through
  synthetic providers; do not skip the community-versus-custom callback distinction.
- Exercise all three presets, Manual/Heat, Standby/Off, target confirmation, explicit
  timed expiry, and action dispatch. Verify that existing timed-hold automations
  still resolve the same action and target entity.
- Exercise mismatch rejection and recovery separately. Do not weaken the runtime
  guard to make a test pass. Keep beta backups outside the import path.
- Produce sanitized source digests, framework versions, test commands, results,
  and explicit gaps. Only a later user-authorized implementation may update the
  exact allowlist, and a later merged Core revision requires its own comparison.

## Risks / Trade-offs

- Framework differences: run each stage on its intended framework and document unsupported transitions.
- OAuth behavior drift: include fresh authorization and reauthentication, not just cached-token startup.
- False confidence from fixtures: distinguish isolated evidence from live vendor authorization.
- Unknown final merge: eligibility applies only to the exact tested source.

## Migration Plan

This proposal itself changes no migration or handoff behavior. If tests pass,
prepare a minimal separately authorized beta allowlist update with evidence and
recovery instructions. If any capability fails, report it while the beta remains
active. Production and hardware remain outside the isolated test scope.
