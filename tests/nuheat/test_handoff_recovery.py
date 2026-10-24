"""Exercise reversible retirement failures without authorizing new Core source."""

from functools import partial
from pathlib import Path
import shutil
from unittest.mock import AsyncMock

from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState
from homeassistant.helpers import issue_registry as ir

from custom_components.nuheat import core_handoff


def isolated_override(hass, tmp_path, monkeypatch):
    """Create synthetic beta files and use the existing known-source fixture."""
    component = tmp_path / "custom_components/nuheat"
    component.mkdir(parents=True)
    (component / "sentinel.py").write_text("synthetic preserved beta\n")
    shipped = Path(core_handoff.__file__).parent
    shutil.copyfile(shipped / "core-handoff.json", component / "core-handoff.json")
    fixture = Path(__file__).parents[1] / "fixtures/core_candidate/nuheat"
    checker = core_handoff.compatible_core
    hass.config.config_dir = str(tmp_path)
    hass.set_state(CoreState.starting)
    monkeypatch.setattr(core_handoff, "_COMPONENT_DIR", component)
    monkeypatch.setattr(core_handoff, "compatible_core", partial(checker, fixture))
    return component


async def test_failed_rename_preserves_override_and_reports_issue(
    hass, tmp_path, monkeypatch
):
    """A filesystem failure cannot remove beta files or request restart."""
    component = isolated_override(hass, tmp_path, monkeypatch)
    restart = AsyncMock()
    hass.services.async_register("homeassistant", "restart", restart)
    original = Path.rename

    def fail_retirement(path, target):
        if path == component:
            raise OSError("synthetic rename failure")
        return original(path, target)

    monkeypatch.setattr(Path, "rename", fail_retirement)
    assert await core_handoff.async_schedule_core_handoff(hass)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()
    assert (component / "sentinel.py").read_text() == "synthetic preserved beta\n"
    restart.assert_not_awaited()
    assert ir.async_get(hass).async_get_issue("nuheat", "beta_handoff_failed")


async def test_missing_restart_preserves_backup_for_explicit_recovery(
    hass, tmp_path, monkeypatch
):
    """A dispatch failure after rename leaves a complete restorable backup."""
    component = isolated_override(hass, tmp_path, monkeypatch)
    assert await core_handoff.async_schedule_core_handoff(hass)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()
    assert not component.exists()
    backups = list((tmp_path / ".storage/nuheat_beta_backups").iterdir())
    assert len(backups) == 1
    backup = backups[0]
    assert not backup.is_relative_to(tmp_path / "custom_components")
    assert (backup / "sentinel.py").read_text() == "synthetic preserved beta\n"
    assert ir.async_get(hass).async_get_issue("nuheat", "beta_handoff_failed")
    backup.rename(component)
    assert (component / "sentinel.py").read_text() == "synthetic preserved beta\n"
    assert not backup.exists()
