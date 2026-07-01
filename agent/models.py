from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SourceRecord:
    """One extracted source captured for evals and citations."""

    url: str
    title: str
    markdown: str
    score: float = 0.0


@dataclass
class RunRecord:
    """JSON-serializable record of one pipeline run."""

    topic: str
    slug: str
    sources: list[SourceRecord] = field(default_factory=list)
    article_body: str = ""
    concepts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
