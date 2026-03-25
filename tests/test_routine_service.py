"""Tests for the RoutineService."""

from datetime import date

import pytest

from parenting.models.routines import RoutineDefinition, RoutineExecution
from parenting.services.routine_service import RoutineService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def routine_service(tmp_store: JsonStore) -> RoutineService:
    """Provide a RoutineService backed by a temporary store."""
    return RoutineService(store=tmp_store)


SAMPLE_STEPS = [
    {"order": 1, "name": "Wake up", "duration_minutes": 2},
    {"order": 2, "name": "Brush teeth", "duration_minutes": 3},
    {"order": 3, "name": "Get dressed", "duration_minutes": 5},
]


class TestCreateRoutine:
    def test_create_routine(self, routine_service: RoutineService) -> None:
        # given
        name = "Morning Routine"
        steps = SAMPLE_STEPS

        # when
        routine = routine_service.create_routine(
            name=name,
            steps=steps,
            child_id="max",
            target_start_time="07:00",
            target_duration_minutes=15,
        )

        # then
        assert routine.name == name
        assert routine.child_id == "max"
        assert len(routine.steps) == 3
        assert routine.steps[0].name == "Wake up"
        assert routine.steps[1].duration_minutes == 3
        assert routine.target_start_time == "07:00"
        assert routine.target_duration_minutes == 15
        assert routine.id  # non-empty


class TestGetRoutines:
    def test_get_routines_empty(self, routine_service: RoutineService) -> None:
        # given — empty store

        # when
        routines = routine_service.get_routines()

        # then
        assert routines == []

    def test_get_routines_returns_created(
        self, routine_service: RoutineService
    ) -> None:
        # given
        routine_service.create_routine(name="Morning", steps=SAMPLE_STEPS)
        routine_service.create_routine(name="Bedtime", steps=SAMPLE_STEPS)

        # when
        routines = routine_service.get_routines()

        # then
        assert len(routines) == 2
        names = {r.name for r in routines}
        assert names == {"Morning", "Bedtime"}


class TestUpdateRoutine:
    def test_update_routine(self, routine_service: RoutineService) -> None:
        # given
        routine = routine_service.create_routine(
            name="Morning", steps=SAMPLE_STEPS, target_start_time="07:00"
        )

        # when
        updated = routine_service.update_routine(
            routine.id, name="Morning v2", target_start_time="06:30"
        )

        # then
        assert updated.name == "Morning v2"
        assert updated.target_start_time == "06:30"
        assert len(updated.steps) == 3  # steps unchanged

    def test_update_nonexistent_raises(
        self, routine_service: RoutineService
    ) -> None:
        # given — no routines

        # when / then
        with pytest.raises(KeyError, match="not found"):
            routine_service.update_routine("nonexistent", name="Nope")


class TestDeleteRoutine:
    def test_delete_routine(self, routine_service: RoutineService) -> None:
        # given
        routine = routine_service.create_routine(
            name="Temporary", steps=SAMPLE_STEPS
        )

        # when
        routine_service.delete_routine(routine.id)

        # then
        assert routine_service.get_routines() == []

    def test_delete_nonexistent_raises(
        self, routine_service: RoutineService
    ) -> None:
        # given — no routines

        # when / then
        with pytest.raises(KeyError, match="not found"):
            routine_service.delete_routine("ghost")


class TestLogRoutine:
    def test_log_routine_execution(
        self, routine_service: RoutineService
    ) -> None:
        # given
        routine = routine_service.create_routine(
            name="Morning", steps=SAMPLE_STEPS
        )

        # when
        execution = routine_service.log_routine(
            routine_id=routine.id,
            child_id="max",
            steps_completed=[1, 2, 3],
            resistance_level=1,
            notes="Went well overall",
        )

        # then
        assert execution.routine_id == routine.id
        assert execution.child_id == "max"
        assert execution.steps_completed == [1, 2, 3]
        assert execution.resistance_level == 1
        assert execution.notes == "Went well overall"
        assert execution.date == date.today().isoformat()

    def test_log_nonexistent_routine_raises(
        self, routine_service: RoutineService
    ) -> None:
        # given — no routines

        # when / then
        with pytest.raises(KeyError, match="not found"):
            routine_service.log_routine(
                routine_id="ghost",
                child_id="max",
                steps_completed=[1],
            )


