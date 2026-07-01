# Design: exe (Experiential Explainer)

**Date:** 2026-07-01  
**Status:** Approved pending final spec review  
**Assignment:** Tavily FDE Take-Home, Option 1

---

## 1. Thesis

The starter answers in the console and forgets. **exe** researches the live web, remembers your voice and what it has already covered, and ships a durable, cited, illustrated explainer as a public artifact in this repo.

Project name: **exe** (experiential-explainer). Repo folder: `exe`.

---

## 2. Scope

### In scope: eight pipeline stages

1. **Research** — Tavily search + extract
2. **Memory read** — Mem0 style profile + glossary
3. **Generate** — Nebius model drafts cited explainer (agent core)
4. **Illustrate** — Ian-style line-art via Gemini image API
5. **Memory write** — Mem0 stores new concepts + style updates
6. **Publish** — commit article, index, and assets to this repo
7. **Tracing** — LangSmith spans across every stage
8. **Evals** — grounding check + memory-behavior check

### Out of scope (enforced)

No orchestration gateway (Arcade, Composio), no multi-agent teams, no vector DB or RAG-over-corpus, no web UI, no code-execution sandbox, no prompt-injection hardening, no retry/queue infrastructure.

---

## 3. Architecture

Linear pipeline in `pipeline.py`. Each stage is a direct call. The agent sits in the middle for research, illustration, and synthesis.

```
CLI (typer)
  → memory read        Mem0 hosted: style + glossary           [direct]
  → agent run          create_agent(ChatNebius, tools)       [streaming]
  → parse output       split article body from JSON trailer
  → memory write       Mem0: concepts + style notes          [direct]
  → publish            git commit article + index + assets
  → run record         JSON artifact for evals
```

Tracing wraps every stage (section 8).

### Agent boundary (chosen approach)

**One agent run with three tools** (recommended and locked):

- `TavilySearch` — find candidate sources
- `TavilyExtract` — pull full content of chosen source(s)
- `illustrate` — generate Ian-style PNG, return relative path

The agent researches, illustrates, and drafts the cited explainer as its final answer. This preserves the starter's streaming UX and keeps synthesis inside the agent.

Rejected alternatives:

- **Research agent + separate generation call** — two LLM passes, weaker agent story
- **No agent** — discards starter lineage entirely

---

## 4. Module breakdown

```
exe/
  README.md
  pyproject.toml
  AGENTS.md
  .cursor/rules/standards.mdc
  .env.example
  .gitignore
  agent/
    __init__.py
    cli.py                 typer + rich streaming (starter idioms)
    pipeline.py            orchestrates linear flow
    research.py            TavilySearch + TavilyExtract tools
    memory.py              Mem0 read/write (style + glossary only)
    explainer.py           prompt assembly, agent build, output parse
    illustrate.py          illustrate tool (Gemini image API)
    publish.py             git commit/push artifact folder
    tracing.py             LangSmith setup + @traceable spans
  evals/
    fixtures/
    test_grounding.py
    test_memory.py
  docs/
    technical-statement.md
    build-record.md
  published/               generated artifacts (committed per run)
```

---

## 5. Tavily usage

Verified API constraints:

- `TavilySearch(max_results=5, include_raw_content=True)` — set **at instantiation** in `research.py`, never per call.
- Domain targeting via **`include_domains` tool argument at invocation**. System prompt instructs: for "top posts on X" requests, pass `include_domains=["reddit.com"]` (or the named site). Never use `site:` query strings.
- Flow: search to find candidates, `TavilyExtract` to pull full content of chosen source(s). Extract results are captured into the run record for evals.

---

## 6. Memory (Mem0 hosted)

Deployment: **hosted Mem0 platform** (`MEM0_API_KEY`).

Two record kinds per user:

- **Style profile** — voice, formatting preferences
- **Glossary** — concepts already explained, with dates

**Read** before run: condition prompt on voice, skip or cross-reference covered concepts.

**Write** after run: agent's final answer ends with a fenced JSON trailer:

```json
{"concepts": ["..."], "style_notes": ["..."]}
```

Pipeline parses it, stores to Mem0, strips from published markdown.

**Context hygiene:** Mem0 receives only style configs and glossary. Never raw Tavily content.

---

## 7. Illustration

`illustrate(scene: str, slug: str) -> str` — LangChain tool.

- Wraps scene in ian-xiaohei prompt template (pure white hand-drawn look, sparse red/orange/blue annotations per skill instructions)
- Calls Gemini low-cost image model via `google-genai` SDK (`gemini-2.5-flash-image`)
- Saves PNG to run artifact folder `assets/<slug>.png`
- Returns relative path for agent to embed: `![caption](assets/<slug>.png)`
- System prompt caps at 1–3 illustrations per run
- If `GEMINI_API_KEY` absent: tool not registered, prompt drops illustration instruction

---

## 8. Publishing

Target: **same repo** (`exe`). Each run writes to:

```
published/<YYYY-MM-DD>-<slug>/
  article.md      # final public explainer, illustrations embedded inline
  index.md        # short landing page linking to article + metadata
  assets/
    *.png         # illustration files referenced by article.md
```

### article.md (Option 2 quality bar)

