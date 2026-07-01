# Gemini image API verified against google-genai 2.10.0:
# client.models.generate_images(model=..., prompt=...) -> GenerateImagesResponse
# response.generated_images[0].image.image_bytes
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

IAN_STYLE_PREFIX = (
    "16:9 horizontal illustration, pure white background, hand-drawn black ink sketch, "
    "sparse red orange blue annotations, clean editorial Ian Xiaohei style. Scene: "
)


def _generate_image(prompt: str) -> Any:
    """Call Gemini image model; isolated for testing."""
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return client.models.generate_images(
        model="gemini-2.5-flash-image",
        prompt=prompt,
    )


def build_illustrate_tool(*, assets_dir: Path) -> object:
    """Return LangChain illustrate tool writing PNG to assets_dir."""

    @tool
    def illustrate(scene: str, slug: str) -> str:
        """Generate Ian-style line art; return relative assets path."""
        prompt = IAN_STYLE_PREFIX + scene
        response = _generate_image(prompt)
        images = response.generated_images or []
        if not images or not images[0].image or not images[0].image.image_bytes:
            return f"assets/{slug}.png (generation failed)"
        image_bytes = images[0].image.image_bytes
        assets_dir.mkdir(parents=True, exist_ok=True)
        out = assets_dir / f"{slug}.png"
        out.write_bytes(image_bytes)
        return f"assets/{slug}.png"

    return illustrate
