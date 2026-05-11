"""
state.py — LangGraph Shared State Definition
=============================================
This is the HEART of the LangGraph system. Every node reads from and writes
to this shared state. Understanding this file is key to understanding the
whole workflow.

KEY CONCEPTS:
- TypedDict        : Defines the shape of our state (like a schema)
- Annotated        : Adds extra metadata (reducers) to type hints
- operator.add     : Concatenates lists — used as a reducer
- Reducer          : A function that merges partial state updates

WHY PARTIAL UPDATES?
Each node receives the full state, but only RETURNS the keys it changes.
LangGraph automatically merges these partial dicts into the master state.

WHY Annotated[list[str], add]?
When web_search, wiki_search, and pdf_search all run in parallel, they each
return {"web_results": [...]} etc. The `add` reducer CONCATENATES them
instead of overwriting, so no data is lost from parallel execution.
"""

from typing import TypedDict, Annotated
from operator import add


class ResearchState(TypedDict):
    """
    Central shared state for the AI Research Assistant workflow.
    Flows through every node in the LangGraph pipeline.
    """

    # ── INPUT ──────────────────────────────────────────────────────────────────
    query: str                          # The user's original question

    # ── ROUTING ────────────────────────────────────────────────────────────────
    route: str                          # "research" | "coding" | "normal_chat"
    route_reason: str                   # Why the router chose this route
    route_confidence: float             # Confidence score 0.0 – 1.0

    # ── PARALLEL RESEARCH RESULTS (with reducers for safe parallel merging) ───
    # Annotated[list[str], add] means: if two nodes update the same key,
    # LangGraph calls add(existing, new) → concatenates them.
    web_results: Annotated[list[str], add]    # Results from Tavily web search
    wiki_results: Annotated[list[str], add]   # Results from Wikipedia
    pdf_results: Annotated[list[str], add]    # Results from PDF knowledge base

    # ── SUMMARIZATION ──────────────────────────────────────────────────────────
    summary: str                        # Aggregated & summarized research

    # ── REFLECTION / QUALITY CONTROL ───────────────────────────────────────────
    reflection_score: int               # Quality score 0–10
    reflection_decision: str            # "improve" | "finish"
    reflection_feedback: str            # Detailed feedback from reflection node
    iteration_count: int                # How many reflection loops have run

    # ── FINAL OUTPUT ───────────────────────────────────────────────────────────
    final_report: str                   # The polished, final AI-generated report
    citations: Annotated[list[str], add]        # Source citations

    # ── DIRECT ANSWERS (for non-research routes) ───────────────────────────────
    direct_answer: str                  # Used by coding_agent / chatbot_agent

    # ── METADATA & LOGGING ────────────────────────────────────────────────────
    # execution_trace uses add reducer so every node can append its own log
    execution_trace: Annotated[list[str], add]
    chat_history: list[dict]            # Persisted conversation history
