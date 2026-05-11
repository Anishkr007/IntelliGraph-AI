"""
wiki_search_agent.py — Wikipedia Search Agent
===============================================
WORKFLOW TYPE: Parallel (runs simultaneously with web + pdf agents)

Queries Wikipedia for the user's topic and returns structured summaries.
Uses the `wikipedia` Python package which wraps the Wikipedia API.

This node demonstrates:
- External API integration in a LangGraph node
- Graceful error handling (disambiguation, page not found)
- Partial state updates (only returns 'wiki_results')
"""

import wikipedia

from backend.state import ResearchState
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Limit Wikipedia summary length to avoid overwhelming the summarizer
MAX_CHARS = 1200


def wiki_search_agent(state: ResearchState) -> dict:
    """
    Searches Wikipedia for the query and returns page summaries.

    Returns partial state with 'wiki_results' key.
    """
    query = state["query"]
    logger.info(f"[Wikipedia] Searching for: '{query[:60]}'")

    results = []

    try:
        # Search Wikipedia for relevant page titles
        search_hits = wikipedia.search(query, results=3)
        logger.info(f"[Wikipedia] Found titles: {search_hits}")

        for title in search_hits[:2]:   # Fetch top 2 to keep it fast
            try:
                page = wikipedia.page(title, auto_suggest=False)
                snippet = page.summary[:MAX_CHARS]
                results.append(
                    f"[WIKI] {page.title}: {snippet} "
                    f"(Source: {page.url})"
                )
                logger.info(f"[Wikipedia] Fetched page: '{page.title}'")

            except wikipedia.exceptions.DisambiguationError as e:
                # Disambiguation page — try the first option
                try:
                    page = wikipedia.page(e.options[0], auto_suggest=False)
                    snippet = page.summary[:MAX_CHARS]
                    results.append(
                        f"[WIKI] {page.title}: {snippet} "
                        f"(Source: {page.url})"
                    )
                except Exception:
                    pass

            except wikipedia.exceptions.PageError:
                logger.warning(f"[Wikipedia] Page not found: '{title}'")

    except Exception as e:
        logger.error(f"[Wikipedia] Search failed: {e}")
        results.append(
            f"[WIKI-FALLBACK] Wikipedia search was unavailable for '{query}'. "
            f"This may be due to network issues or an ambiguous query term."
        )

    if not results:
        results.append(
            f"[WIKI] No Wikipedia articles found for '{query}'. "
            f"The query may be too specific or use different terminology."
        )

    logger.info(f"[Wikipedia] Returning {len(results)} result(s)")

    return {
        "wiki_results": results,
        "execution_trace": [
            f"📖 Wikipedia Agent → found {len(results)} article(s)"
        ],
    }
