"""Education domain models — reading, homework, and learning goals."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ReadingEntry(BaseModel):
    """A single reading session logged for a child."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique entry identifier",
    )
    child_id: str = Field(
        ...,
        description="ID of the child",
    )
    date: str = Field(
        ...,
        description="ISO date of the reading session",
    )
    book_title: str = Field(
        ...,
        description="Title of the book",
        min_length=1,
    )
    pages_read: int | None = Field(
        default=None,
        ge=0,
        description="Number of pages read",
    )
    minutes_read: int | None = Field(
        default=None,
        ge=0,
        description="Duration in minutes",
    )
    finished_book: bool = Field(
        default=False,
        description="Whether the child finished the book",
    )
    enjoyment: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Enjoyment rating 1-5",
    )
    notes: str = Field(
        default="",
        description="Additional notes",
    )


class HomeworkEntry(BaseModel):
    """A homework session logged for a child."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique entry identifier",
    )
    child_id: str = Field(
        ...,
        description="ID of the child",
    )
    date: str = Field(
        ...,
        description="ISO date of the homework session",
    )
    subject: str = Field(
        ...,
        description="Subject area (math, reading, science, etc.)",
        min_length=1,
    )
    duration_minutes: int = Field(
        ...,
        ge=0,
        description="Duration in minutes",
    )
    struggle_level: int = Field(
        default=0,
        ge=0,
        le=3,
        description="0=easy, 1=moderate, 2=hard, 3=meltdown",
    )
    completed: bool = Field(
        default=True,
        description="Whether the homework was completed",
    )
    help_needed: str = Field(
        default="",
        description="Description of help needed",
    )
    notes: str = Field(
        default="",
        description="Additional notes",
    )


class LearningGoal(BaseModel):
    """A learning goal with milestones for a child."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique goal identifier",
    )
    child_id: str = Field(
        ...,
        description="ID of the child",
    )
    goal: str = Field(
        ...,
        description="Description of the learning goal",
        min_length=1,
    )
    category: str = Field(
        default="",
        description="Category: reading, math, writing, etc.",
    )
    target_date: str | None = Field(
        default=None,
        description="ISO date target for completion",
    )
    milestones: list[str] = Field(
        default_factory=list,
        description="Ordered list of milestone descriptions",
    )
    milestones_completed: list[int] = Field(
        default_factory=list,
        description="Indices of completed milestones",
    )
    status: str = Field(
        default="active",
        description="Goal status: active, completed, paused, abandoned",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO datetime when the goal was created",
    )
    completed_at: str | None = Field(
        default=None,
        description="ISO datetime when the goal was completed",
    )
    reflection: str = Field(
        default="",
        description="Parent/child reflection on the goal",
    )
