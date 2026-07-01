from __future__ import annotations

from agent.explainer import build_system_prompt, parse_agent_output


SAMPLE_OUTPUT = """# Black Holes

Black holes are regions where gravity wins.

Sources: https://example.com/a

```json
{"concepts": ["black hole", "event horizon"], "style_notes": ["ELI5 tone"]}
```
"""


def test_parse_agent_output_splits_body_and_trailer() -> None:
    body, trailer = parse_agent_output(SAMPLE_OUTPUT)
    assert "# Black Holes" in body
    assert "event horizon" in trailer["concepts"][1]
    assert "style_notes" in trailer


def test_build_system_prompt_includes_date_and_glossary() -> None:
    prompt = build_system_prompt(
        today="2026-07-01",
        style="Use ELI5 tone.",
        glossary=["event horizon"],
    )
    assert "2026-07-01" in prompt
    assert "event horizon" in prompt
    assert "include_domains" in prompt
