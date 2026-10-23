"""Bound mode confirmation with synthetic readback, clocks and credentials."""

from asyncio import Event, create_task, sleep
from dataclasses import replace
from datetime import timedelta

import pytest
from chemelex_nuheat import (
    HoldUntilStatus,
    NuHeatApiError,
    NuHeatAuthError,
    ScheduleMode,
    ThermostatState,
)
from homeassistant.components.climate import HVACMode
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.nuheat.climate import NuHeatClimateEntity
from .test_integration import coordinator_with, thermostat
from .test_permanent_hold import permanent
from .test_setpoint_reconciliation import advance


def scheduled(serial="ABC123"):
    return thermostat(
        serial, mode=1, hold_until=None, hold_until_status=HoldUntilStatus.NULL
    )


def manual(serial="ABC123"):
    return replace(permanent(operating=2), serial_number=serial)


async def command(entity, control):
    if control in ("run_schedule", "temporary_hold", "permanent_hold"):
        await entity.async_set_preset_mode(control)
    elif control == "off":
        await entity.async_turn_off()
    elif control == "on":
        await entity.async_turn_on()
    else:
        await entity.async_set_hvac_mode(HVACMode(control))


@pytest.mark.parametrize(
    ("control", "fresh"),
    [
        ("run_schedule", scheduled()),
        ("auto", scheduled()),
        ("on", scheduled()),
        ("heat", manual()),
        ("off", permanent(target=500, operating=2)),
        ("temporary_hold", thermostat()),
        ("permanent_hold", permanent()),
    ],
)
async def test_all_controls_retry_stale_then_confirm(hass, freezer, control, fresh):
    initial = manual() if control == "temporary_hold" else thermostat()
    coordinator, api, _ = await coordinator_with(hass, initial)
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await command(entity, control)
    assert entity.assumed_state
    await advance(hass, freezer, 2)
    assert entity.assumed_state
    reads = api.list_thermostats.await_count
    api.list_thermostats.return_value = [fresh]
    await advance(hass, freezer, 8)
    assert api.list_thermostats.await_count == reads + 1
    assert not entity.assumed_state
    assert api.set_schedule_mode.await_count + api.set_standby.await_count == 1
    reads = api.list_thermostats.await_count
    await advance(hass, freezer, 40)
    assert api.list_thermostats.await_count == reads
    await coordinator.async_shutdown()


@pytest.mark.parametrize("confirms", [False, True])
async def test_standby_clears_on_confirmation_or_deadline(
    hass, freezer, caplog, confirms
):
    coordinator, api, _ = await coordinator_with(hass, scheduled())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await entity.async_turn_off()
    assert entity.hvac_mode is HVACMode.OFF
    if confirms:
        api.list_thermostats.return_value = [permanent(target=500, operating=2)]
    for seconds in (2, 8, 8, 8, 4):
        await advance(hass, freezer, seconds)
    assert not entity.assumed_state
    assert ("mode was not confirmed" in caplog.text) is not confirms
    api.list_thermostats.return_value = [scheduled()]
    await coordinator.async_refresh()
    assert entity.hvac_mode is HVACMode.AUTO
    await coordinator.async_shutdown()


@pytest.mark.parametrize("error", [NuHeatApiError, NuHeatAuthError])
async def test_failed_mode_write_does_not_assume_or_retry(hass, freezer, error):
    coordinator, api, _ = await coordinator_with(hass, scheduled())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    api.set_standby.side_effect = error("synthetic write or post-write read failure")
    with pytest.raises(error):
        await entity.async_turn_off()
    assert not entity.assumed_state
    await advance(hass, freezer, 2)
    assert api.set_standby.await_count == 1
    assert api.list_thermostats.await_count == 2
    await coordinator.async_shutdown()


@pytest.mark.parametrize("error", [NuHeatApiError, NuHeatAuthError])
async def test_mode_read_failure_expires(hass, freezer, error):
    coordinator, api, _ = await coordinator_with(hass, scheduled())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await entity.async_turn_off()
    api.list_thermostats.side_effect = error("synthetic read failure")
    await advance(hass, freezer, 2)
    assert not coordinator.last_update_success
    await advance(hass, freezer, 28)
    assert not entity.assumed_state
    assert entity.hvac_mode is HVACMode.AUTO
    await coordinator.async_shutdown()


async def test_old_inflight_response_cannot_confirm_new_generation(hass):
    coordinator, api, _ = await coordinator_with(hass, scheduled())
    coordinator.async_set_pending_mode("ABC123", ScheduleMode.AUTO)
    started, release = Event(), Event()

    async def read():
        started.set()
        await release.wait()
        return [permanent()]

    api.list_thermostats.side_effect = read
    refresh = create_task(coordinator.async_refresh())
    await started.wait()
    coordinator.async_set_pending_mode("ABC123", ScheduleMode.PERMANENT_HOLD)
    release.set()
    await refresh
    assert coordinator.pending_mode("ABC123") is ThermostatState.PERMANENT_HOLD
    await coordinator.async_refresh()
    assert coordinator.pending_mode("ABC123") is None
    await coordinator.async_shutdown()


