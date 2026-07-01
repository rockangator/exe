from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent.memory import read_context, write_context


def test_read_context_returns_style_and_glossary(fixtures_dir: str) -> None:
    style_payload = json.loads(
        Path(fixtures_dir, "mem0_search_style.json").read_text(encoding="utf-8")
    )
    glossary_payload = json.loads(
        Path(fixtures_dir, "mem0_search_glossary.json").read_text(encoding="utf-8")
    )
    mock_client = MagicMock()
    mock_client.search.side_effect = [style_payload, glossary_payload]

    with patch("agent.memory._get_client", return_value=mock_client):
        style, glossary = read_context(user_id="demo-user")

    assert "ELI5" in style
    assert "event horizon" in glossary
    calls = mock_client.search.call_args_list
    assert calls[0].kwargs["filters"] == {"user_id": "demo-user"}
    assert calls[1].kwargs["filters"] == {"user_id": "demo-user"}


def test_write_context_calls_add_not_search() -> None:
    mock_client = MagicMock()
    with patch("agent.memory._get_client", return_value=mock_client):
        write_context(
            user_id="demo-user",
            concepts=["singularity"],
            style_notes=["more diagrams"],
        )
    assert mock_client.add.called
    assert not mock_client.search.called
    mock_client.add.assert_called_once()
    _, kwargs = mock_client.add.call_args
    assert kwargs["user_id"] == "demo-user"
