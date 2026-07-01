from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


def require_env(name: str, instructions: str = "") -> None:
    """Exit 1 if required env var is missing."""
    if os.getenv(name):
        return
    console.print(f"[bold red]Missing {name}[/bold red]")
    if instructions:
        console.print(instructions)
    sys.exit(1)


def optional_env(name: str, feature: str) -> bool:
    """Return True if optional env var is set; print dim warning and return False if missing."""
    if os.getenv(name):
        return True
    console.print(f"[dim]Skipping {feature}: {name} not set[/dim]")
    return False
