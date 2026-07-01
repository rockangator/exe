from __future__ import annotations

import json
from pathlib import Path

from agent.evals.grounding import all_citations_grounded, citation_urls


def test_all_citations_grounded_passes_when_urls_in_sources(fixtures_dir: str) -> None:
    article = Path(fixtures_dir, "sample_article.md").read_text(encoding="utf-8")
    record = json.loads(Path(fixtures_dir, "sample_run_record.json").read_text(encoding="utf-8"))
    source_urls = {s["url"] for s in record["sources"]}
    citations = citation_urls(article)
    assert all_citations_grounded(citations, source_urls) is True


def test_all_citations_grounded_fails_on_invented_url() -> None:
    article = "See https://invented.example/fake"
    source_urls = {"https://example.com/black-holes"}
    assert all_citations_grounded(citation_urls(article), source_urls) is False
