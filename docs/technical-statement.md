# Technical Statement

## Thesis

The starter answers in the console and forgets. **exe** researches the live web, remembers style and glossary via Mem0, drafts a cited illustrated explainer, and publishes a durable artifact to GitHub.

## What it is

A linear CLI pipeline with an agent core for synthesis. Tavily handles search and extract. Mem0 stores style and glossary only. The Nebius-hosted model drafts the article. Ian Xiaohei illustrations optional via Gemini. PyGithub publishes markdown and assets.

## Four moves and their value

1. **Tavily search + extract** — domain targeting via `include_domains`, full markdown from extract, zero transformation into the artifact.
2. **Mem0** — style profile and glossary prevent repetition; raw Tavily content never enters memory.
3. **GitHub publish** — real shareable URL with `article.md`, `index.md`, and `assets/`.
4. **LangSmith + fixture evals** — spans per stage; offline tests guard grounding and memory conditioning.

## What we deliberately did not build

- No orchestration gateway, multi-agent teams, or web UI.
- No vector DB or RAG-over-corpus beyond live Tavily retrieval.
- No prompt-injection hardening or code-execution sandbox.

Composition over a heavy runtime.

## Verification

- `uv run pytest evals/ -q` offline suite green.
- Live runs produce `published/<date>-<slug>/` with cited `article.md`.
- LangSmith shows `research`, `memory.read`, `generate`, `memory.write`, `publish` spans when tracing is enabled.
