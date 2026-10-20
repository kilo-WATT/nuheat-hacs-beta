"""Retire the beta automatically only for an explicitly tested Core source."""

from datetime import UTC, datetime
import hashlib
import json
import logging
from pathlib import Path
from uuid import uuid4

import homeassistant
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.helpers import issue_registry as ir

PENDING = "nuheat_beta_core_handoff_pending"
_LOGGER = logging.getLogger(__name__)
_COMPONENT_DIR = Path(__file__).resolve().parent
_CORE_DIR = Path(homeassistant.__file__).resolve().parent / "components/nuheat"


def compatible_core(core_dir: Path = _CORE_DIR) -> bool:
    """Recognize the exact integration source already tested for handoff."""
    try:
        expected = json.loads((_COMPONENT_DIR / "core-handoff.json").read_text())
        manifest = json.loads((core_dir / "manifest.json").read_text())
        if manifest.get("domain") != "nuheat" or manifest.get("requirements") != [
            "chemelex-nuheat==0.1.1"
        ]:
            return False
        return all(
            hashlib.sha256((core_dir / name).read_bytes()).hexdigest() == digest
            for name, digest in expected["files"].items()
        )
    except OSError, ValueError, KeyError:
        return False


def _retire_override(config_dir: str) -> Path:
    """Atomically preserve the override outside custom_components."""
    config = Path(config_dir).resolve()
    source = _COMPONENT_DIR.resolve()
    if source != config / "custom_components/nuheat" or not source.is_dir():
        raise ValueError("NuHeat beta path does not match this HA configuration")
    backups = config / ".storage/nuheat_beta_backups"
    backups.mkdir(parents=True, exist_ok=True)
    if not backups.resolve().is_relative_to(config):
        raise ValueError("NuHeat beta backup directory leaves the HA configuration")
    destination = backups / (
        datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    )
    source.rename(destination)
    return destination


async def async_schedule_core_handoff(hass: HomeAssistant) -> bool:
    """Retire the override and request one restart after HA startup finishes."""
    if not await hass.async_add_executor_job(compatible_core):
        return False
    if hass.data.get(PENDING):
        return True
    hass.data[PENDING] = True

    async def retire_and_restart(_event=None):
        try:
            await hass.async_add_executor_job(_retire_override, hass.config.config_dir)
            _LOGGER.warning(
                "A verified Core NuHeat replacement is installed; beta files were backed up and retired. Restarting Home Assistant to load Core."
            )
            await hass.services.async_call("homeassistant", "restart", blocking=False)
        except Exception:
            _LOGGER.exception("NuHeat beta automatic handoff could not finish")
            ir.async_create_issue(
                hass,
                "nuheat",
                "beta_handoff_failed",
                is_fixable=False,
                severity=ir.IssueSeverity.ERROR,
                translation_key="beta_handoff_failed",
            )

    if hass.state is CoreState.running:
        hass.async_create_task(retire_and_restart(), "nuheat beta Core handoff")
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, retire_and_restart)
    return True
