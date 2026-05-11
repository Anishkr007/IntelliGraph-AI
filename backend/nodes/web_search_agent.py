"""
web_search_agent.py — DuckDuckGo Web Search Agent
====================================================
WORKFLOW TYPE: Parallel (runs simultaneously with wiki + pdf agents)

Searches the web using DuckDuckGo (100% free, no API key needed).
Falls back to a mock response if the search fails for any reason.

Uses the `duckduckgo-search` package:
    pip install duckduckgo-search
    from duckduckgo_search import DDGS
"""

from duckduckgo_search import DDGS

from backend.state import ResearchState
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def web_search_agent(state: ResearchState) -> dict:
    """
    Performs a live DuckDuckGo web search for the user query.
    Falls back to mock data if the search fails.

    Returns partial state with 'web_results' key.
    """
    query = state["query"]
    logger.info(f"[WebSearch] DuckDuckGo search for: '{query[:60]}'")

    results = []

    try:
        # DDGS().text() returns a list of dicts:
        # {"title": ..., "href": ..., "body": ...}
        with DDGS() as ddgs:
            hits = list(ddgs.text(query, max_results=4))

        for hit in hits:
            title = hit.get("title", "")
            body = hit.get("body", "")
            url = hit.get("href", "")
            results.append(
                f"[WEB] {title}: {body[:400]} (Source: {url})"
            )

        logger.info(f"[WebSearch] Found {len(results)} results via DuckDuckGo")

        return {
            "web_results": results,
            "execution_trace": [
                f"🌐 Web Search Agent (DuckDuckGo) --> found {len(results)} results"
            ],
        }

    except Exception as e:
        logger.warning(f"[WebSearch] DuckDuckGo search failed: {e}. Using mock.")

    # ── MOCK FALLBACK ──────────────────────────────────────────────────────────
    mock_results = [
        f"[WEB-MOCK] Overview of '{query}': This topic has gained significant "
        f"attention recently. Researchers have explored multiple dimensions "
        f"including theoretical foundations, practical applications, and implications.",

        f"[WEB-MOCK] Latest developments in '{query}': Current trends show "
        f"rapid advancement with new methodologies being published in top journals. "
        f"Industry adoption is accelerating globally.",

        f"[WEB-MOCK] Expert analysis on '{query}': Leading experts suggest "
        f"the field is transforming how we approach complex problems. "
        f"Key challenges remain around scalability, ethics, and accessibility.",
    ]

    return {
        "web_results": mock_results,
        "execution_trace": [
            f"🌐 Web Search Agent --> {len(mock_results)} results (mock fallback — DuckDuckGo unavailable)"
        ],
    }
