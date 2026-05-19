# engram-crewai

[CrewAI](https://github.com/crewAIInc/crewAI) integration for [Engram](https://lumetra.io) — durable shared memory for multi-agent crews.

Returns two CrewAI Tools (`engram_store_memory`, `engram_query_memory`) bound to a single Engram bucket that every agent in the crew can read from and write to. The crew's accumulated knowledge survives across runs, processes, and machines.

## Install

```bash
pip install lumetra-engram crewai
```

Vendor `engram_crewai.py` from this repo (~60 LOC). PyPI release coming.

```bash
export ENGRAM_API_KEY="eng_live_..."
```

## Get an Engram API key

Sign up at <https://lumetra.io> — free tier, no card. You'll see an `eng_live_…` token in your dashboard.

**Don't forget BYOK** — Engram is bring-your-own-key end-to-end for the LLM that does extraction + synthesis. Configure a provider at <https://lumetra.io/models>. DeepSeek is what we recommend. Without one, store/query returns HTTP 412.

## Usage

```python
from crewai import Agent, Crew, Task
from engram_crewai import engram_tools

tools = engram_tools(bucket="my-crew")

researcher = Agent(
    role="Researcher",
    goal="Investigate topics and remember findings for the rest of the crew.",
    backstory="You are a careful researcher who never forgets a fact.",
    tools=tools,
)

writer = Agent(
    role="Writer",
    goal="Synthesize findings into briefs. Consult Engram for context before writing.",
    backstory="...",
    tools=tools,
)

crew = Crew(agents=[researcher, writer], tasks=[...])
crew.kickoff()
```

Both agents now have:

- `engram_store_memory(content)` — save an atomic fact to the shared bucket.
- `engram_query_memory(question)` — hybrid retrieval + synthesized answer over everything the crew has stored so far.

## Why this beats CrewAI's built-in memory

- **Persists across runs.** CrewAI's built-in memory is per-process; the next `kickoff()` starts blank. Engram doesn't.
- **Shared across agents in the crew.** Engram is the team's institutional memory, not a per-agent scratchpad.
- **Hybrid retrieval** — BM25 + vector + knowledge graph fusion, not vector-only.
- **Bring-your-own-LLM** for extraction and synthesis (<https://lumetra.io/models>).
- **Per-crew buckets** — pass `bucket=f"crew-{project_id}"` and isolation is automatic.

## Verified

Smoke-tested against live `api.lumetra.io` — three facts stored to a shared bucket via the `engram_store_memory` tool, then a `engram_query_memory` call asked a question whose answer required combining two of them. Engram returned a single synthesized answer that fused both source memories, and the explanation trace cited each.

## License

MIT — Lumetra
