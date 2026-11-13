"""Native contract probes supplement real minimum-framework service tests."""

from datetime import UTC, datetime, timedelta
import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest
from homeassistant.components.climate import ClimateEntity, HVACMode
from homeassistant.const import UnitOfTemperature
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
from chemelex_nuheat import ScheduleMode

from custom_components.nuheat import climate
from .helpers import temperature_service
from .test_integration import add_entity_state, coordinator_with, thermostat


class NativeClimateContract(ClimateEntity):
    """Reject legacy integration access while probing the new native branch.

    This test contract is supplemental and does not represent a current HA
    installation. Actual matching-framework validation is tracked separately.
    """

    @property
    def native_temperature_unit(self):
        return self._attr_native_temperature_unit

    def __getattribute__(self, name):
        if name in {"temperature_unit", "current_temperature", "target_temperature"}:
            raise AssertionError("Deprecated temperature property accessed")
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name == "_attr_temperature_unit":
            raise AssertionError("Deprecated temperature attribute assigned")
        super().__setattr__(name, value)


@pytest.fixture
def native_entity_class():
    spec = importlib.util.spec_from_file_location(
        "custom_components.nuheat._native_contract", Path(climate.__file__)
    )
    module = importlib.util.module_from_spec(spec)
    with patch("homeassistant.components.climate.ClimateEntity", NativeClimateContract):
        spec.loader.exec_module(module)
    assert module.NATIVE_TEMPERATURE_API
    return module.NuHeatClimateEntity


@pytest.mark.parametrize("imperial", [False, True])
async def test_native_branch_avoids_legacy_access(hass, imperial, native_entity_class):
    if imperial:
        hass.config.units = US_CUSTOMARY_SYSTEM
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entity = native_entity_class(coordinator, "ABC123")
    entity.hass = hass
    assert entity.native_temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.native_current_temperature == 21.5
    assert entity.native_target_temperature == 23
    assert entity.min_temp == 5
    assert entity.max_temp == 35
    assert "current_temperature" not in native_entity_class.__dict__
    assert "target_temperature" not in native_entity_class.__dict__
    await entity.async_set_temperature(temperature=25)
    assert api.set_target_temperature.await_args.args == ("ABC123", 25)
    assert entity.native_target_temperature == 25
    end = (datetime.now(UTC) + timedelta(hours=2)).replace(second=0, microsecond=0)
    await entity.async_set_temporary_hold(77 if imperial else 25, end)
    api.set_target_temperature.assert_awaited_with(
        "ABC123", 25, mode=ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE, hold_until=end
    )
    assert entity.unique_id == "ABC123"
    await coordinator.async_shutdown()


@pytest.mark.parametrize("imperial", [False, True])
async def test_real_framework_display_units_and_step(hass, imperial):
    if imperial:
        hass.config.units = US_CUSTOMARY_SYSTEM
    coordinator, _, _ = await coordinator_with(hass, thermostat())
    entity = climate.NuHeatClimateEntity(coordinator, "ABC123")
    state = await add_entity_state(hass, entity, "climate.synthetic_native_units")
    assert state.attributes["current_temperature"] == (71 if imperial else 21.5)
    assert state.attributes["temperature"] == (73 if imperial else 23)
    assert state.attributes["min_temp"] == (41 if imperial else 5)
    assert state.attributes["max_temp"] == (95 if imperial else 35)
    assert state.attributes["target_temp_step"] == (1 if imperial else 0.5)
    await entity.async_will_remove_from_hass()
    await coordinator.async_shutdown()


@pytest.mark.parametrize("imperial", [False, True])
async def test_setup_state_and_controls_avoid_temperature_deprecations(
    hass, imperial, caplog
):
    if imperial:
        hass.config.units = US_CUSTOMARY_SYSTEM
    coordinator, _, _ = await coordinator_with(hass, thermostat())
    entity = climate.NuHeatClimateEntity(coordinator, "ABC123")
    await add_entity_state(hass, entity, "climate.synthetic_temperature_warnings")
    await temperature_service(hass, entity, 77 if imperial else 25)
    end = (datetime.now(UTC) + timedelta(hours=2)).replace(second=0, microsecond=0)
    await entity.async_set_temporary_hold(77 if imperial else 25, end)
    await entity.async_turn_off()
    await entity.async_set_hvac_mode(HVACMode.AUTO)
    entity.async_write_ha_state()
    assert not any(
        "deprecat" in record.getMessage().lower()
        and "temperature" in record.getMessage().lower()
        for record in caplog.records
    )
    await entity.async_will_remove_from_hass()
    await coordinator.async_shutdown()
