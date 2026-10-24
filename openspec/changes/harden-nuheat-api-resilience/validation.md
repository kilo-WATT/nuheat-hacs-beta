# Local implementation validation

2026-10-24. Implemented under the user's `opsx:apply` authorization. No commits,
pushes, releases, hardware commands, production access or Core edits were made.

## Results

- SDK: 133 tests passed; Ruff lint/format and strict mypy passed.
- Beta: 343 tests passed, one existing skip, against the installed candidate
  wheel in an isolated HA 2026.10.2 environment. Ruff lint and formatting of all
  changed Python files passed. Both repositories passed `git diff --check`.
- Strict OpenSpec validation: ten items passed, none failed.
- Candidate ZIP: 29 entries, including 18 runtime files; every entry matches
  the working source. Dependency and provenance checks passed.
- SDK wheel source bytes match the working SDK, includes `py.typed`, and the
  source distribution includes the resilience and permanent-hold tests.
- Known private-data scan: 18 private values checked, no matches in 138 beta
  files and 17 SDK files or scanned beta ZIP contents. Values were not printed.
- Protected OAuth registration/provider, migration, account identity, behavior,
  Core handoff guard and allowlist files match their original Git bytes.
- Core remains clean at `9ab210660371eaf6bda2083a518cf15eea29318f`.
  Existing stable/Core environments still have SDK 0.1.2 installed.
- Release packaging rejects publication. No published tag or asset was changed.

## Local artifacts

- SDK `chemelex_nuheat-0.1.3.dev0-py3-none-any.whl`, SHA256
  `2211a95b54612d839ca175a8b2e655a9624cbb927ea2e30f527159436224dbea`.
- Beta `nuheat-0.1.0b9-UNRELEASED.zip`, SHA256
  `00dd0158d412d048a05141cb512aa68a87002f1bafc42d415f1d588010f731bf`.

The SDK development version is local only. The manifest/test pins deliberately
identify that candidate; release gates remain pending and publication disabled.
Publishing a supported SDK and selecting release versions require separate
authorization and fresh release validation.

## Scope and limits

Synthetic clocks/sessions cover permission failures, optional-v1 fallback,
persistent 401, rate-limit header variants, shared cooldown, stalled requests,
accepted writes with failed readback, lock deadlines, overlapping reads and
shutdown cancellation. Existing migration, identity, mode, unit and hold tests
also passed. No new real-hardware or vendor load measurements were performed.
The 15-second request, 30-second operation and 60-second fallback defaults are
tested budgets, not a measured vendor service guarantee.

Package verification caught formatting-only drift in the public registration
file; its exact original bytes were restored before final validation. That file
has no final diff. Final privacy scanning is scoped to known private values and
does not constitute a claim that an automated scan proves all data public.

See [Core alignment](core-alignment.md) for corresponding source/tests and
framework-specific port checks. The private coordinator refresh hooks need
verification against future HA versions. No Core implementation tests or GitHub
CI runs are claimed; all changes remain uncommitted locally.

## Subsequent authorized hardware validation — 2026-10-24

The user separately approved an immediate isolated test on their linked
thermostat, limited to six commands within ±0.5°C including restoration.
Fresh isolated OAuth authorization was completed; production HA was never read
or modified. The candidate SDK wheel and exact beta runtime files were used in
a throwaway HA instance with an enforced HTTP write budget and target bounds.

Result: passed. Four target PUTs and one schedule-restoration PUT were sent;
all returned HTTP 204. The original target, scheduled mode and absence
of hold were confirmed by cloud readback and the isolated HA entity.

- HA entity target updates took 0.2664, 0.2623, 0.7143 and 0.2611 seconds from
  service invocation. These measure entity state, not rendered dashboard pixels.
- Initial post-write API responses were genuinely stale for commands 1, 2 and
  restoration command 4. HA showed the accepted target despite those responses.
- For command 1, delayed reconciliation began 2.0022 seconds after optimism
  was published and confirmed the target 2.3750 seconds after service invocation.
- The rapid pair of changes started 0.9504 seconds apart. Both displayed their
  requested target; the last target was confirmed by delayed cloud readback.
- After restoration and unload, no extra observed reconciliation reads occurred
  during the 35-second cleanup observation.

Private raw evidence and the sanitized measurement summary remain outside this
repository under `nuheat-beta-private/setpoint-hardware-validation/`.
Rate limiting, permission failures, stalled requests and cancellation continue
to rely on synthetic regression coverage; none were induced against the vendor
or the live thermostat. No commits, pushes, releases or Core edits were made.

## Preparation branch publication

The subsequent user request authorizes committing and pushing the beta changes
on `codex/harden-nuheat-api-resilience`. Main, published releases, Core and
production remain outside that publication scope. The companion SDK source
remains local; its publication is a separate step.

This branch is for review, not HACS installation. Its 0.1.3.dev0 dependency was
validated from a locally built wheel. The standard GitHub integration-test job
installs dependencies from the package index and cannot pass while that SDK is
unpublished. This is a dependency-availability gate, not evidence that remote
integration tests passed. No test is skipped to conceal that gate.
