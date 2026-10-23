"""Three-preset behavior with explicit schedule details, separate from HVAC mode."""

from dataclasses import replace
import pytest
from chemelex_nuheat import (
    HoldUntilStatus,
    NuHeatApiError,
    ScheduleMode,
)
from homeassistant.components.climate import HVACMode
from custom_components.nuheat.climate import NuHeatClimateEntity
from custom_components.nuheat.const import (
    PRESET_PERMANENT_HOLD,
    PRESET_RUN,
    PRESET_TEMPORARY_HOLD,
)
from .test_integration import coordinator_with, thermostat, add_entity_state


def permanent(*, target=2300, operating=1):
    return replace(
        thermostat(
            mode=3,
            raw_target_temperature=target,
            hold_until=None,
            hold_until_status=HoldUntilStatus.NULL,
        ),
        operating_mode=operating,
        schedule_mode=3,
    )


async def test_preset_menu_and_app_driven_permanent_hold(hass):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await add_entity_state(hass, entity, "climate.synthetic_hold")
    assert entity.preset_modes == [
        PRESET_RUN,
        PRESET_TEMPORARY_HOLD,
        PRESET_PERMANENT_HOLD,
    ]
    assert entity.preset_mode == PRESET_PERMANENT_HOLD
    assert entity.hvac_mode is HVACMode.AUTO
    assert entity.unique_id == "ABC123"
    assert (
        hass.states.get(entity.entity_id).attributes["preset_mode"]
        == PRESET_PERMANENT_HOLD
    )
    await entity.async_will_remove_from_hass()
    await coordinator.async_shutdown()


async def test_select_permanent_hold_preserves_target(hass):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    api.list_thermostats.return_value = [permanent()]
    await entity.async_set_preset_mode(PRESET_PERMANENT_HOLD)
    api.set_schedule_mode.assert_awaited_once_with(
        "ABC123", ScheduleMode.PERMANENT_HOLD, temperature=23
    )
    assert entity.preset_mode == PRESET_PERMANENT_HOLD
    await coordinator.async_shutdown()


@pytest.mark.parametrize("imperial", [False, True])
async def test_setpoint_change_stays_permanent_and_is_optimistic(hass, imperial):
    if imperial:
        from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM

        hass.config.units = US_CUSTOMARY_SYSTEM
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    requested = 75.2 if imperial else 24
    await entity.async_set_temperature(temperature=requested)
    api.set_target_temperature.assert_awaited_once_with(
        "ABC123", 24, mode=ScheduleMode.PERMANENT_HOLD
    )
    assert entity.target_temperature == pytest.approx(requested)
    assert entity.assumed_state
    assert entity.preset_mode == PRESET_PERMANENT_HOLD
    await coordinator.async_shutdown()


@pytest.mark.parametrize(
    ("operating", "target", "mode", "preset"),
    [
        (2, 2300, HVACMode.HEAT, None),
        (2, 500, HVACMode.OFF, None),
        (1, 500, HVACMode.AUTO, PRESET_PERMANENT_HOLD),
    ],
)
async def test_manual_and_standby_not_mislabeled(hass, operating, target, mode, preset):
    coordinator, _, _ = await coordinator_with(
        hass, permanent(target=target, operating=operating)
    )
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    assert entity.hvac_mode is mode
    assert entity.preset_mode == preset
    await coordinator.async_shutdown()


async def test_conflicting_or_missing_details_do_not_guess_permanent(hass):
    value = replace(permanent(), operating_mode=None, schedule_mode=None)
    coordinator, _, _ = await coordinator_with(hass, value)
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    assert entity.preset_mode is None
    assert entity.hvac_mode is HVACMode.HEAT
    await coordinator.async_shutdown()


