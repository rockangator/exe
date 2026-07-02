# Gemini image API verified 2026-07-01:
# gemini-3.1-flash-lite-image uses generate_content + response_modalities=["IMAGE"]
# NOT generate_images (returns 404 for this model)
# Docs: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-image
# Skill: https://github.com/tojileon/ian-xiaohei-illustrations-en
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from agent.illustrations.prompt import (
    STRUCTURE_TYPES,
    IllustrationSpec,
    build_xiaohei_prompt,
    extension_for_mime,
)

DEFAULT_IMAGE_MODEL = "gemini-3.1-flash-lite-image"


def _generate_image(prompt: str, *, model: str | None = None) -> tuple[bytes, str]:
    """Call Gemini Nano Banana Lite; return image bytes and mime type."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=model or os.getenv("GEMINI_IMAGE_MODEL", DEFAULT_IMAGE_MODEL),
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            mime = part.inline_data.mime_type or "image/png"
            return part.inline_data.data, mime
    raise RuntimeError("Gemini returned no image data")


def build_illustrate_tool(*, assets_dir: Path, article_theme: str = "") -> object:
    """Return LangChain illustrate tool using Ian Xiaohei prompt contract."""

    structure_help = ", ".join(STRUCTURE_TYPES)

    @tool
    def illustrate(
        core_idea: str,
        structure_type: str,
        xiaohei_action: str,
        slug: str,
        labels: str = "",
        composition: str = "",
    ) -> str:
        """Generate one Ian Xiaohei 16:9 body illustration for the article.

        Args:
            core_idea: One cognitive anchor this image explains.
            structure_type: One of Workflow, System Fragment, Before/After Contrast,
                Character State, Conceptual Metaphor, Layered Method, Route Map,
                Small Comic Sequence.
            xiaohei_action: What Xiaohei physically does in the scene.
            slug: Filename slug, e.g. rag-retrieval-loop.
            labels: Comma-separated short English labels (3-5).
            composition: Optional layout description.
        """
        label_list = [part.strip() for part in labels.split(",") if part.strip()]
        spec = IllustrationSpec(
            core_idea=core_idea,
            structure_type=structure_type,
            xiaohei_action=xiaohei_action,
            slug=slug,
            article_theme=article_theme,
            composition=composition,
            labels=label_list,
        )
        prompt = build_xiaohei_prompt(spec)
        image_bytes, mime_type = _generate_image(prompt)
        ext = extension_for_mime(mime_type)
        assets_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{slug}{ext}"
        out = assets_dir / filename
        out.write_bytes(image_bytes)
        return f"assets/{filename}"

    illustrate.description = (
        "Generate one Ian Xiaohei weird-but-clean 16:9 article illustration. "
        f"structure_type must be one of: {structure_help}. "
        "Xiaohei must perform the core action. Returns relative assets path."
    )
    return illustrate
