from __future__ import annotations

import importlib.util
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT / "tools/runtime_config.py"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_installer_config_supplies_host_and_root_tool(monkeypatch, tmp_path) -> None:
    config = tmp_path / "config.json"
    root = tmp_path / "samsung-tv-root"
    config.write_text(
        json.dumps({"tv_host": "192.0.2.44", "root_executable": str(root)}),
        encoding="utf-8",
    )
    monkeypatch.setenv("SAMSUNG_TV_DEBLOAT_CONFIG", str(config))
    monkeypatch.delenv("DAYBREAK_TV_HOST", raising=False)
    monkeypatch.delenv("SAMSUNG_TV_ROOT_EXECUTABLE", raising=False)
    runtime = load_module("runtime_config_saved")

    assert runtime.tv_host() == "192.0.2.44"
    assert runtime.root_executable(PROJECT) == root


def test_environment_overrides_saved_config(monkeypatch, tmp_path) -> None:
    config = tmp_path / "config.json"
    config.write_text('{"tv_host": "192.0.2.44"}', encoding="utf-8")
    monkeypatch.setenv("SAMSUNG_TV_DEBLOAT_CONFIG", str(config))
    monkeypatch.setenv("DAYBREAK_TV_HOST", "192.0.2.55")
    runtime = load_module("runtime_config_environment")

    assert runtime.tv_host() == "192.0.2.55"
