from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "live: live API tests")


@pytest.fixture
def fixtures_dir() -> str:
    from pathlib import Path

    return str(Path(__file__).parent / "fixtures")
