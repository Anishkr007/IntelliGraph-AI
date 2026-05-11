"""
graph.py — LangGraph Workflow Assembly
=======================================
THIS IS THE CORE OF THE ENTIRE SYSTEM.

This file wires together all nodes using LangGraph's StateGraph API
to create a complete multi-agent orchestration pipeline that demonstrates
ALL 4 workflow patterns simultaneously.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPLETE WORKFLOW GRAPH:

  START
    │
    ▼
  [router_node]  ← Classifies query (Conditional Workflow)
    │
    ├──── route="research" ────► [research_dispatcher]
    │                                 │
    │                    ┌────────────┼────────────┐
    │                    ▼            ▼            ▼
    │           [web_search]  [wiki_search]  [pdf_search]
    │                    │            │            │
    │                    └────────────┴────────────┘
    │                                 │
    │                            (fan-in / merge via reducers)
    │                                 ▼
    │                          [summarizer_node]  ◄──────┐
    │                                 │                   │
    │                          [reflection_node]          │ "improve"
    │                                 │                   │
    │                      ┌──────────┴──────────┐        │
    │               "finish"                  "improve" ──┘
    │                      │
    │                      ▼
    │               [final_report_node]
    │                      │
    │                      ▼
    │                     END
    │
    ├──── route="coding" ─────► [coding_agent] ──► END
    │
    └──── route="normal_chat" ► [chatbot_agent] ─► END

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY LANGGRAPH CONCEPTS USED:

1. StateGraph(ResearchState)
   Creates a graph that passes ResearchState between all nodes.

2. add_node("name", function)
   Registers a Python function as a graph node.

3. add_edge(START, "router")
   Hardwired edge — always go from START to router.

4. add_conditional_edges("router", route_fn, mapping)
   Runtime routing — the route_fn reads state and returns
   a string key that maps to the next node name.

5. add_edge("dispatcher", "web_search") × 3
   Multiple edges from one node = PARALLEL EXECUTION.
   LangGraph runs all three targets simultaneously.

6. add_edge("web_search", "summarizer") × 3
   Multiple edges TO one node = FAN-IN (wait for all).
   Annotated[list, add] reducers merge the results safely.

7. add_conditional_edges("reflection", reflect_fn, mapping)
   The ITERATIVE LOOP — can route back to "summarizer"
   or forward to "final_report" based on quality score.

8. workflow.compile()
   Validates the graph (checks for unreachable nodes, etc.)
   and returns a runnable CompiledGraph object.
"""

from langgraph.graph import StateGraph, START, END

