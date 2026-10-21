"""Verify the beta uses HA's persistent credential provider for Core handoff."""

import pytest

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


@pytest.fixture(autouse=True)
def synthetic_community_client(monkeypatch, hass):
    """Exercise the bootstrap without using the distributed client values."""
    from custom_components.nuheat import community_oauth

    hass.config.components.add("my")
    monkeypatch.setattr(community_oauth, "CLIENT_ID", "synthetic-community-client")
    monkeypatch.setattr(community_oauth, "CLIENT_SECRET", "synthetic-community-secret")


@pytest.mark.parametrize(
    ("client_id", "client_secret"),
    [("", ""), ("synthetic-client", ""), ("", "synthetic-secret")],
)
async def test_incomplete_client_is_not_registered(
    hass, monkeypatch, client_id, client_secret
):
    from custom_components.nuheat import community_oauth

    monkeypatch.setattr(community_oauth, "CLIENT_ID", client_id)
    monkeypatch.setattr(community_oauth, "CLIENT_SECRET", client_secret)
    assert await async_setup_component(hass, DOMAIN, {})
    assert not await async_get_implementations(hass, DOMAIN)


async def test_local_community_registration_bootstraps_pkce(hass):
    """The community client registers PKCE and remains usable after setup repeats."""
    assert await async_setup_component(hass, DOMAIN, {})
    first = await async_get_implementations(hass, DOMAIN)
    assert list(first) == [DOMAIN]
    assert isinstance(first[DOMAIN], LocalOAuth2ImplementationWithPkce)
    assert await async_setup(hass, {})
    second = await async_get_implementations(hass, DOMAIN)
    assert list(second) == [DOMAIN]
    assert isinstance(second[DOMAIN], LocalOAuth2ImplementationWithPkce)


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
    assert set(providers) == {"synthetic-existing-provider", DOMAIN}
    assert (
        providers["synthetic-existing-provider"].client_id
        == "synthetic-existing-client"
    )
    assert isinstance(
        providers["synthetic-existing-provider"], LocalOAuth2ImplementationWithPkce
    )


async def test_first_flow_registers_client_before_domain_startup(hass):
    """A fresh install opens OAuth without requiring a loaded config entry."""
    assert DOMAIN not in hass.config.components
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    # The beta selects its registered community provider for a fresh flow.
    assert result["type"] == "external"
    assert result["step_id"] == "auth"
    providers = await async_get_implementations(hass, DOMAIN)
    assert isinstance(providers[DOMAIN], LocalOAuth2ImplementationWithPkce)
