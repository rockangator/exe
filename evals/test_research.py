from __future__ import annotations

from unittest.mock import MagicMock, patch

from agent.research import build_research_tools, research_topic


def test_build_research_tools_instantiates_with_locked_params() -> None:
    with patch("agent.research.TavilySearch") as mock_search, patch(
        "agent.research.TavilyExtract"
    ) as mock_extract:
        mock_search.return_value = MagicMock(name="tavily_search")
        mock_extract.return_value = MagicMock(name="tavily_extract")
        tools = build_research_tools()
        mock_search.assert_called_once_with(max_results=5, include_raw_content=True)
        mock_extract.assert_called_once_with(extract_depth="advanced", format="markdown")
        assert len(tools) == 2


def test_research_topic_returns_structured_sources() -> None:
    search_payload = {
        "results": [
            {
                "url": "https://example.com/a",
                "title": "A",
                "score": 0.91,
                "content": "snippet",
            }
        ]
    }
    extract_payload = {
        "results": [
            {
                "url": "https://example.com/a",
                "title": "A",
                "raw_content": "# A\n\nBody",
            }
        ]
    }
    mock_search = MagicMock()
    mock_search.invoke.return_value = search_payload
    mock_extract = MagicMock()
    mock_extract.invoke.return_value = extract_payload

    with patch("agent.research._get_search_tool", return_value=mock_search), patch(
        "agent.research._get_extract_tool", return_value=mock_extract
    ):
        sources = research_topic("black holes", include_domains=["reddit.com"])

    assert len(sources) == 1
    assert sources[0].url == "https://example.com/a"
    assert sources[0].score == 0.91
    assert sources[0].markdown == "# A\n\nBody"
    mock_search.invoke.assert_called_once_with(
        {"query": "black holes", "include_domains": ["reddit.com"]}
    )
