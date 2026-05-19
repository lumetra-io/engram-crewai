"""
engram_crewai — durable shared memory for CrewAI multi-agent crews.

CrewAI's built-in memory is per-process and dies with the run. This wrapper
gives a crew a hosted Engram bucket they all share — store_memory and
query_memory become Tools that any agent in the crew can call mid-run.

Usage:

    from crewai import Agent, Crew, Task
    from engram_crewai import engram_tools

    tools = engram_tools(bucket="my-crew")
    researcher = Agent(
        role="Researcher",
        goal="Investigate and remember findings.",
        backstory="...",
        tools=tools,
    )
"""

from __future__ import annotations

import os
from typing import List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from lumetra_engram import EngramClient


class _StoreInput(BaseModel):
    content: str = Field(description="Atomic fact to remember.")


class _QueryInput(BaseModel):
    question: str = Field(description="Question to search prior memories for.")


def engram_tools(
    bucket: str,
    *,
    client: Optional[EngramClient] = None,
) -> List[BaseTool]:
    """Return a list of CrewAI tools wired to a single Engram bucket."""
    c = client or EngramClient(api_key=os.environ.get("ENGRAM_API_KEY"))

    class StoreMemory(BaseTool):
        name: str = "engram_store_memory"
        description: str = (
            "Save an atomic fact to durable shared memory the whole crew can "
            "read later. Store one concept per call, declarative form."
        )
        args_schema: type[BaseModel] = _StoreInput

        def _run(self, content: str) -> str:
            r = c.store_memory(content, bucket)
            return f"stored {r.get('memory_id', '(unknown)')}"

    class QueryMemory(BaseTool):
        name: str = "engram_query_memory"
        description: str = (
            "Hybrid retrieval + synthesized answer over the crew's shared "
            "memory. Use before answering questions about prior decisions, "
            "user preferences, or accumulated context."
        )
        args_schema: type[BaseModel] = _QueryInput

        def _run(self, question: str) -> str:
            r = c.query(question, buckets=[bucket])
            ans = r.get("answer") or ""
            return ans.split("FINAL ANSWER:")[-1].strip() or "No memories found."

    return [StoreMemory(), QueryMemory()]
