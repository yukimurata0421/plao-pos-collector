from __future__ import annotations

from pathlib import Path
import pytest


@pytest.fixture()
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture()
def copy_fixture(fixtures_dir):
    def _copy(name: str, dst: Path) -> None:
        src = fixtures_dir / name
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return _copy
