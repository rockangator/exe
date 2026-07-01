from __future__ import annotations

from typing import Any

from langchain_tavily import TavilyExtract, TavilySearch

from agent.models import SourceRecord

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


def research_topic(
    query: str,
    *,
    include_domains: list[str] | None = None,
    top_n: int = 1,
) -> list[SourceRecord]:
    """Search Tavily, extract top result(s), return structured sources."""
    search = _get_search_tool()
    extract = _get_extract_tool()

    invoke_args: dict[str, Any] = {"query": query}
    if include_domains:
        invoke_args["include_domains"] = include_domains

    search_payload = search.invoke(invoke_args)
    results = search_payload.get("results", []) if isinstance(search_payload, dict) else []
    if not results:
        return []

    chosen = results[:top_n]
    urls = [r["url"] for r in chosen if r.get("url")]
    if not urls:
        return []

    extract_payload = extract.invoke({"urls": urls})
    if not isinstance(extract_payload, dict):
        return []

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
