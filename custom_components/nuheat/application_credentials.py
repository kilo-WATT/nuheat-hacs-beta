"""Local Application Credentials fallback for NuHeat development."""

from homeassistant.components.application_credentials import ClientCredential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    MY_AUTH_CALLBACK_PATH,
    AbstractOAuth2Implementation,
    LocalOAuth2ImplementationWithPkce,
)

from .const import AUTHORIZE_URL, TOKEN_URL


class NamedOAuth2Implementation(LocalOAuth2ImplementationWithPkce):
    """Keep stored Application Credentials recognizable in the provider picker."""

    credential_name: str = "Local application credentials"

    @property
    def name(self) -> str:
        """Return the stored application name."""
        return self.credential_name


class CommunityOAuth2Implementation(NamedOAuth2Implementation):
    """Use the callback registered for the shared community application."""

    @property
    def redirect_uri(self) -> str:
        """Avoid HA's instance-specific fallback when My Home Assistant is absent."""
        return MY_AUTH_CALLBACK_PATH


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> AbstractOAuth2Implementation:
    """Return the user-supplied NuHeat OAuth implementation."""
    from .community_oauth import CLIENT_ID

    implementation = (
        CommunityOAuth2Implementation
        if CLIENT_ID and credential.client_id == CLIENT_ID
        else NamedOAuth2Implementation
    )
    provider = implementation(
        hass,
        auth_domain,
        credential.client_id,
        authorize_url=AUTHORIZE_URL,
        token_url=TOKEN_URL,
        client_secret=credential.client_secret,
        code_verifier_length=128,
    )
    provider.credential_name = (
        "NuHeat community beta"
        if isinstance(provider, CommunityOAuth2Implementation)
        else credential.name or "Local application credentials"
    )
    return provider


async def async_get_description_placeholders(
    hass: HomeAssistant,
) -> dict[str, str]:
    """Describe where users obtain legitimate application credentials."""
    return {"docs_url": "https://api.nam.mynuheat.com/"}