async def test_ambiguous_or_offline_read_does_not_confirm(hass):
    coordinator, api, _ = await coordinator_with(hass, scheduled())
    coordinator.async_set_pending_mode("ABC123", ScheduleMode.PERMANENT_HOLD)
    for value in (
        replace(permanent(), operating_mode=None, schedule_mode=None),
        replace(permanent(), online=False),
    ):
        api.list_thermostats.return_value = [value]
        await coordinator.async_refresh()
        assert coordinator.pending_mode("ABC123") is not None
    await coordinator.async_shutdown()


async def test_mode_devices_independent_and_unload_cancels(hass, freezer, caplog):
    coordinator, api, _ = await coordinator_with(hass, scheduled(), scheduled("XYZ789"))
    coordinator.async_set_pending_mode("ABC123", None)
    await advance(hass, freezer, 20)
    coordinator.async_set_pending_mode("XYZ789", None)
    await advance(hass, freezer, 10)
    assert coordinator.pending_mode("ABC123") is None
    assert coordinator.pending_mode("XYZ789") is ThermostatState.STANDBY
    reads = api.list_thermostats.await_count
    caplog.clear()
    await coordinator.async_shutdown()
    await advance(hass, freezer, 60)
    assert api.list_thermostats.await_count == reads
    assert coordinator.pending_mode("XYZ789") is None
    assert "not confirmed" not in caplog.text


async def test_slow_mode_read_cannot_extend_deadline(hass, freezer):
    coordinator, api, _ = await coordinator_with(hass, scheduled())
    coordinator.async_set_pending_mode("ABC123", None)
    started, release = Event(), Event()

    async def read():
        started.set()
        await release.wait()
        return [scheduled()]

    api.list_thermostats.side_effect = read
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await started.wait()
    try:
        freezer.tick(timedelta(seconds=28))
        async_fire_time_changed(hass)
        await sleep(0)
        assert coordinator.pending_mode("ABC123") is None
    finally:
        release.set()
        await hass.async_block_till_done()
        await coordinator.async_shutdown()


@pytest.mark.parametrize(
    ("preset", "expected"),
    [
        ("permanent_hold", ScheduleMode.PERMANENT_HOLD),
        ("temporary_hold", ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE),
        ("run_schedule", ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE),
    ],
)
async def test_fast_target_preserves_accepted_mode(hass, preset, expected):
    coordinator, api, _ = await coordinator_with(hass, scheduled())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await entity.async_set_preset_mode(preset)
    await entity.async_set_temperature(temperature=24)
    api.set_target_temperature.assert_awaited_once_with("ABC123", 24, mode=expected)
    assert coordinator.pending_setpoint("ABC123") == 24
    await coordinator.async_shutdown()


async def test_mode_supersedes_expiry_and_target(hass):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    coordinator.async_set_pending_setpoint(
        "ABC123", 24, hold_until=entity.thermostat.hold_until
    )
    await entity.async_set_preset_mode("run_schedule")
    assert coordinator.pending_hold_until("ABC123") is None
    await entity.async_set_temperature(temperature=25)
    api.set_target_temperature.assert_awaited_once_with(
        "ABC123", 25, mode=ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE
    )
    await coordinator.async_shutdown()


async def test_mixed_writes_are_serialized(hass):
    coordinator, api, _ = await coordinator_with(hass, scheduled())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    started, release = Event(), Event()

    async def write(*args, **kwargs):
        started.set()
        await release.wait()

    api.set_schedule_mode.side_effect = write
    first = create_task(entity.async_set_preset_mode("permanent_hold"))
    await started.wait()
    second = create_task(entity.async_set_temperature(temperature=24))
    await sleep(0)
    api.set_target_temperature.assert_not_awaited()
    release.set()
    await first
    await second
    api.set_target_temperature.assert_awaited_once_with(
        "ABC123", 24, mode=ScheduleMode.PERMANENT_HOLD
    )
    await coordinator.async_shutdown()


async def test_fast_target_after_standby_uses_new_accepted_preset(hass):
    coordinator, api, _ = await coordinator_with(
        hass, permanent(target=500, operating=2)
    )
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await entity.async_set_preset_mode("permanent_hold")
    await entity.async_set_temperature(temperature=24)
    api.set_target_temperature.assert_awaited_once_with(
        "ABC123", 24, mode=ScheduleMode.PERMANENT_HOLD
    )
    await coordinator.async_shutdown()


async def test_next_schedule_preset_does_not_restore_previous_expiry(hass):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    # The first immediate read remains stale, then the debouncer coalesces reads.
    await entity.async_set_preset_mode("permanent_hold")
    await entity.async_set_preset_mode("temporary_hold")
    await entity.async_set_temperature(temperature=24)
    api.set_target_temperature.assert_awaited_once_with(
        "ABC123", 24, mode=ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE
    )
    await coordinator.async_shutdown()
