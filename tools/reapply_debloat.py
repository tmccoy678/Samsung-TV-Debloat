#!/usr/bin/env python3
"""Reapply volatile TU7000 service masks once per TV boot."""

from __future__ import annotations

import fcntl
import json
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from runtime_config import root_executable, tv_host  # noqa: E402
from sdb_direct import SDB as DirectSDB  # noqa: E402

TV_HOST = tv_host()
ROOT_TOOL = root_executable(PROJECT)
SDB = PROJECT / "tools/sdb"
STATE_DIR = Path.home() / "Library/Application Support/DaybreakSamsungTV"
STATE_FILE = STATE_DIR / "debloat-state.json"
LOCK_FILE = STATE_DIR / "debloat.lock"
LAST_RESULT = PROJECT / "artifacts/launchd-last-debloat.json"

ROOT_COMMAND = (
    "DAYBREAK_INITIAL_DELAY_SECONDS=0 "
    "DAYBREAK_SETTLE_DELAY_SECONDS=0 "
    "DAYBREAK_PASS_DELAY_SECONDS=0 "
    "sh -s</opt/usr/share/daybreak-tv-guard/root-enforce.sh"
)


def tv_reachable() -> bool:
    try:
        with socket.create_connection((TV_HOST, 26101), timeout=2):
            return True
    except OSError:
        return False


def tv_boot_id() -> str:
    client = DirectSDB(TV_HOST, timeout=10)
    try:
        client.open_stream("shell:0 cat /proc/sys/kernel/random/boot_id")
        output = client.read_stream().decode("utf-8", "replace")
    finally:
        client.close()
    marker = "\n[exit:0]"
    if marker not in output:
        raise RuntimeError("TV boot ID command failed")
    boot_id = output.split(marker, 1)[0].strip()
    if len(boot_id) != 36:
        raise RuntimeError("TV returned an invalid boot ID")
    return boot_id


def read_state() -> dict[str, object]:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_state(boot_id: str, passes: int) -> None:
    payload = {
        "tv_host": TV_HOST,
        "boot_id": boot_id,
        "passes": passes,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, STATE_FILE)


def reapply() -> None:
    command = [
        str(ROOT_TOOL),
        "--output",
        "json",
        "--sdb",
        str(SDB),
        "archive-root",
        "root",
        TV_HOST,
        "--accept-timeout",
        "30",
        "--command-timeout",
        "60",
        "--command",
        ROOT_COMMAND,
    ]
    completed = subprocess.run(
        command,
        cwd=PROJECT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    LAST_RESULT.parent.mkdir(parents=True, exist_ok=True)
    LAST_RESULT.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"root cleanup exited {completed.returncode}: {completed.stderr.strip()}"
        )
    result = json.loads(completed.stdout)
    commands = result.get("commands", [])
    if (
        not result.get("authenticated")
        or result.get("uid") != 0
        or not result.get("staging_cleaned")
        or not result.get("system_files_unchanged")
        or len(commands) != 1
        or commands[0].get("exit_code") != 0
    ):
        raise RuntimeError("root cleanup did not satisfy its acceptance checks")


def main() -> int:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LOCK_FILE.open("w", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        if not tv_reachable():
            return 0
        boot_id = tv_boot_id()
        state = read_state()
        passes = int(state.get("passes", 0)) if state.get("boot_id") == boot_id else 0
        if passes >= 2:
            return 0
        if passes == 1:
            completed_at = state.get("completed_at")
            if isinstance(completed_at, str):
                elapsed = datetime.now(timezone.utc) - datetime.fromisoformat(completed_at)
                if elapsed.total_seconds() < 120:
                    return 0
        reapply()
        write_state(boot_id, passes + 1)
        print(f"Applied TU7000 boot guard pass {passes + 1} for {boot_id}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"TU7000 boot guard: {error}", file=sys.stderr)
        raise SystemExit(1)
