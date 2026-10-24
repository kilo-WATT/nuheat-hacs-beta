# NuHeat development with OpenSpec

This repository owns the shared planning record for the HACS beta, the
`chemelex-nuheat` client, and Core PR #176586. OpenSpec is a development tool,
not a Home Assistant dependency. Its files and Node dependencies are excluded
from the allowlisted HACS ZIP. Production and upstream Core are not modified by
installing or validating it.

## Setup and commands

Use this repository's root, not an older checkout or the workspace's parent
proof-of-concept repository. Requires Node.js 20.19.0 or newer. The lockfile pins
OpenSpec 1.14.3 and its dependencies.

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm run specs:check
npm run specs:list
npm run specs -- list
npm run specs -- status --change validate-updated-core-handoff
```

The wrapper disables telemetry and update checks and keeps CLI configuration in
ignored `node_modules/.cache/nuheat-openspec`. It does not install a global CLI or
change other projects' OpenSpec settings. Installation runs no dependency lifecycle
scripts. Review package/lockfile changes when deliberately upgrading the tool.

Codex workflows are already generated in `.agents/skills/`. Reopen this repository
in Codex if new skills are not yet visible. To regenerate the pinned defaults:

```sh
npm run specs:setup
```

In Codex desktop, select a workflow in Skills; other Codex clients can use
`$openspec-explore`, `$openspec-propose`, and `$openspec-apply-change`. Generated
instructions use the bare `openspec` command: run the equivalent through
`npm run specs -- <arguments>` in this project so it uses the pinned local tool
and privacy settings. Your existing global OpenSpec CLI remains available. The npm scripts pin the
project version for reproducible local and CI runs without changing global settings.

## Source of truth and workflow

- `openspec/specs/` records current behavior, including limits. It is not a promise
  that a proposal is already shipped.
- `openspec/changes/<name>/` holds a proposal, behavioral deltas, technical design,
  and unchecked implementation/verification tasks.
- `openspec/config.yaml` supplies concise NuHeat constraints to the workflows.
- [SPEC_TRACEABILITY.md](SPEC_TRACEABILITY.md) maps contracts to current code,
  tests, evidence, and known gaps.

Start by reading the relevant baseline, implementation, and tests. Use explore
for an uncertain issue and propose for a concrete change. Review observable
behavior and failure handling before applying a plan. Pair code changes with
regression tests and user documentation, then verify the implementation before
syncing specifications and archiving the completed change.

The OpenSpec skills guide planning and implementation; they do not independently
authorize production access, thermostat commands, pushes, releases, or allowlist
changes. Follow the user's current scope. Core ports use Core's own repository
instructions and human-review policy; do not add these project workflows to the
upstream Core PR or copy community OAuth registration values into it.

## Verification

Maintenance configuration contracts run with
`python -m pytest -q tests/test_maintenance_automation.py` and require no account
or network access. They cover dependency-update boundaries and HACS workflow
permissions, events and exact-candidate selection. See
[maintenance automation](MAINTAINING.md#maintenance-automation) for bot review,
coordinated manual pin updates, HACS triage and the deferred CodeQL assessment.
Keep npm package/lock changes together and review generated OpenSpec skills
separately when changing the pinned tool. Workflow-only checks never authorize
production access, hardware commands or publication.

Supported maintainer commands:

| Command | Purpose | Side effects |
| --- | --- | --- |
| `python tools/package.py` | Validate and build an allowlisted local candidate | Writes local artifacts; never publishes |
| `python tools/verify_release.py --help` | Verify a selected public release | Public reads and JSON stdout only |
| `python tools/privacy_check.py --help` | Audit an explicit Git view and selected ZIPs | Local reads and count-only JSON stdout |
| `npm run specs:check` | Validate OpenSpec structure | No HA/runtime changes |

See [maintaining](MAINTAINING.md) for complete release-verification and privacy
examples, exit codes, required tools and limitations. Synthetic maintainer tests
run with `python -m pytest -q tests/test_verify_release.py tests/test_privacy_check.py tests/test_historical_tools.py`.
No accounts, network, thermostat or private baseline is required for those tests.

`adapt_stable.py`, `transition.py` and `core_handoff.py` at their original tool
paths are now explanatory stubs. Their former implementations are preserved as
inert [historical references](../tools/historical/README.md); ordinary invocation
does not rewrite source or run transition processes. The historical privacy
implementation is preserved there too. Earlier validation notes retain their
original command descriptions as historical evidence. Use the active Core
handoff proposal for new transition work and never claim old fixtures prove
official Cloud linking is deployed or current Core source is eligible.

`npm run specs:check` runs strict structural validation for all current specs and
active changes. The specification GitHub workflow runs the same command from a
clean npm install. A valid document or artifact status of "done" means its shape
or file exists; it does not prove the behavior is implemented or its tasks passed.

For runtime changes, use the existing isolated HA suite and packaging checks:

```sh
python -m pytest -q
ruff check custom_components tests tools
python tools/package.py
```

Use the project's Python environment and test dependency pins. Check release
packaging only in the user's authorized release scope. No live hardware is
required just to validate specs. Record synthetic tests, vendor authorization,
hardware observations, production observations, and unverified claims separately.
Never store real accounts, serial numbers, tokens, or callback URLs in OpenSpec
artifacts or examples. The npm tooling does not authorize publication of secrets.

## Refinement records

1. [Bounded mode confirmation and accepted-target preservation](../openspec/changes/archive/2026-10-23-confirm-mode-changes/proposal.md):
   completed and archived after b9 publication. The baseline specs include bounded
   confirmation, expiring Standby assumptions and preservation of accepted targets
   during rapid control changes. The Core port is in PR #176586. Archived validation
   records retain their original testing scope and limits.
2. [Updated Core handoff validation](../openspec/changes/validate-updated-core-handoff/proposal.md):
   prove identity, OAuth, action, hold, and recovery compatibility before a separate
   allowlist update. Isolated checks are recorded in the change's investigation;
   automatic retirement/restart and eligibility remain pending.

Task checklists distinguish completed local validation from pending Core and handoff work.

## Tool attribution

OpenSpec is provided by [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
under the MIT license. Generated skills retain their upstream MIT metadata. NuHeat's
own license and runtime dependency contract are unchanged.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for PR scope and proportionate checks,
and [MAINTAINING.md](MAINTAINING.md) for triage, label provisioning and release/promotion.
