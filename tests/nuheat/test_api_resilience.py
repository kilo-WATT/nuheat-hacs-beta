"""Cooldown, deadline and permission behavior with synthetic requests only."""

from asyncio import CancelledError, Event, create_task, sleep
from datetime import UTC, datetime, timedelta
import time
from unittest.mock import AsyncMock, PropertyMock, patch

import pytest
from chemelex_nuheat import NuHeatPermissionError, NuHeatRateLimitError
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    HomeAssistantError,
    ServiceValidationError,
)

from custom_components.nuheat import climate
from custom_components.nuheat.climate import NuHeatClimateEntity

from .test_integration import coordinator_with, thermostat
from .test_permanent_hold import permanent
from .test_hold_action import command, CONTROLS
from .test_setpoint_reconciliation import advance


@pytest.mark.parametrize("provider", ["community", "custom"])
async def test_permission_failure_during_reauth_keeps_entry_and_registries(
    hass, hass_client_no_auth, provider
):
    from copy import deepcopy
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from homeassistant.helpers import entity_registry as er, device_registry as dr
    from .test_migration import create_customized_registry_records
    from .test_integration import oauth_data, oauth_implementation, ACCOUNT_SUBJECT
    from .helpers import complete_oauth_flow

    entry = MockConfigEntry(
        domain="nuheat",
        version=3,
        unique_id=ACCOUNT_SUBJECT,
        data={**oauth_data(), "auth_implementation": provider},
        options={"synthetic": "kept"},
    )
    entry.add_to_hass(hass)
    create_customized_registry_records(hass, entry, "ABC123")
    entities = dict(er.async_get(hass).entities)
    devices = deepcopy(list(dr.async_get(hass).devices))
    original = deepcopy(dict(entry.data))
    with patch(
        "custom_components.nuheat.config_flow.NuHeatClient.get_account",
        AsyncMock(side_effect=NuHeatPermissionError("synthetic", status=403)),
    ):
        result = await complete_oauth_flow(
            hass,
            hass_client_no_auth,
            oauth_implementation(domain=provider),
            entry=entry,
            confirmation_step="reauth_confirm",
        )
    assert result["reason"] == "permission_denied"
    assert dict(entry.data) == original and entry.options == {"synthetic": "kept"}
    assert list(hass.config_entries.async_entries("nuheat")) == [entry]
    assert dict(er.async_get(hass).entities) == entities
    assert list(dr.async_get(hass).devices) == devices


