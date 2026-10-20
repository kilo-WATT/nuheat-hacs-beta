"""One-time adaptation of pinned Core tests for the custom component harness."""

import json
from pathlib import Path
import shutil

ROOT = Path(__file__).parent
component = ROOT / "custom_components/nuheat"
candidate = ROOT / "tests/fixtures/core_candidate/nuheat"
if not candidate.exists():
    shutil.copytree(component, candidate)
manifest = json.loads((component / "manifest.json").read_text())
manifest.update(
    version="0.1.0b1",
    codeowners=["@kilo-WATT"],
    issue_tracker="https://github.com/kilo-WATT/nuheat-chemelex-ha-poc/issues",
)
(component / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
strings = (component / "strings.json").read_text()
replacements = {
    "[%key:common::config_flow::abort::already_configured_account%]": "This NuHeat account is already configured.",
    "[%key:common::config_flow::abort::oauth2_missing_configuration%]": "OAuth application credentials are missing.",
    "[%key:common::config_flow::data::implementation%]": "OAuth application",
    "[%key:common::config_flow::description::implementation%]": "Choose the OAuth application to link your account.",
    "[%key:common::config_flow::title::oauth2_pick_implementation%]": "Choose an OAuth application",
}
for old, new in replacements.items():
    strings = strings.replace(old, new)
assert "[%key:" not in strings
(component / "translations").mkdir(exist_ok=True)
(component / "translations/en.json").write_text(strings)
for path in (ROOT / "tests/nuheat").glob("*.py"):
    text = path.read_text().replace(
        "homeassistant.components.nuheat", "custom_components.nuheat"
    )
    text = text.replace(
        "from tests.common import",
        "from pytest_homeassistant_custom_component.common import",
    )
    text = text.replace(
        "from tests.typing import",
        "from pytest_homeassistant_custom_component.typing import",
    )
    path.write_text(text)
(ROOT / "tests/__init__.py").touch()
print(
    "Prepared HACS metadata, English translations, candidate fixture, and test imports."
)
