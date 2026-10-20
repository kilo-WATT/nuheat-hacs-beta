"""Register the beta client before startup or an OAuth setup flow needs it."""

from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    ImplementationUnavailableError,
    async_get_implementations,
)

from .const import DOMAIN


async def async_ensure_community_credentials(hass: HomeAssistant) -> None:
    """Preserve existing providers and import the beta client only when absent."""
    from .community_oauth import CLIENT_ID, CLIENT_SECRET

    if not CLIENT_ID or not CLIENT_SECRET:
        return
    try:
        implementations = await async_get_implementations(hass, DOMAIN)
    except ImplementationUnavailableError:
        return
    if not implementations:
        await async_import_client_credential(
            hass,
            DOMAIN,
            ClientCredential(CLIENT_ID, CLIENT_SECRET, "NuHeat community beta"),
            auth_domain=DOMAIN,
        )
