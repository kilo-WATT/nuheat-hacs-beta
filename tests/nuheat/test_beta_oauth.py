"""Exercise actual HA PKCE request construction with synthetic credentials."""

import base64
import hashlib

import pytest
from homeassistant.components.application_credentials import ClientCredential

from custom_components.nuheat.application_credentials import (
    async_get_auth_implementation,
)
from custom_components.nuheat.const import DOMAIN, TOKEN_URL


@pytest.mark.parametrize("secret", ["", "synthetic-client-secret"])
async def test_s256_code_exchange(hass, aioclient_mock, secret):
    """Public and confidential registrations send the matching verifier."""
    implementation = await async_get_auth_implementation(
        hass, DOMAIN, ClientCredential("synthetic-client-id", secret)
    )
    verifier = implementation.extra_token_resolve_data["code_verifier"]
    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )
    assert len(verifier) == 128
    assert implementation.extra_authorize_data == {
        "code_challenge": expected,
        "code_challenge_method": "S256",
    }
    token = {
        "access_token": "synthetic-access",
        "refresh_token": "synthetic-refresh",
        "expires_in": 3600,
    }
    aioclient_mock.post(TOKEN_URL, json=token)
    assert (
        await implementation.async_resolve_external_data(
            {
                "code": "synthetic-code",
                "state": {"redirect_uri": "https://example.com/auth/external/callback"},
            }
        )
        == token
    )
    sent = aioclient_mock.mock_calls[0][2]
    assert sent["code_verifier"] == verifier
    assert sent["grant_type"] == "authorization_code"
    assert sent["client_id"] == "synthetic-client-id"
    assert sent.get("client_secret", "") == secret
