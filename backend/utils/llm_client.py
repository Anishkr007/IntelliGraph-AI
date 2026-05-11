"""
llm_client.py — Groq LLM Client Factory
=========================================
Central place to create LLM instances.
All nodes import get_llm() from here — this means you only need to
change the model name / temperature in ONE place.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load .env file so GROQ_API_KEY is available
load_dotenv()


def get_llm(temperature: float = 0.1) -> ChatGroq:
    """
    Returns a configured Groq ChatGroq LLM instance.

    Args:
        temperature: Creativity level (0.0 = deterministic, 1.0 = creative).
                     Router/Reflection use 0.0 for consistency.
                     Summarizer/Report use 0.3–0.5 for richer language.

    Returns:
        ChatGroq instance ready to invoke.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Please add it to your .env file."
        )

    return ChatGroq(
        model="llama-3.1-8b-instant",   # Fast, capable Llama 3.1 model
        temperature=temperature,
        api_key=api_key,
        max_tokens=4096,                 # Max tokens per response
    )
