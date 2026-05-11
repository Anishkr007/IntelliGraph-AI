"""
router_node.py — Conditional Router Agent
==========================================
WORKFLOW TYPE: Conditional Routing

This is the FIRST node in the graph. It reads the user query and decides
which branch to take:
  - "research"     → runs parallel web/wiki/pdf agents
  - "coding"       → runs the coding agent
  - "normal_chat"  → runs the chatbot agent

HOW IT WORKS:
1. Builds a prompt explaining the task to the LLM
2. Uses llm.with_structured_output(RouteDecision) for guaranteed JSON output
3. Returns a partial state dict with only the keys it updates

STRUCTURED OUTPUT:
Instead of parsing raw LLM text (fragile), we use Pydantic + LangChain's
with_structured_output() to get a validated RouteDecision object every time.
"""

import json
from langchain_core.messages import SystemMessage, HumanMessage

from backend.state import ResearchState
from backend.schemas import RouteDecision
from backend.utils.llm_client import get_llm
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# System prompt that tells the LLM how to classify queries
ROUTER_SYSTEM_PROMPT = """You are an intelligent query router for an AI research assistant.

Your job is to classify the user's query into exactly one of three categories:

1. "research"     — Factual, informational, or analytical questions that benefit 
                    from web search and Wikipedia lookup.
                    Examples: "Explain quantum computing", "What is CRISPR?",
                              "History of the Roman Empire", "AI in healthcare"

2. "coding"       — Programming tasks, code generation, debugging, or technical 
                    implementation questions.
                    Examples: "Write a Python bubble sort", "Fix this SQL query",
                              "Explain recursion with code", "How do I use async/await?"

3. "normal_chat"  — Greetings, casual conversation, or very simple questions 
                    that don't need research.
                    Examples: "Hello!", "How are you?", "What is 2+2?", "Tell me a joke"

Respond ONLY with valid JSON matching the required schema. No extra text."""


def router_node(state: ResearchState) -> dict:
    """
    Classifies the user query and sets the routing direction.

    Args:
        state: The current LangGraph state (full state passed in)

    Returns:
        Partial state dict — only the keys this node updates.
        LangGraph merges this into the master state automatically.
    """
    logger.info(f"[Router] Classifying query: '{state['query'][:80]}...'")

    # Build messages for the LLM
    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=f"Classify this query: {state['query']}"),
    ]

    # ── STRUCTURED OUTPUT ──────────────────────────────────────────────────────
    # with_structured_output() wraps the LLM call and automatically:
    # 1. Adds the JSON schema to the prompt
    # 2. Forces the model to return valid JSON
    # 3. Parses and validates it into a RouteDecision Pydantic object
    llm = get_llm(temperature=0.0)   # Temperature=0 for consistent routing

    try:
        structured_llm = llm.with_structured_output(RouteDecision)
        decision: RouteDecision = structured_llm.invoke(messages)
    except Exception as e:
        # Fallback: parse JSON from raw response
        logger.warning(f"[Router] Structured output failed, using fallback: {e}")
        raw = llm.invoke(messages)
        try:
            data = json.loads(raw.content)
            decision = RouteDecision(**data)
        except Exception:
            # Last resort default
            decision = RouteDecision(
                route="research",
                reason="Fallback: could not parse LLM response",
                confidence=0.5,
            )

    logger.info(
        f"[Router] Route='{decision.route}' | "
        f"Confidence={decision.confidence:.2f} | Reason='{decision.reason}'"
    )

    # Return PARTIAL state — only the keys we're updating
    return {
        "route": decision.route,
        "route_reason": decision.reason,
        "route_confidence": decision.confidence,
        "execution_trace": [
            f"🧭 Router → route='{decision.route}' "
            f"(confidence={decision.confidence:.0%}): {decision.reason}"
        ],
    }
