# Research Explainer Agent

Tavily FDE take-home (Option 1): a CLI that researches the live web with Tavily and ships a cited, illustrated explainer as a shareable artifact.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```bash
# Create virtual environment and install dependencies
uv sync

# Copy env template and add your keys
cp .env.example .env
```

Required keys:

- `TAVILY_API_KEY` from [app.tavily.com](https://app.tavily.com)
- `NEBIUS_API_KEY` from [tokenfactory.nebius.com](https://tokenfactory.nebius.com)

## Verify starter agent (local only)

The original `starter_agent.py` is kept locally for smoke tests but is not committed to this repo.

```bash
uv run starter_agent.py "What changed in the AI search market this year?"
```

## Project status

Initial environment setup. Full pipeline implementation in progress.
