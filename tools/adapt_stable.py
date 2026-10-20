"""Apply the documented stable climate API adaptation to a pinned snapshot."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in (
    "custom_components/nuheat/climate.py",
    "tests/nuheat/test_integration.py",
):
    path = ROOT / relative
    text = path.read_text()
    for old, new in (
        ("native_temperature_unit", "temperature_unit"),
        ("native_current_temperature", "current_temperature"),
        ("native_target_temperature", "target_temperature"),
    ):
        text = text.replace(old, new)
    path.write_text(text)
path = ROOT / "tests/nuheat/test_integration.py"
text = path.read_text()
text = text.replace(
    'load_json("homeassistant/components/nuheat/strings.json")',
    'load_json("custom_components/nuheat/strings.json")',
)
text = text.replace(
    'load_json("homeassistant/components/homeassistant/strings.json")',
    'load_json(str(Path(homeassistant.__file__).parent / "components/homeassistant/strings.json"))',
)
text = text.replace("import homeassistant\nfrom pathlib import Path\n", "")
text = text.replace(
    '"""Tests for the NuHeat integration."""\n',
    '"""Tests for the NuHeat integration."""\n\nimport homeassistant\nfrom pathlib import Path\n',
)
lines = text.splitlines(keepends=True)
for node in reversed(ast.parse(text).body):
    if isinstance(node, ast.AsyncFunctionDef) and node.name.startswith("test_"):
        source = ast.get_source_segment(text, node)
        if (
            "await coordinator_with(" in source
            and "await coordinator.async_shutdown()" not in source
        ):
            lines.insert(node.end_lineno, "    await coordinator.async_shutdown()\n")
path.write_text("".join(lines))
