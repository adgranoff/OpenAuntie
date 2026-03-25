"""Tests for the HealthService."""

from datetime import datetime, timedelta, timezone

import pytest

from parenting.models.health import Appointment, GrowthRecord, Medication, MedicationLog
from parenting.services.health_service import HealthService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def health_service(tmp_store: JsonStore) -> HealthService:
    """Provide a HealthService backed by a temporary store."""
    return HealthService(store=tmp_store)


class TestAddMedication:
    def test_add_medication(self, health_service: HealthService) -> None:
        # given
        child_id = "max"

        # when
        med = health_service.add_medication(
            child_id=child_id,
            name="Amoxicillin",
            dosage="250mg",
            frequency="twice_daily",
            time_of_day=["morning", "evening"],
        )

        # then
        assert isinstance(med, Medication)
        assert med.child_id == "max"
        assert med.name == "Amoxicillin"
        assert med.dosage == "250mg"
        assert med.frequency == "twice_daily"
        assert med.time_of_day == ["morning", "evening"]
        assert med.active is True

    def test_add_medication_minimal(self, health_service: HealthService) -> None:
        # given / when
        med = health_service.add_medication(child_id="emma", name="Tylenol")

        # then
        assert med.name == "Tylenol"
        assert med.dosage == ""
        assert med.frequency == "daily"


class TestGetMedications:
    def test_get_medications_active_only(
        self, health_service: HealthService
    ) -> None:
        # given
        health_service.add_medication(child_id="max", name="Med A")
        med_b = health_service.add_medication(child_id="max", name="Med B")
        # Deactivate Med B by rewriting the data
        data = health_service._load_data()
        for m in data["medications"]:
            if m["id"] == med_b.id:
                m["active"] = False
        health_service._save_data(data)

        # when
        active = health_service.get_medications(child_id="max", active_only=True)

        # then
        assert len(active) == 1
        assert active[0].name == "Med A"

    def test_get_medications_all(self, health_service: HealthService) -> None:
        # given
        health_service.add_medication(child_id="max", name="Med A")
        health_service.add_medication(child_id="emma", name="Med B")

        # when
        all_meds = health_service.get_medications(active_only=False)

        # then
        assert len(all_meds) == 2

    def test_get_medications_by_child(
        self, health_service: HealthService
    ) -> None:
        # given
        health_service.add_medication(child_id="max", name="Med A")
        health_service.add_medication(child_id="emma", name="Med B")

        # when
        emma_meds = health_service.get_medications(child_id="emma")

        # then
        assert len(emma_meds) == 1
        assert emma_meds[0].child_id == "emma"


class TestLogMedication:
    def test_log_medication(self, health_service: HealthService) -> None:
        # given
        med = health_service.add_medication(child_id="max", name="Amoxicillin")

        # when
        log = health_service.log_medication(
            medication_id=med.id, child_id="max", notes="Taken with food"
        )

        # then
        assert isinstance(log, MedicationLog)
        assert log.medication_id == med.id
        assert log.child_id == "max"
        assert log.skipped is False
        assert log.notes == "Taken with food"

    def test_log_medication_skipped(self, health_service: HealthService) -> None:
        # given
        med = health_service.add_medication(child_id="max", name="Amoxicillin")

        # when
        log = health_service.log_medication(
            medication_id=med.id,
            child_id="max",
            skipped=True,
            skip_reason="Vomiting",
        )

        # then
        assert log.skipped is True
        assert log.skip_reason == "Vomiting"


class TestGetMedicationHistory:
    def test_get_medication_history(self, health_service: HealthService) -> None:
        # given
        med = health_service.add_medication(child_id="max", name="Amoxicillin")
        health_service.log_medication(medication_id=med.id, child_id="max")
        health_service.log_medication(medication_id=med.id, child_id="max")

        # when
        history = health_service.get_medication_history(child_id="max", days=7)

        # then
        assert len(history) == 2

    def test_get_medication_history_empty(
        self, health_service: HealthService
    ) -> None:
        # given — no logs

        # when
        history = health_service.get_medication_history(child_id="max")

        # then
        assert history == []


class TestAddAppointment:
    def test_add_appointment(self, health_service: HealthService) -> None:
        # given
        future = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

        # when
        appt = health_service.add_appointment(
            provider="Dr. Smith",
            date_time=future,
            child_id="max",
            type="pediatrician",
            location="123 Main St",
        )

        # then
        assert isinstance(appt, Appointment)
        assert appt.provider == "Dr. Smith"
        assert appt.child_id == "max"
        assert appt.type == "pediatrician"
        assert appt.completed is False


class TestGetAppointmentsUpcoming:
    def test_get_appointments_upcoming(
        self, health_service: HealthService
    ) -> None:
        # given
        future = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        past = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        health_service.add_appointment(provider="Dr. Future", date_time=future)
        health_service.add_appointment(provider="Dr. Past", date_time=past)

        # when
        upcoming = health_service.get_appointments(upcoming_only=True)

        # then
        assert len(upcoming) == 1
        assert upcoming[0].provider == "Dr. Future"

    def test_get_appointments_all(self, health_service: HealthService) -> None:
        # given
        future = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        past = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        health_service.add_appointment(provider="Dr. Future", date_time=future)
        health_service.add_appointment(provider="Dr. Past", date_time=past)

        # when
        all_appts = health_service.get_appointments(upcoming_only=False)

        # then
        assert len(all_appts) == 2


class TestUpdateAppointment:
    def test_update_appointment(self, health_service: HealthService) -> None:
        # given
        future = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        appt = health_service.add_appointment(
            provider="Dr. Smith", date_time=future
        )

        # when
        updated = health_service.update_appointment(
            appt.id, completed=True, follow_up_needed=True,
            follow_up_notes="Recheck in 2 weeks"
        )

        # then
        assert updated.completed is True
        assert updated.follow_up_needed is True
        assert updated.follow_up_notes == "Recheck in 2 weeks"

    def test_update_appointment_not_found(
        self, health_service: HealthService
    ) -> None:
        # given — no appointments

        # when / then
        with pytest.raises(KeyError, match="not found"):
            health_service.update_appointment("nonexistent", completed=True)


class TestLogGrowth:
    def test_log_growth(self, health_service: HealthService) -> None:
        # given / when
        record = health_service.log_growth(
            child_id="max",
            height_inches=42.5,
            weight_pounds=38.0,
            notes="Annual checkup",
        )

        # then
        assert isinstance(record, GrowthRecord)
        assert record.child_id == "max"
        assert record.height_inches == 42.5
        assert record.weight_pounds == 38.0

    def test_log_growth_partial(self, health_service: HealthService) -> None:
        # given / when — only weight
        record = health_service.log_growth(child_id="emma", weight_pounds=25.0)

        # then
        assert record.height_inches is None
        assert record.weight_pounds == 25.0


class TestGetGrowthHistory:
    def test_get_growth_history(self, health_service: HealthService) -> None:
        # given
        health_service.log_growth(child_id="max", height_inches=40.0)
        health_service.log_growth(child_id="max", height_inches=42.0)
        health_service.log_growth(child_id="emma", height_inches=30.0)

        # when
        history = health_service.get_growth_history("max")

        # then
        assert len(history) == 2
        assert all(r.child_id == "max" for r in history)

    def test_get_growth_history_empty(
        self, health_service: HealthService
    ) -> None:
        # given — no records

        # when
        history = health_service.get_growth_history("max")

        # then
        assert history == []
