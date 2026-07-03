
# From answer to artifact

**The starter agent answers a question in the console and forgets the run
ever happened. This one researches the live web, writes in a style it
remembers, illustrates the result, and commits a cited explainer to GitHub.
One command in, public URL out.**

---

## What it is

The starter's CLI, extended into a pipeline. Same foundation: LangChain
`create_agent`, a Nebius-hosted model, `typer` entry, `rich` streaming. What
changed is where the output goes: the console print at the end of the starter
is now a research, memory, generation, illustration, and publish sequence
that ends in a versioned artifact instead of scrollback.

## What it does

Give it a topic. It searches with Tavily, extracts the strongest source as
markdown, drafts an explainer in the remembered style, skips concepts it has
already explained to you, generates hand-drawn illustrations, and commits the
finished piece to GitHub. Every claim cites its source. Every stage lands in
one trace.

**See one:** [What are sea lions?](https://github.com/rockangator/exe/blob/main/published/2026-07-01-what-are-sea-lions/article.md)



## Five components, one pipeline


| Component                                                                                                          | Role here                                                                                                                                                                                                                    | Assignment direction it hits                     |
| ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| **Tavily Search + Extract**                                                                                        | `include_domains` targeting finds the right community source; Extract pulls it as markdown, so retrieved content feeds the artifact with zero transformation                                                                 | Retrieval quality, source handling and citations |
| **Mem0**                                                                                                           | Stores only a style profile and a glossary of explained concepts. Second run adapts and skips. A memory layer alongside the Tavily stack  | A useful integration, context engineering        |
| **Ian's illustrate skill** ([ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations)) | Hand-drawn body illustrations generated in-pipeline, referenced by relative path                                                                                                                                             | A useful integration                             |
| **GitHub publish**                                                                                                 | Commits markdown and PNGs together, returns the public URL. No image host dependency                                                                                                                                         | Adapt to a specific customer workflow            |
| **LangSmith + evals**                                                                                              | One span per stage with metadata tags; grounding and memory tests on recorded fixtures                                                                                                                                       | Evaluation loop, observability bonus             |


## The value

**Business.** Research-to-published-doc is a daily workflow for content teams,
dev-rel, and internal docs: one person, twelve tabs, half a day per piece.
This runs it as one command.

- The output is cited and grounding-checked, so it can be published without a
  full manual fact pass. That check is what makes the automation usable, not
  a nice-to-have on top of it.
- Memory carries a style profile and a glossary across runs, so the second
  artifact costs the same command but fits the user better and repeats
  nothing. Per-run value goes up with use instead of resetting.
- Publishing lands in GitHub, where a content team already reviews and
  versions. The agent joins an existing workflow rather than adding a new
  destination.

**Technical.** One deliberate decision per integration:

- **langchain-tavily**: `TavilySearch` is instantiated with
  `include_raw_content=True` locked in, Tavily's own guardrail for
  predictable response sizes, with `include_domains` passed per query for
  source targeting. `TavilyExtract` runs with `format="markdown"`, so
  extracted content is already in the artifact's format and citations
  survive untouched.
- **Mem0**: `add()` extracts facts asynchronously, so the pipeline never
  reads back what it just wrote within a run. Memory stores only the style
  profile and glossary, never raw Tavily content, keeping reads small and
  retrieval fresh every run.
- **PyGithub**: markdown and PNGs commit together in one push, images
  referenced by relative path. The published artifact has no external image
  host to break.
- **LangSmith**: each pipeline stage is a named span with metadata tags. A
  bad artifact is attributable to research, memory, generation, or publish
  from the trace alone, no rerun.
- **pytest on recorded fixtures**: the eval suite makes no network calls.
  Grounding and memory behavior are tested deterministically, which Mem0's
  async writes would otherwise make impossible against the live API.

  
## How I got here

I spec'd this in conversation with an AI before writing a line, then fed the brief into Cursor running the Superpowers methodology: brainstorm, plan, execute, with TDD and scope locked up front. Every third-party SDK got validated in isolation, one real call with real output inspected, before anything was built on it. Mem0's async fact extraction surfaced this way, so the design never reads back what it just wrote, and the eval suite runs on fixtures instead of a live API.

My first instinct was different. I had found a non-UTF-8 encoding bug in the Research endpoint and wanted to build around fixing it. It was real, but it was a bug report, not a build, and a different problem from what a user of this starter faces. Meanwhile the demand for this build was everywhere I looked: Tavily's own deep research writeup names content generation as where research agents are headed, builders are publishing research-to-article agents on Tavily right now, and Option 2 of this assignment literally asks for an explainer. The need was sitting in the brief. I built the machine that produces it.

Full build record: [docs/build-record.md](./build-record.md). Complete session traces: [https://traces.com/s/jn7501whf555rarz09m8w59rdn89vmty](https://traces.com/s/jn7501whf555rarz09m8w59rdn89vmty)

## A pattern, not a product

The explainer is one instantiation. Swap the prompt and the publish target and the same eight stages become a competitive-brief agent posting to Notion, a changelog-to-blog pipeline for dev-rel, a meeting-prep researcher dropping briefs into a CRM, or a personalized learning track that never re-teaches what you know. Research, remember, ground, publish, trace. The spine holds.

## Observability and evals

Each pipeline stage is its own LangSmith span with metadata tags, so a bad artifact is diagnosable to a stage in seconds, not a rerun.

Example trace for `What are sea lions?`: [LangSmith public trace](https://smith.langchain.com/public/cfdcab9a-f3cd-4af7-bf87-e2746220e57b/r/019f2049-cf28-7711-bd9b-0d912a203e78)

![LangSmith trace: LangGraph run with model and illustrate tool spans for What are sea lions?](demo/langsmith_trace.PNG)

Two evals guard the two claims that matter. `test_grounding.py` asserts every factual claim in the explainer traces to the extracted source: retrieved web content is untrusted input, and the artifact must never say more than its source supports. `test_memory.py` asserts a second run skips a concept already in the glossary. Both run on recorded fixtures, deterministic and fast.

## What I did not build

No orchestration gateway. No multi-agent team. No vector DB. No web UI. Every integration is a direct call, because at this scale a framework between you and five APIs is surface area, not leverage. Small thing, done well.

## Why it fits Tavily

Research-to-cited-artifact is the pattern Tavily already ships to customers: the use-cases repo compiles cited research reports, tavily-sheets fills spreadsheets with sourced insights. This build keeps that pattern transparent, self-hosted on Nebius, and observable end to end.

