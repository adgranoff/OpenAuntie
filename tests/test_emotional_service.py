"""Tests for the EmotionalService."""

from datetime import datetime, timedelta, timezone

import pytest

from parenting.models.emotional import ConflictRecord, DevelopmentalMilestone, MoodEntry
from parenting.services.emotional_service import EmotionalService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def emo_service(tmp_store: JsonStore) -> EmotionalService:
    """Provide an EmotionalService backed by a temporary store."""
    return EmotionalService(store=tmp_store)


class TestLogMood:
    def test_log_mood(self, emo_service: EmotionalService) -> None:
        # given / when
        entry = emo_service.log_mood(
            child_id="max",
            zone="green",
            intensity=2,
            emotions=["happy", "excited"],
            context="After school",
            coping_used=["deep breathing"],
        )

        # then
        assert isinstance(entry, MoodEntry)
        assert entry.child_id == "max"
        assert entry.zone == "green"
        assert entry.intensity == 2
        assert entry.emotions == ["happy", "excited"]
        assert entry.coping_used == ["deep breathing"]

    def test_log_mood_minimal(self, emo_service: EmotionalService) -> None:
        # given / when
        entry = emo_service.log_mood(child_id="emma")

        # then
        assert entry.zone is None
        assert entry.intensity is None
        assert entry.emotions == []
        assert entry.context == ""

    def test_log_mood_persists(self, emo_service: EmotionalService) -> None:
        # given
        emo_service.log_mood(child_id="max", zone="yellow")

        # when
        trends = emo_service.get_mood_trends(child_id="max")

        # then
        assert len(trends["entries"]) == 1


class TestGetMoodTrendsZoneDistribution:
    def test_get_mood_trends_zone_distribution(
        self, emo_service: EmotionalService
    ) -> None:
        # given
        emo_service.log_mood(child_id="max", zone="green", intensity=2)
        emo_service.log_mood(child_id="max", zone="green", intensity=3)
        emo_service.log_mood(child_id="max", zone="yellow", intensity=4)
        emo_service.log_mood(child_id="max", zone="red", intensity=5)

        # when
        trends = emo_service.get_mood_trends(child_id="max")

        # then
        assert trends["zone_distribution"]["green"] == 0.5
        assert trends["zone_distribution"]["yellow"] == 0.25
        assert trends["zone_distribution"]["red"] == 0.25
        assert trends["average_intensity"] == pytest.approx(3.5, abs=0.1)

    def test_get_mood_trends_common_emotions(
        self, emo_service: EmotionalService
    ) -> None:
        # given
        emo_service.log_mood(
            child_id="max", emotions=["frustrated", "angry"]
        )
        emo_service.log_mood(
            child_id="max", emotions=["frustrated", "sad"]
        )
        emo_service.log_mood(child_id="max", emotions=["happy"])

        # when
        trends = emo_service.get_mood_trends(child_id="max")

        # then — frustrated should be the most common
        assert trends["common_emotions"][0] == "frustrated"

    def test_get_mood_trends_empty(
        self, emo_service: EmotionalService
    ) -> None:
        # given — no entries

        # when
        trends = emo_service.get_mood_trends(child_id="max")

        # then
        assert trends["entries"] == []
        assert trends["zone_distribution"] == {}
        assert trends["average_intensity"] is None
        assert trends["common_emotions"] == []


class TestLogConflict:
    def test_log_conflict(self, emo_service: EmotionalService) -> None:
        # given / when
        record = emo_service.log_conflict(
            children_involved=["max", "emma"],
            trigger="Toy sharing",
            description="Both wanted the same toy",
            resolution="Took turns with a timer",
            resolution_type="mediated",
            what_worked="Timer made it feel fair",
            what_didnt_work="Verbal negotiation alone",
        )

        # then
        assert isinstance(record, ConflictRecord)
        assert record.children_involved == ["max", "emma"]
        assert record.trigger == "Toy sharing"
        assert record.resolution_type == "mediated"
        assert record.what_worked == "Timer made it feel fair"

    def test_log_conflict_minimal(self, emo_service: EmotionalService) -> None:
        # given / when
        record = emo_service.log_conflict(
            children_involved=["max", "emma"],
            trigger="Screen time",
        )

        # then
        assert record.description == ""
        assert record.resolution_type == "mediated"


class TestGetConflictPatterns:
    def test_get_conflict_patterns(
        self, emo_service: EmotionalService
    ) -> None:
        # given
        emo_service.log_conflict(
            children_involved=["max", "emma"],
            trigger="Toy sharing",
            resolution_type="mediated",
        )
        emo_service.log_conflict(
            children_involved=["max", "emma"],
            trigger="Toy sharing",
            resolution_type="self_resolved",
        )
        emo_service.log_conflict(
            children_involved=["max"],
            trigger="Bedtime",
            resolution_type="mediated",
        )

        # when
        patterns = emo_service.get_conflict_patterns(days=30)

        # then
        assert patterns["total_conflicts"] == 3
        assert patterns["common_triggers"][0] == "Toy sharing"
        assert patterns["resolution_types"]["mediated"] == 2
        assert patterns["resolution_types"]["self_resolved"] == 1
        # max involved in all 3, emma in 2
        assert patterns["children_frequency"]["max"] == 3
        assert patterns["children_frequency"]["emma"] == 2

    def test_get_conflict_patterns_empty(
        self, emo_service: EmotionalService
    ) -> None:
        # given — no conflicts

        # when
        patterns = emo_service.get_conflict_patterns()

        # then
        assert patterns["total_conflicts"] == 0
        assert patterns["common_triggers"] == []


class TestLogMilestone:
    def test_log_milestone(self, emo_service: EmotionalService) -> None:
        # given / when
        milestone = emo_service.log_milestone(
            child_id="emma",
            description="First complete sentence",
            category="language",
        )

        # then
        assert isinstance(milestone, DevelopmentalMilestone)
        assert milestone.child_id == "emma"
        assert milestone.description == "First complete sentence"
        assert milestone.category == "language"

    def test_log_milestone_default_category(
        self, emo_service: EmotionalService
    ) -> None:
        # given / when
        milestone = emo_service.log_milestone(
            child_id="max", description="Tied own shoes"
        )

        # then
        assert milestone.category == "general"


class TestGetMilestonesByChild:
    def test_get_milestones_by_child(
        self, emo_service: EmotionalService
    ) -> None:
        # given
        emo_service.log_milestone(
            child_id="max", description="Rode a bike"
        )
        emo_service.log_milestone(
            child_id="emma", description="First word"
        )
        emo_service.log_milestone(
            child_id="max", description="Tied shoes"
        )

        # when
        max_milestones = emo_service.get_milestones(child_id="max")

        # then
        assert len(max_milestones) == 2
        assert all(m.child_id == "max" for m in max_milestones)

    def test_get_milestones_all(self, emo_service: EmotionalService) -> None:
        # given
        emo_service.log_milestone(
            child_id="max", description="Milestone A"
        )
        emo_service.log_milestone(
            child_id="emma", description="Milestone B"
        )

        # when
        all_milestones = emo_service.get_milestones()

        # then
        assert len(all_milestones) == 2

    def test_get_milestones_empty(
        self, emo_service: EmotionalService
    ) -> None:
        # given — no milestones

        # when
        result = emo_service.get_milestones(child_id="max")

        # then
        assert result == []