async def test_resume_schedule_clears_pending_target(hass):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    coordinator.async_set_pending_setpoint("ABC123", 24)
    api.list_thermostats.return_value = [
        thermostat(mode=1, hold_until=None, hold_until_status=HoldUntilStatus.NULL)
    ]
    await entity.async_set_preset_mode(PRESET_RUN)
    assert coordinator.pending_setpoint("ABC123") is None
    assert entity.preset_mode == PRESET_RUN
    assert not entity.assumed_state
    await coordinator.async_shutdown()


async def test_failed_preset_write_preserves_state_and_does_not_retry(hass):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    api.set_schedule_mode.side_effect = NuHeatApiError("synthetic failure")
    with pytest.raises(NuHeatApiError):
        await entity.async_set_preset_mode(PRESET_PERMANENT_HOLD)
    assert entity.preset_mode == PRESET_TEMPORARY_HOLD
    assert not entity.assumed_state
    assert api.set_schedule_mode.await_count == 1
    await coordinator.async_shutdown()


async def test_failed_post_write_read_reconciles_without_repeating_command(
    hass, freezer
):
    from pytest_homeassistant_custom_component.common import async_fire_time_changed
    from datetime import timedelta

    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    api.set_schedule_mode.side_effect = NuHeatApiError(
        "synthetic post-PUT read failure"
    )
    with pytest.raises(NuHeatApiError):
        await entity.async_set_preset_mode(PRESET_PERMANENT_HOLD)
    assert entity.preset_mode == PRESET_TEMPORARY_HOLD
    api.list_thermostats.return_value = [permanent()]
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert entity.preset_mode == PRESET_PERMANENT_HOLD
    assert api.set_schedule_mode.await_count == 1
    await coordinator.async_shutdown()


async def test_permanent_from_standby_and_delayed_confirmation(hass, freezer):
    from pytest_homeassistant_custom_component.common import async_fire_time_changed
    from datetime import timedelta

    coordinator, api, _ = await coordinator_with(
        hass, permanent(target=500, operating=2)
    )
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity._optimistic_standby = True
    await entity.async_set_preset_mode(PRESET_PERMANENT_HOLD)
    api.set_schedule_mode.assert_awaited_once_with(
        "ABC123", ScheduleMode.PERMANENT_HOLD, temperature=5
    )
    api.list_thermostats.return_value = [permanent(target=500)]
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert entity.preset_mode == PRESET_PERMANENT_HOLD
    assert entity.hvac_mode is HVACMode.AUTO
    assert entity.target_temperature == 5
    await coordinator.async_shutdown()


async def test_preset_reconciliation_timer_is_cancelled_on_unload(hass, freezer):
    from pytest_homeassistant_custom_component.common import async_fire_time_changed
    from datetime import timedelta

    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await entity.async_set_preset_mode(PRESET_PERMANENT_HOLD)
    reads = api.list_thermostats.await_count
    await coordinator.async_shutdown()
    freezer.tick(timedelta(seconds=40))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert api.list_thermostats.await_count == reads


async def test_missing_schedule_details_do_not_silently_convert_hold_to_manual(hass):
    from homeassistant.exceptions import ServiceValidationError

    value = replace(
        permanent(),
        operating_mode=None,
        schedule_mode=None,
        schedule_details_requested=True,
    )
    coordinator, api, _ = await coordinator_with(hass, value)
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    with pytest.raises(ServiceValidationError):
        await entity.async_set_temperature(temperature=24)
    api.set_target_temperature.assert_not_awaited()
    await entity.async_set_temperature(temperature=24, hvac_mode=HVACMode.HEAT)
    api.set_target_temperature.assert_awaited_once_with(
        "ABC123", 24, mode=ScheduleMode.MANUAL
    )
    await coordinator.async_shutdown()


