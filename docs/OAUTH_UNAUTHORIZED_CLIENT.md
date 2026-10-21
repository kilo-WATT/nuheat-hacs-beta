# OAuth correction - v0.1.0b6

These changes are included in v0.1.0b6 and are absent from the unchanged
v0.1.0b5 tag. The maintainer approved publication after preparation CI passed.
Production HA and the upstream Core branch were untouched during this investigation.

## Confirmed request defects

In Home Assistant 2026.10.2, a local OAuth provider uses the registered My callback
when `my` is loaded, and otherwise derives a direct callback from the frontend URL.
Fresh setup and legacy reauthentication use the same request-generation path.
Older YAML installations can omit `my`/`default_config`; affected testers have not
yet confirmed this configuration difference.

Unauthenticated vendor probes kept endpoint, scopes, and valid S256 PKCE constant.
They sent no secret, account login, token, device identifier, or thermostat command:

| Request | Result before login |
| --- | --- |
| Community client + `https://my.home-assistant.io/redirect/oauth` | `/Account/Login` |
| Same request + synthetic direct HA callback | `unauthorized_client` |
| Synthetic invalid client + registered callback | `unauthorized_client` |

Synthetic HA tests also confirmed that any stored NuHeat Application Credentials
provider suppresses community import in v0.1.0b5. A stale client can therefore be
selected. Stored legacy username/password data is not Application Credentials and
does not itself suppress import. A custom application is not necessarily stale.

## My integration: full-path verification

The [HA documentation](https://www.home-assistant.io/integrations/my/) and
[My FAQ](https://my.home-assistant.io/faq/) require `my` for My links. The current
[My service source](https://github.com/home-assistant/my.home-assistant.io/blob/main/src/entrypoints/my-redirect.ts)
special-cases successful OAuth returns to `/auth/external/callback`, while its
Decline link still uses `/_my_redirect/oauth`, handled by the My frontend panel.
The deployed browser page showed those same routes.

A browser-assisted test through the real My service completed with `my` absent:
real HA callback/state validation, a real HTTP token exchange with a synthetic
vendor, PKCE verifier, account-subject checks, and entry creation passed. Account
and thermostat API responses were synthetic. This proves today's success path
works without `my`, not that every return/cancellation path is supported.

The final candidate explicitly requires `my` before opening community sign-in.
It explains how to enable `my:` and retry the existing entry; it does not silently
load components or edit configuration. Custom applications retain HA's normal
callback selection and can use a properly registered direct callback without `my`.

## Provider selection and preservation

Community registration is ensured alongside existing credentials, without
updating or deleting them. Existing community keys are reused; unrelated provider
key collisions receive a distinct persistent key. With multiple providers, fresh
and legacy flows show an explicit picker with stored application names and a
clear community label. Legitimate custom clients are not forced to community.
Existing OAuth entries retain their associated provider during reauthentication.

Community state and token exchange use the registered callback. Endpoints, scopes,
S256 PKCE, secrets, tokens, account matching, registry migration, setpoints, and the
handoff allowlist are unchanged. A stored community client with an incorrect
secret is not silently overwritten; that would affect token exchange, not the
reported pre-login rejection. An existing OAuth entry bound to an invalid custom
application needs diagnosis rather than automatic rebinding.

## End-to-end and regression results

On October 20, 2026, a live read-only test completed vendor consent, the deployed
My redirect, the final candidate's isolated HA callback, real PKCE token exchange,
account and thermostat API reads, and entry creation with the real `my` component
loaded. Zero thermostat writes and no production HA access occurred. No account
identifiers, authorization codes, secrets, or tokens are included here.
Earlier attempts stopped at test-harness DNS/socket restrictions; these were
resolved only within the private opt-in test process, without product workarounds.

Automated round trips cover success and denial with the real My component for
community/custom clients, and custom direct callbacks with My absent. Other tests
cover missing-My guidance before vendor redirect, fresh/legacy provider choices,
provider names and key retention, existing OAuth associations, migration/identity
preservation, and handoff safeguards. The full suite passed 208 tests with 1 skip; lint, changed-file formatting,
allowlisted packaging, and the known-private-value source/archive scan passed.

## Core compatibility and remaining confirmations

Provider keys and entries retain HA's standard Application Credentials format.
No shared registration is copied into Core. The beta-specific adapters do not
change arbitrary Core client registrations. The existing handoff allowlist stays
unchanged and rejects the updated Core setpoint source. Before extending it,
validate reauthentication and missing-My handling with the final Core provider.

Affected users should report only whether their redirect is the exact My callback
or a direct instance callback, whether `my`/`default_config` is enabled, whether
NuHeat Application Credentials exist, and whether this is legacy migration or an
OAuth reauthentication. Do not paste full URLs, secrets, tokens, storage, or serials.
Do not delete NuHeat entries. Testers still need to confirm corrected relinking
and unchanged entity IDs after approval to distribute a candidate.

No account restriction has been established. Chemelex confirmation is needed for
its definitive registration policy, or vendor logs if correct client/callback/
scope/PKCE requests still fail. Error references should be shared privately with
the vendor. Custom registrations cannot be verified against the vendor using
synthetic credentials; their selection and complete local round trips are tested.
