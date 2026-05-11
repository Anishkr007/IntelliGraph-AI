"""
pdf_search_agent.py — PDF Knowledge Base Agent (Mock Implementation)
=====================================================================
WORKFLOW TYPE: Parallel (runs simultaneously with web + wiki agents)

This agent simulates searching a PDF knowledge base. In a production system,
this would use a vector database (FAISS, Chroma, Pinecone) with embeddings.
Here we use a keyword-matched mock corpus to demonstrate the PATTERN.

This node demonstrates:
- How a RAG (Retrieval-Augmented Generation) agent fits into LangGraph
- Partial state updates for parallel execution
- How to build a fallback/mock that still provides useful output
"""

from backend.state import ResearchState
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# ── MOCK PDF KNOWLEDGE BASE ───────────────────────────────────────────────────
# In production: replace with FAISS/Chroma vector search + PDF embeddings
PDF_KNOWLEDGE_BASE = [
    {
        "title": "Introduction to Artificial Intelligence",
        "keywords": ["ai", "artificial intelligence", "machine learning", "deep learning", "neural"],
        "content": (
            "Artificial Intelligence (AI) refers to the simulation of human intelligence "
            "in machines. Key subfields include Machine Learning (ML), Deep Learning (DL), "
            "Natural Language Processing (NLP), Computer Vision, and Robotics. "
            "AI systems learn from data, identify patterns, and make decisions with minimal "
            "human intervention. Modern AI is powered by transformer architectures like GPT and BERT."
        ),
        "source": "PDF: AI_Fundamentals_2024.pdf (p. 1-12)",
    },
    {
        "title": "Large Language Models and LangChain",
        "keywords": ["llm", "langchain", "langgraph", "gpt", "llama", "groq", "agent", "workflow"],
        "content": (
            "Large Language Models (LLMs) are transformer-based models trained on vast text corpora. "
            "LangChain is a framework for building LLM-powered applications. LangGraph extends "
            "LangChain with graph-based multi-agent orchestration, supporting parallel execution, "
            "conditional routing, and iterative reflection loops. Key providers include OpenAI, "
            "Anthropic, and Groq (offering ultra-fast inference via custom hardware)."
        ),
        "source": "PDF: LangChain_LangGraph_Guide.pdf (p. 5-28)",
    },
    {
        "title": "Healthcare and Medicine",
        "keywords": ["healthcare", "medical", "medicine", "hospital", "disease", "drug", "clinical"],
        "content": (
            "AI in healthcare encompasses diagnostic imaging analysis, drug discovery, "
            "personalized medicine, and clinical decision support systems. Deep learning models "
            "can detect cancer in radiology images with superhuman accuracy. NLP systems "
            "extract insights from medical records. Challenges include data privacy (HIPAA), "
            "model interpretability, and regulatory approval (FDA clearance)."
        ),
        "source": "PDF: AI_in_Healthcare_Review.pdf (p. 3-19)",
    },
    {
        "title": "Climate Change and Sustainability",
        "keywords": ["climate", "environment", "carbon", "sustainability", "green", "energy", "global warming"],
        "content": (
            "Climate change refers to long-term shifts in global temperatures and weather patterns. "
            "AI is being used to optimize renewable energy grids, predict extreme weather events, "
            "and model carbon capture solutions. Key metrics include CO2 concentration (420+ ppm), "
            "global temperature rise (+1.1°C since pre-industrial), and sea level rise (3.3mm/yr)."
        ),
        "source": "PDF: Climate_AI_Solutions_2024.pdf (p. 1-15)",
    },
    {
        "title": "Quantum Computing",
        "keywords": ["quantum", "qubit", "superposition", "entanglement", "computing"],
        "content": (
            "Quantum computing leverages quantum mechanical phenomena — superposition and "
            "entanglement — to process information in fundamentally new ways. Unlike classical "
            "bits (0 or 1), qubits can exist in superposition (both simultaneously). "
            "Quantum algorithms like Shor's (factoring) and Grover's (search) offer exponential "
            "speedups for specific problems. Companies leading: IBM, Google, IonQ, Rigetti."
        ),
        "source": "PDF: Quantum_Computing_Primer.pdf (p. 2-22)",
    },
    {
        "title": "Python Programming",
        "keywords": ["python", "programming", "code", "algorithm", "data structure", "function"],
        "content": (
            "Python is a high-level, interpreted programming language known for readability "
            "and versatility. It dominates AI/ML (PyTorch, TensorFlow, scikit-learn), "
            "web development (FastAPI, Django, Flask), and data science (pandas, NumPy, matplotlib). "
            "Key concepts: list comprehensions, generators, decorators, async/await, "
            "type hints, dataclasses, and virtual environments."
        ),
        "source": "PDF: Python_Best_Practices.pdf (p. 1-45)",
    },
    {
        "title": "General Research Findings",
        "keywords": [],   # Matches any query as a fallback
        "content": (
            "Cross-domain research indicates that interdisciplinary approaches yield the most "
            "innovative solutions. The integration of multiple data sources — web, academic, "
            "and domain-specific knowledge bases — provides comprehensive understanding. "
            "Critical evaluation of sources and iterative refinement of findings are "
            "essential for producing high-quality research outputs."
        ),
        "source": "PDF: Research_Methodology_Handbook.pdf (p. 7-11)",
    },
]


def pdf_search_agent(state: ResearchState) -> dict:
    """
    Searches the mock PDF knowledge base using keyword matching.

    In production: replace this with a vector similarity search
    (FAISS + HuggingFace embeddings or OpenAI embeddings).

    Returns partial state with 'pdf_results' key.
    """
    query = state["query"].lower()
    logger.info(f"[PDFSearch] Searching knowledge base for: '{query[:60]}'")

    matched = []
    query_words = set(query.split())

    for doc in PDF_KNOWLEDGE_BASE:
        # Score: count how many keywords match the query
        keyword_hits = sum(
            1 for kw in doc["keywords"] if kw in query
        )
        word_hits = sum(
            1 for word in query_words if word in doc["title"].lower()
        )
        score = keyword_hits * 2 + word_hits

        if score > 0:
            matched.append((score, doc))

    # Sort by relevance score (highest first)
    matched.sort(key=lambda x: x[0], reverse=True)

    results = []
    for _, doc in matched[:2]:   # Return top 2 matches
        results.append(
            f"[PDF] {doc['title']}: {doc['content'][:600]} ({doc['source']})"
        )

    # Always include the general fallback if no strong matches
    if not results:
        fallback = PDF_KNOWLEDGE_BASE[-1]
        results.append(
            f"[PDF] {fallback['title']}: {fallback['content'][:600]} ({fallback['source']})"
        )

    logger.info(f"[PDFSearch] Returning {len(results)} result(s)")

    return {
        "pdf_results": results,
        "execution_trace": [
            f"📄 PDF Search Agent → found {len(results)} relevant document(s)"
        ],
    }
