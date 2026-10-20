"""Verify fail-closed, reversible automatic retirement of the custom override."""

from pathlib import Path
import shutil
from unittest.mock import AsyncMock

import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState

from custom_components.nuheat import core_handoff


def test_recognizes_only_tested_core_source(tmp_path):
    candidate = Path(__file__).resolve().parents[1] / "fixtures/core_candidate/nuheat"
    core = tmp_path / "core"
    shutil.copytree(candidate, core)
    assert core_handoff.compatible_core(core)
    (core / "coordinator.py").write_text("# untested replacement\n")
    assert not core_handoff.compatible_core(core)
    assert not core_handoff.compatible_core(tmp_path / "missing")


def test_local_setpoint_candidate_is_not_automatically_allowlisted(tmp_path):
    """Testing a local fix must not silently authorize a new Core handoff."""
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    core = tmp_path / "core"
    shutil.copytree(fixtures / "core_candidate/nuheat", core)
    for source in (fixtures / "setpoint_candidate/nuheat").glob("*.py"):
        shutil.copyfile(source, core / source.name)
    assert not core_handoff.compatible_core(core)


async def test_retirement_preserves_backup_and_requests_one_restart(
    hass, tmp_path, monkeypatch
):
    component = tmp_path / "custom_components/nuheat"
    component.mkdir(parents=True)
    (component / "sentinel.py").write_text("synthetic beta source")
    hass.config.config_dir = str(tmp_path)
    hass.set_state(CoreState.starting)
    monkeypatch.setattr(core_handoff, "_COMPONENT_DIR", component)
    monkeypatch.setattr(core_handoff, "compatible_core", lambda: True)
    restart = AsyncMock()
    hass.services.async_register("homeassistant", "restart", restart)
    assert await core_handoff.async_schedule_core_handoff(hass)
    assert await core_handoff.async_schedule_core_handoff(hass)
    assert component.is_dir()
    restart.assert_not_called()
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()
    assert not component.exists()
    backups = list((tmp_path / ".storage/nuheat_beta_backups").glob("*/sentinel.py"))
    assert len(backups) == 1
    assert backups[0].read_text() == "synthetic beta source"
    restart.assert_awaited_once()


async def test_unknown_core_does_not_retire_or_restart(hass, monkeypatch):
    monkeypatch.setattr(core_handoff, "compatible_core", lambda: False)
    assert not await core_handoff.async_schedule_core_handoff(hass)
    assert core_handoff.PENDING not in hass.data


def test_retirement_refuses_another_configuration(tmp_path, monkeypatch):
    other = tmp_path / "another_config/custom_components/nuheat"
    other.mkdir(parents=True)
    monkeypatch.setattr(core_handoff, "_COMPONENT_DIR", other)
    with pytest.raises(ValueError):
        core_handoff._retire_override(str(tmp_path / "intended_config"))
    assert other.is_dir()
