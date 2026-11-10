"""Canonical expiries match vendor readback without guessing another hold."""

from datetime import UTC, datetime, timedelta
import asyncio

import pytest
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import async_fire_time_changed
from chemelex_nuheat import ScheduleMode

from custom_components.nuheat.climate import NuHeatClimateEntity
from .test_integration import coordinator_with, thermostat
from .test_permanent_hold import permanent


@pytest.mark.parametrize("hours", [1, 25, 168])
async def test_fractional_expiry_confirms_and_retains_identity(hass, freezer, hours):
    freezer.move_to("2026-11-10T12:00:00+00:00")
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    end = datetime.now(UTC) + timedelta(hours=hours, microseconds=123456)
    canonical = end.replace(microsecond=0)
    await entity.async_set_temporary_hold(24, end)
    assert api.set_target_temperature.await_args.kwargs["hold_until"] == canonical
    assert coordinator.pending_hold_until("ABC123") == canonical
    api.list_thermostats.return_value = [
        thermostat(raw_target_temperature=2400, hold_until=canonical)
    ]
    await coordinator.async_refresh()
    assert coordinator.pending_hold_until("ABC123") is None
    assert not entity.assumed_state
    assert entity.unique_id == "ABC123"
    await coordinator.async_shutdown()


async def test_expiry_checked_after_waiting_for_control_lock(hass, freezer):
    freezer.move_to("2026-11-10T12:00:00+00:00")
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    await entity._setpoint_lock.acquire()
    end = datetime.now(UTC) + timedelta(seconds=5)
    operation = asyncio.create_task(entity.async_set_temporary_hold(24, end))
    await asyncio.sleep(0)
    freezer.tick(timedelta(seconds=4))
    entity._setpoint_lock.release()
    with pytest.raises(ServiceValidationError):
        await operation
    api.set_target_temperature.assert_not_awaited()
    await coordinator.async_shutdown()


async def test_different_expiry_not_falsely_confirmed(hass, freezer):
    freezer.move_to("2026-11-10T12:00:00+00:00")
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    end = datetime.now(UTC) + timedelta(hours=1)
    await entity.async_set_temporary_hold(24, end)
    api.list_thermostats.return_value = [
        thermostat(raw_target_temperature=2400, hold_until=end + timedelta(seconds=1))
    ]
    await coordinator.async_refresh()
    assert coordinator.pending_hold_until("ABC123") == end
    await coordinator.async_shutdown()


@pytest.mark.parametrize("retarget", [False, True])
async def test_expiry_too_close_never_writes_or_loses_mode(hass, freezer, retarget):
    freezer.move_to("2026-11-10T12:00:00+00:00")
    end = datetime.now(UTC) + timedelta(seconds=1, microseconds=900000)
    coordinator, api, _ = await coordinator_with(hass, thermostat(hold_until=end))
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    with pytest.raises(ServiceValidationError):
        if retarget:
            await entity.async_set_temperature(temperature=24)
        else:
            await entity.async_set_temporary_hold(24, end)
    api.set_target_temperature.assert_not_awaited()
    api.set_schedule_mode.assert_not_awaited()
    await coordinator.async_shutdown()


@pytest.mark.parametrize("rewritten", ["minute_precision", "shorter_duration"])
async def test_device_rewritten_expiry_times_out_without_write_replay(
    hass, freezer, rewritten
):
    """A changed cloud expiry is observable state, never exact confirmation."""
    freezer.move_to("2026-11-10T12:00:00+00:00")
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    hours = 22 if rewritten == "minute_precision" else 25
    requested = datetime.now(UTC) + timedelta(hours=hours, seconds=37)
    reported = (
        requested.replace(second=0)
        if rewritten == "minute_precision"
        else datetime.now(UTC) + timedelta(hours=23)
    )
    await entity.async_set_temporary_hold(24, requested)
    api.list_thermostats.return_value = [
        thermostat(raw_target_temperature=2400, hold_until=reported)
    ]
    await coordinator.async_refresh()
    assert coordinator.pending_hold_until("ABC123") == requested
    assert entity.assumed_state
    assert coordinator.data["ABC123"].hold_until == reported
    assert api.set_target_temperature.await_count == 1

    freezer.tick(timedelta(seconds=31))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert coordinator.pending_hold_until("ABC123") is None
    assert not entity.assumed_state
    assert coordinator.data["ABC123"].hold_until == reported
    assert api.set_target_temperature.await_count == 1
    api.set_schedule_mode.assert_not_awaited()

    # A later deliberate target change retains the actually reported expiry,
    # not the rejected pending intent or an invented new end time.
    await entity.async_set_temperature(temperature=25)
    api.set_target_temperature.assert_awaited_with(
        "ABC123", 25, mode=ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE, hold_until=reported
    )
    assert entity.unique_id == "ABC123"
    await coordinator.async_shutdown()


async def test_whole_minute_expiry_confirms_and_retargets_exactly(hass, freezer):
    """Conservative minute-aligned inputs need no confirmation tolerance."""
    freezer.move_to("2026-11-10T12:00:00+00:00")
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    end = datetime.now(UTC) + timedelta(hours=22)
    await entity.async_set_temporary_hold(24, end)
    api.list_thermostats.return_value = [
        thermostat(raw_target_temperature=2400, hold_until=end)
    ]
    await coordinator.async_refresh()
    assert not entity.assumed_state
    await entity.async_set_temperature(temperature=25)
    api.set_target_temperature.assert_awaited_with(
        "ABC123", 25, mode=ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE, hold_until=end
    )
    await coordinator.async_shutdown()
