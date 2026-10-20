"""Load the private installer configuration used by Samsung control tools."""

from __future__ import annotations

import json
import os
from pathlib import Path


CONFIG_PATH = Path(
    os.environ.get(
        "SAMSUNG_TV_DEBLOAT_CONFIG",
        str(Path.home() / ".config/samsung-tv-debloat/config.json"),
    )
)


def load_config() -> dict[str, str]:
    try:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return {str(key): str(value) for key, value in payload.items() if value is not None}


def tv_host() -> str:
    return os.environ.get("DAYBREAK_TV_HOST") or load_config().get("tv_host", "192.0.2.1")


def root_executable(project: Path) -> Path:
    configured = os.environ.get("SAMSUNG_TV_ROOT_EXECUTABLE")
    if configured:
        return Path(configured).expanduser()
    saved = load_config().get("root_executable")
    if saved:
        return Path(saved).expanduser()
    return project / "tools/archive_root_cli.py"
