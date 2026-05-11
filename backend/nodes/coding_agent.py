"""
coding_agent.py — Coding Query Handler
=======================================
WORKFLOW TYPE: Conditional branch (activated when route == "coding")

Handles programming and code-related queries directly.
Skips all research agents and goes straight to END.

This demonstrates how LangGraph's conditional routing lets you
bypass entire sub-graphs based on query type.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from backend.state import ResearchState
from backend.utils.llm_client import get_llm
from backend.utils.logger import get_logger

logger = get_logger(__name__)

CODING_SYSTEM_PROMPT = """You are an expert software engineer and coding assistant.

Provide clear, well-commented, production-quality code solutions.
Structure your response as:

1. **Problem Understanding** — restate what the user is asking
2. **Solution** — the complete code with inline comments
3. **Explanation** — walk through the logic step by step
4. **Example Usage** — show how to run/use the code
5. **Edge Cases** — mention any gotchas or limitations

Use markdown code blocks with language specification (```python, ```javascript, etc.)
Keep explanations beginner-friendly but code production-quality."""


def coding_agent(state: ResearchState) -> dict:
    """
    Generates a detailed code solution for the user's programming query.

    Returns partial state with 'direct_answer' and 'final_report'.
    """
    query = state["query"]
    logger.info(f"[CodingAgent] Handling coding query: '{query[:60]}'")

    messages = [
        SystemMessage(content=CODING_SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]

    llm = get_llm(temperature=0.1)
    response = llm.invoke(messages)
    answer = response.content

    logger.info("[CodingAgent] Generated code solution successfully")

    return {
        "direct_answer": answer,
        "final_report": answer,
        "execution_trace": ["💻 Coding Agent → generated code solution"],
    }
