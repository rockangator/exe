from __future__ import annotations

import json
from pathlib import Path

from agent.sources import sources_from_extract_payload


def test_sources_from_extract_payload(fixtures_dir: str) -> None:
    payload = json.loads(
        Path(fixtures_dir, "extract_result.json").read_text(encoding="utf-8")
    )
    sources = sources_from_extract_payload(payload)
    assert len(sources) == 1
    assert sources[0].url == "https://example.com/black-holes"
    assert sources[0].markdown.startswith("# Black Holes")
