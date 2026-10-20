import runpy
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

REMOTE = Path(__file__).parents[1] / "tools/samsung_remote.py"


def load_remote(monkeypatch, host="192.0.2.44"):
    monkeypatch.setenv("DAYBREAK_TV_HOST", host)
    monkeypatch.delenv("DAYBREAK_TV_KEYCHAIN_SERVICE", raising=False)
    return runpy.run_path(str(REMOTE))


def test_keychain_service_follows_configured_tv_host(monkeypatch):
    remote = load_remote(monkeypatch)

    assert remote["KEYCHAIN_SERVICE"] == "daybreak-samsung-tv-192.0.2.44"


def test_keychain_write_failure_never_exposes_token(monkeypatch):
    remote = load_remote(monkeypatch)
    secret = "never-print-this-token"

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1),
    )

    with pytest.raises(RuntimeError) as failure:
        remote["save_keychain_token"](secret)

    assert secret not in str(failure.value)
