"""
reflection_node.py — Quality Evaluation & Iterative Improvement Controller
===========================================================================
WORKFLOW TYPE: Iterative (creates a loop back to summarizer if needed)

This is the most architecturally interesting node. It:
1. Evaluates the current summary against quality criteria
2. Decides: "improve" (loop back) OR "finish" (proceed to final report)
3. Increments the iteration counter to prevent infinite loops

HOW THE LOOP WORKS:
  summarizer → reflection → (if "improve") → summarizer → reflection → ...
                          → (if "finish")  → final_report → END

The loop is implemented via add_conditional_edges() in graph.py:
  - The routing function reads state["reflection_decision"]
  - If "improve": go to "summarizer"
  - If "finish":  go to "final_report"

LOOP GUARD:
  Max 3 iterations (configurable via MAX_ITERATIONS).
  After that, reflection always returns "finish" regardless of score.
"""

import json

from langchain_core.messages import SystemMessage, HumanMessage

from backend.state import ResearchState
from backend.schemas import ReflectionDecision
from backend.utils.llm_client import get_llm
from backend.utils.logger import get_logger

logger = get_logger(__name__)

MAX_ITERATIONS = 3    # Maximum allowed improvement loops
QUALITY_THRESHOLD = 7  # Score below this triggers another iteration


REFLECTION_SYSTEM_PROMPT = """You are a rigorous quality-control reviewer for AI-generated research reports.

Evaluate the provided summary on these criteria:
1. **Completeness** — Does it fully answer the query? Are key aspects missing?
2. **Accuracy**     — Is the information factually sound and well-supported?
3. **Clarity**      — Is it easy to understand? Well-structured?
4. **Depth**        — Does it go beyond surface-level? Includes specific details?
5. **Coherence**    — Do the ideas flow logically?

Scoring guide:
  9-10: Excellent — comprehensive, accurate, clear, and insightful
  7-8:  Good — addresses the query well with minor gaps
  5-6:  Fair — covers basics but missing important aspects
  3-4:  Poor — significant gaps or unclear
  0-2:  Unacceptable — does not address the query

Respond with JSON matching the required schema."""


def reflection_node(state: ResearchState) -> dict:
    """
    Evaluates summary quality and decides whether to improve or finish.

    Returns partial state with reflection_score, reflection_decision,
    reflection_feedback, and incremented iteration_count.
    """
    summary = state.get("summary", "")
    query = state["query"]
    iteration = state.get("iteration_count", 0)

    logger.info(f"[Reflection] Evaluating summary | iteration={iteration}")

    # ── LOOP GUARD ─────────────────────────────────────────────────────────────
    if iteration >= MAX_ITERATIONS:
        logger.info(
            f"[Reflection] Max iterations ({MAX_ITERATIONS}) reached → forcing finish"
        )
        return {
            "reflection_score": 7,
            "reflection_decision": "finish",
            "reflection_feedback": f"Maximum iterations ({MAX_ITERATIONS}) reached. Accepting current summary.",
            "iteration_count": iteration + 1,
            "execution_trace": [
                f"🔁 Reflection → max iterations reached → FINISH (score: 7/10)"
            ],
        }

    # ── QUALITY EVALUATION ─────────────────────────────────────────────────────
    messages = [
        SystemMessage(content=REFLECTION_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"ORIGINAL QUERY: {query}\n\n"
                f"SUMMARY TO EVALUATE:\n{summary}\n\n"
                f"This is evaluation iteration #{iteration + 1}. "
                f"Evaluate the summary quality and provide your decision."
            )
        ),
    ]

    llm = get_llm(temperature=0.0)   # Deterministic for consistent evaluation

    try:
        structured_llm = llm.with_structured_output(ReflectionDecision)
        decision: ReflectionDecision = structured_llm.invoke(messages)
    except Exception as e:
        logger.warning(f"[Reflection] Structured output failed, using fallback: {e}")
        try:
            raw = llm.invoke(messages)
            data = json.loads(raw.content)
            decision = ReflectionDecision(**data)
        except Exception:
            decision = ReflectionDecision(
                score=7,
                decision="finish",
                feedback="Could not evaluate quality — defaulting to finish.",
            )

    # Override: if score is good enough, always finish
    if decision.score >= QUALITY_THRESHOLD:
        decision.decision = "finish"

    logger.info(
        f"[Reflection] Score={decision.score}/10 | "
        f"Decision='{decision.decision}' | Feedback='{decision.feedback[:80]}...'"
    )

    emoji = "✅" if decision.decision == "finish" else "🔄"
    return {
        "reflection_score": decision.score,
        "reflection_decision": decision.decision,
        "reflection_feedback": decision.feedback,
        "iteration_count": iteration + 1,
        "execution_trace": [
            f"{emoji} Reflection (iter {iteration+1}) → "
            f"score={decision.score}/10 → {decision.decision.upper()}: {decision.feedback[:100]}"
        ],
    }
