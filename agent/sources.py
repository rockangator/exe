from __future__ import annotations

from typing import Any

from agent.models import SourceRecord


def sources_from_extract_payload(payload: dict[str, Any]) -> list[SourceRecord]:
    """Map TavilyExtract JSON payload to SourceRecords; zero markdown transformation."""
    records: list[SourceRecord] = []
    for item in payload.get("results", []):
        markdown = item.get("raw_content") or item.get("content") or ""
        records.append(
            SourceRecord(
                url=item.get("url", ""),
                title=item.get("title", "Untitled"),
                markdown=markdown,
            )
        )
    return records
