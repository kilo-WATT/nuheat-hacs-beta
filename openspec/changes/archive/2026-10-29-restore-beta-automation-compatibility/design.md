# Design

## Context

See proposal.md for the report and scope. HA's final preset service handler validates membership in the entity's advertised presets before invoking integration code. Consequently, accepting aliases only inside the beta's mapping cannot repair the observed rejection. The ordinary temperature service similarly checks the entity's advertised range; the beta currently inherits HA's generic 7–35°C defaults and separately repeats those limits in timed-hold validation.

The SDK already encodes finite Celsius temperatures and implements explicit Standby at 5°C. Swagger's temperature fields do not specify numeric bounds. Existing isolated migration tests verify multi-entry consolidation, unrelated-entry retention, and wrong-account rollback. These observations do not justify changing migration logic or claiming all hardware accepts the fallback bounds.

## Goals / Non-Goals

**Goals:** Restore action compatibility through HA's actual service validation, use one temperature-bound contract across controls, and make migration instructions match existing ownership safeguards.

**Non-Goals:** Core or SDK changes, new modes, automatic automation rewrites, new OAuth behavior, production access, hardware commands, version bumps, or publishing. The user explicitly separated Core's maintainer-directed work from this beta change.

## Decisions

### Advertise aliases normally

Update `custom_components/nuheat/const.py` and `behavior.py` so advertised presets contain the three preferred values followed by the three aliases. Map both forms to identical API controls; map readback only to preferred values:

| Preferred reported value | Accepted action alias |
| --- | --- |
| `Run Schedule` | `run_schedule` |
| `Temporary Hold` | `temporary_hold` |
| `Permanent Hold` | `permanent_hold` |

Retain the existing control and confirmation paths. Reject unknown values without writes. Do not override HA's final handler or disguise list membership. Three-only advertising would keep legacy action failures; six choices are the explicitly accepted UI tradeoff. Alias acceptance is not a promise that old state comparisons continue to work.

### Share explicit beta temperature constants

Define 5°C minimum and 35°C maximum in the beta constants and use them in `climate.py` for advertised limits and timed-hold validation. Retain unit conversion and finiteness checks. No new SDK dependency is expected. Ordinary actions must be tested through HA's validation, not merely direct entity method calls.

Keep temperature and mode independent: setting 5°C retains intended mode/expiry; explicit Off continues to request Standby. Preserve existing exceptions, optimistic state rollback, reconciliation deadlines, rate-limit handling, and cleanup. Never silently clip a target or substitute Off after vendor rejection.

Keeping the generic 7°C minimum contradicts observed Signature use and existing Standby support. Inventing model-specific bounds lacks an API contract. The chosen bounds are an explicit fallback; the unchanged 35°C maximum is not newly verified vendor-wide support.

### Document account scope without migration edits

Update README, `docs/AUTHENTICATION.md`, and `docs/PERMANENT_HOLD.md` where applicable. Explain matching-entry authorization, same-account ownership verification, existing-account consolidation, unrelated or temporarily unmatched entries, and retries. Do not promise every repair prompt vanishes immediately or suggest deleting entries. Include exact YAML action and reported-state mappings, and distinguish state strings from translated display labels.

### Keep validation and provenance scoped

Extend existing climate/behavior tests for six service inputs, canonical readback, invalid inputs, boundary units, and timed expiry retention. Reuse existing migration regressions; add coverage only for uncovered behavior claimed by the instructions. Run existing stale-read, failed-write, rapid-command, cooldown, timeout, and unload regressions. Update only required hashes for changed protected runtime files using the repository's existing provenance process; never change OAuth registration digests or handoff allowlists to bypass checks.

## Risks / Trade-offs

- Duplicate presets in standard UI → Put preferred names first and explain aliases briefly.
- Changed reported state strings → Explicit upgrade warning and mapping for template/state-trigger comparisons; no automatic edits.
- Model-specific vendor rejection → Describe evidence limits and preserve errors, with no substitute writes. Further hardware validation requires separate authorization.
- Documentation mistaken for migration redesign → Keep ownership logic and identity assertions unchanged.

## Migration Plan

Implementation will keep the domain, config entries, credentials, registry associations, and handoff behavior intact. Before a future release, document state-comparison updates and test the packaged integration with existing synthetic entries. This proposal authorizes no release. Rolling back a future installation restores old reported strings and 7°C floor; users who updated state comparisons must revert those comparisons if rolling back. Neither upgrade nor rollback requires deleting NuHeat entries.
