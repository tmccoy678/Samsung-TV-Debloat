from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT / "tools" / "reapply_debloat.py"
EXPECTED_ROOT_COMMAND = (
    "DAYBREAK_INITIAL_DELAY_SECONDS=0 "
    "DAYBREAK_SETTLE_DELAY_SECONDS=0 "
    "DAYBREAK_PASS_DELAY_SECONDS=0 "
    "sh -s</opt/usr/share/daybreak-tv-guard/root-enforce.sh"
)


def load_reapply_module():
    spec = importlib.util.spec_from_file_location("reapply_debloat", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load reapply_debloat.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReapplyDebloatTests(unittest.TestCase):
    def test_manual_reapply_delegates_to_the_tv_local_guard(self) -> None:
        module = load_reapply_module()
        accepted = {
            "authenticated": True,
            "uid": 0,
            "staging_cleaned": True,
            "system_files_unchanged": True,
            "commands": [{"exit_code": 0}],
        }

        with tempfile.TemporaryDirectory() as temporary:
            module.LAST_RESULT = Path(temporary) / "result.json"
            completed = type(
                "Completed",
                (),
                {"returncode": 0, "stdout": json.dumps(accepted), "stderr": ""},
            )()
            with patch.object(module.subprocess, "run", return_value=completed) as run:
                module.reapply()

        command = run.call_args.args[0]
        root_command_index = command.index("--command") + 1
        self.assertEqual(command[root_command_index], EXPECTED_ROOT_COMMAND)


if __name__ == "__main__":
    unittest.main()
