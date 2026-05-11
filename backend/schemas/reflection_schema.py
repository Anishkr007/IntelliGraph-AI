"""
reflection_schema.py — Pydantic Schema for Reflection / Quality Evaluation
===========================================================================
Used by the reflection node to decide whether to loop back and improve
the summary, or accept it and move on to the final report.
"""

from pydantic import BaseModel, Field
from typing import Literal


class ReflectionDecision(BaseModel):
    """Structured output for the Reflection / Quality-Control Node."""

    score: int = Field(
        ge=0, le=10,
        description=(
            "Quality score for the current summary. "
            "0 = completely wrong/empty, 10 = perfect and comprehensive."
        )
    )
    decision: Literal["improve", "finish"] = Field(
        description=(
            "'improve' if the summary needs another iteration, "
            "'finish' if it is good enough to publish."
        )
    )
    feedback: str = Field(
        description=(
            "Concrete, actionable feedback explaining what is missing "
            "or what should be improved in the next iteration."
        )
    )