async def test_real_client_and_entity_complete_four_control_roundtrip(
    hass, aiohttp_server, socket_enabled
):
    from aiohttp import web
    from chemelex_nuheat import NuHeatClient
    from homeassistant.config_entries import ConfigEntryState
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from custom_components.nuheat.coordinator import NuHeatCoordinator

    state = {"mode": 1, "target": 2300, "operating": 1, "schedule": 1}
    writes = []

    def v2():
        return {
            "serialNumber": "ABC123",
            "name": "Synthetic thermostat",
            "currentTemperature": 2100,
            "online": True,
            "isHeating": False,
            "setPointTemperature": state["target"],
            "holdUntil": None,
            "mode": state["mode"],
            "errorState": None,
        }

    def v1():
        return {
            "serialNumber": "ABC123",
            "operatingMode": state["operating"],
            "scheduleMode": state["schedule"],
            "setPointTemp": state["target"],
            "holdSetPointDateTime": None,
            "online": True,
        }

    async def read(request):
        item = v1() if "/v1/" in request.path else v2()
        return web.json_response(item if request.path.endswith("/ABC123") else [item])

    async def write(request):
        body = await request.json()
        writes.append((request.path, body))
        if request.path == "/api/v1/Thermostat":
            assert set(body) == {"serialNumber", "setPointTemp", "scheduleMode"}
            assert body["scheduleMode"] == 3
            state.update(mode=3, target=body["setPointTemp"], operating=1, schedule=3)
        elif request.path.endswith("/Auto"):
            state.update(mode=1, target=2300, operating=1, schedule=1)
        elif request.path.endswith("/Hold"):
            state.update(mode=2, target=body["temperature"], operating=1, schedule=2)
        elif request.path.endswith("/Manual"):
            state.update(mode=3, target=body["temperature"], operating=2, schedule=3)
        else:
            raise AssertionError("Unexpected synthetic command")
        return web.Response(status=204)

    app = web.Application()
    for version in ("v1", "v2"):
        app.router.add_get(f"/api/{version}/Thermostat", read)
        app.router.add_get(f"/api/{version}/Thermostat/ABC123", read)
    app.router.add_put("/api/v1/Thermostat", write)
    app.router.add_put("/api/v2/Mode/{mode}", write)
    server = await aiohttp_server(app)

    async def token(_force):
        return "synthetic-token"

    client = NuHeatClient(
        async_get_clientsession(hass),
        token,
        base_url=str(server.make_url("/")),
        include_schedule_details=True,
    )
    entry = MockConfigEntry(domain="nuheat", data={})
    entry.add_to_hass(hass)
    entry.mock_state(hass, ConfigEntryState.SETUP_IN_PROGRESS)
    coordinator = NuHeatCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await add_entity_state(hass, entity, "climate.synthetic_roundtrip")
    assert entity.preset_mode == PRESET_RUN
    await entity.async_set_preset_mode(PRESET_PERMANENT_HOLD)
    await coordinator.async_refresh()
    assert (
        entity.preset_mode == PRESET_PERMANENT_HOLD
        and entity.hvac_mode is HVACMode.AUTO
    )
    await entity.async_set_temperature(temperature=24)
    await coordinator.async_refresh()
    assert (
        entity.target_temperature == 24 and entity.preset_mode == PRESET_PERMANENT_HOLD
    )
    assert writes[-1] == (
        "/api/v1/Thermostat",
        {"serialNumber": "ABC123", "setPointTemp": 2400, "scheduleMode": 3},
    )
    await entity.async_set_preset_mode(PRESET_TEMPORARY_HOLD)
    await coordinator.async_refresh()
    assert entity.preset_mode == PRESET_TEMPORARY_HOLD
    await entity.async_set_preset_mode(PRESET_RUN)
    await coordinator.async_refresh()
    assert entity.preset_mode == PRESET_RUN
    await entity.async_turn_off()
    await coordinator.async_refresh()
    assert entity.hvac_mode is HVACMode.OFF and entity.target_temperature is None
    assert state["target"] == 500
    await entity.async_turn_on()
    await coordinator.async_refresh()
    assert entity.hvac_mode is HVACMode.AUTO and entity.preset_mode == PRESET_RUN
    assert (
        entity.unique_id == "ABC123"
        and entity.entity_id == "climate.synthetic_roundtrip"
    )
    assert hass.config_entries.async_get_entry(entry.entry_id) is entry
    await entity.async_will_remove_from_hass()
    await coordinator.async_shutdown()


