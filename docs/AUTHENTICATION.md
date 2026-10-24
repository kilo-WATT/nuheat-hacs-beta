# Authentication in beta 0.1.0b7

OAuth behavior is unchanged from v0.1.0b6. v0.1.0b7 is a regular GitHub release, visible by default in HACS.
Explicitly select its tag; beta visibility is not required.

This unofficial beta intentionally includes the temporary shared community OAuth
registration in `community_oauth.py`. Version v0.1.0b6 ensures that client is
registered alongside existing NuHeat Application Credentials without overwriting
them. Multiple providers are offered by name during fresh/legacy setup; existing
OAuth entries retain their provider. Users choosing community credentials do not
need to register a developer application or enter client credentials.
Community sign-in requires `my`; enable `my:` and restart HA if not using
`default_config:`. Custom clients keep HA's standard callback selection.

The unchanged v0.1.0b3 tag only runs this bootstrap during integration startup.
Opening setup first can report missing credentials. Existing users can enable
their existing entry and restart before reconnecting. The published v0.1.0b4 release
also registers the client before the setup flow checks for providers;
fresh installs should use v0.1.0b5 or a newer published release. v0.1.0b5 is a
regular GitHub release and does not require beta visibility in HACS. Select the
release tag rather than `main`, and verify that
HACS's installed version displays that tag. See the README for branch-to-release
instructions that retain existing NuHeat entries.

Each user still signs in to their own NuHeat account on Chemelex's login page.
The shared client registration is not an account password or a shared account
token. Each installation receives its own account authorization and stores its
access and refresh tokens locally in HA. Do not share those tokens, passwords,
authorization codes, callback URLs, backups or thermostat identifiers in issues.

## Login and callback

Use a desktop browser to reconnect the existing NuHeat entry. Mobile browsers
and the Home Assistant app can hand the link to the installed NuHeat phone app
and interrupt the return to HA. This was observed during production setup;
desktop authorization succeeded. Normal HA mobile use works after authorization.

The registered redirect is `https://my.home-assistant.io/redirect/oauth`.
My Home Assistant forwards the authorization result to the user's HA instance;
if prompted, select that instance's reachable URL, not a lab or example address.
No beta-operated OAuth relay or additional hosted service is used.

The beta uses HA's `LocalOAuth2ImplementationWithPkce`, S256 PKCE, a
128-character verifier, state validation and scopes `openid openapi offline_access`.
Live checks passed fresh authorization, matching-verifier exchange, rejection of
a deliberately incorrect verifier, API reads, refresh rotation and persistence
across restart. See [validation](VALIDATION.md) for the test boundaries.

## Permission and attribution

The registration comes from
[SmilesGalore's NuHeat Conductor integration](https://github.com/SmilesGalore/HA-Nuheat-Conductor).
The author explains its deliberate community use in
[issue #3](https://github.com/SmilesGalore/HA-Nuheat-Conductor/issues/3).
The beta maintainer reports Chemelex permission to share this registration via
a private Discord message. That report is accepted for this beta; the message
was not independently inspected and is not published. No independently verified
public vendor commitment or service-level guarantee is claimed.

The integration code is derived from
[Home Assistant Core PR #176586](https://github.com/home-assistant/core/pull/176586),
with exact source and community-client provenance in `provenance.json`.
The source projects use Apache-2.0; the license is included in this repository.
This beta's shared registration must not be copied into the Core PR or the
standalone API library.

## Confirmed properties and remaining risks

The client secret is intentionally public in this beta. It therefore cannot
serve as proof that a caller is a trusted installation. Possessing it alone
does not provide a user's thermostat authorization; the user still completes
OAuth, and the live test confirmed rejection of an incorrect PKCE verifier.

The confirmed operational dependency is one vendor-controlled registration for
all beta users. Revocation, rotation, callback changes or registration limits
could interrupt new logins or refreshes. Abuse, throttling and vendor revocation
are possible failure modes, not observed incidents from this audit. There is
no evidence here of account compromise. Shared-client permission does not
guarantee continued service or cover unrelated registrations.

Existing credentials and account tokens survive the tested Core-candidate
handoff. If the final official integration adopts a different client or Cloud
Account Linking, users may need to authorize the existing entry again. The
beta does not promise that account relinking will never be necessary.

## v0.1.0b6 authorization correction

Version v0.1.0b6 ensures community registration alongside stored clients,
requires `my` explicitly for community sign-in, and presents a provider picker when
custom credentials also exist. It does not load `my` automatically or override
legitimate custom applications. Without `default_config:`, enable `my:` in
`configuration.yaml`, restart HA, and retry the existing entry. These changes first appear in v0.1.0b6. See the
[reproductions, safeguards, and remaining tester questions](OAUTH_UNAUTHORIZED_CLIENT.md).


## Local unpublished permission-error handling

The API-resilience candidate distinguishes HTTP 403 (application permission)
from HTTP 401 (authorization). A 403 does not force token refresh, delete stored
credentials or switch providers. Verify the application's endpoint permissions;
relinking the same application may not fix them. A required read or requested
Permanent Hold write still fails visibly; it never falls back to Manual.

If v2 reads work but optional v1 details are forbidden, the entity remains based
on v2 data. Manual/Permanent Hold can remain unresolved, and implicit temperature
changes requiring that distinction are refused. Do not recreate the thermostat.
Persistent 401 after the existing single refresh/retry still uses reauthentication.

Rate-limit errors ask users to wait, not relink. Timeout messages report uncertain
outcomes without exposing vendor response bodies or identifiers. Existing community
and custom provider associations, PKCE and migration identity checks are unchanged.
Future official Cloud relinking remains a separate, unimplemented transition.
