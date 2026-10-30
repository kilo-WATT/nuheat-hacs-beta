# Proposal

## Why

The working b10 beta includes published SDK 0.1.3, cooldown-aware command reconciliation, bounded operations, permission-specific feedback and private local diagnostics. Core PR #176586 still pins SDK 0.1.2 and lacks these additions, so eventual Core users would lose the beta's fault handling and support snapshot behavior.

## What Changes

- Port validated b10 resilience semantics and synthetic regressions to Core's current NuHeat implementation, preserving native units, service dispatch, lifecycle APIs and provider behavior.
- Upgrade Core's exact SDK pin to the published 0.1.3 release and regenerate dependency metadata through Core tooling.
- Add allowlisted cached diagnostics with Core-appropriate version metadata and privacy tests.
- Verify runtime equivalence on Core's framework, including rate limits, stale reads, failed writes, rapid commands, deadlines, cancellation and identity retention.
- Keep the beta, SDK source, community registration and exact-source handoff allowlist unchanged. Official Cloud enablement and final transition remain in the separate handoff proposal.

## Capabilities

### New Capabilities

- `core-parity`: Observable equivalence of Core's NuHeat fault handling and private diagnostics with the validated beta, independent of handoff eligibility.

### Modified Capabilities

None. Existing authentication and command-reconciliation requirements remain the behavioral reference; this change applies them to the Core distribution without modifying beta semantics. The active optional-capabilities proposal still owns its beta diagnostics and unresolved vendor-gated features.

## Impact

Observed on 2026-10-24: Core is clean at `9ab210660371eaf6bda2083a518cf15eea29318f`, uses SDK 0.1.2, lacks diagnostics.py and does not implement the b10 integration-level cooldown/timeout mappings. Beta b10 at `3f77a85f459fb61021ea688d094229f4429fba9c` uses SDK 0.1.3; subsequent beta changes concern maintenance only. The archived resilience alignment report maps the required adapters.

Implementation targets only Core's NuHeat modules/tests and generated dependency metadata. Planning and sanitized parity evidence remain in this beta repository. No new dashboard controls, presets, optional sensors, push connections, hold-duration policy or account relinking are introduced. This proposal does not edit Core, run hardware tests, publish or authorize upstream submission; a later apply request starts implementation, and human review precedes submission under Core's AI policy.
