"""Push only invalidates cached state; polling and control deadlines remain."""

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.nuheat.const import CONF_PUSH_UPDATES, SCAN_INTERVAL
from .test_integration import coordinator_with, thermostat


async def tick(hass, freezer, seconds=1):
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_default_off_and_one_listener_shutdown(hass):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    listener = MagicMock()
    listener.close = AsyncMock()
    api.create_notifications = MagicMock(return_value=listener)
    assert coordinator._push_listener is None
    api.create_notifications.assert_not_called()
    coordinator.async_start_push()
    coordinator.async_start_push()
    listener.start.assert_called_once()
    known, _invalidate = api.create_notifications.call_args.args
    assert known() == {"ABC123"}
    assert coordinator.update_interval == SCAN_INTERVAL
    await coordinator.async_shutdown()
    listener.close.assert_awaited_once()


async def test_push_burst_coalesces_and_timer_does_not_move(hass, freezer):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    for _ in range(50):
        coordinator.async_request_push_refresh()
    scheduled = coordinator._cancel_push_refresh
    coordinator.async_request_push_refresh()
    assert coordinator._cancel_push_refresh is scheduled
    await tick(hass, freezer)
    assert api.list_thermostats.await_count == 2
    api.set_target_temperature.assert_not_awaited()
    api.set_schedule_mode.assert_not_awaited()
    await coordinator.async_shutdown()


async def test_changed_event_during_read_gets_one_followup(hass, freezer):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    entered, release = asyncio.Event(), asyncio.Event()
    calls = 0

    async def read():
        nonlocal calls
        calls += 1
        if calls == 1:
            entered.set()
            await release.wait()
        return [thermostat()]

    api.list_thermostats.side_effect = read
    first = asyncio.create_task(coordinator.async_refresh())
    await entered.wait()
    for _ in range(20):
        coordinator.async_request_push_refresh()
    # Start the queued read while the poll is still blocked, without waiting
    # for HA's entire task pool (which intentionally contains this fake read).
    freezer.tick(timedelta(seconds=1))
    async_fire_time_changed(hass)
    await asyncio.sleep(0)
    release.set()
    await first
    await hass.async_block_till_done()
    assert calls == 2
    await coordinator.async_shutdown()


async def test_push_cooldown_keeps_deadline_and_unload_cancels(hass, freezer):
    coordinator, api, _ = await coordinator_with(hass, thermostat())
    coordinator.async_set_pending_setpoint("ABC123", 24)
    api.cooldown_remaining = 120
    coordinator.async_request_push_refresh()
    await tick(hass, freezer, 31)
    assert coordinator.pending_setpoint("ABC123") is None
    assert api.list_thermostats.await_count == 1
    api.cooldown_remaining = 0
    await tick(hass, freezer, 90)
    assert api.list_thermostats.await_count == 2
    coordinator.async_request_push_refresh()
    await coordinator.async_shutdown()
    await tick(hass, freezer, 10)
    assert api.list_thermostats.await_count == 2


async def test_push_read_does_not_confirm_stale_target_or_extend_deadline(
    hass, freezer
):
    coordinator, _, _ = await coordinator_with(hass, thermostat())
    coordinator.async_set_pending_setpoint("ABC123", 24)
    coordinator.async_request_push_refresh()
    await tick(hass, freezer)
    assert coordinator.pending_setpoint("ABC123") == 24
    coordinator.async_request_push_refresh()
    await tick(hass, freezer, 30)
    assert coordinator.pending_setpoint("ABC123") is None
    await coordinator.async_shutdown()


async def test_options_preserve_existing_credentials_and_options(hass):
    coordinator, _, entry = await coordinator_with(hass, thermostat())
    entry.mock_state(hass, ConfigEntryState.LOADED)
    hass.config_entries.async_update_entry(
        entry, options={"synthetic_existing_option": True}
    )
    original = dict(entry.data)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["step_id"] == "init"
    assert result["data_schema"]({}) == {CONF_PUSH_UPDATES: False}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_PUSH_UPDATES: True}
    )
    assert result["data"] == {
        "synthetic_existing_option": True,
        CONF_PUSH_UPDATES: True,
    }
    assert dict(entry.data) == original
    await coordinator.async_shutdown()


