# Build Record

## Method

Spec developed in conversation with an AI, then executed in Cursor with the
Superpowers methodology: brainstorm to design doc, design doc to task-level
plan, plan to execution with per-task verification. Every third-party SDK was
validated in isolation with one real call before anything was built on it.

Complete traces: [Traces](https://traces.com/s/jn7827mq05azyzw1vt1718f2cs89r4vj)

## Milestones


| Milestone      | Commit        | Delivered                                                         | Verified by                                                |
| -------------- | ------------- | ----------------------------------------------------------------- | ---------------------------------------------------------- |
| Bootstrap      | `ab4c56f`     | uv project, deps, gitignore, env template                         | `uv sync` and starter imports                              |
| Standards      | `0c01613`     | AGENTS.md, cursor rule                                            | files listed back                                          |
| Design + plan  | *(no commit)* | design doc, docs/PLAN.md                                          | approved in session; see course corrections                |
| Research layer | `7151bb3`     | agent/research.py TavilySearch and TavilyExtract factories        | live search and extract; markdown in `raw_content`         |
| Memory layer   | `2693354`     | agent/memory.py                                                   | Gate A `MemoryClient.search` live call; `2 passed` mocked  |
| Explainer      | `d742467`     | agent/explainer.py agent builder and output parser                | `evals/test_explainer.py` green                            |
| Illustrate     | `d61f0ff`     | agent/illustrate.py Ian Xiaohei tool, gemini-3.1-flash-lite-image | `evals/test_illustrate.py` mocked PNG write                |
| Publish        | `debff84`     | agent/publish.py artifact folder and PyGithub publish             | Gate C signature check; `evals/test_publish.py` green      |
| Tracing        | `97bdc5e`     | agent/tracing.py                                                  | `evals/test_tracing.py` with and without LANGSMITH_API_KEY |
| Evals          | `f05279e`     | evals/ on fixtures                                                | `uv run pytest` offline, no network                        |
| Docs + hygiene | `2c827b0`     | README demo, example artifact paths                               | README sections and published example linked               |


**Flag:** Design + plan has no matching commit. `docs/PLAN.md` and `docs/superpowers/specs/2026-07-01-experiential-explainer-design.md` exist on disk but were never committed.

## Key decisions


| Decision       | Choice                                                                                 |
| -------------- | -------------------------------------------------------------------------------------- |
| Agent boundary | Research deterministic in `agent/research.py`; agent synthesizes from injected sources |
| Default model  | `deepseek-ai/DeepSeek-V4-Pro` on Nebius (Kimi fallback)                                |
| Illustration   | Ian Xiaohei skill references bundled; Gemini `gemini-3.1-flash-lite-image`             |
| Publish        | PyGithub to `rockangator/exe`, repo auto-resolved from git remote                      |
| Evals          | Fixture-only pytest; no network in CI                                                  |


## Course corrections

1. **Design review.** User: "only change would be for step 7, where along with index and assets, i would also want the final explainer article with the illustration built in... This project is called exe... Also the nebius model might result in Error 500, use DeepSeek-V4-Pro as a fallback model." Added `article.md`, renamed project to exe, added Kimi-to-DeepSeek fallback.
2. **AGENTS.md conventions.** User supplied a corrected convention set (Mem0 `MemoryClient`, Tavily instantiation rules, LangSmith `LANGSMITH`_*) replacing the brief list; copied verbatim into AGENTS.md and standards.mdc.
3. **Mem0 async constraint.** User convention: "add() extracts asynchronously, so never read-after-write in the same run." Confirmed during Gate A before Task 8; fixture-only evals, no read-after-write in pipeline.
4. **Publish mechanism.** Design specified git subprocess; Gate C verified PyGithub `create_file` / `update_file` and implementation used PyGithub instead.
5. **Mid-execution: model, publish, Tavily visibility.** User: "lets keep deepseek as the default model"; GitHub push to `rockangator/exe`; TavilyExtract ran in LangSmith but not CLI. Swapped primary to DeepSeek, added `resolve_github_repo()`, moved Tavily into deterministic Research stage with Rich panels (`2fbe166`).
6. **Mid-execution: illustration.** User pointed to `gemini-3.1-flash-lite-image` (Nano Banana Lite) and [ian-xiaohei-illustrations-en](https://github.com/tojileon/ian-xiaohei-illustrations-en); refactored to `generate_content` with `response_modalities=["IMAGE"]` and bundled skill reference assets (`d61f0ff`).

## Build session trace

Published to [Traces](https://traces.com): [https://traces.com/s/jn7827mq05azyzw1vt1718f2cs89r4vj](https://traces.com/s/jn7827mq05azyzw1vt1718f2cs89r4vj)

Visibility: direct (link-only). Agent: Cursor. Trace ID: `005be0ef-110c-47ec-8fa0-e3cad690a07c`.