"""Historical entry points and preserved reference code cannot run on import."""

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ["adapt_stable", "transition", "core_handoff"]


def load(path):
    spec = importlib.util.spec_from_file_location(
        "synthetic_historical_" + path.stem, path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("name", NAMES)
def test_original_entry_points_help_and_default_are_safe(name, monkeypatch, capsys):
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    with (
        patch("subprocess.run", side_effect=AssertionError("runtime process")),
        patch("subprocess.check_output", side_effect=AssertionError("runtime process")),
        patch(
            "urllib.request.OpenerDirector.open", side_effect=AssertionError("network")
        ),
        patch.object(Path, "write_text", side_effect=AssertionError("source write")),
        patch.object(Path, "write_bytes", side_effect=AssertionError("source write")),
    ):
        module = load(ROOT / "tools" / (name + ".py"))
        with pytest.raises(SystemExit) as exc:
            module.main(["--help"])
        assert exc.value.code == 0
        assert module.main([]) == 2
    assert "historical" in capsys.readouterr().out.lower()


@pytest.mark.parametrize("name", NAMES + ["privacy_check"])
def test_preserved_references_are_inert_and_complete(name, monkeypatch, capsys):
    manifest = json.loads((ROOT / "tools/historical/source-manifest.json").read_text())
    path = ROOT / "tools/historical" / (name + ".py")
    tree = ast.parse(path.read_text())
    reference = next(
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "_historical_reference"
    )
    fingerprint = hashlib.sha256(
        ast.dump(ast.Module(body=reference.body, type_ignores=[])).encode()
    ).hexdigest()
    assert fingerprint == manifest["files"][name]["ast_sha256"]
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    with (
        patch("subprocess.run", side_effect=AssertionError("runtime process")),
        patch.object(Path, "write_text", side_effect=AssertionError("source write")),
    ):
        module = load(path)
        assert module.main() == 2
    assert "reference only" in capsys.readouterr().out


@pytest.mark.parametrize("name", NAMES)
def test_obsolete_script_invocation_fails_with_explanation(name):
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / (name + ".py"))],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 2
    assert "Historical helper" in result.stdout
    assert not result.stderr
