"""
route_schema.py — Pydantic Schema for Router Decision
======================================================
Used with LLM structured output so the router always returns
a predictable, validated JSON object instead of raw text.
"""

from pydantic import BaseModel, Field
from typing import Literal


class RouteDecision(BaseModel):
    """Structured output for the Conditional Router Agent."""

    route: Literal["research", "coding", "normal_chat"] = Field(
        description=(
            "The category of the user query. "
            "'research' for factual/informational questions, "
            "'coding' for programming tasks, "
            "'normal_chat' for greetings or casual conversation."
        )
    )
    reason: str = Field(
        description="One sentence explaining why this route was chosen."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score between 0.0 and 1.0."
    )
