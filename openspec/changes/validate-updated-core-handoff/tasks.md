# Tasks

## 1. Reproducible isolated candidate

- [x] 1.1 Resolve the intended Core source, framework, SDK pin, and beta baseline; verify immutable source digests in a sanitized test manifest.
- [x] 1.2 Build synthetic legacy and account storage fixtures on isolated installations; verify the fixtures contain no real accounts, credentials, or thermostat identifiers.
- [ ] 1.3 Determine Core PR support for official Home Assistant Cloud linking and any separate maintainer enablement; verify actual provider availability independently of PR merge.

## 2. Transition and capability evidence

- [ ] 2.1 Run legacy-to-beta migration, restart, official-provider relinking and beta-to-candidate-Core handoff; preserve entry/entity/unique/device IDs and configuration while intentionally updating the community provider association and tokens.
- [ ] 2.2 Test official-provider authorization, refresh and reauthentication with synthetic endpoints, then verify the deployed official path when available; cover cancellation, wrong account, unavailable provider and explicit custom-provider choice without deleting existing entries or credentials.
- [x] 2.3 Exercise all presets, HVAC controls, target confirmation, timed expiry, and existing automation action dispatch after handoff; verify equivalent observed behavior on the matching framework.
- [x] 2.4 Test unknown-source rejection, failed retirement, restart, and recovery; verify the shipped allowlist is untouched and recoverable beta files remain outside the import path.

## 3. Readiness decision

- [x] 3.1 Update the sanitized report for the official-provider transition; retain earlier community-provider results as historical evidence and identify the revised checks not yet run.
- [x] 3.2 Only after official linking and the revised transition pass, prepare exact source/SDK eligibility changes for separate authorization; otherwise record blockers and keep the beta active.
- [x] 3.3 Run npm run specs:check and review the test/report mapping; do not claim a later merged Core source or real hardware was validated by the isolated run.

## Workflow follow-up

- Obtain the user's implementation/release scope before changing the shipped allowlist or publishing.
- Revalidate if the actual final Core source changes; do not archive unfinished transition validation.
- User clarification: official Cloud linking replaces community OAuth after handoff.
  Earlier community/My tests do not complete the reopened official-provider tasks.
  Existing control and recovery evidence remains scoped to the tested candidate;
  repeat it if the eventual official transition changes relevant behavior.
