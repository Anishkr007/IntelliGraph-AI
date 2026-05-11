"""
chatbot_agent.py — Normal Chat Handler
========================================
WORKFLOW TYPE: Conditional branch (activated when route == "normal_chat")

Handles casual conversation, greetings, and simple questions.
Skips research agents and goes straight to END.

Demonstrates how LangGraph routes different query types to
completely different node chains — true conditional workflow.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from backend.state import ResearchState
from backend.utils.llm_client import get_llm
from backend.utils.logger import get_logger

logger = get_logger(__name__)

CHAT_SYSTEM_PROMPT = """You are a friendly, helpful, and engaging AI assistant.

For casual conversations and simple questions:
- Be warm, natural, and conversational
- Keep responses concise and engaging
- Add a touch of personality
- If the user asks what you can do, mention that you can:
  * Answer research questions with multi-source analysis
  * Help with programming and coding tasks
  * Have casual conversations
  * Generate detailed research reports

Always be helpful and guide the user toward asking better questions if relevant."""


def chatbot_agent(state: ResearchState) -> dict:
    """
    Handles casual conversation and simple queries.

    Returns partial state with 'direct_answer' and 'final_report'.
    """
    query = state["query"]
    logger.info(f"[ChatbotAgent] Handling chat query: '{query[:60]}'")

    # Include recent chat history for context
    messages = [SystemMessage(content=CHAT_SYSTEM_PROMPT)]

    # Add last 4 messages from chat history (for memory/context)
    for msg in state.get("chat_history", [])[-4:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        # (Assistant messages could be added with AIMessage for full memory)

    messages.append(HumanMessage(content=query))

    llm = get_llm(temperature=0.7)   # Higher temperature for natural conversation
    response = llm.invoke(messages)
    answer = response.content

    logger.info("[ChatbotAgent] Generated chat response successfully")

    return {
        "direct_answer": answer,
        "final_report": answer,
        "execution_trace": ["💬 Chatbot Agent → generated conversational response"],
    }
