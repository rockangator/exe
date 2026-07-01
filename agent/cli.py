from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from agent.config import require_env
from agent.explainer import PRIMARY_MODEL
from agent.pipeline import run_pipeline

app = typer.Typer(add_completion=False)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    topic: Annotated[list[str] | None, typer.Argument(help="Topic or question")] = None,
    model: Annotated[str, typer.Option(help="Primary model")] = PRIMARY_MODEL,
    skip_publish: Annotated[bool, typer.Option(help="Skip GitHub publish")] = False,
    user_id: Annotated[str, typer.Option(help="Mem0 user id")] = "default",
) -> None:
    """Research and publish an experiential explainer."""
    if ctx.invoked_subcommand is not None:
        return
    if not topic:
        console.print("[red]Topic required.[/red]")
        raise typer.Exit(code=1)

    require_env("TAVILY_API_KEY", "Create one at https://app.tavily.com")
    require_env("NEBIUS_API_KEY", "Create one at https://tokenfactory.nebius.com")

    topic_text = " ".join(topic)
    console.print(Panel.fit(topic_text, title="Topic", border_style="cyan"))

    try:
        run_pipeline(
            topic=topic_text,
            model=model,
            skip_publish=skip_publish,
            user_id=user_id,
        )
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted.[/red]")
        raise typer.Exit(code=130) from None
    except Exception as exc:
        console.print(f"\n[bold red]Pipeline failed:[/bold red] {exc}")
        raise typer.Exit(code=1) from None
