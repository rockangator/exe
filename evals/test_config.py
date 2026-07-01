from __future__ import annotations

import os

import pytest

from agent.config import optional_env, require_env


def test_require_env_passes_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    require_env("TAVILY_API_KEY")  # should not raise


def test_require_env_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(SystemExit) as exc:
        require_env("TAVILY_API_KEY")
    assert exc.value.code == 1


def test_optional_env_returns_false_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MEM0_API_KEY", raising=False)
    assert optional_env("MEM0_API_KEY", feature="Mem0 memory") is False
