"""Feedback domain models — parent ratings of technique effectiveness."""

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class AdviceFeedback(BaseModel):
    """Parent's rating of how well a technique worked for their family."""

    id: str = Field(
        default_factory=lambda: str(uuid4())[:8],
        description="Unique feedback entry identifier",
    )
    child_id: str = Field(
        ...,
        description="Which child the technique was used with",
        examples=["max", "emma"],
        min_length=1,
    )
    technique: str = Field(
        ...,
        description="The technique that was tried (e.g. 'logical consequences', 'emotion coaching')",
        examples=["logical consequences", "emotion coaching", "time-in"],
        min_length=1,
    )
    context: str = Field(
        default="",
        description="Situation context (e.g. 'homework resistance', 'bedtime battles')",
        examples=["homework resistance", "bedtime battles"],
    )
    setting: str = Field(
        default="",
        description="Environmental setting (e.g. 'calm Saturday', 'rushed school morning')",
        examples=["calm Saturday", "rushed school morning"],
    )
    outcome: int = Field(
        ...,
        ge=1,
        le=5,
        description="How well the technique worked: 1=made worse, 3=no change, 5=worked great",
    )
    confidence: int = Field(
        default=3,
        ge=1,
        le=5,
        description="How confident in this rating (1=very uncertain, 5=very confident)",
    )
    used_as_intended: bool = Field(
        default=True,
        description="Whether the technique was used as described",
    )
    duration_tried: str = Field(
        default="",
        description="How long the technique was tried: one_time, few_days, week, ongoing",
        examples=["one_time", "few_days", "week", "ongoing"],
    )
    notes: str = Field(
        default="",
        description="Additional notes about the experience",
    )
    knowledge_source: str = Field(
        default="",
        description="Which knowledge file suggested this technique",
        examples=["discipline.md", "emotional-regulation.md"],
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of when feedback was recorded",
    )
