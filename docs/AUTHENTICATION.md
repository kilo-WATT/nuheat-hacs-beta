# OAuth investigation

Checked 2026-10-19 (America/New_York). OAuth client secrets are not included in
this distribution. User passwords, account tokens and private identifiers are
also excluded. No credential values have been printed or permission-request
messages sent to third parties.

Sources:
- https://github.com/SmilesGalore/HA-Nuheat-Conductor
- https://github.com/SmilesGalore/HA-Nuheat-Conductor/blob/main/custom_components/nuheat_conductor/config_flow.py
- https://identity.nam.mynuheat.com/.well-known/openid-configuration
- https://github.com/home-assistant/core/pull/176586

The public SmilesGalore config flow references client credentials and uses
LocalOAuth2Implementation. A source scan found no code_challenge, code_verifier,
or WithPkce usage in that file. This does not establish PKCE is prohibited;
it establishes that this implementation provides no evidence it was tested.

Chemelex's discovery document advertises S256 and plain code challenges,
authorization_code, and refresh_token. These are server capabilities and do not
prove a particular registered client's grant, scopes or callback permissions.
The beta retains HA's LocalOAuth2ImplementationWithPkce with a 128-character
verifier. A mocked S256 test can verify the client implementation, but live
code exchange and refresh rotation still require authorized registration.

The user reports that Chemelex approved sharing this specific community OAuth
client through a private message from its representative. The user authorizes
reuse and distribution for this beta. That report is accepted as authorization;
the private message has not been independently inspected. No private message
or personal contact details will be included in the distribution.

The distribution nevertheless keeps the client secret out of GitHub. Configure
the approved client once through HA's Application Credentials UI. It persists
across beta upgrades and the tested Core handoff. A public embedded client is
not required for migration preservation. The intentionally published registration
is in the author's [source](https://github.com/SmilesGalore/HA-Nuheat-Conductor/blob/main/custom_components/nuheat_conductor/const.py);
use only a registration you are authorized to use. Do not paste it into issues.

The public `community_oauth.py` file has blank values and therefore has no
effect by default. It is provided only as a local-build template: if an
authorized maintainer supplies both values in their own checkout, setup imports
them into HA's standard credential store when none exists. That edit is local,
is overwritten by HACS updates, and must never be committed or attached to an
issue.

SmilesGalore also publicly describes the credentials as intentionally provided
for community use in issue #3. That corroborates the author's intended use,
while the user's report supplies the vendor permission. Live callback, S256
PKCE, requested scopes (`openid openapi offline_access`) and refresh rotation
still require validation. This beta-only shared registration must not be added
to the Core PR or standalone API library.

Live checks passed consent, state validation, exchange with the matching
verifier, rejection of the wrong verifier, API reads, refresh-token replacement
and post-restart refresh. See VALIDATION.md for sanitized outcomes. Codes,
account tokens and private callback data remain outside the beta repository.