@pytest.mark.parametrize("enabled", [False, True])
async def test_setup_opt_in_and_options_only_reload(hass, enabled):
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from .test_integration import oauth_data, ACCOUNT_SUBJECT
    from .helpers import FakeOAuthImplementation

    entry = MockConfigEntry(
        domain="nuheat",
        data=oauth_data(),
        unique_id=ACCOUNT_SUBJECT,
        version=3,
        options={CONF_PUSH_UPDATES: enabled},
    )
    entry.add_to_hass(hass)
    listener = MagicMock()
    listener.close = AsyncMock()
    with (
        patch(
            "custom_components.nuheat.OAuth2Session.async_ensure_token_valid",
            AsyncMock(),
        ),
        patch(
            "custom_components.nuheat.async_get_config_entry_implementation",
            AsyncMock(return_value=FakeOAuthImplementation()),
        ),
        patch(
            "custom_components.nuheat.NuHeatCoordinator.async_config_entry_first_refresh",
            AsyncMock(),
        ),
        patch(
            "custom_components.nuheat.NuHeatClient.create_notifications",
            return_value=listener,
        ) as factory,
        patch.object(hass.config_entries, "async_forward_entry_setups", AsyncMock()),
        patch.object(
            hass.config_entries, "async_unload_platforms", AsyncMock(return_value=True)
        ),
        patch.object(hass.config_entries, "async_reload", AsyncMock()) as reload,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        assert factory.call_count == int(enabled)
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, "synthetic_updated": True}
        )
        await hass.async_block_till_done()
        reload.assert_not_awaited()
        hass.config_entries.async_update_entry(
            entry, options={CONF_PUSH_UPDATES: not enabled}
        )
        await hass.async_block_till_done()
        reload.assert_awaited_once_with(entry.entry_id)
        await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        assert listener.close.await_count == int(enabled)


async def test_fake_hub_event_triggers_real_sdk_get_without_write(
    hass, freezer, aiohttp_server, socket_enabled
):
    import json
    from aiohttp import web
    from chemelex_nuheat import NuHeatClient
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from custom_components.nuheat.coordinator import NuHeatCoordinator

    reads, writes = [], []
    target = 2300
    send = asyncio.Event()
    ready = asyncio.Event()

    async def read(request):
        reads.append(request.method)
        return web.json_response(
            [
                {
                    "serialNumber": "SYNTHETIC",
                    "currentTemperature": 2100,
                    "setPointTemperature": target,
                    "holdUntil": None,
                    "mode": 1,
                    "online": True,
                    "isHeating": False,
                }
            ]
        )

    async def unexpected_write(request):
        writes.append(request.method)
        return web.Response(status=500)

    async def hub(request):
        assert request.headers["Authorization"] == "Bearer synthetic-token"
        socket = web.WebSocketResponse()
        await socket.prepare(request)
        await socket.receive_str()
        await socket.send_str("{}\x1e")
        await socket.receive_str()
        await socket.send_str('{"type":3,"invocationId":"1","result":null}\x1e')
        ready.set()
        await send.wait()
        await socket.send_str(
            json.dumps(
                {
                    "type": 1,
                    "target": "Notify",
                    "arguments": [
                        {
                            "type": 2,
                            "id": "SYNTHETIC",
                            "timeStamp": "2030-01-01T00:00:00Z",
                        }
                    ],
                }
            )
            + "\x1e"
        )
        async for _ in socket:
            pass
        return socket

    app = web.Application()
    app.router.add_get("/api/v2/Thermostat", read)
    app.router.add_get("/v2/notificationsHost", hub)
    app.router.add_put("/{path:.*}", unexpected_write)
    server = await aiohttp_server(app)

    async def token(_force):
        return "synthetic-token"

    client = NuHeatClient(
        async_get_clientsession(hass), token, base_url=str(server.make_url("/"))
    )
    entry = MockConfigEntry(domain="nuheat", data={})
    entry.add_to_hass(hass)
    entry.mock_state(hass, ConfigEntryState.SETUP_IN_PROGRESS)
    coordinator = NuHeatCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    coordinator.async_start_push()
    try:
        await asyncio.wait_for(ready.wait(), 3)
        for _ in range(100):
            if coordinator._cancel_push_refresh:
                break
            await asyncio.sleep(0)
        await tick(hass, freezer)
        before = len(reads)
        target = 2400
        send.set()
        for _ in range(100):
            if coordinator._cancel_push_refresh:
                break
            await asyncio.sleep(0)
        await tick(hass, freezer)
        assert len(reads) == before + 1
        assert coordinator.data["SYNTHETIC"].target_temperature == 24
        assert not writes
    finally:
        send.set()
        await coordinator.async_shutdown()
