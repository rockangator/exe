from __future__ import annotations

import json
from pathlib import Path

from agent.explainer import build_system_prompt


def test_prompt_instructs_skip_for_glossary_concepts(fixtures_dir: str) -> None:
    data = json.loads(
        Path(fixtures_dir, "glossary_with_event_horizon.json").read_text(encoding="utf-8")
    )
    prompt = build_system_prompt(glossary=data["glossary"])
    assert "event horizon" in prompt
    assert "skip" in prompt.lower() or "cross-reference" in prompt.lower()
