"""Journal domain models — freeform parenting journal entries."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class JournalEntry(BaseModel):
    """A single journal entry for family or child-level observations."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique entry identifier",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the entry was created (UTC)",
    )
    child_id: str | None = Field(
        default=None,
        description="Child this entry is about, or None for family-level",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Journal entry text",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization (e.g. 'milestone', 'concern')",
    )
