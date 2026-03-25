"""Tests for the EducationService."""

from datetime import datetime, timedelta, timezone

import pytest

from parenting.models.education import HomeworkEntry, LearningGoal, ReadingEntry
from parenting.services.education_service import EducationService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def edu_service(tmp_store: JsonStore) -> EducationService:
    """Provide an EducationService backed by a temporary store."""
    return EducationService(store=tmp_store)


class TestLogReading:
    def test_log_reading(self, edu_service: EducationService) -> None:
        # given / when
        entry = edu_service.log_reading(
            child_id="max",
            book_title="Charlotte's Web",
            pages_read=25,
            minutes_read=30,
            finished_book=False,
            enjoyment=4,
        )

        # then
        assert isinstance(entry, ReadingEntry)
        assert entry.child_id == "max"
        assert entry.book_title == "Charlotte's Web"
        assert entry.pages_read == 25
        assert entry.minutes_read == 30
        assert entry.enjoyment == 4

    def test_log_reading_minimal(self, edu_service: EducationService) -> None:
        # given / when
        entry = edu_service.log_reading(child_id="emma", book_title="Goodnight Moon")

        # then
        assert entry.pages_read is None
        assert entry.minutes_read is None
        assert entry.finished_book is False


class TestGetReadingLogWithStats:
    def test_get_reading_log_with_stats(
        self, edu_service: EducationService
    ) -> None:
        # given
        edu_service.log_reading(
            child_id="max", book_title="Book A", pages_read=20,
            minutes_read=15, finished_book=True,
        )
        edu_service.log_reading(
            child_id="max", book_title="Book B", pages_read=30,
            minutes_read=25, finished_book=False,
        )

        # when
        result = edu_service.get_reading_log(child_id="max")

        # then
        assert len(result["entries"]) == 2
        assert result["stats"]["books_completed"] == 1
        assert result["stats"]["total_pages"] == 50
        assert result["stats"]["total_minutes"] == 40

    def test_get_reading_log_empty(self, edu_service: EducationService) -> None:
        # given — no entries

        # when
        result = edu_service.get_reading_log(child_id="max")

        # then
        assert result["entries"] == []
        assert result["stats"]["books_completed"] == 0
        assert result["stats"]["reading_streak"] == 0


class TestReadingStreak:
    def test_reading_streak_consecutive_days(
        self, edu_service: EducationService
    ) -> None:
        # given — manually insert entries with consecutive dates
        today = datetime.now(timezone.utc).date()
        data = edu_service._load_data()
        for i in range(3):
            entry = ReadingEntry(
                child_id="max",
                date=(today - timedelta(days=i)).isoformat(),
                book_title=f"Book {i}",
            )
            data["reading_entries"].append(entry.model_dump(mode="json"))
        edu_service._save_data(data)

        # when
        result = edu_service.get_reading_log(child_id="max")

        # then
        assert result["stats"]["reading_streak"] == 3

    def test_reading_streak_with_gap(
        self, edu_service: EducationService
    ) -> None:
        # given — entries with a gap
        today = datetime.now(timezone.utc).date()
        data = edu_service._load_data()
        # Today and yesterday (streak of 2), then skip a day, then 3 days ago
        for offset in [0, 1, 3]:
            entry = ReadingEntry(
                child_id="max",
                date=(today - timedelta(days=offset)).isoformat(),
                book_title=f"Book {offset}",
            )
            data["reading_entries"].append(entry.model_dump(mode="json"))
        edu_service._save_data(data)

        # when
        result = edu_service.get_reading_log(child_id="max")

        # then
        assert result["stats"]["reading_streak"] == 2


class TestLogHomework:
    def test_log_homework(self, edu_service: EducationService) -> None:
        # given / when
        entry = edu_service.log_homework(
            child_id="max",
            subject="math",
            duration_minutes=30,
            struggle_level=1,
            completed=True,
            help_needed="Long division",
        )

        # then
        assert isinstance(entry, HomeworkEntry)
        assert entry.subject == "math"
        assert entry.duration_minutes == 30
        assert entry.struggle_level == 1
        assert entry.help_needed == "Long division"


