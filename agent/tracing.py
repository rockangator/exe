from __future__ import annotations

import os
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable[..., object])

_tracing_enabled = False


def setup_tracing() -> None:
    """Enable LangSmith when LANGSMITH_* vars are set; no-op otherwise."""
    global _tracing_enabled
    if not os.getenv("LANGSMITH_API_KEY"):
        _tracing_enabled = False
        return
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGSMITH_PROJECT", "exe")
    os.environ.setdefault("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    _tracing_enabled = os.getenv("LANGSMITH_TRACING", "").lower() == "true"


def configure_tracing() -> None:
    """Alias for setup_tracing."""
    setup_tracing()


def is_tracing_enabled() -> bool:
    """Return whether tracing is active."""
    return _tracing_enabled


def traceable(name: str, **kwargs: object) -> Callable[[F], F]:
    """Decorator wrapping langsmith @traceable when available, else identity."""

    def identity(fn: F) -> F:
        return fn

    if not is_tracing_enabled():
        return identity

    from langsmith import traceable as ls_traceable

    return ls_traceable(name=name, **kwargs)  # type: ignore[return-value]
