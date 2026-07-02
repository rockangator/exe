from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REFERENCES_DIR = Path(__file__).parent / "references"

STRUCTURE_TYPES = (
    "Workflow",
    "System Fragment",
    "Before/After Contrast",
    "Character State",
    "Conceptual Metaphor",
    "Layered Method",
    "Route Map",
    "Small Comic Sequence",
)


@dataclass
class IllustrationSpec:
    """Ian Xiaohei illustration spec before image generation."""

    core_idea: str
    structure_type: str
    xiaohei_action: str
    slug: str
    article_theme: str = ""
    composition: str = ""
    labels: list[str] | None = None
    sequence: int = 1


def _read_reference(name: str) -> str:
    return (REFERENCES_DIR / name).read_text(encoding="utf-8")


def build_xiaohei_prompt(spec: IllustrationSpec) -> str:
    """Build a full Ian Xiaohei image prompt from bundled skill references."""
    labels = spec.labels or []
    label_text = " / ".join(labels) if labels else "short English labels only"
    theme = spec.article_theme or spec.core_idea
    composition = spec.composition or (
        f"Xiaohei {spec.xiaohei_action}. Show one clear {spec.structure_type.lower()} structure."
    )
    style_dna = _read_reference("style-dna.md")
    xiaohei_ip = _read_reference("xiaohei-ip.md")

    return f"""Generate one standalone 16:9 horizontal English article illustration.

Visual DNA (from Ian Xiaohei style DNA):
{style_dna}

Recurring IP character (from Xiaohei IP):
{xiaohei_ip}

Theme:
{theme}

Structure type:
{spec.structure_type}

Core idea:
{spec.core_idea}

Composition:
{composition}

Xiaohei action:
{spec.xiaohei_action}

English handwritten labels:
{label_text}

Color use:
Black for main line art and Xiaohei. Orange for main flow/path/arrows. Red only for key warnings/problems/results. Blue only for secondary notes or feedback/system state.

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten English labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Invent a fresh visual metaphor for this article. Clear but not instructional, interesting but not childish, strange but clean.
"""


def extension_for_mime(mime_type: str) -> str:
    """Map response mime type to file extension."""
    if mime_type == "image/png":
        return ".png"
    if mime_type in {"image/jpeg", "image/jpg"}:
        return ".jpg"
    if mime_type == "image/webp":
        return ".webp"
    return ".png"
