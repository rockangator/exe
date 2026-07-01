from __future__ import annotations

import json
import re
from datetime import date
from typing import Any


JSON_TRAILER_RE = re.compile(
    r"```json\s*(\{.*?\})\s*```\s*$",
    re.DOTALL,
)


def parse_agent_output(raw: str) -> tuple[str, dict[str, Any]]:
    """Split agent final answer into article body and parsed JSON trailer."""
    match = JSON_TRAILER_RE.search(raw.strip())
    if not match:
        return raw.strip(), {"concepts": [], "style_notes": []}
    body = raw[: match.start()].strip()
    trailer = json.loads(match.group(1))
    return body, trailer


def build_system_prompt(
    *,
    today: str | None = None,
    style: str = "",
    glossary: list[str] | None = None,
    illustrate: bool = True,
) -> str:
    """Assemble system prompt with date, memory, Tavily rules, and article contract."""
    today = today or date.today().isoformat()
    glossary = glossary or []
    glossary_block = ", ".join(glossary) if glossary else "none yet"
    illustration_rule = (
        "Generate 1-3 illustrations via the illustrate tool; embed paths in the article."
        if illustrate
        else "Do not call illustrate."
    )
    return f"""You are exe, an experiential explainer agent. Today is {today}.

Write a public-ready article (Option 2 explainer quality): clear, useful to a technical reader, with inline source URLs and embedded illustration paths.

Style profile: {style or "default concise technical"}
Already explained concepts (skip or cross-reference): {glossary_block}

Tavily rules:
- Use TavilySearch to find sources. Pass include_domains at invocation for site targeting (e.g. ["reddit.com"]). Never put site: in the query string.
- Use TavilyExtract to pull full markdown from chosen URLs.
{illustration_rule}

End your final answer with a fenced JSON trailer:
```json
{{"concepts": ["..."], "style_notes": ["..."]}}
```
"""
