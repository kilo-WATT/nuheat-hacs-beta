# Contributing to NuHeat Beta

For installation or login help, use the [README](README.md) or
[issue chooser](https://github.com/kilo-WATT/nuheat-hacs-beta/issues/new/choose).
You do not need Node.js or OpenSpec to use the integration or report a problem.
All public reports and attachments must omit account identifiers, passwords,
tokens, OAuth secrets, authorization headers, serial numbers, callback URLs,
backups and private `.storage` files. Sanitized logs are optional.

## Before changing behavior

Check existing issues and [OpenSpec changes](openspec/changes). Connect an issue
to an existing change when one applies. For a feature, nontrivial refactor or
behavior fix, agree on the behavior and failure cases before implementing it.
Use the propose -> implement -> verify -> sync/archive workflow described in
[DEVELOPMENT.md](docs/DEVELOPMENT.md). A typo or small documentation correction
needs proportionate content/link checks, not a new behavior proposal.

Keep the `nuheat` domain, existing entries, unique IDs, device/entity associations,
OAuth provider choices, migration rollback and exact-source Core handoff guards.
Never ask users to delete/recreate entries as a routine workaround. Do not copy
the beta's community OAuth registration into Core, SDK code, tests or examples.
Use synthetic thermostat identifiers and credentials in tests.

## Local setup and checks

Follow [the existing development setup](docs/DEVELOPMENT.md#setup-and-commands)
and [verification commands](docs/DEVELOPMENT.md#verification). Use a Python 3.14
virtual environment with `requirements-test.txt`; install its pins with
`python -m pip install -r requirements-test.txt`. Keep the environment outside
tracked files. Node/OpenSpec is development-only, and `npm ci --ignore-scripts
--no-audit --no-fund` installs the pinned tooling when needed.

For runtime changes, run the relevant isolated HA tests, Ruff and packaging checks.
Controls need coverage for stale responses, failed/uncertain writes, rapid and
concurrent commands, deadlines, unload, units and expiry as applicable. Distinguish
accepted/assumed state from confirmed API state. No maintainer account, production
HA or live thermostat is needed for the synthetic suite. Hardware commands and
production operations require their own explicit authorization.

For templates and documentation, check YAML/form structure, links, wording,
applicable OpenSpec deltas and packaging boundaries. A full runtime test run or
hardware test is not required just to change prose. Do not add tests that merely
mirror text. State what was actually checked and what remains unverified.

## Branches and pull requests

Use a descriptive `codex/<purpose>` branch for ordinary changes. Release
preparation follows `codex/release-prep-vVERSION`; keep an existing workstream's
branch name rather than repeatedly renaming it. Do not edit tags or publish a
release as part of an ordinary fix. Include a related issue and applicable
OpenSpec change in the PR, describe user-visible behavior, and record the exact
checks and limitations using the [PR template](.github/PULL_REQUEST_TEMPLATE.md).

Core PR #176586 lives in a separate repository and framework. Preserve its native
temperature properties, lifecycle/service APIs and accepted-target handling;
port tested behavior deliberately rather than copying whole beta files. Follow
Core's repository instructions and review policy. A beta fix does not authorize
a Core push or an automatic handoff allowlist update.

See [MAINTAINING.md](docs/MAINTAINING.md) for labels, triage and release/promotion
checks. Follow the [Apache-2.0 license](LICENSE.md) and preserve attribution.