@pytest.mark.parametrize("control", ["preset", "hvac"])
@pytest.mark.parametrize("initial", ["manual", "permanent", "standby"])
async def test_resume_schedule_reconciles_stale_immediate_response(
    hass, freezer, control, initial
):
    """A successful Auto command must not leave stale Heat/hold until polling."""
    from datetime import timedelta
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    value = permanent(
        operating=2 if initial != "permanent" else 1,
        target=500 if initial == "standby" else 2300,
    )
    coordinator, api, _ = await coordinator_with(hass, value)
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await add_entity_state(hass, entity, "climate.synthetic_resume")
    if control == "preset":
        await entity.async_set_preset_mode(PRESET_RUN)
    else:
        await entity.async_set_hvac_mode(HVACMode.AUTO)
    api.set_schedule_mode.assert_awaited_once_with("ABC123", ScheduleMode.AUTO)
    # The first cloud read still contains the old mode; no second write is needed.
    api.list_thermostats.return_value = [
        thermostat(
            mode=1,
            raw_target_temperature=3100,
            hold_until=None,
            hold_until_status=HoldUntilStatus.NULL,
        )
    ]
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert entity.hvac_mode is HVACMode.AUTO
    assert entity.preset_mode == PRESET_RUN
    assert entity.target_temperature == 31
    assert hass.states.get(entity.entity_id).state == HVACMode.AUTO
    assert api.set_schedule_mode.await_count == 1
    await entity.async_will_remove_from_hass()
    await coordinator.async_shutdown()


@pytest.mark.parametrize("control", ["preset", "hvac"])
async def test_failed_resume_does_not_invent_auto_or_repeat_write(
    hass, freezer, control
):
    from datetime import timedelta
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    coordinator, api, _ = await coordinator_with(hass, permanent(operating=2))
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    api.set_schedule_mode.side_effect = NuHeatApiError("synthetic uncertain write")
    with pytest.raises(NuHeatApiError):
        if control == "preset":
            await entity.async_set_preset_mode(PRESET_RUN)
        else:
            await entity.async_set_hvac_mode(HVACMode.AUTO)
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert entity.hvac_mode is HVACMode.HEAT
    assert entity.target_temperature == 23
    assert entity.preset_mode is None
    assert api.set_schedule_mode.await_count == 1
    assert api.list_thermostats.await_count == 2
    await coordinator.async_shutdown()


@pytest.mark.parametrize("control", ["preset", "hvac"])
async def test_resume_then_permanent_reconciles_latest_command(hass, freezer, control):
    from datetime import timedelta
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    coordinator, api, _ = await coordinator_with(hass, permanent(operating=2))
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    if control == "preset":
        await entity.async_set_preset_mode(PRESET_RUN)
    else:
        await entity.async_set_hvac_mode(HVACMode.AUTO)
    await entity.async_set_preset_mode(PRESET_PERMANENT_HOLD)
    api.list_thermostats.return_value = [permanent()]
    reads = api.list_thermostats.await_count
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert entity.preset_mode == PRESET_PERMANENT_HOLD
    assert api.list_thermostats.await_count == reads + 1
    assert api.set_schedule_mode.await_count == 2
    await coordinator.async_shutdown()


@pytest.mark.parametrize("control", ["preset", "hvac"])
async def test_resume_reconciliation_cancelled_on_unload(hass, freezer, control):
    from datetime import timedelta
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    if control == "preset":
        await entity.async_set_preset_mode(PRESET_RUN)
    else:
        await entity.async_set_hvac_mode(HVACMode.AUTO)
    reads = api.list_thermostats.await_count
    await coordinator.async_shutdown()
    freezer.tick(timedelta(seconds=40))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert api.list_thermostats.await_count == reads
