from __future__ import annotations

from agent.models import RunRecord, SourceRecord


def test_run_record_serializes_extracted_sources() -> None:
    record = RunRecord(
        topic="black holes ELI5",
        slug="black-holes-el5",
        sources=[
            SourceRecord(
                url="https://example.com/a",
                title="A",
                markdown="# A",
                score=0.9,
            ),
        ],
    )
    data = record.to_dict()
    assert data["topic"] == "black holes ELI5"
    assert data["sources"][0]["url"] == "https://example.com/a"
    assert data["sources"][0]["score"] == 0.9
