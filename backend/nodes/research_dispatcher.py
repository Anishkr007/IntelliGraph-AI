"""
research_dispatcher.py — Parallel Research Fan-Out Node
=========================================================
WORKFLOW TYPE: Parallel (this node triggers the fan-out)

This is a lightweight pass-through node that sits between the router
and the parallel research agents. Its job is simply to log the dispatch
and let LangGraph fan out to all three agents simultaneously.

WHY IS THIS NODE NEEDED?
The router uses conditional_edges to pick a single next node.
We can't fan out directly from conditional edges.
So router → dispatcher → [web, wiki, pdf] (all at once).

In LangGraph, adding multiple add_edge() calls from one source node
causes ALL target nodes to execute in parallel automatically.
"""

from backend.state import ResearchState
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def research_dispatcher(state: ResearchState) -> dict:
    """
    Pass-through node that logs the dispatch and lets LangGraph
    fan out to parallel agents.

    Returns partial state with execution_trace only.
    """
    query = state["query"]
    logger.info(f"[Dispatcher] Fanning out to parallel research agents for: '{query[:60]}'")

    return {
        "execution_trace": [
            "🔀 Research Dispatcher → launching web, wikipedia, and PDF agents in parallel"
        ],
    }
