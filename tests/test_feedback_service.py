"""Tests for the FeedbackService."""

import pytest

from parenting.models.feedback import AdviceFeedback
from parenting.services.feedback_service import FeedbackService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def feedback_service(tmp_store: JsonStore) -> FeedbackService:
    """Provide a FeedbackService backed by a temporary store."""
    return FeedbackService(store=tmp_store)


def _rate(
    svc: FeedbackService,
    child_id: str = "max",
    technique: str = "emotion coaching",
    outcome: int = 4,
    context: str = "bedtime battles",
    **kwargs: object,
) -> AdviceFeedback:
    """Helper to rate a technique with sensible defaults."""
    return svc.rate_advice(
        child_id=child_id,
        technique=technique,
        outcome=outcome,
        context=context,
        **kwargs,
    )


class TestRateAdvice:
    def test_rate_advice(self, feedback_service: FeedbackService) -> None:
        # given — empty feedback store

        # when
        feedback = _rate(feedback_service)

        # then
        assert feedback.id is not None
        assert len(feedback.id) == 8
        assert feedback.child_id == "max"
        assert feedback.technique == "emotion coaching"
        assert feedback.outcome == 4
        assert feedback.context == "bedtime battles"
        assert feedback.used_as_intended is True
        assert feedback.confidence == 3
        assert feedback.timestamp is not None


class TestGetFeedbackHistoryAll:
    def test_get_feedback_history_all(
        self, feedback_service: FeedbackService
    ) -> None:
        # given
        _rate(feedback_service, child_id="max", technique="emotion coaching")
        _rate(feedback_service, child_id="emma", technique="logical consequences")

        # when
        history = feedback_service.get_feedback_history()

        # then
        assert len(history) == 2


class TestGetFeedbackHistoryByChild:
    def test_get_feedback_history_by_child(
        self, feedback_service: FeedbackService
    ) -> None:
        # given
        _rate(feedback_service, child_id="max", technique="emotion coaching")
        _rate(feedback_service, child_id="emma", technique="logical consequences")
        _rate(feedback_service, child_id="max", technique="time-in")

        # when
        max_history = feedback_service.get_feedback_history(child_id="max")

        # then
        assert len(max_history) == 2
        assert all(e.child_id == "max" for e in max_history)


class TestGetFeedbackHistoryByTechnique:
    def test_get_feedback_history_by_technique(
        self, feedback_service: FeedbackService
    ) -> None:
        # given
        _rate(feedback_service, child_id="max", technique="emotion coaching")
        _rate(feedback_service, child_id="emma", technique="emotion coaching")
        _rate(feedback_service, child_id="max", technique="logical consequences")

        # when
        coaching = feedback_service.get_feedback_history(technique="emotion coaching")

        # then
        assert len(coaching) == 2
        assert all(e.technique == "emotion coaching" for e in coaching)


class TestGetFamilyInsightsStructure:
    def test_get_family_insights_structure(
        self, feedback_service: FeedbackService
    ) -> None:
        # given
        _rate(feedback_service, child_id="max", technique="emotion coaching", outcome=5)
        _rate(feedback_service, child_id="max", technique="emotion coaching", outcome=4)
        _rate(feedback_service, child_id="max", technique="time-in", outcome=2)

        # when
        insights = feedback_service.get_family_insights()

        # then
        assert "children" in insights
        assert "total_feedback_entries" in insights
        assert "note" in insights
        assert insights["total_feedback_entries"] == 3
        assert "max" in insights["children"]

        max_insights = insights["children"]["max"]
        assert "techniques" in max_insights
        assert "most_effective" in max_insights
        assert "least_effective" in max_insights

        # Check technique stats have required fields
        for tech in max_insights["techniques"]:
            assert "technique" in tech
            assert "average_outcome" in tech
            assert "sample_size" in tech
            assert "days_since_last_feedback" in tech
            assert "confidence_level" in tech


class TestGetFamilyInsightsConfidenceLabels:
    def test_get_family_insights_confidence_labels(
        self, feedback_service: FeedbackService
    ) -> None:
        # given — 2 ratings (early signal), 5 ratings (developing), 10 ratings (established)
        for _ in range(2):
            _rate(feedback_service, child_id="max", technique="emotion coaching", outcome=4)
        for _ in range(5):
            _rate(feedback_service, child_id="max", technique="time-in", outcome=3)
        for _ in range(10):
            _rate(feedback_service, child_id="max", technique="logical consequences", outcome=5)

        # when
        insights = feedback_service.get_family_insights(child_id="max")

        # then
        techniques = insights["children"]["max"]["techniques"]
        by_name = {t["technique"]: t for t in techniques}

        assert by_name["emotion coaching"]["confidence_level"] == "early family signal"
        assert by_name["time-in"]["confidence_level"] == "developing pattern"
        assert by_name["logical consequences"]["confidence_level"] == "established pattern"


class TestGetTechniqueSummary:
    def test_get_technique_summary(
        self, feedback_service: FeedbackService
    ) -> None:
        # given
        _rate(feedback_service, child_id="max", technique="emotion coaching", outcome=5, context="bedtime")
        _rate(feedback_service, child_id="emma", technique="emotion coaching", outcome=3, context="homework")

        # when
        summary = feedback_service.get_technique_summary("emotion coaching")

        # then
        assert summary["technique"] == "emotion coaching"
        assert summary["total_ratings"] == 2
        assert summary["average_outcome"] == 4.0
        assert "max" in summary["per_child"]
        assert "emma" in summary["per_child"]
        assert summary["per_child"]["max"]["average_outcome"] == 5.0
        assert summary["per_child"]["emma"]["average_outcome"] == 3.0
        assert "bedtime" in summary["contexts_used"]
        assert "homework" in summary["contexts_used"]

    def test_get_technique_summary_empty(
        self, feedback_service: FeedbackService
    ) -> None:
        # given — no feedback

        # when
        summary = feedback_service.get_technique_summary("nonexistent technique")

        # then
        assert summary["total_ratings"] == 0
        assert "No feedback recorded" in summary["note"]


class TestInsightsSortByEffectiveness:
    def test_insights_sort_by_effectiveness(
        self, feedback_service: FeedbackService
    ) -> None:
        # given — techniques with different effectiveness levels
        _rate(feedback_service, child_id="max", technique="time-in", outcome=2)
        _rate(feedback_service, child_id="max", technique="emotion coaching", outcome=5)
        _rate(feedback_service, child_id="max", technique="logical consequences", outcome=4)

        # when
        insights = feedback_service.get_family_insights(child_id="max")

        # then — techniques should be sorted highest outcome first
        techniques = insights["children"]["max"]["techniques"]
        outcomes = [t["average_outcome"] for t in techniques]
        assert outcomes == sorted(outcomes, reverse=True)
        assert techniques[0]["technique"] == "emotion coaching"
        assert techniques[-1]["technique"] == "time-in"
