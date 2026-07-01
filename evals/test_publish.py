from __future__ import annotations

from pathlib import Path

from agent.publish import build_index_md, write_artifact_folder


def test_write_artifact_folder_creates_article_index_assets(tmp_path: Path) -> None:
    folder = write_artifact_folder(
        base_dir=tmp_path,
        slug="black-holes",
        date_str="2026-07-01",
        topic="black holes ELI5",
        article_body="# Black Holes\n\nSee ![hole](assets/hole.png)",
        source_count=2,
    )
    assert (folder / "article.md").exists()
    assert (folder / "index.md").exists()
    assert (folder / "assets").is_dir()
    assert "black holes ELI5" in (folder / "index.md").read_text(encoding="utf-8")


def test_build_index_md_links_article() -> None:
    md = build_index_md(
        title="Black Holes",
        summary="ELI5 guide",
        topic="black holes",
        source_count=1,
        date_str="2026-07-01",
    )
    assert "[Read the explainer](./article.md)" in md
