from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from agent.illustrate import IAN_STYLE_PREFIX, build_illustrate_tool


def test_build_illustrate_tool_writes_png(tmp_path: Path) -> None:
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    mock_image = MagicMock()
    mock_image.image_bytes = b"fakepng"
    mock_generated = MagicMock()
    mock_generated.image = mock_image
    mock_response = MagicMock()
    mock_response.generated_images = [mock_generated]

    with patch("agent.illustrate._generate_image", return_value=mock_response):
        tool = build_illustrate_tool(assets_dir=assets_dir)
        result = tool.invoke({"scene": "a black hole", "slug": "black-hole"})

    assert result == "assets/black-hole.png"
    assert (assets_dir / "black-hole.png").exists()


def test_ian_style_prefix_present() -> None:
    assert "pure white background" in IAN_STYLE_PREFIX.lower()
