from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def message_text(message: Any) -> str:
    """Extract streamed text from a LangChain message or message chunk."""
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return ""


def flush() -> None:
    console.file.flush()


def truncate(value: Any, limit: int = 900) -> str:
    text = str(value).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def print_tool_call(name: str, args: Any) -> None:
    console.print()
    console.print(
        Panel(
            Text(truncate(args, limit=700)),
            title=f"Tool call: {name}",
            border_style="yellow",
        )
    )


def format_tool_result(content: Any) -> str:
    try:
        payload = json.loads(content) if isinstance(content, str) else content
    except json.JSONDecodeError:
        return truncate(content)

    if not isinstance(payload, dict) or "results" not in payload:
        return truncate(payload)

    lines = [f"Query: {payload.get('query', '')}", ""]
    for index, result in enumerate(payload.get("results", [])[:5], start=1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        snippet = " ".join(str(result.get("content", "")).split())
        lines.append(f"{index}. {title}")
        lines.append(f"   {url}")
        if snippet:
            lines.append(f"   {truncate(snippet, limit=220)}")
        lines.append("")
    return "\n".join(lines).strip()


def print_tool_result(message: Any) -> None:
    name = getattr(message, "name", None) or "tool"
    content = format_tool_result(getattr(message, "content", ""))
    console.print()
    console.print(
        Panel(
            Text(content),
            title=f"Tool result: {name}",
            border_style="yellow",
        )
    )


def stream_agent(agent: Any, question: str) -> str:
    """Stream agent run to console; return collected assistant text."""
    console.rule("[bold blue]Agent stream")
    tool_buffers: dict[str, dict[str, str]] = {}
    printed_tool_calls: set[str] = set()
    assistant_started = False
    last_event_was_text = False
    collected: list[str] = []

    stream = agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode=["messages", "updates"],
    )

    for mode, data in stream:
        if mode == "messages":
            message, _metadata = data
            if getattr(message, "type", None) == "tool":
                continue

            tool_call_chunks = getattr(message, "tool_call_chunks", []) or []
            if tool_call_chunks:
                if last_event_was_text:
                    console.print()
                    last_event_was_text = False
                for chunk in tool_call_chunks:
                    key = str(chunk.get("id") or chunk.get("index") or "tool_call")
                    buffer = tool_buffers.setdefault(key, {"name": "", "args": ""})
                    if chunk.get("name"):
                        buffer["name"] += chunk["name"]
                    if chunk.get("args"):
                        buffer["args"] += chunk["args"]
                    if key not in printed_tool_calls and buffer["name"]:
                        printed_tool_calls.add(key)
                        console.print(
                            f"\n[bold yellow]Tool call[/bold yellow] [yellow]{buffer['name']}[/yellow]",
                            highlight=False,
                        )
                        console.print("[dim yellow]args: [/dim yellow]", end="")
                    if chunk.get("args"):
                        console.print(chunk["args"], style="yellow", end="", highlight=False)
                        flush()
                continue

            text = message_text(message)
            if text:
                if not assistant_started:
                    if printed_tool_calls:
                        console.print()
                    console.print("\n[bold green]Assistant[/bold green]")
                    assistant_started = True
                console.print(text, end="", highlight=False, markup=False)
                collected.append(text)
                flush()
                last_event_was_text = True

        elif mode == "updates":
            for node_update in data.values():
                for message in node_update.get("messages", []):
                    if getattr(message, "type", None) == "ai":
                        for tool_call in getattr(message, "tool_calls", []) or []:
                            key = str(
                                tool_call.get("id") or tool_call.get("name") or "tool_call"
                            )
                            if key not in printed_tool_calls:
                                printed_tool_calls.add(key)
                                print_tool_call(
                                    tool_call.get("name", "tool"),
                                    tool_call.get("args", {}),
                                )
                    if getattr(message, "type", None) == "tool":
                        if last_event_was_text:
                            console.print()
                            last_event_was_text = False
                        print_tool_result(message)

    if last_event_was_text:
        console.print()
    return "".join(collected)
