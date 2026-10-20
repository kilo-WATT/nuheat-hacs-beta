"""Run the PR tests against the custom component in isolated HA fixtures."""

import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture(autouse=True)
def custom_integrations(enable_custom_integrations):
    """Enable custom component discovery using the real HA loader."""
    yield
