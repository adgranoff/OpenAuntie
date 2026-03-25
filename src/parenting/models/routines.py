"""Routines domain models — routine definitions, steps, and execution logs."""

import uuid

from pydantic import BaseModel, Field


class RoutineStep(BaseModel):
    """A single step within a routine."""

    order: int = Field(
        ...,
        ge=1,
        description="Step order number (1-based)",
    )
    name: str = Field(
        ...,
        min_length=1,
        description="Step name (e.g. 'Brush teeth')",
    )
    duration_minutes: int = Field(
        default=5,
        ge=1,
        description="Expected duration in minutes",
    )
    description: str = Field(
        default="",
        description="Optional step description or guidance",
    )


class RoutineDefinition(BaseModel):
    """A reusable routine template with ordered steps."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique routine identifier",
    )
    name: str = Field(
        ...,
        min_length=1,
        description="Routine name (e.g. 'Morning', 'Bedtime', 'Homework')",
    )
    child_id: str | None = Field(
        default=None,
        description="Child this routine is for, or None for family-wide",
    )
    steps: list[RoutineStep] = Field(
        default_factory=list,
        description="Ordered steps in this routine",
    )
    target_start_time: str | None = Field(
        default=None,
        description="Target start time in HH:MM format (e.g. '07:00')",
    )
    target_duration_minutes: int = Field(
        default=30,
        ge=1,
        description="Target total duration in minutes",
    )
    days_of_week: list[int] = Field(
        default_factory=lambda: [0, 1, 2, 3, 4, 5, 6],
        description="Days of week this routine applies (0=Monday, 6=Sunday)",
    )


class RoutineExecution(BaseModel):
    """A single execution record for a routine on a given day."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique execution identifier",
    )
    routine_id: str = Field(
        ...,
        description="ID of the routine that was executed",
    )
    child_id: str = Field(
        ...,
        description="ID of the child who performed the routine",
    )
    date: str = Field(
        ...,
        description="ISO date string (e.g. '2026-03-24')",
    )
    started_at: str | None = Field(
        default=None,
        description="ISO datetime when execution started",
    )
    completed_at: str | None = Field(
        default=None,
        description="ISO datetime when execution completed",
    )
    steps_completed: list[int] = Field(
        default_factory=list,
        description="Step order numbers that were completed",
    )
    steps_skipped: list[int] = Field(
        default_factory=list,
        description="Step order numbers that were skipped",
    )
    resistance_level: int = Field(
        default=0,
        ge=0,
        le=3,
        description="Resistance level: 0=none, 1=mild, 2=moderate, 3=high",
    )
    notes: str = Field(
        default="",
        description="Free-text notes about the execution",
    )
