from __future__ import annotations

import json
import re
from datetime import date
from typing import Any

from langchain.agents import create_agent
from langchain_nebius import ChatNebius

from agent.models import SourceRecord
from agent.streaming import console, stream_agent

PRIMARY_MODEL = "deepseek-ai/DeepSeek-V4-Pro"
FALLBACK_MODEL = "moonshotai/Kimi-K2.6"

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
    sources: list[SourceRecord] | None = None,
    illustrate: bool = True,
) -> str:
    """Assemble system prompt with date, memory, sources, Tavily rules, and article contract."""
    today = today or date.today().isoformat()
    glossary = glossary or []
    sources = sources or []
    glossary_block = ", ".join(glossary) if glossary else "none yet"
    illustration_rule = (
        "Generate 1-3 illustrations via illustrate(core_idea, structure_type, xiaohei_action, slug, labels). "
        "Pick structure_type from Workflow, System Fragment, Before/After Contrast, Character State, "
        "Conceptual Metaphor, Layered Method, Route Map, Small Comic Sequence. "
        "Embed returned assets paths in the article."
        if illustrate
        else "Do not call illustrate."
    )
    source_blocks: list[str] = []
    for src in sources:
        excerpt = src.markdown[:12000]
        source_blocks.append(
            f"### {src.title}\nURL: {src.url}\nScore: {src.score}\n\n{excerpt}"
        )
    sources_section = (
        "\n\n".join(source_blocks)
        if source_blocks
        else "No pre-extracted sources. Use only what you know."
    )
    return f"""You are exe, an experiential explainer agent. Today is {today}.

Write a public-ready article (Option 2 explainer quality): clear, useful to a technical reader, with inline source URLs and embedded illustration paths.

Style profile: {style or "default concise technical"}
Already explained concepts (skip or cross-reference): {glossary_block}

Pre-extracted sources (cite these URLs; do not invent sources):
{sources_section}

Research is already complete. Do not call TavilySearch or TavilyExtract.
{illustration_rule}

End your final answer with a fenced JSON trailer:
```json
{{"concepts": ["..."], "style_notes": ["..."]}}
```
"""


def build_agent(*, system_prompt: str, tools: list[object], model: str) -> Any:
    """Build LangChain agent with Nebius chat model."""
    chat = ChatNebius(model=model, streaming=True)
    return create_agent(model=chat, tools=tools, system_prompt=system_prompt)


def run_agent_with_fallback(
    *,
    system_prompt: str,
    tools: list[object],
    model: str,
    question: str,
) -> str:
    """Run agent; on provider error retry once with FALLBACK_MODEL."""
    try:
        agent = build_agent(system_prompt=system_prompt, tools=tools, model=model)
        return stream_agent(agent, question)
    except Exception as exc:
        if model == FALLBACK_MODEL:
            raise
        console.print(
            f"[dim yellow]Primary model unavailable ({exc}), falling back to {FALLBACK_MODEL}[/dim yellow]"
        )
        agent = build_agent(system_prompt=system_prompt, tools=tools, model=FALLBACK_MODEL)
        return stream_agent(agent, question)