from backend.state import ResearchState
from backend.nodes import (
    router_node,
    research_dispatcher,
    web_search_agent,
    wiki_search_agent,
    pdf_search_agent,
    coding_agent,
    chatbot_agent,
    summarizer_node,
    reflection_node,
    final_report_node,
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# ── ROUTING FUNCTIONS ──────────────────────────────────────────────────────────
# These are simple functions that read one state key and return a string.
# LangGraph uses the returned string to look up which node to go to next
# in the mapping dict passed to add_conditional_edges().

def route_query(state: ResearchState) -> str:
    """
    Reads the 'route' key set by router_node.
    Returns one of: "research", "coding", "normal_chat"

    Used by: add_conditional_edges("router", route_query, {...})
    """
    return state.get("route", "normal_chat")


def route_reflection(state: ResearchState) -> str:
    """
    Reads the 'reflection_decision' key set by reflection_node.
    Returns one of: "improve", "finish"

    Used by: add_conditional_edges("reflection", route_reflection, {...})
    """
    return state.get("reflection_decision", "finish")


# ── GRAPH BUILDER ──────────────────────────────────────────────────────────────

def build_graph():
    """
    Assembles and compiles the complete LangGraph workflow.

    Returns:
        CompiledGraph — ready to invoke with an initial state dict.

    Example usage:
        graph = build_graph()
        result = graph.invoke({"query": "Explain AI in healthcare", ...})
    """
    logger.info("[Graph] Building LangGraph workflow...")

    # 1. Create the StateGraph with our ResearchState schema
    workflow = StateGraph(ResearchState)

    # ── 2. REGISTER ALL NODES ─────────────────────────────────────────────────
    # Each add_node() call registers a Python function as a named node.
    # The function signature must be: fn(state: ResearchState) -> dict

    workflow.add_node("router", router_node)
    workflow.add_node("dispatcher", research_dispatcher)
    workflow.add_node("web_search", web_search_agent)
    workflow.add_node("wiki_search", wiki_search_agent)
    workflow.add_node("pdf_search", pdf_search_agent)
    workflow.add_node("coding", coding_agent)
    workflow.add_node("chatbot", chatbot_agent)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("final_report", final_report_node)

    # ── 3. ENTRY POINT ────────────────────────────────────────────────────────
    # Always start the workflow at the router node.
    workflow.add_edge(START, "router")

    # ── 4. CONDITIONAL ROUTING (Workflow Type 3: Conditional) ─────────────────
    # After router runs, call route_query(state) to get the next node name.
    # The returned string is looked up in the mapping dict.
    workflow.add_conditional_edges(
        "router",           # Source node
        route_query,        # Function that reads state and returns a string
        {
            "research":     "dispatcher",   # → parallel research pipeline
            "coding":       "coding",       # → coding agent directly
            "normal_chat":  "chatbot",      # → chatbot agent directly
        }
    )

    # ── 5. PARALLEL FAN-OUT (Workflow Type 2: Parallel) ───────────────────────
    # Adding THREE edges from "dispatcher" to three different nodes tells
    # LangGraph to execute all three SIMULTANEOUSLY (true parallelism).
    workflow.add_edge("dispatcher", "web_search")
    workflow.add_edge("dispatcher", "wiki_search")
    workflow.add_edge("dispatcher", "pdf_search")

    # ── 6. PARALLEL FAN-IN ────────────────────────────────────────────────────
    # All three agents converge on "summarizer".
    # LangGraph automatically WAITS for all three to finish before running
    # summarizer. The Annotated[list[str], add] reducers in state.py handle
    # the safe merging of their results.
    workflow.add_edge("web_search", "summarizer")
    workflow.add_edge("wiki_search", "summarizer")
    workflow.add_edge("pdf_search", "summarizer")

    # ── 7. SEQUENTIAL PIPELINE (Workflow Type 1: Sequential) ──────────────────
    # After summarization, always evaluate quality.
    workflow.add_edge("summarizer", "reflection")

    # ── 8. ITERATIVE LOOP (Workflow Type 4: Iterative) ────────────────────────
    # After reflection, decide: loop back to improve OR proceed to final report.
    workflow.add_conditional_edges(
        "reflection",       # Source node
        route_reflection,   # Reads state["reflection_decision"]
        {
            "improve":  "summarizer",       # Loop back! Re-summarize with feedback
            "finish":   "final_report",     # Quality approved → generate report
        }
    )

    # ── 9. TERMINAL EDGES ─────────────────────────────────────────────────────
    # All branches eventually reach END.
    workflow.add_edge("final_report", END)
    workflow.add_edge("coding", END)
    workflow.add_edge("chatbot", END)

    # ── 10. COMPILE ───────────────────────────────────────────────────────────
    # compile() validates the graph structure and returns a runnable object.
    # It will raise an error if there are unreachable nodes or missing edges.
    compiled = workflow.compile()

    logger.info("[Graph] Workflow compiled successfully (OK)")
    logger.info(
        "[Graph] Nodes: router -> dispatcher -> [web|wiki|pdf] -> "
        "summarizer <-> reflection -> final_report -> END"
    )

    return compiled


# ── SINGLETON GRAPH INSTANCE ───────────────────────────────────────────────────
# Build once at import time so FastAPI doesn't rebuild it on every request.
# This is important for performance — graph compilation takes a moment.
research_graph = build_graph()
