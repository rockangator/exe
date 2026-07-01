from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from agent.config import require_env
from agent.explainer import PRIMARY_MODEL
from agent.pipeline import run_pipeline

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    topic: str = typer.Argument(..., help="Topic or question"),
    model: str = typer.Option(PRIMARY_MODEL, help="Primary model"),
    skip_publish: bool = typer.Option(False, "--skip-publish", help="Skip GitHub publish"),
    user_id: str = typer.Option("default", help="Mem0 user id"),
) -> None:
    """Research and publish an experiential explainer."""
    require_env("TAVILY_API_KEY", "Create one at https://app.tavily.com")
    require_env("NEBIUS_API_KEY", "Create one at https://tokenfactory.nebius.com")

    console.print(Panel.fit(topic, title="Topic", border_style="cyan"))

    try:
        run_pipeline(
            topic=topic,
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
