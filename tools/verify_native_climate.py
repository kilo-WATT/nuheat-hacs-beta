"""Exercise the exact official native climate API on the isolated HA test host."""

import ast
import base64
import json
import os
import urllib.request
import hashlib
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1] / "artifacts/native-framework-source"
SOURCE_BLOBS = [
    {
        "path": "homeassistant/components/climate/__init__.py",
        "blob": "d825b339eada0e05d635abb525fc285d9b025104",
    },
    {
        "path": "homeassistant/components/climate/entity.py",
        "blob": "d51c5316faf42a62843d3e9cf21d0caf81b33da5",
    },
    {
        "path": "homeassistant/components/climate/const.py",
        "blob": "7d497f063646290e0b17137f930cacda60b0c42e",
    },
    {
        "path": "homeassistant/components/climate/services.py",
        "blob": "0a97071932e6e2212844dfc5ef52e00c63f2e62b",
    },
    {
        "path": "homeassistant/helpers/deprecation.py",
        "blob": "4f5094a3744b878084b024d420318704b85db607",
    },
]


def ensure_sources(root: Path) -> None:
    """Verify cached or fetched official blobs before persisting or loading them."""
    for entry in SOURCE_BLOBS:
        path = root / entry["path"]
        downloaded = not path.exists()
        if downloaded:
            url = (
                "https://api.github.com/repos/home-assistant/core/git/blobs/"
                + entry["blob"]
            )
            headers = {"Accept": "application/vnd.github+json"}
            if token := os.environ.get("GITHUB_TOKEN"):
                headers["Authorization"] = "Bearer " + token
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if payload["encoding"] != "base64":
                raise RuntimeError("Unexpected official source encoding")
            raw = base64.b64decode(payload["content"])
        else:
            raw = path.read_bytes()
        digest = hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw
        ).hexdigest()
        if digest != entry["blob"]:
            raise RuntimeError(
                "Official source blob verification failed: " + entry["path"]
            )

        if downloaded:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)


def main() -> int:
    ensure_sources(HERE)

    # Load the installed integration first, then supply the official native entity
    # and its exact const/deprecation dependencies without editing site-packages.
    import homeassistant.components.climate as climate
    from homeassistant.components.climate import services

    def load(name, relative):
        spec = importlib.util.spec_from_file_location(name, HERE / relative)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    load("homeassistant.helpers.deprecation", "homeassistant/helpers/deprecation.py")
    const = load(
        "homeassistant.components.climate.const",
        "homeassistant/components/climate/const.py",
    )
    entity = load(
        "homeassistant.components.climate.entity",
        "homeassistant/components/climate/entity.py",
    )
    climate.ClimateEntity = entity.ClimateEntity
    climate.ClimateEntityDescription = entity.ClimateEntityDescription
    for name in vars(const):
        if not name.startswith("_"):
            setattr(climate, name, getattr(const, name))

    # Execute the official temperature handler with its real native-unit conversion.
    # Unrelated service schemas belong to a newer validation dependency and are not
    # needed to test this handler. This is a climate API overlay, not a full HA install.
    source = ast.parse(
        (HERE / "homeassistant/components/climate/services.py").read_text()
    )
    handler = next(
        node
        for node in source.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "_async_service_temperature_set"
    )
    from homeassistant.helpers.temperature import display_temp

    namespace = {**vars(services), **vars(const), "display_temp": display_temp}
    exec(
        compile(
            ast.Module(body=[handler], type_ignores=[]),
            "official-climate-services",
            "exec",
        ),
        namespace,
    )
    services._async_service_temperature_set = namespace[
        "_async_service_temperature_set"
    ]
    print(
        "Official native climate entity and temperature handler loaded; source blobs verified."
    )
    import pytest

    return int(
        pytest.main(sys.argv[1:] or ["-q", "tests/nuheat/test_native_temperature.py"])
    )


if __name__ == "__main__":
    raise SystemExit(main())
