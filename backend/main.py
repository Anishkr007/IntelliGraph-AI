"""
main.py — FastAPI Backend Entry Point
======================================
Provides REST API endpoints that the Streamlit frontend calls.

ENDPOINTS:
  GET  /health          — Health check
  POST /workflow        — Main endpoint: auto-routes any query
  POST /chat            — Direct chat (skips research)
  POST /research        — Forces research route

Run with:
  uvicorn backend.main:app --reload --port 8000
"""

import time
import traceback
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.graph import research_graph
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# ── APP SETUP ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Research & Evaluation Assistant",
    description=(
        "A multi-agent AI system using LangGraph, LangChain, and Groq. "
        "Supports parallel research, iterative reflection, and conditional routing."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow Streamlit frontend (running on port 8501) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # In production: specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REQUEST / RESPONSE MODELS ──────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """Request body for all workflow endpoints."""
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's question or prompt.",
        examples=["Explain how AI is transforming healthcare"],
    )
    chat_history: list[dict] = Field(
        default=[],
        description="Previous conversation turns for context.",
    )
    force_route: Optional[str] = Field(
        default=None,
        description="Override automatic routing: 'research', 'coding', or 'normal_chat'.",
    )


class WorkflowResponse(BaseModel):
    """Structured response returned by all workflow endpoints."""
    success: bool
    route: str
    final_report: str
    summary: str
    web_results: list[str]
    wiki_results: list[str]
    pdf_results: list[str]
    citations: list[str]
    reflection_score: int
    reflection_decision: str
    reflection_feedback: str
    iteration_count: int
    execution_trace: list[str]
    execution_time_ms: float
    error: Optional[str] = None


def _build_initial_state(request: QueryRequest) -> dict:
    """Build the initial LangGraph state from an API request."""
    state = {
        "query": request.query,
        "route": request.force_route or "",  # Empty = auto-route
        "route_reason": "",
        "route_confidence": 0.0,
        "web_results": [],
        "wiki_results": [],
        "pdf_results": [],
        "summary": "",
        "reflection_score": 0,
        "reflection_decision": "",
        "reflection_feedback": "",
        "iteration_count": 0,
        "final_report": "",
        "citations": [],
        "direct_answer": "",
        "chat_history": request.chat_history,
        "execution_trace": [f"🚀 Workflow started for query: '{request.query[:60]}'"],
    }

    # If force_route is set, we skip the router by pre-setting the route.
    # The router will still run but will see the pre-set value.
    # For a true force, you'd skip the router node — this is a simple override.
    return state


def _parse_result(result: dict, exec_time: float) -> WorkflowResponse:
    """Convert the LangGraph output state to a WorkflowResponse."""
    return WorkflowResponse(
        success=True,
        route=result.get("route", "unknown"),
        final_report=result.get("final_report", ""),
        summary=result.get("summary", ""),
        web_results=result.get("web_results", []),
        wiki_results=result.get("wiki_results", []),
        pdf_results=result.get("pdf_results", []),
        citations=result.get("citations", []),
        reflection_score=result.get("reflection_score", 0),
        reflection_decision=result.get("reflection_decision", ""),
        reflection_feedback=result.get("reflection_feedback", ""),
        iteration_count=result.get("iteration_count", 0),
        execution_trace=result.get("execution_trace", []),
        execution_time_ms=exec_time,
    )


# ── ENDPOINTS ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Simple health check — verify the API is running."""
    return {
        "status": "healthy",
        "service": "AI Research Assistant Backend",
        "version": "1.0.0",
        "graph_nodes": [
            "router", "dispatcher", "web_search", "wiki_search",
            "pdf_search", "coding", "chatbot", "summarizer",
            "reflection", "final_report"
        ],
    }


@app.post("/workflow", response_model=WorkflowResponse)
async def run_workflow(request: QueryRequest):
    """
    MAIN ENDPOINT — Processes any query through the full LangGraph workflow.

    The router automatically classifies the query and routes it to:
    - Research pipeline (parallel agents + summarizer + reflection)
    - Coding agent
    - Chat agent

    Returns a fully structured response with the report, traces, and metadata.
    """
    logger.info(f"[API /workflow] Received query: '{request.query[:80]}'")
    start_time = time.time()

    try:
        initial_state = _build_initial_state(request)
        result = research_graph.invoke(initial_state)
        exec_time = (time.time() - start_time) * 1000

        logger.info(
            f"[API /workflow] Completed in {exec_time:.0f}ms | "
            f"route={result.get('route')} | "
            f"score={result.get('reflection_score')}"
        )
        return _parse_result(result, exec_time)

    except Exception as e:
        logger.error(f"[API /workflow] Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}"
        )


@app.post("/research", response_model=WorkflowResponse)
async def run_research(request: QueryRequest):
    """
    Forces the research route — runs parallel web/wiki/pdf agents
    regardless of query type. Useful for explicitly requesting research.
    """
    logger.info(f"[API /research] Forced research for: '{request.query[:80]}'")
    request.force_route = "research"
    return await run_workflow(request)


@app.post("/chat", response_model=WorkflowResponse)
async def run_chat(request: QueryRequest):
    """
    Forces the chat route — returns a direct conversational response
    without running any research agents.
    """
    logger.info(f"[API /chat] Direct chat for: '{request.query[:80]}'")
    request.force_route = "normal_chat"
    return await run_workflow(request)
