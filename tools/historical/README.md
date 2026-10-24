# Historical maintainer tools

These files preserve the original preparation helpers from the b10 source tree
for inspection. Their old implementations are inside `_historical_reference`,
which is never called by import, help or normal invocation. They are not a
supported way to modify the current checkout or validate a future Core release.
The original three command paths now explain this boundary and exit nonzero.

`source-manifest.json` records the original b10 commit, original byte hashes and
AST fingerprints. Tests compare the preserved function bodies with those semantic
fingerprints without depending on Git history being available in a shallow clone.

- `adapt_stable.py`: one-time native-temperature property/test adaptation. The
  former top-level body rewrote source at import time. Do not reapply it to
  working integration code.
- `transition.py`: historical seed/beta/restart/candidate process orchestration.
  Its archived expected-failure/framework assumptions are not the current
  official-provider transition contract.
- `core_handoff.py`: expected one historical Core source SHA and a specific
  `.venv` layout. A new Core revision requires the active handoff plan and its
  matching framework. Do not weaken the runtime allowlist to make this run.
- `privacy_check.py`: earlier secret-free policy, including rejection of the
  shared registration. It does not represent the current release policy.

Old evidence remains unchanged. Existing persistence tests also remain intact;
their historical command hint is not a claim that this tool validates b10's
future official Cloud handoff. No supported current transition runner is added
by this cleanup.

See [development](../../docs/DEVELOPMENT.md) and
[maintaining](../../docs/MAINTAINING.md) for supported commands. The supported
privacy audit is `tools/privacy_check.py`, not this reference. Release checking
is `tools/verify_release.py`; local packaging is `tools/package.py`.
