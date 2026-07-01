from __future__ import annotations

from agent.streaming import message_text, truncate


def test_message_text_from_string() -> None:
    class Msg:
        content = "hello"

    assert message_text(Msg()) == "hello"


def test_truncate_shortens_long_text() -> None:
    assert truncate("a" * 1000, limit=100).endswith("...")
