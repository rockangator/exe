from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from agent.illustrate import DEFAULT_IMAGE_MODEL, build_illustrate_tool
from agent.illustrations.prompt import IllustrationSpec, build_xiaohei_prompt


def test_build_xiaohei_prompt_includes_xiaohei_and_structure() -> None:
    prompt = build_xiaohei_prompt(
        IllustrationSpec(
            core_idea="RAG retrieves docs before generation",
            structure_type="Workflow",
            xiaohei_action="pulls documents into a funnel",
            slug="rag-workflow",
            labels=["retrieve", "augment", "generate"],
        )
    )
    assert "Xiaohei" in prompt
    assert "Workflow" in prompt
    assert "pulls documents into a funnel" in prompt
    assert "Pure white background" in prompt


def test_build_illustrate_tool_writes_image(tmp_path: Path) -> None:
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()

    with patch(
        "agent.illustrate._generate_image",
        return_value=(b"fakejpeg", "image/jpeg"),
    ):
        tool = build_illustrate_tool(assets_dir=assets_dir, article_theme="RAG explainer")
        result = tool.invoke(
            {
                "core_idea": "retrieval before generation",
                "structure_type": "Workflow",
                "xiaohei_action": "carries documents to the model",
                "slug": "rag-loop",
                "labels": "search,context,answer",
            }
        )

    assert result == "assets/rag-loop.jpg"
    assert (assets_dir / "rag-loop.jpg").exists()


def test_default_image_model_is_nano_banana_lite() -> None:
    assert DEFAULT_IMAGE_MODEL == "gemini-3.1-flash-lite-image"
