"""
report_schema.py — Pydantic Schema for the Final Report
=========================================================
The final_report_node produces a structured report object that
the FastAPI backend serialises to JSON and the Streamlit UI renders.
"""

from pydantic import BaseModel, Field


class FinalReport(BaseModel):
    """Structured schema for the AI-generated final research report."""

    title: str = Field(description="A concise, descriptive title for the report.")
    executive_summary: str = Field(
        description="A 2–3 sentence executive summary of the findings."
    )
    detailed_summary: str = Field(
        description="A comprehensive, paragraph-level explanation of the topic."
    )
    key_points: list[str] = Field(
        description="5–7 bullet-point key takeaways from the research."
    )
    citations: list[str] = Field(
        description="List of sources used (URLs, Wikipedia page names, etc.)."
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Overall confidence in the report's accuracy."
    )
    suggested_follow_ups: list[str] = Field(
        description="2–3 follow-up questions the user might want to explore next."
    )
