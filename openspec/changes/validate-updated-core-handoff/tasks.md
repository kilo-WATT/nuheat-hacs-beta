# Tasks

## 1. Reproducible isolated candidate

- [ ] 1.1 Resolve the intended Core source, framework, SDK pin, and beta baseline; verify immutable source digests in a sanitized test manifest.
- [ ] 1.2 Build synthetic legacy and account storage fixtures on isolated installations; verify the fixtures contain no real accounts, credentials, or thermostat identifiers.

## 2. Transition and capability evidence

- [ ] 2.1 Run legacy-to-beta migration, restart, and beta-to-candidate-Core handoff; verify unchanged entry IDs, entity IDs, unique IDs, device associations, and provider keys.
- [ ] 2.2 Exercise refresh and authorization/reauthentication for community-associated and custom providers through synthetic endpoints; record callback and My-integration prerequisites with pass/fail evidence.
- [ ] 2.3 Exercise all presets, HVAC controls, target confirmation, timed expiry, and existing automation action dispatch after handoff; verify equivalent observed behavior on the matching framework.
- [ ] 2.4 Test unknown-source rejection, failed retirement, restart, and recovery; verify the shipped allowlist is untouched and recoverable beta files remain outside the import path.

## 3. Readiness decision

- [ ] 3.1 Produce a sanitized validation report covering every transition/capability and failed or unexecuted check; verify each claim has an exact command or test result.
- [ ] 3.2 If every required check passes, prepare the exact minimal allowlist patch and instructions for separate user authorization; otherwise record blockers and verify the beta remains active.
- [ ] 3.3 Run npm run specs:check and review the test/report mapping; do not claim a later merged Core source or real hardware was validated by the isolated run.

## Workflow follow-up

- Obtain the user's implementation/release scope before changing the shipped allowlist or publishing.
- Revalidate if the actual final Core source changes; do not archive unfinished transition validation.
