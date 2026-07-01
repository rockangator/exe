# AGENTS.md

Conventions for **exe** (experiential-explainer).

- uv for everything, Python 3.11+, pytest. Never call pip directly.
- langchain-tavily only. The langchain_community Tavily tool is deprecated.
- TavilySearch: include_raw_content=True and max_results set at instantiation. Tavily locks these at instantiation to keep response sizes predictable, and we rely on that. Domain targeting via include_domains at invocation.
- TavilyExtract: extract_depth="advanced", format="markdown". Extracted markdown feeds a markdown artifact with zero transformation.
- Mem0: platform MemoryClient, not the OSS Memory class. add(messages, user_id=...) and search(query, filters={"user_id": ...}). add() extracts asynchronously, so never read-after-write in the same run. Mem0 receives only style configs and the glossary, never raw Tavily content.
- All keys from environment variables. Never hardcode or print a secret.
- from __future__ import annotations in every module, full type hints, docstring contract on every public function.
- Single responsibility per module. rich for console output, typer for the CLI, mirroring the starter's UX.
- Today's date in the system prompt for time-aware queries (Tavily's own documented tip).
- LangSmith uses current LANGSMITH_ variables, not legacy LANGCHAIN_ ones. Endpoint api.smith.langchain.com.
- Prose, docstrings, comments: punchy, direct, no em dashes, no filler.
- Definition of done per module: docstring contract, at least one green test, runs clean under uv. Verify before reporting done. Never invent an API. If unsure a function or parameter exists, stop and ask.
