# NuHeat development

Read `docs/DEVELOPMENT.md`, `openspec/config.yaml`, and the relevant specifications
before changing behavior. This repository owns planning for the beta, the client,
and Core alignment. Do not copy this tooling into upstream Home Assistant Core.

- Follow the user's current scope. Specifications do not independently authorize
  production access, thermostat commands, commits, pushes, releases, or handoff changes.
- Preserve the `nuheat` domain, entry/entity/device identity, provider associations,
  migration rollback, and exact-source Core handoff safeguards.
- Use synthetic credentials, thermostat identifiers, and examples. Keep private
  account data, serial numbers, tokens, callback URLs, and hardware records out of Git.
  Do not duplicate the beta's distributed community registration into plans, Core, or SDK.
- Distinguish requested, accepted, and confirmed state. Do not describe a two-second
  read as guaranteed confirmation or an optimistic value as authoritative API state.
- Cover every affected control. Include stale reads, failed/uncertain writes, rapid
  commands, timeout, unload, units, and explicit expiry where applicable.
- Keep Core and beta semantics aligned while adapting each framework's API. Follow
  Core's own repository instructions and human-review policy for upstream contributions.
- Separate shipped contracts from proposals. Keep proposal tasks unchecked until
  implemented and verified; OpenSpec validation is not a substitute for behavior tests.
- Use `npm run specs:check` for spec edits. Run the relevant Python tests, lint,
  packaging, and isolated transition checks when implementation changes require them.
- Keep Node dependencies and OpenSpec files out of Home Assistant runtime packages.
