"""Tests for the FamilyService."""

from datetime import date

import pytest

from parenting.models.family import Child, FamilyProfile
from parenting.services.family_service import FamilyService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def family_service(tmp_store: JsonStore) -> FamilyService:
    """Provide a FamilyService backed by a temporary store."""
    return FamilyService(store=tmp_store)


@pytest.fixture
def seeded_service(
    family_service: FamilyService, sample_family: FamilyProfile
) -> FamilyService:
    """Provide a FamilyService with the sample family already saved."""
    family_service.save_family(sample_family)
    return family_service


class TestGetFamily:
    def test_returns_none_for_empty_store(
        self, family_service: FamilyService
    ) -> None:
        # given — empty store

        # when
        result = family_service.get_family()

        # then
        assert result is None

    def test_returns_saved_family(
        self, seeded_service: FamilyService, sample_family: FamilyProfile
    ) -> None:
        # given — family already saved in seeded_service

        # when
        result = seeded_service.get_family()

        # then
        assert result is not None
        assert result.family_name == sample_family.family_name
        assert len(result.children) == 2
        assert len(result.parents) == 2


class TestSaveAndRetrieveFamily:
    def test_save_persists_all_fields(
        self, seeded_service: FamilyService
    ) -> None:
        # given — family saved in seeded_service

        # when
        profile = seeded_service.get_family()

        # then
        assert profile is not None
        assert profile.timezone == "America/Chicago"
        assert "kindness" in profile.values
        assert profile.parents[0].name == "Alice"
        assert profile.children[0].id == "max"


class TestGetChild:
    def test_get_existing_child(self, seeded_service: FamilyService) -> None:
        # given — family with children "max" and "emma"

        # when
        child = seeded_service.get_child("max")

        # then
        assert child is not None
        assert child.name == "Max"
        assert child.date_of_birth == date(2020, 6, 15)

    def test_get_nonexistent_child_returns_none(
        self, seeded_service: FamilyService
    ) -> None:
        # given — family exists but no child "zara"

        # when
        result = seeded_service.get_child("zara")

        # then
        assert result is None

    def test_get_child_returns_none_when_no_family(
        self, family_service: FamilyService
    ) -> None:
        # given — empty store

        # when
        result = family_service.get_child("max")

        # then
        assert result is None


class TestAddChild:
    def test_add_new_child(self, seeded_service: FamilyService) -> None:
        # given
        new_child = Child(
            id="zara",
            name="Zara",
            date_of_birth=date(2025, 3, 1),
        )

        # when
        updated = seeded_service.add_child(new_child)

        # then
        assert len(updated.children) == 3
        assert seeded_service.get_child("zara") is not None
        assert seeded_service.get_child("zara").name == "Zara"  # type: ignore[union-attr]

    def test_add_child_fails_for_duplicate_id(
        self, seeded_service: FamilyService
    ) -> None:
        # given
        duplicate = Child(
            id="max",
            name="Max Duplicate",
            date_of_birth=date(2020, 6, 15),
        )

        # when / then
        with pytest.raises(ValueError, match="already exists"):
            seeded_service.add_child(duplicate)

    def test_add_child_fails_when_no_family(
        self, family_service: FamilyService
    ) -> None:
        # given — empty store
        child = Child(
            id="orphan",
            name="Orphan",
            date_of_birth=date(2024, 1, 1),
        )

        # when / then
        with pytest.raises(RuntimeError, match="No family profile"):
            family_service.add_child(child)


class TestUpdateChild:
    def test_update_child_name(self, seeded_service: FamilyService) -> None:
        # given — child "max" exists

        # when
        updated = seeded_service.update_child("max", name="Maxwell")

        # then
        assert updated.name == "Maxwell"
        assert seeded_service.get_child("max").name == "Maxwell"  # type: ignore[union-attr]

    def test_update_child_strengths(
        self, seeded_service: FamilyService
    ) -> None:
        # given
        new_strengths = ["creativity", "persistence", "math"]

        # when
        updated = seeded_service.update_child("emma", strengths=new_strengths)

        # then
        assert updated.strengths == new_strengths

    def test_update_nonexistent_child_raises(
        self, seeded_service: FamilyService
    ) -> None:
        # given — no child "ghost"

        # when / then
        with pytest.raises(KeyError, match="not found"):
            seeded_service.update_child("ghost", name="Ghost")


class TestChildAgeDescription:
    def test_age_description_format(self) -> None:
        # given — a child born ~3 years and 6 months ago
        today = date.today()
        dob = today.replace(year=today.year - 3, month=today.month)
        # Shift back 6 months, handling year wrap
        month = dob.month - 6
        year = dob.year
        if month <= 0:
            month += 12
            year -= 1
        # Clamp day to valid range for target month
        import calendar

        max_day = calendar.monthrange(year, month)[1]
        day = min(dob.day, max_day)
        dob = date(year, month, day)

        child = Child(id="test", name="Test", date_of_birth=dob)

        # when
        desc = child.age_description

        # then — should contain "years" and "months"
        assert "years" in desc
        assert "months" in desc

    def test_age_description_years_only(self) -> None:
        # given — a child born exactly N years ago today
        today = date.today()
        dob = today.replace(year=today.year - 5)
        child = Child(id="test", name="Test", date_of_birth=dob)

        # when
        desc = child.age_description

        # then
        assert desc == "5 years"

    def test_age_description_months_only(self) -> None:
        # given — a child born a few months ago (same year)
        today = date.today()
        # Go back 3 months, handle year wrap
        month = today.month - 3
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        import calendar

        max_day = calendar.monthrange(year, month)[1]
        day = min(today.day, max_day)
        dob = date(year, month, day)

        child = Child(id="baby", name="Baby", date_of_birth=dob)

        # when
        desc = child.age_description

        # then
        assert desc == "3 months"


class TestGetChildAgeYears:
    def test_age_in_decimal_years(self, seeded_service: FamilyService) -> None:
        # given — "max" was born 2020-06-15
        # The age should be roughly (today - 2020-06-15) / 365.25

        # when
        age = seeded_service.get_child_age_years("max")

        # then
        expected = (date.today() - date(2020, 6, 15)).days / 365.25
        assert abs(age - expected) < 0.01

    def test_age_raises_for_unknown_child(
        self, seeded_service: FamilyService
    ) -> None:
        # given — no child "ghost"

        # when / then
        with pytest.raises(KeyError, match="not found"):
            seeded_service.get_child_age_years("ghost")
