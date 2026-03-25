"""Tests for the activity service."""

from datetime import datetime

from parenting.models.activities import FamilyEvent, TripPlan
from parenting.services.activity_service import ActivityService


class TestLogActivity:
    def test_log_activity_creates_event(self, tmp_store):
        # given
        service = ActivityService(tmp_store)

        # when
        event = service.log_activity(
            name="Park visit",
            date="2026-03-24",
            category="outdoor",
            rating=5,
            would_repeat=True,
        )

        # then
        assert event.name == "Park visit"
        assert event.category == "outdoor"
        assert event.rating == 5
        assert event.would_repeat is True

    def test_log_activity_persists(self, tmp_store):
        # given
        service = ActivityService(tmp_store)
        service.log_activity(name="Bowling", date="2026-03-24")

        # when
        history = service.get_activity_history()

        # then
        assert len(history) == 1
        assert history[0].name == "Bowling"


class TestGetActivityHistory:
    def test_get_history_empty(self, tmp_store):
        # given
        service = ActivityService(tmp_store)

        # when
        history = service.get_activity_history()

        # then
        assert history == []

    def test_filter_by_category(self, tmp_store):
        # given
        service = ActivityService(tmp_store)
        service.log_activity(name="Hiking", date="2026-03-24", category="outdoor")
        service.log_activity(name="Painting", date="2026-03-24", category="creative")

        # when
        outdoor = service.get_activity_history(category="outdoor")

        # then
        assert len(outdoor) == 1
        assert outdoor[0].name == "Hiking"


class TestTripPlanning:
    def test_plan_trip(self, tmp_store):
        # given
        service = ActivityService(tmp_store)

        # when
        trip = service.plan_trip(
            name="Spring Break",
            start_date="2026-04-01",
            end_date="2026-04-07",
            destination="Beach",
            behavior_plan="3 points per day, spend on activities",
        )

        # then
        assert trip.name == "Spring Break"
        assert trip.destination == "Beach"
        assert trip.active is True

    def test_get_trip_by_id(self, tmp_store):
        # given
        service = ActivityService(tmp_store)
        trip = service.plan_trip(
            name="Cruise",
            start_date="2026-03-23",
            end_date="2026-03-28",
        )

        # when
        found = service.get_trip(trip.id)

        # then
        assert found.name == "Cruise"

    def test_get_active_trips(self, tmp_store):
        # given
        service = ActivityService(tmp_store)
        service.plan_trip(name="Trip 1", start_date="2026-04-01", end_date="2026-04-05")
        service.plan_trip(name="Trip 2", start_date="2026-05-01", end_date="2026-05-05")

        # when
        trips = service.get_trip()

        # then
        assert len(trips) == 2


class TestActivitySuggestions:
    def test_suggest_activity_returns_context(self, tmp_store):
        # given
        service = ActivityService(tmp_store)
        service.log_activity(name="Hiking", date="2026-03-20", category="outdoor", rating=5)

        # when
        suggestion = service.suggest_activity(ages=[7, 10], category="outdoor")

        # then
        assert "request" in suggestion
        assert "family_history" in suggestion
        assert suggestion["request"]["preferred_category"] == "outdoor"
        assert "Hiking" in suggestion["family_history"]["highly_rated_activities"]


class TestFamilyMeetingAgenda:
    def test_agenda_structure(self, tmp_store):
        # given
        service = ActivityService(tmp_store)

        # when
        agenda = service.create_family_meeting_agenda(tmp_store)

        # then
        assert "appreciations" in agenda
        assert "calendar" in agenda
        assert "new_business" in agenda
        assert "fun_planning" in agenda