class TestGetRoutineTrends:
    def _create_and_log(
        self,
        svc: RoutineService,
        steps_completed: list[int],
        steps_skipped: list[int] | None = None,
        resistance_level: int = 0,
        exec_date: str | None = None,
    ) -> tuple[RoutineDefinition, RoutineExecution]:
        """Helper to create a routine and log an execution."""
        routines = svc.get_routines()
        if routines:
            routine = routines[0]
        else:
            routine = svc.create_routine(name="Morning", steps=SAMPLE_STEPS)

        execution = svc.log_routine(
            routine_id=routine.id,
            child_id="max",
            steps_completed=steps_completed,
            steps_skipped=steps_skipped,
            resistance_level=resistance_level,
        )

        # Override date if specified (direct store manipulation for testing)
        if exec_date is not None:
            data = svc._load_data()
            for ex in data["executions"]:
                if ex["id"] == execution.id:
                    ex["date"] = exec_date
            svc._save_data(data)

        return routine, execution

    def test_get_routine_trends_completion_rate(
        self, routine_service: RoutineService
    ) -> None:
        # given — 2 executions: 1 fully completed, 1 partial
        self._create_and_log(routine_service, steps_completed=[1, 2, 3])
        self._create_and_log(routine_service, steps_completed=[1, 2])

        # when
        trends = routine_service.get_routine_trends(days=14)

        # then
        assert trends["total_executions"] == 2
        assert trends["completion_rate"] == 0.5  # 1 of 2 fully complete

    def test_get_routine_trends_streak(
        self, routine_service: RoutineService
    ) -> None:
        # given — full completions on today and yesterday
        today = date.today()
        yesterday = date.fromordinal(today.toordinal() - 1)

        self._create_and_log(
            routine_service,
            steps_completed=[1, 2, 3],
            exec_date=yesterday.isoformat(),
        )
        self._create_and_log(
            routine_service,
            steps_completed=[1, 2, 3],
            exec_date=today.isoformat(),
        )

        # when
        trends = routine_service.get_routine_trends(days=14)

        # then
        assert trends["current_streak"] == 2

    def test_get_routine_trends_regression_detection(
        self, routine_service: RoutineService
    ) -> None:
        # given — first half all complete, second half all incomplete
        today = date.today()

        # First half (days 10-14 ago): all complete
        for offset in range(10, 14):
            d = date.fromordinal(today.toordinal() - offset)
            self._create_and_log(
                routine_service,
                steps_completed=[1, 2, 3],
                exec_date=d.isoformat(),
            )

        # Second half (days 0-3 ago): all incomplete
        for offset in range(0, 4):
            d = date.fromordinal(today.toordinal() - offset)
            self._create_and_log(
                routine_service,
                steps_completed=[1],
                exec_date=d.isoformat(),
            )

        # when
        trends = routine_service.get_routine_trends(days=14)

        # then
        assert trends["regression_flag"] is True

    def test_get_routine_trends_skipped_steps(
        self, routine_service: RoutineService
    ) -> None:
        # given — step 3 skipped often, step 2 skipped once
        self._create_and_log(
            routine_service,
            steps_completed=[1, 2],
            steps_skipped=[3],
        )
        self._create_and_log(
            routine_service,
            steps_completed=[1],
            steps_skipped=[2, 3],
        )

        # when
        trends = routine_service.get_routine_trends(days=14)

        # then
        assert trends["skipped_steps"][3] == 2
        assert trends["skipped_steps"][2] == 1

    def test_get_routine_trends_empty(
        self, routine_service: RoutineService
    ) -> None:
        # given — no executions

        # when
        trends = routine_service.get_routine_trends(days=14)

        # then
        assert trends["completion_rate"] == 0.0
        assert trends["current_streak"] == 0
        assert trends["total_executions"] == 0


class TestGetScheduleToday:
    def test_get_schedule_today(self, routine_service: RoutineService) -> None:
        # given — a routine scheduled for every day
        routine = routine_service.create_routine(
            name="Morning",
            steps=SAMPLE_STEPS,
            target_start_time="07:00",
        )

        # when
        schedule = routine_service.get_schedule_today()

        # then
        assert schedule["date"] == date.today().isoformat()
        assert schedule["scheduled_count"] == 1
        assert schedule["routines"][0]["routine_id"] == routine.id
        assert schedule["routines"][0]["completed"] is False

    def test_get_schedule_today_shows_completed(
        self, routine_service: RoutineService
    ) -> None:
        # given — a routine that has been logged today
        routine = routine_service.create_routine(
            name="Morning", steps=SAMPLE_STEPS
        )
        routine_service.log_routine(
            routine_id=routine.id,
            child_id="max",
            steps_completed=[1, 2, 3],
        )

        # when
        schedule = routine_service.get_schedule_today()

        # then
        assert schedule["routines"][0]["completed"] is True
        assert schedule["routines"][0]["executions_today"] == 1

    def test_get_schedule_today_excludes_other_days(
        self, routine_service: RoutineService
    ) -> None:
        # given — a routine only on Monday (0)
        today_dow = date.today().weekday()
        # Use a day that is NOT today
        other_day = (today_dow + 1) % 7
        routine_service.create_routine(
            name="Monday Only",
            steps=SAMPLE_STEPS,
            days_of_week=[other_day],
        )

        # when
        schedule = routine_service.get_schedule_today()

        # then
        assert schedule["scheduled_count"] == 0
