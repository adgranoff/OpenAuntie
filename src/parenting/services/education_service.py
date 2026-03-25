"""Education service — reading logs, homework tracking, and learning goals."""

from datetime import datetime, timedelta, timezone

from parenting.models.education import HomeworkEntry, LearningGoal, ReadingEntry
from parenting.storage.store import Store

EDUCATION_DOMAIN = "education"

_EMPTY_DATA: dict = {
    "reading_entries": [],
    "homework_entries": [],
    "learning_goals": [],
}


class EducationService:
    """Business logic for managing education-related data.

    Takes a Store backend and operates on the 'education' domain.
    """

    def __init__(self, store: Store) -> None:
        self._store = store

    def _load_data(self) -> dict:
        """Load education data, returning empty structure if none exists."""
        if not self._store.exists(EDUCATION_DOMAIN):
            return {k: list(v) for k, v in _EMPTY_DATA.items()}
        data = self._store.load(EDUCATION_DOMAIN)
        if not data:
            return {k: list(v) for k, v in _EMPTY_DATA.items()}
        return data

    def _save_data(self, data: dict) -> None:
        """Save education data to the store."""
        self._store.save(EDUCATION_DOMAIN, data)

    # ── Reading ──────────────────────────────────────────────────────

    def log_reading(
        self,
        child_id: str,
        book_title: str,
        pages_read: int | None = None,
        minutes_read: int | None = None,
        finished_book: bool = False,
        enjoyment: int | None = None,
    ) -> ReadingEntry:
        """Log a reading session for a child.

        Args:
            child_id: The child who read.
            book_title: Title of the book.
            pages_read: Pages read in this session.
            minutes_read: Duration in minutes.
            finished_book: Whether the child finished the book.
            enjoyment: Enjoyment rating 1-5.

        Returns:
            The created ReadingEntry.
        """
        entry = ReadingEntry(
            child_id=child_id,
            date=datetime.now(timezone.utc).date().isoformat(),
            book_title=book_title,
            pages_read=pages_read,
            minutes_read=minutes_read,
            finished_book=finished_book,
            enjoyment=enjoyment,
        )
        data = self._load_data()
        data["reading_entries"].append(entry.model_dump(mode="json"))
        self._save_data(data)
        return entry

    def get_reading_log(
        self, child_id: str | None = None, days: int | None = None
    ) -> dict:
        """Get reading entries with summary statistics.

        Args:
            child_id: Filter to a specific child, or None for all.
            days: Number of days to look back, or None for all time.

        Returns:
            Dict with 'entries' list and 'stats' dict containing:
            books_completed, total_pages, total_minutes, reading_streak.
        """
        data = self._load_data()
        entries = [ReadingEntry.model_validate(e) for e in data["reading_entries"]]

        if child_id is not None:
            entries = [e for e in entries if e.child_id == child_id]

        if days is not None:
            cutoff = (
                datetime.now(timezone.utc).date() - timedelta(days=days)
            ).isoformat()
            entries = [e for e in entries if e.date >= cutoff]

        # Sort by date descending for display
        entries.sort(key=lambda e: e.date, reverse=True)

        # Compute stats
        books_completed = sum(1 for e in entries if e.finished_book)
        total_pages = sum(e.pages_read or 0 for e in entries)
        total_minutes = sum(e.minutes_read or 0 for e in entries)
        reading_streak = self._compute_reading_streak(entries)

        return {
            "entries": [e.model_dump(mode="json") for e in entries],
            "stats": {
                "books_completed": books_completed,
                "total_pages": total_pages,
                "total_minutes": total_minutes,
                "reading_streak": reading_streak,
            },
        }

    def _compute_reading_streak(self, entries: list[ReadingEntry]) -> int:
        """Compute the current consecutive-day reading streak.

        Args:
            entries: Reading entries (any order).

        Returns:
            Number of consecutive days with at least one reading entry,
            counting backwards from the most recent entry date.
        """
        if not entries:
            return 0

        dates = sorted({e.date for e in entries}, reverse=True)
        streak = 1
        for i in range(1, len(dates)):
            prev = datetime.fromisoformat(dates[i - 1]).date()
            curr = datetime.fromisoformat(dates[i]).date()
            if (prev - curr).days == 1:
                streak += 1
            else:
                break
        return streak

    # ── Homework ─────────────────────────────────────────────────────

    def log_homework(
        self,
        child_id: str,
        subject: str,
        duration_minutes: int,
        struggle_level: int = 0,
        completed: bool = True,
        help_needed: str = "",
    ) -> HomeworkEntry:
        """Log a homework session for a child.

        Args:
            child_id: The child who did homework.
            subject: Subject area.
            duration_minutes: Time spent in minutes.
            struggle_level: Difficulty (0=easy, 1=moderate, 2=hard, 3=meltdown).
            completed: Whether homework was completed.
            help_needed: Description of help needed.

        Returns:
            The created HomeworkEntry.
        """
        entry = HomeworkEntry(
            child_id=child_id,
            date=datetime.now(timezone.utc).date().isoformat(),
            subject=subject,
            duration_minutes=duration_minutes,
            struggle_level=struggle_level,
            completed=completed,
            help_needed=help_needed,
        )
        data = self._load_data()
        data["homework_entries"].append(entry.model_dump(mode="json"))
        self._save_data(data)
        return entry

    def get_homework_trends(
        self, child_id: str | None = None, days: int = 14
    ) -> dict:
        """Analyze homework patterns over a time window.

        Args:
            child_id: Filter to a specific child, or None for all.
            days: Number of days to look back.

        Returns:
            Dict with analytics: subjects_by_struggle, completion_rate,
            average_duration, entries.
        """
        data = self._load_data()
        entries = [HomeworkEntry.model_validate(e) for e in data["homework_entries"]]

        if child_id is not None:
            entries = [e for e in entries if e.child_id == child_id]

        cutoff = (
            datetime.now(timezone.utc).date() - timedelta(days=days)
        ).isoformat()
        entries = [e for e in entries if e.date >= cutoff]

        # Subjects by average struggle level
        subjects: dict[str, list[int]] = {}
        for e in entries:
            subjects.setdefault(e.subject, []).append(e.struggle_level)
        subjects_by_struggle = {
            subj: round(sum(levels) / len(levels), 2)
            for subj, levels in subjects.items()
        }

        # Completion rate
        total = len(entries)
        completed = sum(1 for e in entries if e.completed)
        completion_rate = round(completed / total, 2) if total > 0 else 0.0

        # Average duration
        avg_duration = (
            round(sum(e.duration_minutes for e in entries) / total, 1)
            if total > 0
            else 0.0
        )

        return {
            "entries": [e.model_dump(mode="json") for e in entries],
            "subjects_by_struggle": subjects_by_struggle,
            "completion_rate": completion_rate,
            "average_duration": avg_duration,
        }

    # ── Learning Goals ───────────────────────────────────────────────

    def set_learning_goal(
        self,
        child_id: str,
        goal: str,
        category: str = "",
        milestones: list[str] | None = None,
        target_date: str | None = None,
    ) -> LearningGoal:
        """Create a new learning goal for a child.

        Args:
            child_id: The child this goal is for.
            goal: Description of the goal.
            category: Category (reading, math, writing, etc.).
            milestones: Ordered list of milestone descriptions.
            target_date: ISO date target for completion.

        Returns:
            The created LearningGoal.
        """
        lg = LearningGoal(
            child_id=child_id,
            goal=goal,
            category=category,
            milestones=milestones or [],
            target_date=target_date,
        )
        data = self._load_data()
        data["learning_goals"].append(lg.model_dump(mode="json"))
        self._save_data(data)
        return lg

    def update_learning_goal(self, goal_id: str, **kwargs: object) -> LearningGoal:
        """Update fields on an existing learning goal.

        Args:
            goal_id: The goal's unique identifier.
            **kwargs: Field names and new values to apply.

        Returns:
            The updated LearningGoal.

        Raises:
            KeyError: If the goal is not found.
        """
        data = self._load_data()
        for i, goal_data in enumerate(data["learning_goals"]):
            if goal_data["id"] == goal_id:
                goal_data.update(kwargs)
                updated = LearningGoal.model_validate(goal_data)
                data["learning_goals"][i] = updated.model_dump(mode="json")
                self._save_data(data)
                return updated
        raise KeyError(f"Learning goal '{goal_id}' not found.")

    def get_learning_goals(
        self, child_id: str | None = None, status: str | None = None
    ) -> list[LearningGoal]:
        """List learning goals, optionally filtered.

        Args:
            child_id: Filter to a specific child, or None for all.
            status: Filter by status (active, completed, paused, abandoned).

        Returns:
            List of matching LearningGoal objects.
        """
        data = self._load_data()
        goals = [LearningGoal.model_validate(g) for g in data["learning_goals"]]
        if child_id is not None:
            goals = [g for g in goals if g.child_id == child_id]
        if status is not None:
            goals = [g for g in goals if g.status == status]
        return goals
