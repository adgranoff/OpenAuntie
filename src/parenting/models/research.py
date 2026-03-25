"""Research domain models — tracking external research updates and proposals."""

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class ResearchUpdate(BaseModel):
    """A proposed update to the knowledge base from external research."""

    id: str = Field(
        default_factory=lambda: str(uuid4())[:8],
        description="Unique proposal identifier",
    )
    source: str = Field(
        ...,
        description="Research source (e.g. PubMed, AAP, CDC, WHO)",
        examples=["PubMed", "AAP/HealthyChildren", "CDC"],
        min_length=1,
    )
    source_url: str = Field(
        default="",
        description="URL to the source material",
    )
    title: str = Field(
        ...,
        description="Title of the research finding or update",
        examples=["New guidance on screen time for toddlers"],
        min_length=1,
    )
    summary: str = Field(
        default="",
        description="Brief summary of the research finding",
    )
    relevant_knowledge_file: str = Field(
        ...,
        description="Which knowledge/ file this relates to",
        examples=["discipline.md", "sleep.md", "nutrition.md"],
    )
    proposed_change: str = Field(
        ...,
        description="What should change in the knowledge base",
        examples=["Update recommended screen time limits for ages 2-5"],
    )
    evidence_grade: str = Field(
        default="EMERGING",
        description="Evidence strength: STRONG, MODERATE, EMERGING, CONSENSUS",
    )
    citation: str = Field(
        default="",
        description="Formal citation for the research",
    )
    status: str = Field(
        default="pending",
        description="Proposal status: pending, approved, dismissed",
    )
    reviewer_notes: str = Field(
        default="",
        description="Notes from the reviewer on approval/dismissal",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of proposal creation",
    )
    reviewed_at: str | None = Field(
        default=None,
        description="ISO timestamp of when the proposal was reviewed",
    )
