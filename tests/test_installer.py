from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest


PROJECT = Path(__file__).resolve().parents[1]
LOADER = importlib.machinery.SourceFileLoader("samsung_installer", str(PROJECT / "install"))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
installer = importlib.util.module_from_spec(SPEC)
sys.modules[LOADER.name] = installer
LOADER.exec_module(installer)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_persistence_patch_is_exact_and_length_preserving(monkeypatch) -> None:
    original = b"A" * 100 + installer.PERSISTENCE_OLD
    original += b"B" * (4096 - len(original))
    expected = original.replace(installer.PERSISTENCE_OLD, installer.PERSISTENCE_NEW, 1)
    profile = installer.SupportedProfile(
        block_size=4096,
        original_block_sha256=sha(original),
        patched_block_sha256=sha(expected),
    )
    monkeypatch.setattr(installer, "PROFILE", profile)

    patched = installer.patch_persistence_block(original)

    assert patched == expected
    assert len(patched) == 4096
    assert installer.patch_persistence_block(patched) == patched


def test_persistence_patch_rejects_unknown_block() -> None:
    with pytest.raises(installer.InstallError, match="unsupported persistence block"):
        installer.patch_persistence_block(b"X" * 4096)


def test_root_result_requires_authenticated_verified_session() -> None:
    accepted = {
        "authenticated": True,
        "uid": 0,
        "staging_cleaned": True,
        "system_files_unchanged": True,
        "commands": [{"exit_code": 0, "stdout": "ok\n"}],
    }
    assert installer.root_stdout(accepted) == "ok\n"

    rejected = dict(accepted, uid=901)
    with pytest.raises(installer.InstallError, match="UID 0"):
        installer.root_stdout(rejected)


def test_host_validation_accepts_ipv4_and_rejects_names() -> None:
    assert installer.validate_host("192.0.2.10") == "192.0.2.10"
    with pytest.raises(Exception):
        installer.validate_host("living-room-tv")


def test_guard_success_uses_the_status_fields_the_guard_writes(monkeypatch) -> None:
    arguments = installer.parser().parse_args(["--dry-run"])
    subject = installer.Installer(arguments)
    monkeypatch.setattr(
        subject,
        "root_command",
        lambda command: "DAYBREAK_TV_ROOT_GUARD\npass1_exit=0\npass2_exit=0\n",
    )
    subject.apply_policy()

    monkeypatch.setattr(
        subject,
        "root_command",
        lambda command: "DAYBREAK_TV_ROOT_GUARD\npass1_exit=0\npass2_exit=2\n",
    )
    with pytest.raises(installer.InstallError, match="verified pass"):
        subject.apply_policy()
