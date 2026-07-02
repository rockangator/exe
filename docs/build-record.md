# Build Record

## Approach

Built with Cursor Agent using the Superpowers workflow: brainstorming spec, implementation plan (`docs/PLAN.md`), subagent-driven task execution with TDD, and verification gates before Mem0, LangSmith, PyGithub, and Tavily API calls.

## Key decisions

| Decision | Choice |
|----------|--------|
| Agent boundary | Research deterministic in `agent/research.py`; agent synthesizes from injected sources |
| Default model | `deepseek-ai/DeepSeek-V4-Pro` on Nebius (Kimi fallback) |
| Illustration | Ian Xiaohei skill references bundled; Gemini `gemini-3.1-flash-lite-image` |
| Publish | PyGithub to `rockangator/exe`, repo auto-resolved from git remote |
| Evals | Fixture-only pytest; no network in CI |

## Commits

See `git log --oneline` on `main` from scaffold through illustration and publish fixes.

## API verification notes

- Mem0: `MemoryClient.search(query, filters={"user_id": ...})`, `add(messages, user_id=...)`
- LangSmith: `LANGSMITH_*` env vars, `@traceable` on pipeline stages
- PyGithub: `repo.create_file` / `update_file` for markdown and binary assets
- Tavily: `include_raw_content` and `max_results` at instantiation; `include_domains` at invocation
- Gemini image: `generate_content` with `response_modalities=["IMAGE"]`, not `generate_images`
