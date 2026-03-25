"""Health domain models — medications, appointments, and growth tracking."""

import uuid

from pydantic import BaseModel, Field


class Medication(BaseModel):
    """A medication prescribed or administered to a child."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique medication identifier",
    )
    child_id: str = Field(
        ...,
        description="ID of the child this medication is for",
    )
    name: str = Field(
        ...,
        description="Medication name",
        min_length=1,
    )
    dosage: str = Field(
        default="",
        description="Dosage amount and unit (e.g. '5mg', '2.5ml')",
    )
    frequency: str = Field(
        default="daily",
        description="How often: daily, twice_daily, as_needed",
    )
    time_of_day: list[str] = Field(
        default_factory=list,
        description="When to take: 'morning', 'evening', etc.",
    )
    prescriber: str = Field(
        default="",
        description="Name of prescribing provider",
    )
    start_date: str | None = Field(
        default=None,
        description="ISO date when medication was started",
    )
    end_date: str | None = Field(
        default=None,
        description="ISO date when medication was stopped",
    )
    notes: str = Field(
        default="",
        description="Additional notes",
    )
    active: bool = Field(
        default=True,
        description="Whether the medication is currently active",
    )


class MedicationLog(BaseModel):
    """A single administration event for a medication."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique log entry identifier",
    )
    medication_id: str = Field(
        ...,
        description="ID of the medication administered",
    )
    child_id: str = Field(
        ...,
        description="ID of the child",
    )
    administered_at: str = Field(
        ...,
        description="ISO datetime when medication was administered",
    )
    administered_by: str = Field(
        default="",
        description="Who administered the medication",
    )
    notes: str = Field(
        default="",
        description="Additional notes",
    )
    skipped: bool = Field(
        default=False,
        description="Whether this dose was skipped",
    )
    skip_reason: str = Field(
        default="",
        description="Reason the dose was skipped",
    )


class Appointment(BaseModel):
    """A medical or therapy appointment."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique appointment identifier",
    )
    child_id: str | None = Field(
        default=None,
        description="ID of the child (None for family-wide appointments)",
    )
    provider: str = Field(
        ...,
        description="Provider name",
        min_length=1,
    )
    type: str = Field(
        default="pediatrician",
        description="Appointment type: pediatrician, dentist, specialist, therapy",
    )
    date_time: str = Field(
        ...,
        description="ISO datetime of the appointment",
    )
    location: str = Field(
        default="",
        description="Appointment location",
    )
    notes: str = Field(
        default="",
        description="Additional notes",
    )
    completed: bool = Field(
        default=False,
        description="Whether the appointment has been completed",
    )
    follow_up_needed: bool = Field(
        default=False,
        description="Whether a follow-up is needed",
    )
    follow_up_notes: str = Field(
        default="",
        description="Notes about needed follow-up",
    )


class GrowthRecord(BaseModel):
    """A point-in-time growth measurement for a child."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique record identifier",
    )
    child_id: str = Field(
        ...,
        description="ID of the child",
    )
    date: str = Field(
        ...,
        description="ISO date of the measurement",
    )
    height_inches: float | None = Field(
        default=None,
        ge=0,
        description="Height in inches",
    )
    weight_pounds: float | None = Field(
        default=None,
        ge=0,
        description="Weight in pounds",
    )
    notes: str = Field(
        default="",
        description="Additional notes",
    )
