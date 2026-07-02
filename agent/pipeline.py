from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from agent.config import optional_env
from agent.explainer import (
    PRIMARY_MODEL,
    build_system_prompt,
    parse_agent_output,
    run_agent_with_fallback,
)
from agent.illustrate import build_illustrate_tool
from agent.memory import read_context, write_context
from agent.models import RunRecord, SourceRecord
from agent.publish import publish_to_github, write_artifact_folder
from agent.research import infer_include_domains, research_topic
from agent.tracing import setup_tracing, traceable

console = Console()


def slugify(topic: str) -> str:
    """Convert topic to filesystem slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return slug[:60] or "explainer"


@traceable(name="research", run_type="chain", metadata={"stage": "research"})
def stage_research(topic: str, include_domains: list[str] | None) -> list[SourceRecord]:
    """Tavily search then extract; return structured sources."""
    return research_topic(topic, include_domains=include_domains)


@traceable(name="memory.read", run_type="chain", metadata={"stage": "memory"})
def stage_memory_read(user_id: str) -> tuple[str, list[str]]:
    """Read style and glossary from Mem0."""
    return read_context(user_id=user_id)


@traceable(name="generate", run_type="chain", metadata={"stage": "generate"})
def stage_generate(
    *,
    topic: str,
    system_prompt: str,
    tools: list[object],
    model: str,
) -> str:
    """Run agent to draft explainer article."""
    return run_agent_with_fallback(
        system_prompt=system_prompt,
        tools=tools,
        model=model,
        question=topic,
    )


@traceable(name="memory.write", run_type="chain", metadata={"stage": "memory"})
def stage_memory_write(
    *,
    user_id: str,
    concepts: list[str],
    style_notes: list[str],
) -> None:
    """Write new concepts and style notes to Mem0."""
    write_context(user_id=user_id, concepts=concepts, style_notes=style_notes)


@traceable(name="publish", run_type="chain", metadata={"stage": "publish"})
def stage_publish(folder: Path, *, slug: str) -> str:
    """Publish artifact folder via PyGithub."""
    return publish_to_github(folder, slug=slug)


def run_pipeline(
    *,
    topic: str,
    user_id: str = "default",
    model: str = PRIMARY_MODEL,
    publish_base: Path | None = None,
    skip_publish: bool = False,
    include_domains: list[str] | None = None,
) -> RunRecord:
    """Orchestrate research, memory, generate, publish pipeline."""
    setup_tracing()
    publish_base = publish_base or Path("published")
    date_str = date.today().isoformat()
    slug = slugify(topic)
    folder = publish_base / f"{date_str}-{slug}"
    assets_dir = folder / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    console.rule("[bold cyan]Memory read")
    style, glossary = stage_memory_read(user_id)

    console.rule("[bold cyan]Research")
    domains = include_domains or infer_include_domains(topic)
    sources = stage_research(topic, domains)

    illustrate_enabled = optional_env("GEMINI_API_KEY", feature="Illustration")
    tools: list[object] = []
    if illustrate_enabled:
        tools.append(build_illustrate_tool(assets_dir=assets_dir, article_theme=topic))

    system_prompt = build_system_prompt(
        style=style,
        glossary=glossary,
        sources=sources,
        illustrate=illustrate_enabled,
    )

    console.rule("[bold cyan]Generate")
    raw = stage_generate(topic=topic, system_prompt=system_prompt, tools=tools, model=model)
    article_body, trailer = parse_agent_output(raw)
    concepts = trailer.get("concepts", [])

    console.rule("[bold cyan]Memory write")
    stage_memory_write(
        user_id=user_id,
        concepts=concepts,
        style_notes=trailer.get("style_notes", []),
    )

    console.rule("[bold cyan]Publish")
    folder = write_artifact_folder(
        base_dir=publish_base,
        slug=slug,
        date_str=date_str,
        topic=topic,
        article_body=article_body,
        source_count=len(sources),
    )
    if not skip_publish:
        if not optional_env("GITHUB_TOKEN", feature="GitHub publish"):
            console.print("[dim]Skipping publish: GITHUB_TOKEN not set[/dim]")
        else:
            try:
                url = stage_publish(folder, slug=slug)
                console.print(Panel(f"[link={url}]{url}[/link]", title="Published", border_style="green"))
            except Exception as exc:
                console.print(
                    Panel(
                        f"Local artifact saved at {folder}\nPublish failed: {exc}",
                        title="Publish failed",
                        border_style="red",
                    )
                )

    return RunRecord(
        topic=topic,
        slug=slug,
        sources=sources,
        article_body=article_body,
        concepts=concepts,
    )
