"""Shared test fixtures for OpenAuntie tests."""

from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from parenting.models.family import Child, FamilyProfile, Parent
from parenting.storage.json_store import JsonStore


@pytest.fixture
def tmp_store(tmp_path: Path) -> JsonStore:
    """Provide a JsonStore backed by a temporary directory."""
    return JsonStore(data_dir=tmp_path)


@pytest.fixture
def sample_family() -> FamilyProfile:
    """Return a FamilyProfile with 2 children for testing."""
    return FamilyProfile(
        family_name="TestFamily",
        parents=[
            Parent(id="parent-1", name="Alice", role="parent"),
            Parent(id="parent-2", name="Bob", role="co-parent"),
        ],
        children=[
            Child(
                id="max",
                name="Max",
                date_of_birth=date(2020, 6, 15),
                temperament_notes="Energetic and curious",
                strengths=["creativity", "persistence"],
                challenges=["transitions"],
                special_considerations=[],
            ),
            Child(
                id="emma",
                name="Emma",
                date_of_birth=date(2023, 1, 10),
                temperament_notes="Calm and observant",
                strengths=["empathy"],
                challenges=["separation anxiety"],
                special_considerations=["dairy allergy"],
            ),
        ],
        timezone="America/Chicago",
        values=["kindness", "curiosity", "resilience"],
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
