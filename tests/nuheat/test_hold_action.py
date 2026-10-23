"""Every write reconciles; explicit timed holds use the existing entity safely."""

from datetime import UTC, datetime, timedelta
import logging
from types import SimpleNamespace

from chemelex_nuheat import HoldUntilStatus, NuHeatApiError, ScheduleMode
import pytest

from homeassistant.components.climate import HVACMode
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import EntityPlatform
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.nuheat.climate import NuHeatClimateEntity, async_setup_entry
from custom_components.nuheat.const import (
    PRESET_RUN,
    PRESET_TEMPORARY_HOLD,
    PRESET_PERMANENT_HOLD,
    SCAN_INTERVAL,
)
from .test_integration import coordinator_with, thermostat
from .test_permanent_hold import permanent

CONTROLS = ["run", "temporary", "permanent", "heat", "auto", "off", "on"]


async def command(entity, control):
    if control in ("run", "temporary", "permanent"):
        await entity.async_set_preset_mode(
            {
                "run": PRESET_RUN,
                "temporary": PRESET_TEMPORARY_HOLD,
                "permanent": PRESET_PERMANENT_HOLD,
            }[control]
        )
    elif control in ("heat", "auto"):
        await entity.async_set_hvac_mode(
            HVACMode.HEAT if control == "heat" else HVACMode.AUTO
        )
    elif control == "off":
        await entity.async_turn_off()
    else:
        await entity.async_turn_on()


@pytest.mark.parametrize("control", CONTROLS)
async def test_all_controls_refresh_after_stale_read(hass, freezer, control):
    coordinator, api, _ = await coordinator_with(hass, permanent(operating=2))
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await command(entity, control)
    fresh = {
        "run": thermostat(
            mode=1,
            raw_target_temperature=3100,
            hold_until=None,
            hold_until_status=HoldUntilStatus.NULL,
        ),
        "temporary": thermostat(),
        "permanent": permanent(),
        "heat": permanent(operating=2),
        "off": permanent(operating=2, target=500),
    }
    api.list_thermostats.return_value = [fresh.get(control, fresh["run"])]
    reads = api.list_thermostats.await_count
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert api.list_thermostats.await_count == reads + 1
    assert entity.thermostat == api.list_thermostats.return_value[0]
    assert api.set_schedule_mode.await_count + api.set_standby.await_count == 1
    await coordinator.async_shutdown()


@pytest.mark.parametrize("control", CONTROLS)
async def test_all_controls_failed_writes_read_without_retry(hass, freezer, control):
    coordinator, api, _ = await coordinator_with(hass, permanent(operating=2))
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    api.set_schedule_mode.side_effect = NuHeatApiError("synthetic uncertain write")
    api.set_standby.side_effect = NuHeatApiError("synthetic uncertain write")
    with pytest.raises(NuHeatApiError):
        await command(entity, control)
    reads = api.list_thermostats.await_count
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert api.list_thermostats.await_count == reads + 1
    assert entity.hvac_mode is HVACMode.HEAT
    assert entity.preset_mode is None
    assert not entity.assumed_state
    assert api.set_schedule_mode.await_count + api.set_standby.await_count == 1
    await coordinator.async_shutdown()


@pytest.mark.parametrize("control", CONTROLS)
async def test_all_controls_coalesce_and_cancel_on_unload(hass, freezer, control):
    coordinator, api, _ = await coordinator_with(hass, permanent(operating=2))
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await command(entity, control)
    await command(entity, control)
    reads = api.list_thermostats.await_count
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert api.list_thermostats.await_count == reads + 1
    await command(entity, control)
    reads = api.list_thermostats.await_count
    await coordinator.async_shutdown()
    freezer.tick(timedelta(seconds=40))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert api.list_thermostats.await_count == reads


@pytest.mark.parametrize("imperial", [False, True])
async def test_real_action_dispatch_units_local_timezone_and_expiry_preserved(
    hass, freezer, imperial
):
    freezer.move_to("2026-10-22T20:00:00+00:00")
    await hass.config.async_set_time_zone("America/New_York")
    if imperial:
        hass.config.units = US_CUSTOMARY_SYSTEM
    coordinator, api, entry = await coordinator_with(hass, permanent())
    entry.runtime_data = SimpleNamespace(coordinator=coordinator)
    platform = EntityPlatform(
        hass=hass,
        logger=logging.getLogger(__name__),
        domain="climate",
        platform_name="nuheat",
        platform=None,
        scan_interval=SCAN_INTERVAL,
        entity_namespace=None,
    )
    entities = []
    await async_setup_entry(hass, entry, entities.extend)
    await platform.async_add_entities(entities)
    entity = entities[0]
    original_id = entity.entity_id
    expected = datetime(2026, 10, 23, 0, 30, tzinfo=UTC)
    await hass.services.async_call(
        "nuheat",
        "set_temporary_hold",
        {
            "entity_id": original_id,
            "temperature": 75.2 if imperial else 24,
            "hold_until": "2026-10-22T20:30:00",
        },
        blocking=True,
    )
    api.set_target_temperature.assert_awaited_once_with(
        "ABC123", 24, mode=ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE, hold_until=expected
    )
    assert entity.assumed_state
    assert entity.target_temperature == pytest.approx(75.2 if imperial else 24)
    api.list_thermostats.return_value = [
        thermostat(raw_target_temperature=2400, hold_until=expected)
    ]
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert entity.preset_mode == PRESET_TEMPORARY_HOLD
    assert not entity.assumed_state
    await entity.async_set_temperature(temperature=77 if imperial else 25)
    assert api.set_target_temperature.await_args.kwargs["hold_until"] == expected
    assert entity.entity_id == original_id and entity.unique_id == "ABC123"
    await platform.async_reset()
    await coordinator.async_shutdown()


