"""Complete OAuth through real isolated HTTP callbacks and token exchange."""

from urllib.parse import parse_qs, urlparse
from unittest.mock import AsyncMock, patch
import pytest
from aiohttp import web
from chemelex_nuheat import Account
from homeassistant.setup import async_setup_component
from homeassistant.helpers.config_entry_oauth2_flow import (
    LocalOAuth2ImplementationWithPkce,
)
from .helpers import jwt_access_token
from .test_integration import thermostat


@pytest.mark.parametrize("outcome", ["success", "denied"])
@pytest.mark.parametrize(
    ("client_kind", "my_enabled"),
    [("community", True), ("custom", True), ("custom", False)],
)
async def test_community_roundtrip_with_real_my(
    hass,
    hass_client_no_auth,
    aiohttp_server,
    socket_enabled,
    monkeypatch,
    outcome,
    client_kind,
    my_enabled,
):
    from custom_components.nuheat import community_oauth

    monkeypatch.setattr(community_oauth, "CLIENT_ID", "synthetic-community-client")
    monkeypatch.setattr(community_oauth, "CLIENT_SECRET", "synthetic-community-secret")
    if my_enabled:
        assert await async_setup_component(hass, "my", {})
        assert "_my_redirect" in hass.data["frontend_panels"]
    client_id = f"synthetic-{client_kind}-client"
    client_secret = f"synthetic-{client_kind}-secret"
    if client_kind == "custom":
        from homeassistant.components.application_credentials import (
            ClientCredential,
            async_import_client_credential,
        )

        assert await async_setup_component(hass, "application_credentials", {})
        await async_import_client_credential(
            hass,
            "nuheat",
            ClientCredential(client_id, client_secret, "My custom application"),
            auth_domain="synthetic-custom",
        )
    callback = (
        "https://my.home-assistant.io/redirect/oauth"
        if my_enabled
        else "https://ha.example.invalid/auth/external/callback"
    )
    seen = {}

    async def token(request):
        data = dict(await request.post())
        seen.update(data)
        assert data["code"] == "synthetic-code"
        assert data["client_id"] == client_id
        assert data["client_secret"] == client_secret
        assert data["redirect_uri"] == callback
        return web.json_response(
            {
                "access_token": jwt_access_token(),
                "refresh_token": "synthetic-refresh",
                "expires_in": 3600,
            }
        )

    app = web.Application()
    app.router.add_post("/token", token)
    vendor = await aiohttp_server(app)
    with (
        patch(
            "custom_components.nuheat.config_flow.NuHeatClient.get_account",
            AsyncMock(return_value=Account("Synthetic account")),
        ),
        patch(
            "custom_components.nuheat.config_flow.NuHeatClient.list_thermostats",
            AsyncMock(return_value=[thermostat()]),
        ),
    ):
        from types import SimpleNamespace
        from homeassistant.helpers import http

        with patch.object(http, "current_request") as request:
            request.get.return_value = SimpleNamespace(
                headers={"HA-Frontend-Base": "https://ha.example.invalid"}
            )
            result = await hass.config_entries.flow.async_init(
                "nuheat", context={"source": "user"}
            )
            if client_kind == "custom":
                assert result["step_id"] == "pick_implementation"
                result = await hass.config_entries.flow.async_configure(
                    result["flow_id"], {"implementation": "synthetic-custom"}
                )
        assert result["type"] == "external"
        flow = hass.config_entries.flow._progress[result["flow_id"]]
        provider = flow.flow_impl
        provider.token_url = str(vendor.make_url("/token"))
        query = parse_qs(urlparse(result["url"]).query)
        assert query["code_challenge"] == [
            LocalOAuth2ImplementationWithPkce.compute_code_challenge(
                provider.code_verifier
            )
        ]
        client = await hass_client_no_auth()
        params = {"state": query["state"][0]}
        params.update(
            {"code": "synthetic-code"}
            if outcome == "success"
            else {"error": "access_denied"}
        )
        response = await client.get("/auth/external/callback", params=params)
        assert response.status == 200
        result = await hass.config_entries.flow.async_configure(result["flow_id"])
    if outcome == "denied":
        assert result["type"] == "abort"
        assert result["reason"] == "user_rejected_authorize"
        assert not seen
        assert not hass.config_entries.async_entries("nuheat")
    else:
        assert result["type"] == "create_entry"
        assert result["result"].unique_id == "synthetic-account-subject"
        assert result["data"]["auth_implementation"] == (
            "nuheat" if client_kind == "community" else "synthetic-custom"
        )
        assert seen["code_verifier"] == provider.code_verifier
