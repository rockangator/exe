from __future__ import annotations

import re


def citation_urls(article: str) -> set[str]:
    """Extract markdown link URLs and bare https URLs from article text."""
    urls: set[str] = set(re.findall(r"\(https?://[^)]+\)", article))
    urls = {u.strip("()") for u in urls}
    urls.update(re.findall(r"https?://[^\s)>]+", article))
    return urls


def all_citations_grounded(citations: set[str], source_urls: set[str]) -> bool:
    """Return True when every citation URL appears in extracted sources."""
    if not citations:
        return True
    return citations.issubset(source_urls)
