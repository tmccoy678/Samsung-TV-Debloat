from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.shell_fakes import quote, write_command


PROJECT = Path(__file__).resolve().parents[1]
BOOT_HOOK = PROJECT / "on-tv-guard" / "boot_hook.sh"


class BootHookTests(unittest.TestCase):
    def test_non_root_shell_is_a_side_effect_free_noop(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            log = root / "calls.log"

            write_command(
                fake_bin / "id",
                """
                printf 'id %s\n' "$*" >> "$DAYBREAK_TEST_LOG"
                printf '501\n'
                """,
            )
            write_command(
                fake_bin / "cat",
                """
                printf 'cat %s\n' "$*" >> "$DAYBREAK_TEST_LOG"
                printf 'test-boot-id\n'
                """,
            )
            write_command(
                fake_bin / "mkdir",
                """
                printf 'mkdir %s\n' "$*" >> "$DAYBREAK_TEST_LOG"
                """,
            )

            environment = os.environ.copy()
            environment.update(
                {
                    "BASH_ENV": str(BOOT_HOOK),
                    "DAYBREAK_TEST_LOG": str(log),
                    "PATH": f"{fake_bin}:/usr/bin:/bin",
                }
            )
            completed = subprocess.run(
                ["/bin/bash", "-c", "printf shell-continued"],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(completed.stdout, "shell-continued")
            self.assertEqual(log.read_text(encoding="utf-8"), "id -u\n")

    def test_root_shell_starts_worker_once_per_boot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            log = root / "calls.log"
            guard = root / "guard"
            worker = root / "daybreak-worker.service"
            boot_id = root / "boot-id"
            boot_lock = root / "boot-lock"
            boot_id.write_text("boot-123\n", encoding="utf-8")

            write_command(fake_bin / "id", "printf '0\n'")
            write_command(
                fake_bin / "systemctl",
                "printf 'systemctl %s\n' \"$*\" >> \"$DAYBREAK_TEST_LOG\"",
            )
            write_command(fake_bin / "chown", ":")
            write_command(fake_bin / "chsmack", ":")

            environment = os.environ.copy()
            environment.update(
                {
                    "BASH_ENV": str(BOOT_HOOK),
                    "DAYBREAK_BOOT_ID_FILE": str(boot_id),
                    "DAYBREAK_BOOT_LOCK_DIR": str(boot_lock),
                    "DAYBREAK_GUARD_DIR": str(guard),
                    "DAYBREAK_TEST_LOG": str(log),
                    "DAYBREAK_WORKER_UNIT": str(worker),
                    "PATH": f"{fake_bin}:/usr/bin:/bin",
                }
            )

            for _attempt in range(2):
                completed = subprocess.run(
                    ["/bin/bash", "-c", "printf shell-continued"],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stdout, "shell-continued")

            self.assertEqual(
                log.read_text(encoding="utf-8").splitlines(),
                [
                    "systemctl daemon-reload",
                    "systemctl start --no-block daybreak-tv-root-guard-worker.service",
                ],
            )
            self.assertIn("boot_id=boot-123", (guard / "boot-hook.status").read_text())
            self.assertIn(
                "sh -s</opt/usr/share/daybreak-tv-guard/root-enforce.sh",
                worker.read_text(encoding="utf-8"),
            )
            self.assertIn(
                "DAYBREAK_AUTOMATIC_HOME_REFRESH=0",
                worker.read_text(encoding="utf-8"),
            )
            self.assertIn("Restart=on-failure", worker.read_text(encoding="utf-8"))
            self.assertIn(
                "RestartPreventExitStatus=2",
                worker.read_text(encoding="utf-8"),
            )

    def test_failed_worker_start_is_retried_during_the_same_boot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            log = root / "calls.log"
            attempts = root / "attempts"
            guard = root / "guard"
            boot_id = root / "boot-id"
            boot_id.write_text("boot-retry\n", encoding="utf-8")

            write_command(fake_bin / "id", "printf '0\n'")
            write_command(
                fake_bin / "systemctl",
                f"""
                printf 'systemctl %s\n' "$*" >> {quote(log)}
                if [ "$1" = start ] && [ ! -e {quote(attempts)} ]; then
                  : > {quote(attempts)}
                  exit 1
                fi
                """,
            )
            write_command(fake_bin / "chown", ":")
            write_command(fake_bin / "chsmack", ":")

            environment = os.environ.copy()
            environment.update(
                {
                    "BASH_ENV": str(BOOT_HOOK),
                    "DAYBREAK_BOOT_ID_FILE": str(boot_id),
                    "DAYBREAK_BOOT_LOCK_DIR": str(root / "boot-lock"),
                    "DAYBREAK_GUARD_DIR": str(guard),
                    "DAYBREAK_TEST_LOG": str(log),
                    "DAYBREAK_WORKER_UNIT": str(root / "worker.service"),
                    "PATH": f"{fake_bin}:/usr/bin:/bin",
                }
            )

            results = [
                subprocess.run(
                    ["/bin/bash", "-c", "true"],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                for _attempt in range(2)
            ]

            self.assertEqual([result.returncode for result in results], [0, 0])
            start_calls = [
                line
                for line in log.read_text(encoding="utf-8").splitlines()
                if line.startswith("systemctl start ")
            ]
            self.assertEqual(len(start_calls), 2)
            self.assertIn(
                "worker_start_exit=0",
                (guard / "boot-hook.status").read_text(encoding="utf-8"),
            )

if __name__ == "__main__":
    unittest.main()
