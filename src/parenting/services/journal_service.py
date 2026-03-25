"""Journal service — CRUD operations for parenting journal entries."""

from datetime import datetime, timezone

from parenting.models.journal import JournalEntry
from parenting.storage.store import Store

JOURNAL_DOMAIN = "journal"


class JournalService:
    """Business logic for managing journal entries.

    Operates on the 'journal' domain with structure:
    {"entries": [...]}
    """

    def __init__(self, store: Store) -> None:
        self._store = store

    def _load_data(self) -> dict:
        """Load the journal domain data, initializing if empty."""
        if not self._store.exists(JOURNAL_DOMAIN):
            return {"entries": []}
        data = self._store.load(JOURNAL_DOMAIN)
        if not data:
            return {"entries": []}
        return data

    def _save_data(self, data: dict) -> None:
        """Save the journal domain data."""
        self._store.save(JOURNAL_DOMAIN, data)

    def add_entry(
        self,
        content: str,
        child_id: str | None = None,
        tags: list[str] | None = None,
    ) -> JournalEntry:
        """Add a new journal entry.

        Args:
            content: The journal entry text.
            child_id: Child this entry is about, or None for family-level.
            tags: Optional tags for categorization.

        Returns:
            The created JournalEntry.
        """
        entry = JournalEntry(
            content=content,
            child_id=child_id,
            tags=tags or [],
        )

        data = self._load_data()
        data["entries"].append(entry.model_dump(mode="json"))
        self._save_data(data)
        return entry

    def get_entries(
        self,
        child_id: str | None = None,
        days: int | None = None,
        tags: list[str] | None = None,
    ) -> list[JournalEntry]:
        """Retrieve journal entries with optional filtering.

        Args:
            child_id: Filter to entries about this child (None returns all).
            days: Only return entries from the last N days.
            tags: Only return entries matching any of these tags.

        Returns:
            List of matching JournalEntry objects, newest first.
        """
        data = self._load_data()
        entries = [
            JournalEntry.model_validate(e) for e in data.get("entries", [])
        ]

        # Filter by child_id
        if child_id is not None:
            entries = [e for e in entries if e.child_id == child_id]

        # Filter by recency
        if days is not None:
            now = datetime.now(timezone.utc)
            cutoff = now.timestamp() - (days * 86400)
            entries = [e for e in entries if e.timestamp.timestamp() >= cutoff]

        # Filter by tags (match any)
        if tags is not None:
            tag_set = set(tags)
            entries = [e for e in entries if tag_set & set(e.tags)]

        # Sort newest first
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries
