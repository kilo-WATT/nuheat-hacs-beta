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


async def async_ensure_community_credentials(hass: HomeAssistant) -> str | None:
    """Ensure the community provider without replacing any stored credentials."""
    from .community_oauth import CLIENT_ID, CLIENT_SECRET

    if not CLIENT_ID or not CLIENT_SECRET:
        return
    try:
        implementations = await async_get_implementations(hass, DOMAIN)
    except ImplementationUnavailableError:
        return
    for auth_domain, implementation in implementations.items():
        if getattr(implementation, "client_id", None) == CLIENT_ID:
            return auth_domain

    auth_domain = DOMAIN
    while auth_domain in implementations:
        auth_domain += "_community"
    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential(CLIENT_ID, CLIENT_SECRET, "NuHeat community beta"),
        auth_domain=auth_domain,
    )
    return auth_domain
