from __future__ import annotations

import textwrap
from pathlib import Path


def quote(path: Path) -> str:
    return "'" + str(path).replace("'", "'\\''") + "'"


def write_command(path: Path, body: str) -> None:
    path.write_text(
        "#!/bin/sh\n" + textwrap.dedent(body).lstrip(), encoding="utf-8"
    )
    path.chmod(0o755)


def write_log_command(path: Path, log: Path) -> None:
    write_command(path, f"printf '{path.name} %s\\n' \"$*\" >> {quote(log)}")
