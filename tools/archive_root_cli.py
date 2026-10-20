#!/usr/bin/env python3
"""Narrow CLI for the vendored SDK archive-root transport."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
VENDOR = PROJECT / "vendor/samsung-tv-root"
sys.path.insert(0, str(VENDOR / "python"))

from samsung_tv_root.archive_root import (  # noqa: E402
    ArchiveRootError,
    probe,
)
from samsung_tv_root.sdb import SdbError  # noqa: E402


VERSION = "0.0.8-tu7000.1"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--version", action="version", version=VERSION)
    result.add_argument("--output", choices=("human", "json"), default="human")
    result.add_argument("--sdb", type=Path, required=True)
    top = result.add_subparsers(dest="route", required=True)
    archive = top.add_parser("archive-root")
    actions = archive.add_subparsers(dest="action", required=True)

    def add_common(command: argparse.ArgumentParser) -> None:
        command.add_argument("host")
        command.add_argument("--callback-host")
        command.add_argument("--bind-host")
        command.add_argument("--sdb-timeout", type=float, default=15.0)
        command.add_argument("--accept-timeout", type=float, default=30.0)
        command.add_argument("--payload-directory", type=Path)

    check = actions.add_parser("probe")
    add_common(check)
    root = actions.add_parser("root")
    add_common(root)
    root.add_argument("--command", action="append", required=True)
    root.add_argument("--command-timeout", type=float, default=45.0)
    return result


def emit(payload: dict[str, object], output: str) -> None:
    if output == "json":
        print(json.dumps(payload, sort_keys=True))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def main() -> int:
    arguments = parser().parse_args()
    os.environ["SDB"] = str(arguments.sdb.expanduser().resolve())
    os.environ["SAMSUNG_TV_ROOT_COMMON_PAYLOAD_DIRECTORY"] = str(
        VENDOR / "payloads/common"
    )
    os.environ["SAMSUNG_TV_ROOT_COMMON31_PAYLOAD_DIRECTORY"] = str(
        VENDOR / "payloads/common31"
    )
    commands = tuple(arguments.command) if arguments.action == "root" else ()
    try:
        evidence = asyncio.run(
            probe(
                arguments.host,
                callback_host=arguments.callback_host,
                bind_host=arguments.bind_host,
                sdb_timeout=arguments.sdb_timeout,
                accept_timeout=arguments.accept_timeout,
                command_timeout=getattr(arguments, "command_timeout", 45.0),
                commands=commands,
                payloads=arguments.payload_directory,
            )
        )
    except (ArchiveRootError, SdbError, OSError, ValueError) as error:
        print(f"archive-root: {error}", file=sys.stderr)
        return 1
    emit(evidence, arguments.output)
    if arguments.action == "root":
        for command in evidence.get("commands", []):
            if command.get("timed_out") or command.get("exit_code") != 0:
                return int(command.get("exit_code") or 1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
