"""Exercise preset and temperature compatibility through HA service handlers."""

from datetime import UTC, datetime

from chemelex_nuheat import HoldUntilStatus, NuHeatApiError, ScheduleMode
import pytest

from homeassistant.components.climate import HVACMode
from homeassistant.components.climate.services import _async_service_temperature_set
from homeassistant.core import ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM

from custom_components.nuheat.behavior import api_mode_for_preset
from custom_components.nuheat.climate import NuHeatClimateEntity

from .test_integration import add_entity_state, coordinator_with, thermostat
from .test_permanent_hold import permanent

PRESETS = [
    ("Run Schedule", "run_schedule", ScheduleMode.AUTO),
    ("Temporary Hold", "temporary_hold", ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE),
    ("Permanent Hold", "permanent_hold", ScheduleMode.PERMANENT_HOLD),
]


@pytest.mark.parametrize(("canonical", "alias", "mode"), PRESETS)
@pytest.mark.parametrize("use_alias", [False, True])
async def test_preset_framework_accepts_all_six_and_reports_canonical(
    hass, canonical, alias, mode, use_alias
):
    coordinator, api, _ = await coordinator_with(hass, permanent(operating=2))
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await add_entity_state(hass, entity, "climate.synthetic_compatibility")
    api.list_thermostats.return_value = [
        {
            ScheduleMode.AUTO: thermostat(
                mode=1, hold_until=None, hold_until_status=HoldUntilStatus.NULL
            ),
            ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE: thermostat(),
            ScheduleMode.PERMANENT_HOLD: permanent(),
        }[mode]
    ]
    value = alias if use_alias else canonical
    assert api_mode_for_preset(value) is mode
    await entity.async_handle_set_preset_mode_service(value)
    expected = {} if mode is ScheduleMode.AUTO else {"temperature": 23}
    api.set_schedule_mode.assert_awaited_once_with("ABC123", mode, **expected)
    assert entity.preset_mode == canonical
    assert hass.states.get(entity.entity_id).attributes["preset_mode"] == canonical
    assert entity.unique_id == "ABC123"
    await entity.async_will_remove_from_hass()
    await coordinator.async_shutdown()


async def test_invalid_preset_framework_rejects_without_write(hass):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    with pytest.raises(ServiceValidationError):
        await entity.async_handle_set_preset_mode_service("Permanent hold")
    with pytest.raises(ValueError):
        api_mode_for_preset("Permanent hold")
    api.set_schedule_mode.assert_not_awaited()
    await coordinator.async_shutdown()


async def temperature_service(hass, entity, temperature):
    await _async_service_temperature_set(
        entity,
        ServiceCall(hass, "climate", "set_temperature", {"temperature": temperature}),
    )


@pytest.mark.parametrize("imperial", [False, True])
@pytest.mark.parametrize("target_c", [5, 35])
@pytest.mark.parametrize("initial", ["timed", "permanent", "manual", "scheduled"])
async def test_temperature_service_boundaries_preserve_intent(
    hass, imperial, target_c, initial
):
    if imperial:
        hass.config.units = US_CUSTOMARY_SYSTEM
    expiry = datetime(2027, 1, 1, tzinfo=UTC)
    value, mode = {
        "timed": (thermostat(hold_until=expiry), ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE),
        "permanent": (permanent(), ScheduleMode.PERMANENT_HOLD),
        "manual": (permanent(operating=2), ScheduleMode.MANUAL),
        "scheduled": (
            thermostat(mode=1, hold_until=None, hold_until_status=HoldUntilStatus.NULL),
            ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE,
        ),
    }[initial]
    coordinator, api, _ = await coordinator_with(hass, value)
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    target = target_c * 1.8 + 32 if imperial else target_c
    await temperature_service(hass, entity, target)
    expected = {"hold_until": expiry} if initial == "timed" else {}
    api.set_target_temperature.assert_awaited_once_with(
        "ABC123", target_c, mode=mode, **expected
    )
    api.set_standby.assert_not_awaited()
    assert entity.hvac_mode is not HVACMode.OFF
    assert entity.target_temperature == pytest.approx(target)
    await coordinator.async_shutdown()


@pytest.mark.parametrize("imperial", [False, True])
@pytest.mark.parametrize(
    "target_c", [4.9, 35.1, float("nan"), float("inf"), -float("inf")]
)
async def test_temperature_service_invalid_targets_never_write(
    hass, imperial, target_c
):
    if imperial:
        hass.config.units = US_CUSTOMARY_SYSTEM
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    target = target_c * 1.8 + 32 if imperial else target_c
    with pytest.raises(ServiceValidationError):
        await temperature_service(hass, entity, target)
    api.set_target_temperature.assert_not_awaited()
    api.set_standby.assert_not_awaited()
    await coordinator.async_shutdown()


@pytest.mark.parametrize("imperial", [False, True])
@pytest.mark.parametrize("target_c", [5, 35])
async def test_timed_hold_boundaries_and_rapid_change_keep_expiry(
    hass, freezer, imperial, target_c
):
    freezer.move_to("2026-10-29T12:00:00+00:00")
    if imperial:
        hass.config.units = US_CUSTOMARY_SYSTEM
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    expiry = datetime(2026, 10, 29, 14, tzinfo=UTC)
    target = target_c * 1.8 + 32 if imperial else target_c
    await entity.async_set_temporary_hold(target, expiry)
    await temperature_service(hass, entity, target)
    assert api.set_target_temperature.await_count == 2
    for call in api.set_target_temperature.await_args_list:
        assert call.args == ("ABC123", target_c)
        assert call.kwargs == {
            "mode": ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE,
            "hold_until": expiry,
        }
    api.set_standby.assert_not_awaited()
    await coordinator.async_shutdown()


async def test_vendor_rejection_at_lower_bound_does_not_substitute_or_assume(hass):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    api.set_target_temperature.side_effect = NuHeatApiError(
        "Synthetic device rejection"
    )
    with pytest.raises(NuHeatApiError):
        await temperature_service(hass, entity, 5)
    api.set_target_temperature.assert_awaited_once_with(
        "ABC123", 5, mode=ScheduleMode.PERMANENT_HOLD
    )
    api.set_standby.assert_not_awaited()
    api.set_schedule_mode.assert_not_awaited()
    assert entity.target_temperature == 23
    assert not entity.assumed_state
    await coordinator.async_shutdown()