@pytest.mark.parametrize(
    "until",
    [
        datetime(2020, 1, 1),
        datetime(2020, 1, 1, tzinfo=UTC),
        datetime(2027, 3, 14, 2, 30),
        datetime(2026, 11, 1, 1, 30),
    ],
)
async def test_invalid_or_dst_ambiguous_expiry_never_writes(hass, freezer, until):
    freezer.move_to("2026-10-22T20:00:00+00:00")
    await hass.config.async_set_time_zone("America/New_York")
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    with pytest.raises(ServiceValidationError):
        await entity.async_set_temporary_hold(24, until)
    api.set_target_temperature.assert_not_awaited()
    await coordinator.async_shutdown()


@pytest.mark.parametrize("temperature", [float("nan"), float("inf"), 6, 36])
async def test_invalid_timed_hold_target_never_writes(hass, temperature):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    with pytest.raises(ServiceValidationError):
        await entity.async_set_temporary_hold(
            temperature, datetime.now(UTC) + timedelta(hours=1)
        )
    api.set_target_temperature.assert_not_awaited()
    await coordinator.async_shutdown()


async def test_explicit_dst_offset_and_failed_write(hass, freezer):
    freezer.move_to("2026-10-22T20:00:00+00:00")
    await hass.config.async_set_time_zone("America/New_York")
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    api.set_target_temperature.side_effect = NuHeatApiError("synthetic failure")
    until = datetime.fromisoformat("2026-11-01T01:30:00-04:00")
    with pytest.raises(NuHeatApiError):
        await entity.async_set_temporary_hold(24, until)
    assert api.set_target_temperature.await_args.kwargs["hold_until"] == datetime(
        2026, 11, 1, 5, 30, tzinfo=UTC
    )
    assert not entity.assumed_state
    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert api.set_target_temperature.await_count == 1
    await coordinator.async_shutdown()


async def test_rapid_target_change_preserves_new_expiry_before_cloud_confirmation(
    hass, freezer
):
    freezer.move_to("2026-10-22T20:00:00+00:00")
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    until = datetime(2026, 10, 23, 0, 30, tzinfo=UTC)
    await entity.async_set_temporary_hold(24, until)
    # Even a matching target must not confirm a stale Permanent Hold response.
    api.list_thermostats.return_value = [permanent(target=2400)]
    await coordinator.async_refresh()
    assert coordinator.pending_hold_until("ABC123") == until
    await entity.async_set_temperature(temperature=25)
    api.set_target_temperature.assert_awaited_with(
        "ABC123", 25, mode=ScheduleMode.HOLD_UNTIL_NEXT_SCHEDULE, hold_until=until
    )
    await entity.async_set_preset_mode(PRESET_RUN)
    assert coordinator.pending_hold_until("ABC123") is None
    await coordinator.async_shutdown()


async def test_unconfirmed_timed_hold_expires_and_unload_cancels_timers(hass, freezer):
    freezer.move_to("2026-10-22T20:00:00+00:00")
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entity.hass = hass
    until = datetime(2026, 10, 23, 0, 30, tzinfo=UTC)
    await entity.async_set_temporary_hold(24, until)
    freezer.tick(timedelta(seconds=30))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert coordinator.pending_hold_until("ABC123") is None
    assert not entity.assumed_state
    await entity.async_set_temporary_hold(24, until)
    reads = api.list_thermostats.await_count
    await coordinator.async_shutdown()
    freezer.tick(timedelta(seconds=40))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert api.list_thermostats.await_count == reads


async def test_action_form_selectors_are_valid():
    from pathlib import Path
    import yaml
    from homeassistant.helpers import selector
    from custom_components.nuheat import climate

    data = yaml.safe_load(Path(climate.__file__).with_name("services.yaml").read_text())
    fields = data["set_temporary_hold"]["fields"]
    assert set(fields) == {"temperature", "hold_until"}
    for field in fields.values():
        selector.validate_selector(field["selector"])
