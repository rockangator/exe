# Mem0 SDK verified against mem0ai 2.0.11:
# - from mem0 import MemoryClient  (mem0/__init__.py)
# - MemoryClient(api_key=...)      (mem0/client/main.py:__init__)
# - add(messages, user_id=...)     (mem0/client/main.py:add, kwargs include user_id)
# - search(query, filters={...})     (mem0/client/main.py:search, top-level user_id rejected)
from __future__ import annotations

import json
import os
from typing import Any

from agent.config import optional_env

_client: Any = None


def _get_client() -> Any:
    """Return cached Mem0 MemoryClient."""
    global _client
    if _client is not None:
        return _client
    from mem0 import MemoryClient

    _client = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
    return _client


def read_context(*, user_id: str) -> tuple[str, list[str]]:
    """Fetch style profile and glossary via MemoryClient.search."""
    if not optional_env("MEM0_API_KEY", feature="Mem0 memory"):
        return "", []
    client = _get_client()
    style_resp = client.search("style profile", filters={"user_id": user_id})
    glossary_resp = client.search("glossary concepts explained", filters={"user_id": user_id})
    style = " ".join(r.get("memory", "") for r in style_resp.get("results", []))
    glossary = [r.get("memory", "") for r in glossary_resp.get("results", []) if r.get("memory")]
    return style.strip(), glossary


def write_context(
    *,
    user_id: str,
    concepts: list[str],
    style_notes: list[str],
) -> None:
    """Store glossary and style notes via MemoryClient.add; no read-after-write same run."""
    if not os.getenv("MEM0_API_KEY"):
        return
    client = _get_client()
    messages: list[dict[str, str]] = []
    for concept in concepts:
        messages.append(
            {"role": "user", "content": json.dumps({"kind": "glossary", "concept": concept})}
        )
    for note in style_notes:
        messages.append(
            {"role": "user", "content": json.dumps({"kind": "style", "note": note})}
        )
    if messages:
        client.add(messages=messages, user_id=user_id)