class TestGetHomeworkTrendsBySubject:
    def test_get_homework_trends_by_subject(
        self, edu_service: EducationService
    ) -> None:
        # given
        edu_service.log_homework(
            child_id="max", subject="math", duration_minutes=30, struggle_level=2
        )
        edu_service.log_homework(
            child_id="max", subject="math", duration_minutes=20, struggle_level=0
        )
        edu_service.log_homework(
            child_id="max", subject="reading", duration_minutes=15, struggle_level=0
        )

        # when
        trends = edu_service.get_homework_trends(child_id="max")

        # then
        assert trends["subjects_by_struggle"]["math"] == 1.0  # avg of 2 and 0
        assert trends["subjects_by_struggle"]["reading"] == 0.0
        assert trends["completion_rate"] == 1.0
        assert trends["average_duration"] == pytest.approx(21.7, abs=0.1)

    def test_get_homework_trends_completion_rate(
        self, edu_service: EducationService
    ) -> None:
        # given
        edu_service.log_homework(
            child_id="max", subject="math", duration_minutes=30, completed=True
        )
        edu_service.log_homework(
            child_id="max", subject="science", duration_minutes=20, completed=False
        )

        # when
        trends = edu_service.get_homework_trends(child_id="max")

        # then
        assert trends["completion_rate"] == 0.5


class TestSetLearningGoal:
    def test_set_learning_goal(self, edu_service: EducationService) -> None:
        # given / when
        goal = edu_service.set_learning_goal(
            child_id="max",
            goal="Read 20 books this semester",
            category="reading",
            milestones=["Read 5 books", "Read 10 books", "Read 20 books"],
            target_date="2026-06-30",
        )

        # then
        assert isinstance(goal, LearningGoal)
        assert goal.child_id == "max"
        assert goal.goal == "Read 20 books this semester"
        assert len(goal.milestones) == 3
        assert goal.status == "active"
        assert goal.target_date == "2026-06-30"


class TestUpdateLearningGoalMilestone:
    def test_update_learning_goal_milestone(
        self, edu_service: EducationService
    ) -> None:
        # given
        goal = edu_service.set_learning_goal(
            child_id="max",
            goal="Learn multiplication tables",
            milestones=["2x table", "5x table", "10x table"],
        )

        # when — mark first milestone completed
        updated = edu_service.update_learning_goal(
            goal.id, milestones_completed=[0]
        )

        # then
        assert 0 in updated.milestones_completed
        assert updated.status == "active"

    def test_update_learning_goal_complete(
        self, edu_service: EducationService
    ) -> None:
        # given
        goal = edu_service.set_learning_goal(
            child_id="max", goal="Learn to read"
        )

        # when
        updated = edu_service.update_learning_goal(
            goal.id,
            status="completed",
            completed_at=datetime.now(timezone.utc).isoformat(),
            reflection="Great progress!",
        )

        # then
        assert updated.status == "completed"
        assert updated.completed_at is not None
        assert updated.reflection == "Great progress!"

    def test_update_learning_goal_not_found(
        self, edu_service: EducationService
    ) -> None:
        # given — no goals

        # when / then
        with pytest.raises(KeyError, match="not found"):
            edu_service.update_learning_goal("nonexistent", status="paused")


class TestGetLearningGoalsByStatus:
    def test_get_learning_goals_by_status(
        self, edu_service: EducationService
    ) -> None:
        # given
        edu_service.set_learning_goal(child_id="max", goal="Goal A")
        goal_b = edu_service.set_learning_goal(child_id="max", goal="Goal B")
        edu_service.update_learning_goal(goal_b.id, status="completed")

        # when
        active_goals = edu_service.get_learning_goals(
            child_id="max", status="active"
        )
        completed_goals = edu_service.get_learning_goals(
            child_id="max", status="completed"
        )

        # then
        assert len(active_goals) == 1
        assert active_goals[0].goal == "Goal A"
        assert len(completed_goals) == 1
        assert completed_goals[0].goal == "Goal B"

    def test_get_learning_goals_all(
        self, edu_service: EducationService
    ) -> None:
        # given
        edu_service.set_learning_goal(child_id="max", goal="Goal A")
        edu_service.set_learning_goal(child_id="emma", goal="Goal B")

        # when
        all_goals = edu_service.get_learning_goals()

        # then
        assert len(all_goals) == 2
