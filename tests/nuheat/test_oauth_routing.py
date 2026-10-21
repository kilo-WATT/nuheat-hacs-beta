"""Reproduce community authorization routing without contacting NuHeat."""

from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest
from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.helpers import http
from homeassistant.helpers.config_entry_oauth2_flow import (
    async_get_implementations,
    _decode_jwt,
)
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nuheat.const import DOMAIN, AUTHORIZE_URL, OAUTH_SCOPES

pytest_plugins = []


@pytest.fixture(autouse=True)
def synthetic_client(monkeypatch):
    from custom_components.nuheat import community_oauth

    monkeypatch.setattr(community_oauth, "CLIENT_ID", "synthetic-community-client")
    monkeypatch.setattr(community_oauth, "CLIENT_SECRET", "synthetic-community-secret")


@pytest.mark.parametrize("my_enabled", [False, True])
async def test_community_callback_is_registered_with_or_without_my(hass, my_enabled):
    if my_enabled:
        hass.config.components.add("my")
    assert await async_setup_component(hass, DOMAIN, {})
    provider = (await async_get_implementations(hass, DOMAIN))[DOMAIN]
    with patch.object(http, "current_request") as request:
        request.get.return_value = SimpleNamespace(
            headers={"HA-Frontend-Base": "https://ha.example.invalid"}
        )
        query = parse_qs(
            urlparse(
                await provider.async_generate_authorize_url("synthetic-flow")
            ).query
        )
    assert query["redirect_uri"] == ["https://my.home-assistant.io/redirect/oauth"]
    assert query["code_challenge_method"] == ["S256"]
    assert len(provider.code_verifier) == 128
    state = _decode_jwt(hass, query["state"][0])
    assert state["redirect_uri"] == query["redirect_uri"][0]
    assert state["flow_id"] == "synthetic-flow"
    with patch.object(
        provider, "_token_request", return_value={"access_token": "synthetic-token"}
    ) as token_request:
        await provider.async_resolve_external_data(
            {"code": "synthetic-code", "state": state}
        )
    assert token_request.call_args.args[0]["redirect_uri"] == query["redirect_uri"][0]
    assert token_request.call_args.args[0]["code_verifier"] == provider.code_verifier


@pytest.mark.parametrize("old_domain", [DOMAIN, "synthetic-stale-provider"])
@pytest.mark.parametrize("source", ["user", "reauth"])
@pytest.mark.parametrize("choose_custom", [False, True])
async def test_fresh_and_legacy_flows_allow_each_stored_provider(
    hass, old_domain, source, choose_custom
):
    hass.config.components.add("my")
    assert await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential(
            "synthetic-stale-client", "synthetic-stale-secret", "My custom application"
        ),
        auth_domain=old_domain,
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Synthetic thermostat",
        version=1,
        data={
            "username": "synthetic-user",
            "password": "synthetic-password",
            "serial_number": "SYNTHETIC",
        },
    )
    entry.add_to_hass(hass)
    before = dict(entry.data)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": source, "entry_id": entry.entry_id},
        data=entry.data if source == "reauth" else None,
    )
    if source == "reauth":
        assert result["step_id"] == "migration_confirm"
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["step_id"] == "pick_implementation"
    providers = await async_get_implementations(hass, DOMAIN)
    community_key = next(
        key
        for key, value in providers.items()
        if value.client_id == "synthetic-community-client"
    )
    assert providers[community_key].name == "NuHeat community beta"
    assert providers[old_domain].name == "My custom application"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"implementation": old_domain if choose_custom else community_key},
    )
    assert result["type"] == "external"
    parsed = urlparse(result["url"])
    query = parse_qs(parsed.query)
    assert parsed.scheme + "://" + parsed.netloc + parsed.path == AUTHORIZE_URL
    assert query["client_id"] == [
        "synthetic-stale-client" if choose_custom else "synthetic-community-client"
    ]
    assert query["redirect_uri"] == ["https://my.home-assistant.io/redirect/oauth"]
    assert query["scope"][0].split() == list(OAUTH_SCOPES)
    providers = await async_get_implementations(hass, DOMAIN)
    assert providers[old_domain].client_id == "synthetic-stale-client"
    assert entry.data == before
    assert hass.config_entries.async_get_entry(entry.entry_id) is entry