@pytest.mark.parametrize("kind", ["permission", "throttle", "token_timeout"])
async def test_startup_failures_preserve_entry_and_retry(hass, kind):
    import asyncio
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from homeassistant.config_entries import ConfigEntryState
    from .helpers import FakeOAuthImplementation, jwt_access_token

    entry = MockConfigEntry(
        domain="nuheat",
        version=3,
        unique_id="synthetic-account-subject",
        data={
            "auth_implementation": "test",
            "token": {
                "access_token": jwt_access_token(),
                "refresh_token": "synthetic",
                "expires_at": time.time() + 3600,
                "expires_in": 3600,
            },
        },
    )
    entry.add_to_hass(hass)
    original = dict(entry.data)

    async def hang(*args, **kwargs):
        await Event().wait()

    error = (
        NuHeatPermissionError("synthetic", status=403)
        if kind == "permission"
        else NuHeatRateLimitError(120)
    )
    with (
        patch(
            "custom_components.nuheat.async_get_config_entry_implementation",
            AsyncMock(return_value=FakeOAuthImplementation()),
        ),
        patch("custom_components.nuheat.timeout", lambda _: asyncio.timeout(0.01)),
        patch(
            "custom_components.nuheat.NuHeatClient.list_thermostats",
            AsyncMock(side_effect=error),
        ),
        patch(
            "custom_components.nuheat.OAuth2Session.async_ensure_token_valid",
            AsyncMock(side_effect=hang if kind == "token_timeout" else None),
        ),
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY
    assert dict(entry.data) == original


@pytest.mark.parametrize(
    "first_scheduled,second_scheduled",
    [(False, False), (True, False), (False, True), (True, True)],
)
async def test_overlapping_poll_and_reconciliation_share_one_account_read(
    hass, first_scheduled, second_scheduled
):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entered = Event()
    release = Event()

    async def read():
        entered.set()
        await release.wait()
        return [thermostat()]

    api.list_thermostats.side_effect = read
    before = api.list_thermostats.await_count
    first = create_task(
        coordinator._handle_refresh_interval()
        if first_scheduled
        else coordinator.async_refresh()
    )
    await entered.wait()
    second = create_task(
        coordinator._handle_refresh_interval()
        if second_scheduled
        else coordinator.async_refresh()
    )
    await sleep(0)
    release.set()
    await first
    await second
    assert api.list_thermostats.await_count == before + 1
    await coordinator.async_shutdown()


async def test_zero_retry_after_does_not_create_endless_fast_reads(hass, freezer):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    api.list_thermostats.side_effect = NuHeatRateLimitError(0)
    await coordinator.async_refresh()
    reads = api.list_thermostats.await_count
    await advance(hass, freezer, 30)
    assert api.list_thermostats.await_count == reads
    assert not coordinator._cooldown_read_due
    await coordinator.async_shutdown()


async def test_very_long_cooldown_read_is_cancelled_on_shutdown(hass, freezer):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    api.cooldown_remaining = 31536000000.0
    coordinator.async_schedule_reconciliation()
    reads = api.list_thermostats.await_count
    await coordinator.async_shutdown()
    await advance(hass, freezer, 86401)
    assert api.list_thermostats.await_count == reads
    assert not coordinator._cooldown_read_due


@pytest.mark.parametrize("control", CONTROLS + ["target", "timed"])
async def test_all_controls_reject_cooldown_without_writes(hass, control):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    api.cooldown_remaining = 120.0
    with pytest.raises(ServiceValidationError) as error:
        if control == "target":
            await entity.async_set_temperature(temperature=24)
        elif control == "timed":
            await entity.async_set_temporary_hold(
                24, datetime.now(UTC) + timedelta(hours=1)
            )
        else:
            await command(entity, control)
    assert error.value.translation_key == "rate_limited"
    api.set_target_temperature.assert_not_awaited()
    api.set_schedule_mode.assert_not_awaited()
    api.set_standby.assert_not_awaited()
    assert not entity.assumed_state
    await coordinator.async_shutdown()


async def test_primary_throttle_defers_reads_but_not_pending_expiry(hass, freezer):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    until = time.monotonic() + 120

    async def throttled():
        raise NuHeatRateLimitError(120)

    api.list_thermostats.side_effect = throttled
    with patch.object(
        type(api),
        "cooldown_remaining",
        PropertyMock(side_effect=lambda: max(0, until - time.monotonic())),
        create=True,
    ):
        coordinator.async_set_pending_setpoint("ABC123", 24)
        reads = api.list_thermostats.await_count
        await advance(hass, freezer, 30)
        assert coordinator.pending_setpoint("ABC123") is None
        await coordinator.async_request_refresh()
        await advance(hass, freezer, 89)
        assert api.list_thermostats.await_count == reads
        api.list_thermostats.side_effect = None
        await advance(hass, freezer, 1)
        assert api.list_thermostats.await_count == reads + 1
        assert not entity.assumed_state
    await coordinator.async_shutdown()


async def test_optional_throttle_retains_data_and_one_deferred_read(hass, freezer):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    until = time.monotonic() + 120

    async def optional_throttled():
        api.cooldown_remaining = max(0, until - time.monotonic())
        return [thermostat()]

    api.list_thermostats.side_effect = optional_throttled
    await coordinator.async_refresh()
    assert coordinator.last_update_success
    reads = api.list_thermostats.await_count
    with patch.object(
        type(api),
        "cooldown_remaining",
        PropertyMock(side_effect=lambda: max(0, until - time.monotonic())),
        create=True,
    ):
        await advance(hass, freezer, 119)
        assert api.list_thermostats.await_count == reads
        api.list_thermostats.side_effect = None
        await advance(hass, freezer, 1)
        assert api.list_thermostats.await_count == reads + 1
    await coordinator.async_shutdown()


@pytest.mark.parametrize("control", CONTROLS + ["target", "timed"])
async def test_all_controls_timeout_without_retry_and_release_lock(
    hass, monkeypatch, control
):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")

    async def hang(*args, **kwargs):
        await Event().wait()

    api.set_schedule_mode.side_effect = hang
    api.set_target_temperature.side_effect = hang
    api.set_standby.side_effect = hang
    monkeypatch.setattr(climate, "CONTROL_OPERATION_TIMEOUT", 0.01)
    with pytest.raises(HomeAssistantError) as error:
        if control == "target":
            await entity.async_set_temperature(temperature=24)
        elif control == "timed":
            await entity.async_set_temporary_hold(
                24, datetime.now(UTC) + timedelta(hours=1)
            )
        else:
            await command(entity, control)
    assert error.value.translation_key == "request_timeout"
    assert not entity._setpoint_lock.locked() and not entity._control_tasks
    assert not entity.assumed_state
    assert (
        api.set_target_temperature.await_count
        + api.set_schedule_mode.await_count
        + api.set_standby.await_count
        == 1
    )
    await coordinator.async_shutdown()


async def test_lock_wait_timeout_does_not_send_queued_command(hass, monkeypatch):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    await entity._setpoint_lock.acquire()
    monkeypatch.setattr(climate, "CONTROL_OPERATION_TIMEOUT", 0.01)
    try:
        with pytest.raises(HomeAssistantError):
            await entity.async_set_preset_mode("run_schedule")
    finally:
        entity._setpoint_lock.release()
    api.set_schedule_mode.assert_not_awaited()
    assert not entity._control_tasks
    await coordinator.async_shutdown()


async def test_unload_cancels_control_without_new_reads(hass, freezer):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    entered = Event()

    async def hang(*args, **kwargs):
        entered.set()
        await Event().wait()

    api.set_target_temperature.side_effect = hang
    pending = create_task(entity.async_set_temperature(temperature=24))
    await entered.wait()
    await entity.async_will_remove_from_hass()
    with pytest.raises(CancelledError):
        await pending
    reads = api.list_thermostats.await_count
    await coordinator.async_shutdown()
    await advance(hass, freezer, 360)
    assert api.list_thermostats.await_count == reads
    assert not entity._control_tasks and not entity._setpoint_lock.locked()


async def test_primary_permission_is_not_account_reauth(hass):
    coordinator, api, entry = await coordinator_with(hass, permanent())
    original = dict(entry.data)
    api.list_thermostats.side_effect = NuHeatPermissionError("synthetic", status=403)
    await coordinator.async_refresh()
    assert not isinstance(coordinator.last_exception, ConfigEntryAuthFailed)
    assert "permission" in str(coordinator.last_exception)
    assert dict(entry.data) == original
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    api.set_schedule_mode.side_effect = NuHeatPermissionError("synthetic", status=403)
    with pytest.raises(ServiceValidationError) as error:
        await entity.async_set_preset_mode("permanent_hold")
    assert error.value.translation_key == "permission_denied"
    api.set_target_temperature.assert_not_awaited()
    await coordinator.async_shutdown()


async def test_rate_limit_after_accepted_write_is_uncertain_not_rejected(hass):
    coordinator, api, _ = await coordinator_with(hass, permanent())
    entity = NuHeatClimateEntity(coordinator, "ABC123")
    error = NuHeatRateLimitError(120)
    error.write_applied = True
    api.set_target_temperature.side_effect = error
    with pytest.raises(HomeAssistantError) as raised:
        await entity.async_set_temperature(temperature=24)
    assert raised.value.translation_key == "write_unconfirmed"
    assert not entity.assumed_state
    api.set_target_temperature.assert_awaited_once()
    await coordinator.async_shutdown()
