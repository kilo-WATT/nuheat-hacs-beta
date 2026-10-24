"""Allowlisted diagnostics from cached NuHeat state only."""

from importlib.metadata import PackageNotFoundError, version
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from . import NuHeatConfigEntry
from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: NuHeatConfigEntry
) -> dict[str, Any]:
    """Describe local health without serializing entries, models or exceptions."""
    integration = await async_get_integration(hass, DOMAIN)
    try:
        sdk_version = await hass.async_add_executor_job(version, "chemelex-nuheat")
    except PackageNotFoundError:
        sdk_version = None

    result: dict[str, Any] = {
        "versions": {"integration": integration.version, "sdk": sdk_version},
        "entry_state": entry.state.value,
        "runtime": None,
    }
    if (runtime := getattr(entry, "runtime_data", None)) is None:
        return result

    coordinator = runtime.coordinator
    result["runtime"] = {
        "availability": {
            "last_update_success": coordinator.last_update_success,
            "known_devices": len(coordinator.data or {}),
            "available_devices": sum(
                coordinator.is_thermostat_available(serial)
                for serial in coordinator.data or {}
            ),
        },
        "cooldown_active": coordinator.cooldown_remaining > 0,
        "confirmation": {
            "pending_targets": len(coordinator._pending_setpoints),
            "pending_modes": len(coordinator._pending_modes),
            "pending_expiries": sum(
                pending.hold_until is not None
                for pending in coordinator._pending_setpoints.values()
            ),
        },
    }
    return result