async def test_oauth_reauth_keeps_explicit_custom_provider(hass):
    """A working custom registration is not silently replaced during reauth."""
    hass.config.components.add("my")
    assert await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential("synthetic-custom-client", "synthetic-custom-secret"),
        auth_domain="synthetic-custom",
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Synthetic account",
        version=2,
        data={
            "auth_implementation": "synthetic-custom",
            "token": {"access_token": "synthetic-token"},
        },
        unique_id="synthetic-subject",
    )
    entry.add_to_hass(hass)
    before = dict(entry.data)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "reauth", "entry_id": entry.entry_id},
        data=entry.data,
    )
    assert result["step_id"] == "reauth_confirm"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert parse_qs(urlparse(result["url"]).query)["client_id"] == [
        "synthetic-custom-client"
    ]
    assert entry.data == before
    providers = await async_get_implementations(hass, DOMAIN)
    custom = providers["synthetic-custom"]
    assert custom.client_secret == "synthetic-custom-secret"
    hass.config.components.remove("my")
    with patch.object(http, "current_request") as request:
        request.get.return_value = SimpleNamespace(
            headers={"HA-Frontend-Base": "https://ha.example.invalid"}
        )
        assert (
            custom.redirect_uri == "https://ha.example.invalid/auth/external/callback"
        )


async def test_existing_community_provider_is_reused(hass):
    """Repeated startup preserves provider keys used by persisted OAuth entries."""
    from custom_components.nuheat import async_setup

    assert await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential("synthetic-community-client", "synthetic-community-secret"),
        auth_domain="synthetic-persisted-community",
    )
    assert await async_setup_component(hass, DOMAIN, {})
    assert await async_setup(hass, {})
    providers = await async_get_implementations(hass, DOMAIN)
    assert list(providers) == ["synthetic-persisted-community"]
    assert (
        providers["synthetic-persisted-community"].redirect_uri
        == "https://my.home-assistant.io/redirect/oauth"
    )


async def test_existing_community_oauth_reauth_without_my_is_explicit(hass):
    """Existing OAuth tokens and provider identity survive opening corrected auth."""
    from homeassistant.helpers.config_entry_oauth2_flow import (
        async_get_config_entry_implementation,
    )

    assert await async_setup_component(hass, DOMAIN, {})
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Synthetic account",
        version=2,
        data={
            "auth_implementation": DOMAIN,
            "token": {
                "access_token": "synthetic-token",
                "refresh_token": "synthetic-refresh",
            },
        },
        unique_id="synthetic-subject",
    )
    entry.add_to_hass(hass)
    before = dict(entry.data)
    provider = await async_get_config_entry_implementation(hass, entry)
    assert provider.client_id == "synthetic-community-client"
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "reauth", "entry_id": entry.entry_id},
        data=entry.data,
    )
    assert result["step_id"] == "reauth_confirm"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] == "abort"
    assert result["reason"] == "my_required"
    assert entry.data == before
    assert entry.unique_id == "synthetic-subject"
    assert entry.entry_id in {
        item.entry_id for item in hass.config_entries.async_entries(DOMAIN)
    }


@pytest.mark.parametrize("source", ["user", "reauth"])
async def test_community_without_my_aborts_before_vendor_redirect(hass, source):
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Synthetic thermostat",
        version=1,
        data={
            "username": "synthetic-user",
            "password": "synthetic-password",
            "serial_number": "SYNTHETIC",
        },
    )
    entry.add_to_hass(hass)
    before = dict(entry.data)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": source, "entry_id": entry.entry_id},
        data=entry.data if source == "reauth" else None,
    )
    if source == "reauth":
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] == "abort"
    assert result["reason"] == "my_required"
    assert "my" not in hass.config.components
    assert entry.data == before
    assert hass.config_entries.async_get_entry(entry.entry_id) is entry


async def test_custom_client_can_authorize_without_my(hass):
    """A user-owned application with a direct callback needs no My dependency."""
    assert await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential(
            "synthetic-custom-client",
            "synthetic-custom-secret",
            "My custom application",
        ),
        auth_domain="synthetic-custom",
    )
    with patch.object(http, "current_request") as request:
        request.get.return_value = SimpleNamespace(
            headers={"HA-Frontend-Base": "https://ha.example.invalid"}
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert result["step_id"] == "pick_implementation"
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"implementation": "synthetic-custom"}
        )
    query = parse_qs(urlparse(result["url"]).query)
    assert query["client_id"] == ["synthetic-custom-client"]
    assert query["redirect_uri"] == [
        "https://ha.example.invalid/auth/external/callback"
    ]
    assert "my" not in hass.config.components
