# exe (Experiential Explainer)

Tavily FDE take-home (Option 1): researches the live web, remembers your voice and glossary via Mem0, and publishes a cited explainer to GitHub.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```bash
uv sync
cp .env.example .env   # add your keys
```

**Required:** `TAVILY_API_KEY`, `NEBIUS_API_KEY`  
**Optional:** `MEM0_API_KEY`, `GEMINI_API_KEY`, `GITHUB_TOKEN`, `GITHUB_REPO`, `LANGSMITH_*`

## Run

```bash
uv run exe "black holes ELI5"
uv run exe "top ELI5 posts on reddit" --skip-publish
```

Options: `--model`, `--skip-publish`, `--user-id`

## Output

Each run writes `published/<date>-<slug>/`:

- `article.md` — full explainer with inline citations
- `index.md` — landing page
- `assets/` — illustrations (when enabled)

With `GITHUB_TOKEN` and `GITHUB_REPO` set, publishes via PyGithub.

## Tests

```bash
uv run pytest -v              # offline fixtures only
uv run pytest -m live -v      # live API tests (optional)
```

## LangSmith span tree

When `LANGSMITH_*` is set, expect:

```
run_pipeline
├── research
├── memory.read
├── generate
├── memory.write
└── publish
```

Agent tool calls nest under `generate` via LangChain auto-tracing.
