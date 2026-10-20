"""Verify the beta uses HA's persistent credential provider for Core handoff."""

from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.helpers.config_entry_oauth2_flow import (
    LocalOAuth2ImplementationWithPkce,
    async_get_implementations,
)
from homeassistant.setup import async_setup_component

from custom_components.nuheat import async_setup
from custom_components.nuheat.const import DOMAIN


async def test_missing_registration_is_not_embedded_or_invented(hass):
    assert await async_setup_component(hass, DOMAIN, {})
    first = await async_get_implementations(hass, DOMAIN)
    assert not first
    assert await async_setup(hass, {})
    second = await async_get_implementations(hass, DOMAIN)
    assert not second


async def test_existing_application_credentials_are_retained(hass):
    assert await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential("synthetic-existing-client", "synthetic-existing-secret"),
        auth_domain="synthetic-existing-provider",
    )
    assert await async_setup_component(hass, DOMAIN, {})
    providers = await async_get_implementations(hass, DOMAIN)
    assert list(providers) == ["synthetic-existing-provider"]
    assert isinstance(
        providers["synthetic-existing-provider"], LocalOAuth2ImplementationWithPkce
    )
