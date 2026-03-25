"""Emotional domain models — moods, conflicts, and developmental milestones."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class MoodEntry(BaseModel):
    """A mood check-in for a child, using Zones of Regulation."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique entry identifier",
    )
    child_id: str = Field(
        ...,
        description="ID of the child",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO datetime of the mood check-in",
    )
    zone: str | None = Field(
        default=None,
        description="Zones of Regulation: blue, green, yellow, red",
    )
    intensity: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Intensity level 1-5",
    )
    emotions: list[str] = Field(
        default_factory=list,
        description="Specific emotion words (happy, frustrated, anxious, etc.)",
    )
    context: str = Field(
        default="",
        description="What was happening when this mood was observed",
    )
    coping_used: list[str] = Field(
        default_factory=list,
        description="Coping strategies used (deep breathing, walk, etc.)",
    )
    notes: str = Field(
        default="",
        description="Additional notes",
    )


class ConflictRecord(BaseModel):
    """A conflict between children, with resolution tracking."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique record identifier",
    )
    children_involved: list[str] = Field(
        ...,
        description="IDs of children involved in the conflict",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO datetime when the conflict occurred",
    )
    trigger: str = Field(
        ...,
        description="What triggered the conflict",
        min_length=1,
    )
    description: str = Field(
        default="",
        description="Description of what happened",
    )
    resolution: str = Field(
        default="",
        description="How the conflict was resolved",
    )
    resolution_type: str = Field(
        default="mediated",
        description="Type: mediated, self_resolved, unresolved, escalated",
    )
    what_worked: str = Field(
        default="",
        description="What worked well in resolution",
    )
    what_didnt_work: str = Field(
        default="",
        description="What did not work",
    )


class DevelopmentalMilestone(BaseModel):
    """A developmental milestone achieved by a child."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique milestone identifier",
    )
    child_id: str = Field(
        ...,
        description="ID of the child",
    )
    date: str = Field(
        ...,
        description="ISO date when the milestone was observed",
    )
    category: str = Field(
        default="general",
        description="Category: cognitive, emotional, social, physical, language",
    )
    description: str = Field(
        ...,
        description="Description of the milestone",
        min_length=1,
    )
    notes: str = Field(
        default="",
        description="Additional notes",
    )
