"""Routine service — CRUD and analytics for daily routines."""

from collections import Counter
from datetime import date, datetime, timezone

from parenting.models.routines import RoutineDefinition, RoutineExecution, RoutineStep
from parenting.services.family_service import FamilyService
from parenting.storage.store import Store

ROUTINES_DOMAIN = "routines"


class RoutineService:
    """Business logic for managing routines and tracking their execution.

    Operates on the 'routines' domain with structure:
    {"routines": [...], "executions": [...]}
    """

    def __init__(self, store: Store) -> None:
        self._store = store
        self.family_service = FamilyService(store)

    def _load_data(self) -> dict:
        """Load the routines domain data, initializing if empty."""
        if not self._store.exists(ROUTINES_DOMAIN):
            return {"routines": [], "executions": []}
        data = self._store.load(ROUTINES_DOMAIN)
        if not data:
            return {"routines": [], "executions": []}
        return data

    def _save_data(self, data: dict) -> None:
        """Save the routines domain data."""
        self._store.save(ROUTINES_DOMAIN, data)

    def get_routines(self) -> list[RoutineDefinition]:
        """Load all routine definitions.

        Returns:
            List of all RoutineDefinition objects.
        """
        data = self._load_data()
        return [
            RoutineDefinition.model_validate(r) for r in data.get("routines", [])
        ]

    def create_routine(
        self,
        name: str,
        steps: list[dict],
        child_id: str | None = None,
        target_start_time: str | None = None,
        target_duration_minutes: int = 30,
        days_of_week: list[int] | None = None,
    ) -> RoutineDefinition:
        """Create a new routine definition.

        Args:
            name: Routine name (e.g. "Morning", "Bedtime").
            steps: List of step dicts with 'order', 'name', and optionally
                   'duration_minutes' and 'description'.
            child_id: Child this routine is for, or None for family-wide.
            target_start_time: Target start time in "HH:MM" format.
            target_duration_minutes: Target total duration in minutes.
            days_of_week: Days of week (0=Monday). Defaults to every day.

        Returns:
            The created RoutineDefinition.
        """
        parsed_steps = [RoutineStep.model_validate(s) for s in steps]

        routine = RoutineDefinition(
            name=name,
            child_id=child_id,
            steps=parsed_steps,
            target_start_time=target_start_time,
            target_duration_minutes=target_duration_minutes,
            days_of_week=days_of_week if days_of_week is not None else [0, 1, 2, 3, 4, 5, 6],
        )

        data = self._load_data()
        data["routines"].append(routine.model_dump(mode="json"))
        self._save_data(data)
        return routine

    def update_routine(self, routine_id: str, **kwargs: object) -> RoutineDefinition:
        """Update fields on an existing routine.

        Args:
            routine_id: The routine's unique identifier.
            **kwargs: Field names and new values to apply. If 'steps' is
                      provided as a list of dicts, they will be validated
                      as RoutineStep objects.

        Returns:
            The updated RoutineDefinition.

        Raises:
            KeyError: If the routine is not found.
        """
        data = self._load_data()
        routines = data.get("routines", [])

        for i, raw in enumerate(routines):
            routine = RoutineDefinition.model_validate(raw)
            if routine.id == routine_id:
                updated_data = routine.model_dump()
                # If steps are provided as dicts, validate them
                if "steps" in kwargs and isinstance(kwargs["steps"], list):
                    kwargs["steps"] = [
                        RoutineStep.model_validate(s).model_dump()
                        for s in kwargs["steps"]  # type: ignore[union-attr]
                    ]
                updated_data.update(kwargs)
                updated = RoutineDefinition.model_validate(updated_data)
                routines[i] = updated.model_dump(mode="json")
                data["routines"] = routines
                self._save_data(data)
                return updated

        raise KeyError(f"Routine '{routine_id}' not found.")

    def delete_routine(self, routine_id: str) -> None:
        """Delete a routine definition.

        Args:
            routine_id: The routine's unique identifier.

        Raises:
            KeyError: If the routine is not found.
        """
        data = self._load_data()
        routines = data.get("routines", [])
        original_count = len(routines)

        data["routines"] = [
            r for r in routines
            if RoutineDefinition.model_validate(r).id != routine_id
        ]

        if len(data["routines"]) == original_count:
            raise KeyError(f"Routine '{routine_id}' not found.")

        self._save_data(data)

    def log_routine(
        self,
        routine_id: str,
        child_id: str,
        steps_completed: list[int],
        steps_skipped: list[int] | None = None,
        resistance_level: int = 0,
        notes: str = "",
    ) -> RoutineExecution:
        """Log a routine execution for a child.

        Args:
            routine_id: The routine that was executed.
            child_id: The child who performed the routine.
            steps_completed: Step order numbers that were completed.
            steps_skipped: Step order numbers that were skipped.
            resistance_level: 0=none, 1=mild, 2=moderate, 3=high.
            notes: Free-text notes about the execution.

        Returns:
            The created RoutineExecution.

        Raises:
            KeyError: If the routine is not found.
        """
        # Verify routine exists
        data = self._load_data()
        routines = data.get("routines", [])
        found = any(
            RoutineDefinition.model_validate(r).id == routine_id
            for r in routines
        )
        if not found:
            raise KeyError(f"Routine '{routine_id}' not found.")

        now = datetime.now(timezone.utc)
        execution = RoutineExecution(
            routine_id=routine_id,
            child_id=child_id,
            date=date.today().isoformat(),
            started_at=now.isoformat(),
            completed_at=now.isoformat(),
            steps_completed=steps_completed,
            steps_skipped=steps_skipped or [],
            resistance_level=resistance_level,
            notes=notes,
        )

        data["executions"].append(execution.model_dump(mode="json"))
        self._save_data(data)
        return execution

    def get_routine_trends(
        self,
        routine_id: str | None = None,
        child_id: str | None = None,
        days: int = 14,
    ) -> dict:
        """Compute analytics for routine executions.

        Args:
            routine_id: Filter to a specific routine (optional).
            child_id: Filter to a specific child (optional).
            days: Number of days to look back (default 14).

        Returns:
            Dict with completion_rate, current_streak, skipped_steps,
            resistance_trend, and regression_flag.
        """
        data = self._load_data()
        executions_raw = data.get("executions", [])
        routines_raw = data.get("routines", [])

        # Parse all executions
        executions = [RoutineExecution.model_validate(e) for e in executions_raw]
        routines = [RoutineDefinition.model_validate(r) for r in routines_raw]

        # Build a map of routine_id -> step count
        routine_step_counts: dict[str, int] = {
            r.id: len(r.steps) for r in routines
        }

        # Filter executions by date range
        today = date.today()
        cutoff = today.toordinal() - days
        filtered: list[RoutineExecution] = []
        for ex in executions:
            try:
                ex_date = date.fromisoformat(ex.date)
            except ValueError:
                continue
            if ex_date.toordinal() < cutoff:
                continue
            if routine_id is not None and ex.routine_id != routine_id:
                continue
            if child_id is not None and ex.child_id != child_id:
                continue
            filtered.append(ex)

        if not filtered:
            return {
                "completion_rate": 0.0,
                "current_streak": 0,
                "skipped_steps": {},
                "resistance_trend": 0.0,
                "regression_flag": False,
                "total_executions": 0,
            }

        # Completion rate: % of executions where all steps were completed
        fully_completed = 0
        for ex in filtered:
            step_count = routine_step_counts.get(ex.routine_id, 0)
            if step_count > 0 and len(ex.steps_completed) >= step_count:
                fully_completed += 1
            elif step_count == 0 and len(ex.steps_completed) > 0:
                # Routine has no defined steps but some were logged — count as complete
                fully_completed += 1
        completion_rate = fully_completed / len(filtered) if filtered else 0.0

        # Current streak: consecutive days (working backwards from today)
        # where at least one execution was fully completed
        execution_dates: set[str] = set()
        for ex in filtered:
            step_count = routine_step_counts.get(ex.routine_id, 0)
            if step_count > 0 and len(ex.steps_completed) >= step_count:
                execution_dates.add(ex.date)
            elif step_count == 0 and len(ex.steps_completed) > 0:
                execution_dates.add(ex.date)

        current_streak = 0
        check_date = today
        while check_date.isoformat() in execution_dates:
            current_streak += 1
            check_date = date.fromordinal(check_date.toordinal() - 1)

        # Skipped steps: count which step numbers are most commonly skipped
        skip_counter: Counter[int] = Counter()
        for ex in filtered:
            for step_num in ex.steps_skipped:
                skip_counter[step_num] += 1
        skipped_steps = dict(skip_counter.most_common())

        # Resistance trend: average resistance level
        total_resistance = sum(ex.resistance_level for ex in filtered)
        resistance_trend = total_resistance / len(filtered)

        # Regression detection: compare first half vs second half completion
        midpoint = days // 2
        mid_cutoff = today.toordinal() - midpoint
        first_half = [
            ex for ex in filtered
            if date.fromisoformat(ex.date).toordinal() < mid_cutoff
        ]
        second_half = [
            ex for ex in filtered
            if date.fromisoformat(ex.date).toordinal() >= mid_cutoff
        ]

        def _half_completion_rate(execs: list[RoutineExecution]) -> float:
            if not execs:
                return 0.0
            completed = 0
            for ex in execs:
                step_count = routine_step_counts.get(ex.routine_id, 0)
                if step_count > 0 and len(ex.steps_completed) >= step_count:
                    completed += 1
                elif step_count == 0 and len(ex.steps_completed) > 0:
                    completed += 1
            return completed / len(execs)

        first_rate = _half_completion_rate(first_half)
        second_rate = _half_completion_rate(second_half)
        regression_flag = (
            first_rate > 0 and (first_rate - second_rate) > 0.20
        )

        return {
            "completion_rate": round(completion_rate, 2),
            "current_streak": current_streak,
            "skipped_steps": skipped_steps,
            "resistance_trend": round(resistance_trend, 2),
            "regression_flag": regression_flag,
            "total_executions": len(filtered),
        }

    def get_schedule_today(self) -> dict:
        """Get today's scheduled routines and their completion status.

        Returns:
            Dict with today's date, day_of_week, and a list of scheduled
            routines with their completion status.
        """
        today = date.today()
        # Python weekday: Monday=0, Sunday=6 (matches our convention)
        day_of_week = today.weekday()

        data = self._load_data()
        routines = [
            RoutineDefinition.model_validate(r) for r in data.get("routines", [])
        ]
        executions = [
            RoutineExecution.model_validate(e) for e in data.get("executions", [])
        ]

        # Find today's executions
        today_str = today.isoformat()
        today_executions = [e for e in executions if e.date == today_str]

        # Build schedule
        scheduled: list[dict] = []
        for routine in routines:
            if day_of_week not in routine.days_of_week:
                continue

            # Check if this routine has been executed today
            routine_execs = [
                e for e in today_executions if e.routine_id == routine.id
            ]
            completed = len(routine_execs) > 0

            scheduled.append({
                "routine_id": routine.id,
                "routine_name": routine.name,
                "child_id": routine.child_id,
                "target_start_time": routine.target_start_time,
                "steps_count": len(routine.steps),
                "completed": completed,
                "executions_today": len(routine_execs),
            })

        return {
            "date": today_str,
            "day_of_week": day_of_week,
            "scheduled_count": len(scheduled),
            "routines": scheduled,
        }
