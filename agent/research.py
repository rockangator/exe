from __future__ import annotations

import json
from typing import Any

from langchain_tavily import TavilyExtract, TavilySearch
from rich.panel import Panel
from rich.text import Text

from agent.models import SourceRecord
from agent.streaming import console, truncate

_search_tool: TavilySearch | None = None
_extract_tool: TavilyExtract | None = None


def _get_search_tool() -> TavilySearch:
    """Return singleton TavilySearch with locked instantiation params."""
    global _search_tool
    if _search_tool is None:
        _search_tool = TavilySearch(max_results=5, include_raw_content=True)
    return _search_tool


def _get_extract_tool() -> TavilyExtract:
    """Return singleton TavilyExtract with locked instantiation params."""
    global _extract_tool
    if _extract_tool is None:
        _extract_tool = TavilyExtract(extract_depth="advanced", format="markdown")
    return _extract_tool


def build_research_tools() -> list[Any]:
    """Return TavilySearch and TavilyExtract LangChain tools for the agent."""
    return [_get_search_tool(), _get_extract_tool()]


def infer_include_domains(query: str) -> list[str] | None:
    """Infer include_domains when the query targets a community site."""
    lowered = query.lower()
    if "reddit" in lowered or "eli5" in lowered:
        return ["reddit.com"]
    return None


def research_topic(
    query: str,
    *,
    include_domains: list[str] | None = None,
    top_n: int = 1,
) -> list[SourceRecord]:
    """Search Tavily, extract top result(s), return structured sources."""
    search = _get_search_tool()
    extract = _get_extract_tool()
    include_domains = include_domains or infer_include_domains(query)

    invoke_args: dict[str, Any] = {"query": query}
    if include_domains:
        invoke_args["include_domains"] = include_domains

    console.print(Panel(Text(f"query: {query}\ninclude_domains: {include_domains}"), title="TavilySearch", border_style="yellow"))
    search_payload = search.invoke(invoke_args)
    results = search_payload.get("results", []) if isinstance(search_payload, dict) else []
    if not results:
        console.print("[dim yellow]TavilySearch returned no results[/dim yellow]")
        return []

    summary_lines = []
    for index, result in enumerate(results[:5], start=1):
        summary_lines.append(
            f"{index}. {result.get('title', 'Untitled')} ({result.get('score', 0)})\n   {result.get('url', '')}"
        )
    console.print(Panel(Text("\n".join(summary_lines)), title="TavilySearch results", border_style="yellow"))

    chosen = results[:top_n]
    urls = [r["url"] for r in chosen if r.get("url")]
    if not urls:
        return []

    console.print(Panel(Text(json.dumps({"urls": urls}, indent=2)), title="TavilyExtract", border_style="yellow"))
    extract_payload = extract.invoke({"urls": urls})
    if not isinstance(extract_payload, dict):
        console.print(Panel(Text(truncate(extract_payload)), title="TavilyExtract result", border_style="yellow"))
        return []

    extract_preview = []
    for item in extract_payload.get("results", []):
        markdown = item.get("raw_content") or item.get("content") or ""
        extract_preview.append(
            f"{item.get('title', 'Untitled')}\n{truncate(markdown, limit=500)}"
        )
    if not extract_preview:
        console.print(Panel(Text(truncate(extract_payload)), title="TavilyExtract result", border_style="yellow"))
    else:
        console.print(Panel(Text("\n\n".join(extract_preview)), title="TavilyExtract result", border_style="yellow"))

    score_by_url = {r["url"]: float(r.get("score", 0.0)) for r in chosen if r.get("url")}
    title_by_url = {r["url"]: r.get("title", "Untitled") for r in chosen if r.get("url")}

    sources: list[SourceRecord] = []
    for item in extract_payload.get("results", []):
        url = item.get("url", "")
        markdown = item.get("raw_content") or item.get("content") or ""
        sources.append(
            SourceRecord(
                url=url,
                title=item.get("title") or title_by_url.get(url, "Untitled"),
                markdown=markdown,
                score=score_by_url.get(url, 0.0),
            )
        )
    return sources
