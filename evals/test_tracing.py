from __future__ import annotations

import pytest

from agent.tracing import configure_tracing, is_tracing_enabled


def test_tracing_disabled_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    configure_tracing()
    assert is_tracing_enabled() is False


def test_tracing_enabled_with_all_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "exe")
    configure_tracing()
    assert is_tracing_enabled() is True
