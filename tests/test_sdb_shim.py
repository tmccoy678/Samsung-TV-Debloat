from __future__ import annotations

import runpy
from pathlib import Path


SDB_SHIM = Path(__file__).resolve().parents[1] / "tools/sdb"


def test_device_model_comes_from_the_live_sdb_banner() -> None:
    module = runpy.run_path(str(SDB_SHIM))

    assert module["model_from_banner"]("device::UN65TU7000BXZA::") == "UN65TU7000BXZA"
    assert module["model_from_banner"]("unexpected") == "unknown"