The article is the primary deliverable. It must meet the Option 2 explainer standard:

- Useful to a developer, partner, or technical customer
- Clear documentation and communication; assumes public consumption
- Inline citations to retrieved sources (URLs)
- Embedded illustrations at relevant points in the prose
- Structured for readability: title, intro, sections, conclusion, sources

The agent drafts `article.md` content as its final answer (minus the JSON trailer). The pipeline writes it to disk with image paths resolved to `assets/`.

### index.md

Short entry point for the published folder:

- Title and one-line summary
- Link to `article.md`
- Run metadata: date, topic, source count
- Optional thumbnail of first illustration

### Git publish flow

`publish.py` runs:

```bash
git add published/<folder>/
git commit -m "publish: <slug>"
git push
```

Only the generated folder is staged. Returns public GitHub URL:

`https://github.com/<owner>/exe/blob/main/published/<folder>/article.md`

If push fails (offline), commit stays local and CLI reports it.

---

## 9. Model selection and fallback

Primary model: `moonshotai/Kimi-K2.6` (Nebius, matches starter default).

Fallback model: `deepseek-ai/DeepSeek-V4-Pro` (Nebius).

`explainer.py` wraps agent invocation:

1. Try primary model
2. On HTTP 500 or provider error from Nebius, retry once with fallback
3. Print dim yellow notice: `Primary model unavailable, falling back to DeepSeek-V4-Pro`
4. If both fail, exit 1 with red error panel (starter idiom)

CLI `--model` overrides primary only; fallback is always DeepSeek-V4-Pro unless changed in config constant.

---

## 10. Tracing and observability

LangSmith with current `LANGSMITH_*` variables:

- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT=exe` (or `experiential-explainer`)
- Endpoint: `api.smith.langchain.com`

Agent run traces automatically via LangChain. Each deterministic stage gets `@traceable(name="memory.read")` etc. with metadata tags (topic, run id).

Absent keys: tracing silently off, pipeline still runs.

---

## 11. Evals

Two pytest suites in `evals/`, runnable offline against `fixtures/`:

### Grounding (`test_grounding.py`)

- Deterministic: every citation URL in article appears in run record's extracted sources
- LLM-as-judge claim-to-source check behind `@pytest.mark.live` (CI stays offline)

### Memory behavior (`test_memory.py`)

- Given glossary containing concept X, assembled system prompt instructs skipping X
- Live-marked repeat-run test: second explainer cross-references rather than re-explains

---

## 12. CLI UX and error handling

Entry:

```bash
uv run exe "black holes ELI5"
```

Options:

- `--model` — primary model (default `moonshotai/Kimi-K2.6`)
- `--skip-publish`
- `--skip-illustrate`

Rendering evolves the starter idioms:

- Yellow tool-call/result panels
- Green streamed assistant text
- Cyan `console.rule` banner per pipeline stage

Error handling:

- `require_env` hard-fails for `TAVILY_API_KEY`, `NEBIUS_API_KEY`
- `MEM0_API_KEY`, `GEMINI_API_KEY`, `LANGSMITH_*` optional; each absence prints one dim warning and disables that stage
- `KeyboardInterrupt` → exit 130
- Agent failure → red panel, exit 1

---

## 13. Configuration

`.env.example`:

```
TAVILY_API_KEY=
NEBIUS_API_KEY=
MEM0_API_KEY=
GEMINI_API_KEY=
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=exe
```

Required: `TAVILY_API_KEY`, `NEBIUS_API_KEY`  
Optional: all others (graceful degradation)

Dependencies to add: `google-genai` (Gemini images). Existing: `mem0ai`, `langsmith`, `langchain-*`.

---

## 14. Code conventions

- uv for everything, Python 3.11+, pytest. Never call pip directly.
- `langchain-tavily` only (not deprecated community tool)
- All keys from environment variables. Never hardcode or print secrets.
- `from __future__ import annotations` at top of every module
- Full type hints, docstring contract on every public function
- Single responsibility per module
- rich for console, typer for CLI
- Today's date in system prompt for time-aware queries
- LangSmith uses `LANGSMITH_*` variables, not legacy `LANGCHAIN_*`
- Prose, docstrings, comments: punchy, direct, no em dashes, no filler

---

## 15. Definition of done

Per module: docstring contract, full type hints, at least one green test, runs clean under uv.

End-to-end: one real run producing `published/<folder>/` with `article.md` (cited, illustrated), `index.md`, and `assets/*.png`; visible LangSmith trace; both offline eval suites green.

---

## 16. Decisions log

| Decision | Choice | Rationale |
|---|---|---|
| Agent boundary | One agent, three tools | Preserves starter streaming UX, single synthesis pass |
| Mem0 | Hosted platform | Zero infra, cleanest integration demo |
| Illustration | Gemini via agent tool | Low cost, ian-xiaohei style, keys in env |
| Publish target | Same repo | User choice; no PAT/API needed |
| Article format | Option 2 quality bar | Public-ready explainer with inline diagrams |
| Model fallback | DeepSeek-V4-Pro on 500 | Resilience against Nebius primary failures |
| Project name | exe (experiential-explainer) | User naming |
