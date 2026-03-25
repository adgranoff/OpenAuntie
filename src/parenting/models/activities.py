"""Activities domain models — family events, trip planning, activity suggestions."""

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class FamilyEvent(BaseModel):
    """A family activity or outing."""

    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    name: str = Field(..., description="Activity name", min_length=1)
    date: str = Field(..., description="ISO date string")
    time: str | None = Field(default=None, description="Time in HH:MM format")
    location: str = Field(default="")
    children_involved: list[str] = Field(
        default_factory=list,
        description="Child IDs involved, empty = all",
    )
    category: str = Field(
        default="",
        description="outdoor, educational, social, creative, physical",
    )
    notes: str = Field(default="")
    rating: int | None = Field(default=None, ge=1, le=5, description="How did it go? 1-5")
    would_repeat: bool | None = Field(default=None)


class TripPlan(BaseModel):
    """A vacation or trip plan, optionally with its own point system."""

    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    name: str = Field(..., min_length=1)
    start_date: str = Field(..., description="ISO date")
    end_date: str = Field(..., description="ISO date")
    destination: str = Field(default="")
    activities: list[str] = Field(default_factory=list)
    packing_list: list[str] = Field(default_factory=list)
    behavior_plan: str = Field(
        default="",
        description="Point system or behavior expectations for the trip",
    )
    notes: str = Field(default="")
    active: bool = Field(default=True)


class ActivitySuggestion(BaseModel):
    """A suggested activity based on children's ages and interests."""

    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    name: str
    category: str = Field(default="")
    age_range: str = Field(default="", description="e.g. '5-10'")
    description: str = Field(default="")
    indoor_outdoor: str = Field(default="either", description="indoor, outdoor, either")
    energy_level: str = Field(default="medium", description="low, medium, high")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
