"""Family domain models — children, parents, and the family profile."""

from datetime import date, datetime, timezone

from pydantic import BaseModel, Field, computed_field


class Child(BaseModel):
    """A child in the family, with developmental context for the consultant."""

    id: str = Field(
        ...,
        description="Unique child identifier (slug)",
        examples=["max", "emma"],
    )
    name: str = Field(
        ...,
        description="Child's display name",
        min_length=1,
    )
    date_of_birth: date = Field(
        ...,
        description="Child's date of birth",
    )
    temperament_notes: str = Field(
        default="",
        description="Parent's observations about temperament",
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Child's strengths (strengths-based parenting)",
    )
    challenges: list[str] = Field(
        default_factory=list,
        description="Current growth areas",
    )
    special_considerations: list[str] = Field(
        default_factory=list,
        description="Allergies, ADHD, etc.",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def age_description(self) -> str:
        """Compute age as 'X years Y months' from date_of_birth."""
        today = date.today()
        years = today.year - self.date_of_birth.year
        months = today.month - self.date_of_birth.month

        # Adjust for day-of-month
        if today.day < self.date_of_birth.day:
            months -= 1

        if months < 0:
            years -= 1
            months += 12

        if years == 0:
            return f"{months} months"
        if months == 0:
            return f"{years} years"
        return f"{years} years {months} months"


class Parent(BaseModel):
    """A parent or caregiver in the family."""

    id: str = Field(
        ...,
        description="Unique parent identifier",
    )
    name: str = Field(
        ...,
        description="Parent's display name",
        min_length=1,
    )
    role: str = Field(
        default="parent",
        description="parent, co-parent, guardian, caregiver",
    )


class FamilyProfile(BaseModel):
    """The top-level family profile, stored as the 'family_profile' domain."""

    family_name: str = Field(
        ...,
        description="Family last name",
        min_length=1,
    )
    parents: list[Parent] = Field(default_factory=list)
    children: list[Child] = Field(default_factory=list)
    timezone: str = Field(
        default="America/New_York",
        description="Family timezone (IANA)",
    )
    values: list[str] = Field(
        default_factory=list,
        description="Family values and priorities",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
