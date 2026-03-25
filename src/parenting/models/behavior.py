"""Behavior domain models — points, rewards, chores, and consequences."""

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class PointsConfig(BaseModel):
    """Configuration for the points system."""

    points_per_day: int = Field(
        default=3,
        ge=1,
        description="Max points earnable per day",
    )
    reset_schedule: Literal["daily", "weekly", "never"] = Field(
        default="daily",
        description="How often points reset",
    )
    rollover: bool = Field(
        default=False,
        description="Whether unused points carry over",
    )
    reset_time: str = Field(
        default="00:00",
        description="Reset time in HH:MM format",
    )


class RewardOption(BaseModel):
    """A reward that children can redeem points for."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique reward identifier",
    )
    name: str = Field(
        ...,
        description="Reward name",
        min_length=1,
    )
    point_cost: int = Field(
        ...,
        ge=1,
        description="Points required to redeem",
    )
    description: str = Field(
        default="",
        description="Reward description",
    )
    active: bool = Field(
        default=True,
        description="Whether this reward is currently available",
    )


class PointsEntry(BaseModel):
    """A single points transaction (earned or spent)."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique entry identifier",
    )
    child_id: str = Field(
        ...,
        description="Child this entry belongs to",
    )
    delta: int = Field(
        ...,
        description="Points change: positive=earned, negative=spent/deducted",
    )
    reason: str = Field(
        ...,
        description="Why points were added or removed",
    )
    category: str = Field(
        default="general",
        description="Category: behavior, chore, academic, bonus, spent",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this entry was created",
    )


class ChoreDefinition(BaseModel):
    """A chore that can be assigned to children."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique chore identifier",
    )
    name: str = Field(
        ...,
        description="Chore name",
        min_length=1,
    )
    description: str = Field(
        default="",
        description="Chore description",
    )
    frequency: Literal["daily", "weekly", "as_needed"] = Field(
        default="daily",
        description="How often this chore needs doing",
    )
    assigned_to: list[str] = Field(
        default_factory=list,
        description="Child IDs this chore is assigned to (empty = all)",
    )
    point_value: int = Field(
        default=0,
        ge=0,
        description="Points earned for completing (0 = family duty, no points)",
    )
    age_minimum: int = Field(
        default=0,
        ge=0,
        description="Minimum age in years to be assigned this chore",
    )


class ChoreCompletion(BaseModel):
    """A record of a chore being completed."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique completion identifier",
    )
    chore_id: str = Field(
        ...,
        description="Which chore was completed",
    )
    child_id: str = Field(
        ...,
        description="Which child completed it",
    )
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the chore was completed",
    )
    verified_by: str = Field(
        default="",
        description="Who verified the completion",
    )
    notes: str = Field(
        default="",
        description="Optional notes about the completion",
    )


class ConsequenceLog(BaseModel):
    """A logged consequence for a behavior incident."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique consequence identifier",
    )
    child_id: str = Field(
        ...,
        description="Which child this consequence is for",
    )
    behavior: str = Field(
        ...,
        description="The behavior that triggered the consequence",
    )
    consequence: str = Field(
        ...,
        description="What consequence was applied",
    )
    consequence_type: Literal["natural", "logical", "loss_of_privilege", "other"] = (
        Field(
            default="logical",
            description="Type of consequence",
        )
    )
    context: str = Field(
        default="",
        description="Additional context about the situation",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this was logged",
    )
    follow_up_notes: str = Field(
        default="",
        description="Notes from follow-up conversation",
    )
