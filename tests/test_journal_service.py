"""Tests for the JournalService."""

from datetime import datetime, timedelta, timezone

import pytest

from parenting.models.journal import JournalEntry
from parenting.services.journal_service import JournalService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def journal_service(tmp_store: JsonStore) -> JournalService:
    """Provide a JournalService backed by a temporary store."""
    return JournalService(store=tmp_store)


class TestAddEntry:
    def test_add_entry(self, journal_service: JournalService) -> None:
        # given
        content = "Max had a great day at school today."

        # when
        entry = journal_service.add_entry(
            content=content,
            child_id="max",
            tags=["win", "school"],
        )

        # then
        assert entry.content == content
        assert entry.child_id == "max"
        assert entry.tags == ["win", "school"]
        assert entry.id  # non-empty
        assert entry.timestamp is not None


class TestGetEntries:
    def test_get_entries_all(self, journal_service: JournalService) -> None:
        # given
        journal_service.add_entry(content="Entry one")
        journal_service.add_entry(content="Entry two")
        journal_service.add_entry(content="Entry three")

        # when
        entries = journal_service.get_entries()

        # then
        assert len(entries) == 3

    def test_get_entries_by_child(
        self, journal_service: JournalService
    ) -> None:
        # given
        journal_service.add_entry(content="Max entry", child_id="max")
        journal_service.add_entry(content="Emma entry", child_id="emma")
        journal_service.add_entry(content="Family entry")

        # when
        entries = journal_service.get_entries(child_id="max")

        # then
        assert len(entries) == 1
        assert entries[0].content == "Max entry"

    def test_get_entries_by_days(
        self, journal_service: JournalService
    ) -> None:
        # given — add an entry, then manipulate an older one in the store
        journal_service.add_entry(content="Recent entry")

        # Add an old entry by directly manipulating store
        old_entry = JournalEntry(
            content="Old entry",
            timestamp=datetime.now(timezone.utc) - timedelta(days=30),
        )
        data = journal_service._load_data()
        data["entries"].append(old_entry.model_dump(mode="json"))
        journal_service._save_data(data)

        # when — get entries from last 7 days
        entries = journal_service.get_entries(days=7)

        # then
        assert len(entries) == 1
        assert entries[0].content == "Recent entry"

    def test_get_entries_by_tags(
        self, journal_service: JournalService
    ) -> None:
        # given
        journal_service.add_entry(
            content="Win entry", tags=["win", "milestone"]
        )
        journal_service.add_entry(
            content="Concern entry", tags=["concern"]
        )
        journal_service.add_entry(
            content="Untagged entry"
        )

        # when
        entries = journal_service.get_entries(tags=["win"])

        # then
        assert len(entries) == 1
        assert entries[0].content == "Win entry"

    def test_get_entries_by_tags_matches_any(
        self, journal_service: JournalService
    ) -> None:
        # given
        journal_service.add_entry(content="A", tags=["win"])
        journal_service.add_entry(content="B", tags=["concern"])
        journal_service.add_entry(content="C", tags=["medical"])

        # when — filter by win or concern
        entries = journal_service.get_entries(tags=["win", "concern"])

        # then
        assert len(entries) == 2
        contents = {e.content for e in entries}
        assert contents == {"A", "B"}

    def test_get_entries_returns_newest_first(
        self, journal_service: JournalService
    ) -> None:
        # given
        journal_service.add_entry(content="First")
        journal_service.add_entry(content="Second")
        journal_service.add_entry(content="Third")

        # when
        entries = journal_service.get_entries()

        # then — newest first
        assert entries[0].content == "Third"
        assert entries[-1].content == "First"

    def test_get_entries_empty(
        self, journal_service: JournalService
    ) -> None:
        # given — empty store

        # when
        entries = journal_service.get_entries()

        # then
        assert entries == []
