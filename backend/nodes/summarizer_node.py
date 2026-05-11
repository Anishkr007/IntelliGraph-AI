"""
summarizer_node.py — Research Aggregator & Summarizer
=======================================================
WORKFLOW TYPE: Sequential (runs after all parallel agents complete)

This node is the fan-in point after parallel research.
It receives the merged state (web_results + wiki_results + pdf_results)
and produces a coherent, structured summary.

KEY INSIGHT — HOW FAN-IN WORKS:
After parallel agents run, LangGraph waits for ALL of them to finish,
then passes the fully-merged state to this node. The Annotated[list, add]
reducers already concatenated the results, so this node just reads them.

This node is also the TARGET of the reflection loop — if reflection
decides "improve", this node runs again with improved context.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from backend.state import ResearchState
from backend.utils.llm_client import get_llm
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _build_research_context(state: ResearchState) -> str:
    """Formats all research results into a single context block."""
    sections = []

    if state.get("web_results"):
        sections.append("=== WEB SEARCH RESULTS ===")
        sections.extend(state["web_results"])

    if state.get("wiki_results"):
        sections.append("\n=== WIKIPEDIA RESULTS ===")
        sections.extend(state["wiki_results"])

    if state.get("pdf_results"):
        sections.append("\n=== PDF KNOWLEDGE BASE RESULTS ===")
        sections.extend(state["pdf_results"])

    return "\n".join(sections)


SUMMARIZER_SYSTEM_PROMPT = """You are an expert research analyst and technical writer.

Your task: Synthesize multiple research sources into a clear, comprehensive summary.

Guidelines:
- Integrate information from ALL provided sources
- Remove redundancy while preserving key unique insights
- Maintain factual accuracy — do not hallucinate
- Structure the summary with clear paragraphs
- Highlight the most important and actionable insights
- Be comprehensive but concise (aim for 300-500 words)
- If this is an improvement iteration, address the feedback provided

Format your summary in clear, readable prose — NOT bullet points."""


def summarizer_node(state: ResearchState) -> dict:
    """
    Aggregates parallel research results into a coherent summary.
    Also incorporates reflection feedback when in improvement iterations.

    Returns partial state with 'summary' key.
    """
    query = state["query"]
    iteration = state.get("iteration_count", 0)
    feedback = state.get("reflection_feedback", "")

    logger.info(
        f"[Summarizer] Running summarization | iteration={iteration} | "
        f"web={len(state.get('web_results', []))} wiki={len(state.get('wiki_results', []))} "
        f"pdf={len(state.get('pdf_results', []))} results"
    )

    research_context = _build_research_context(state)

    # Build the user prompt — include feedback if this is an improvement loop
    user_content = f"RESEARCH QUERY: {query}\n\n{research_context}"
    if feedback and iteration > 0:
        user_content += f"\n\n=== IMPROVEMENT FEEDBACK (Iteration {iteration}) ===\n{feedback}"
        user_content += "\nPlease address this feedback in your improved summary."

    messages = [
        SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    llm = get_llm(temperature=0.3)
    response = llm.invoke(messages)
    summary = response.content

    logger.info(
        f"[Summarizer] Generated summary ({len(summary)} chars) "
        f"on iteration {iteration}"
    )

    trace_msg = (
        f"📝 Summarizer → synthesized {len(state.get('web_results', []))} web + "
        f"{len(state.get('wiki_results', []))} wiki + "
        f"{len(state.get('pdf_results', []))} PDF results"
    )
    if iteration > 0:
        trace_msg += f" (improvement iteration #{iteration})"

    return {
        "summary": summary,
        "execution_trace": [trace_msg],
    }
