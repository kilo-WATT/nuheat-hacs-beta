"""Replay serialized synthetic HA storage through separate runtime processes."""

from contextlib import ExitStack
import importlib
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant import loader

STAGE = os.environ.get("NUHEAT_TRANSITION_STAGE")
if STAGE is not None and STAGE != "candidate":
    importlib.import_module("custom_components.nuheat")
ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(STAGE is None, reason="Run with tools/transition.py")


@pytest.fixture(autouse=True)
def restore_input(hass_storage):
    """Load the preceding process's serialized storage before HA initializes."""
    if STAGE is not None and STAGE != "seed":
        directory = Path(os.environ["NUHEAT_TRANSITION_DIR"])
        previous = {"beta": "seed", "restart": "beta", "candidate": "restart"}[STAGE]
        hass_storage.update(json.loads((directory / f"{previous}.json").read_text()))


def inventory(hass):
    """Capture public identities and user customizations, excluding runtime state."""
    entries = hass.config_entries.async_entries("nuheat")
    return {
        "entities": sorted(
            [
                {
                    "id": e.id,
                    "entity_id": e.entity_id,
                    "unique_id": e.unique_id,
                    "device_id": e.device_id,
                    "name": e.name,
                    "icon": e.icon,
                    "area_id": e.area_id,
                    "labels": sorted(e.labels),
                    "disabled_by": e.disabled_by,
                }
                for e in er.async_get(hass).entities.values()
                if e.platform == "nuheat"
            ],
            key=lambda e: e["unique_id"],
        ),
        "devices": sorted(
            [
                {
                    "id": d.id,
                    "identifiers": sorted(d.identifiers),
                    "area_id": d.area_id,
                    "name_by_user": d.name_by_user,
                    "model": d.model,
                }
                for d in dr.async_get(hass).devices
            ],
            key=lambda d: d["id"],
        ),
        "options": {e.entry_id: dict(e.options) for e in entries},
    }


@pytest.mark.parametrize("load_registries", [False])
async def test_persistent_transition(hass, hass_storage, hass_client_no_auth):
    """Migrate, restart and attempt Core candidate load with unchanged identities."""
    directory = Path(os.environ["NUHEAT_TRANSITION_DIR"])
    directory.mkdir(exist_ok=True, parents=True)
    from homeassistant.helpers import (
        area_registry,
        category_registry,
        floor_registry,
        issue_registry,
        label_registry,
    )

    await hass.config_entries.async_initialize()
    dr.async_setup(hass)
    for registry in (
        area_registry,
        category_registry,
        dr,
        er,
        floor_registry,
        issue_registry,
        label_registry,
    ):
        await registry.async_load(hass)
    if STAGE == "seed":
        from tests.nuheat.test_migration import (
            add_legacy_entry,
            create_customized_registry_records,
        )

        anchor = add_legacy_entry(hass, "ABC123")
        redundant = add_legacy_entry(hass, "XYZ789")
        create_customized_registry_records(hass, anchor, "ABC123")
        enabled, *_ = create_customized_registry_records(hass, redundant, "XYZ789")
        er.async_get(hass).async_update_entity(enabled.entity_id, disabled_by=None)
        hass.config_entries.async_update_entry(
            anchor, options={"synthetic_option": "kept"}
        )
        baseline = inventory(hass)
        baseline["anchor_id"] = anchor.entry_id
        baseline["redundant_id"] = redundant.entry_id
        (directory / "baseline.json").write_text(json.dumps(baseline))
        # MockConfigEntry insertion bypasses the normal config-flow save trigger.
        hass.config_entries._async_schedule_save()
    else:
        baseline = json.loads((directory / "baseline.json").read_text())
        anchor = hass.config_entries.async_get_entry(baseline["anchor_id"])
        assert anchor is not None
        if STAGE == "beta":
            from tests.nuheat.test_migration import run_migration_flow, thermostat

            result = await run_migration_flow(
                hass,
                hass_client_no_auth,
                anchor,
                [thermostat("ABC123"), thermostat("XYZ789")],
            )
            assert result["reason"] == "migration_successful"
        if STAGE in ("restart", "candidate"):
            if STAGE == "candidate":
                import homeassistant.components

                homeassistant.components.__path__.insert(
                    0, str(ROOT / "tests/fixtures/core_candidate")
                )
                hass.data[loader.DATA_CUSTOM_COMPONENTS] = {}
                module = "homeassistant.components.nuheat"
            else:
                module = "custom_components.nuheat"
            from tests.nuheat.helpers import FakeOAuthImplementation
            from chemelex_nuheat import Thermostat

            thermostats = [
                Thermostat(
                    serial_number=s,
                    name="Synthetic thermostat",
                    current_temperature=21,
                    target_temperature=23,
                    heating=False,
                    online=True,
                    mode=1,
                    raw_target_temperature=2300,
                )
                for s in ("ABC123", "XYZ789")
            ]
            implementation = FakeOAuthImplementation()
            with ExitStack() as stack:
                stack.enter_context(
                    patch(
                        f"{module}.async_get_config_entry_implementation",
                        AsyncMock(return_value=implementation),
                    )
                )
                stack.enter_context(
                    patch(
                        f"{module}.NuHeatClient.list_thermostats",
                        AsyncMock(return_value=thermostats),
                    )
                )
                integration = await loader.async_get_integration(hass, "nuheat")
                assert integration.is_built_in == (STAGE == "candidate")
                assert await hass.config_entries.async_setup(anchor.entry_id)
                await hass.async_block_till_done()
                state = hass.states.get("climate.custom_xyz789")
                assert state is not None and state.state != "unavailable"
                assert state.attributes["current_temperature"] == 21
                assert state.attributes["temperature"] == 23
                assert anchor.state is ConfigEntryState.LOADED
                assert await hass.config_entries.async_unload(anchor.entry_id)
        assert hass.config_entries.async_get_entry(baseline["redundant_id"]) is None
        assert anchor.version == 3
        assert CONF_PASSWORD not in anchor.data and CONF_USERNAME not in anchor.data
        assert len(hass.config_entries.async_entries("nuheat")) == 1
        current = inventory(hass)
        assert current["entities"] == baseline["entities"]
        assert json.loads(json.dumps(current["devices"])) == baseline["devices"]
        assert dict(anchor.options) == baseline["options"][anchor.entry_id]
        entities = list(er.async_get(hass).entities.values())
        assert all(e.config_entry_id == anchor.entry_id for e in entities)
        assert all(
            d.config_entry_id == anchor.entry_id for d in dr.async_get(hass).devices
        )
    await hass.async_stop(force=True)
    await hass.async_block_till_done()
    assert "core.config_entries" in hass_storage
    assert "core.entity_registry" in hass_storage
    assert "core.device_registry" in hass_storage
    (directory / f"{STAGE}.json").write_text(json.dumps(hass_storage))
