"""Health service — medications, appointments, and growth tracking."""

from datetime import datetime, timedelta, timezone

from parenting.models.health import (
    Appointment,
    GrowthRecord,
    Medication,
    MedicationLog,
)
from parenting.storage.store import Store

HEALTH_DOMAIN = "health"

_EMPTY_DATA: dict = {
    "medications": [],
    "medication_logs": [],
    "appointments": [],
    "growth_records": [],
}


class HealthService:
    """Business logic for managing health-related data.

    Takes a Store backend and operates on the 'health' domain.
    """

    def __init__(self, store: Store) -> None:
        self._store = store

    def _load_data(self) -> dict:
        """Load health data, returning empty structure if none exists."""
        if not self._store.exists(HEALTH_DOMAIN):
            return {k: list(v) for k, v in _EMPTY_DATA.items()}
        data = self._store.load(HEALTH_DOMAIN)
        if not data:
            return {k: list(v) for k, v in _EMPTY_DATA.items()}
        return data

    def _save_data(self, data: dict) -> None:
        """Save health data to the store."""
        self._store.save(HEALTH_DOMAIN, data)

    # ── Medications ──────────────────────────────────────────────────

    def get_medications(
        self, child_id: str | None = None, active_only: bool = True
    ) -> list[Medication]:
        """List medications, optionally filtered by child and active status.

        Args:
            child_id: Filter to a specific child, or None for all.
            active_only: If True, only return active medications.

        Returns:
            List of matching Medication objects.
        """
        data = self._load_data()
        meds = [Medication.model_validate(m) for m in data["medications"]]
        if child_id is not None:
            meds = [m for m in meds if m.child_id == child_id]
        if active_only:
            meds = [m for m in meds if m.active]
        return meds

    def add_medication(
        self,
        child_id: str,
        name: str,
        dosage: str = "",
        frequency: str = "daily",
        time_of_day: list[str] | None = None,
    ) -> Medication:
        """Add a new medication for a child.

        Args:
            child_id: The child this medication is for.
            name: Medication name.
            dosage: Dosage amount and unit.
            frequency: How often (daily, twice_daily, as_needed).
            time_of_day: When to take (morning, evening, etc.).

        Returns:
            The created Medication.
        """
        med = Medication(
            child_id=child_id,
            name=name,
            dosage=dosage,
            frequency=frequency,
            time_of_day=time_of_day or [],
        )
        data = self._load_data()
        data["medications"].append(med.model_dump(mode="json"))
        self._save_data(data)
        return med

    def log_medication(
        self,
        medication_id: str,
        child_id: str,
        skipped: bool = False,
        skip_reason: str = "",
        notes: str = "",
    ) -> MedicationLog:
        """Log a medication administration or skip event.

        Args:
            medication_id: The medication being logged.
            child_id: The child who received (or skipped) the medication.
            skipped: Whether the dose was skipped.
            skip_reason: Reason for skipping.
            notes: Additional notes.

        Returns:
            The created MedicationLog entry.
        """
        log = MedicationLog(
            medication_id=medication_id,
            child_id=child_id,
            administered_at=datetime.now(timezone.utc).isoformat(),
            skipped=skipped,
            skip_reason=skip_reason,
            notes=notes,
        )
        data = self._load_data()
        data["medication_logs"].append(log.model_dump(mode="json"))
        self._save_data(data)
        return log

    def get_medication_history(
        self, child_id: str | None = None, days: int = 30
    ) -> list[MedicationLog]:
        """Get medication log entries within a time window.

        Args:
            child_id: Filter to a specific child, or None for all.
            days: Number of days to look back.

        Returns:
            List of MedicationLog entries within the window.
        """
        data = self._load_data()
        logs = [MedicationLog.model_validate(l) for l in data["medication_logs"]]
        if child_id is not None:
            logs = [l for l in logs if l.child_id == child_id]

        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        logs = [l for l in logs if l.administered_at >= cutoff]
        return logs

    # ── Appointments ─────────────────────────────────────────────────

    def get_appointments(
        self, child_id: str | None = None, upcoming_only: bool = True
    ) -> list[Appointment]:
        """List appointments, optionally filtered.

        Args:
            child_id: Filter to a specific child, or None for all.
            upcoming_only: If True, only return future uncompleted appointments.

        Returns:
            List of matching Appointment objects.
        """
        data = self._load_data()
        appts = [Appointment.model_validate(a) for a in data["appointments"]]
        if child_id is not None:
            appts = [a for a in appts if a.child_id == child_id]
        if upcoming_only:
            now = datetime.now(timezone.utc).isoformat()
            appts = [a for a in appts if a.date_time >= now and not a.completed]
        return appts

    def add_appointment(
        self,
        provider: str,
        date_time: str,
        child_id: str | None = None,
        type: str = "pediatrician",
        location: str = "",
    ) -> Appointment:
        """Add a new appointment.

        Args:
            provider: Provider name.
            date_time: ISO datetime of the appointment.
            child_id: The child, or None for family-wide.
            type: Appointment type.
            location: Where the appointment is.

        Returns:
            The created Appointment.
        """
        appt = Appointment(
            child_id=child_id,
            provider=provider,
            type=type,
            date_time=date_time,
            location=location,
        )
        data = self._load_data()
        data["appointments"].append(appt.model_dump(mode="json"))
        self._save_data(data)
        return appt

    def update_appointment(self, appointment_id: str, **kwargs: object) -> Appointment:
        """Update fields on an existing appointment.

        Args:
            appointment_id: The appointment's unique identifier.
            **kwargs: Field names and new values to apply.

        Returns:
            The updated Appointment.

        Raises:
            KeyError: If the appointment is not found.
        """
        data = self._load_data()
        for i, appt_data in enumerate(data["appointments"]):
            if appt_data["id"] == appointment_id:
                appt_data.update(kwargs)
                updated = Appointment.model_validate(appt_data)
                data["appointments"][i] = updated.model_dump(mode="json")
                self._save_data(data)
                return updated
        raise KeyError(f"Appointment '{appointment_id}' not found.")

    # ── Growth ───────────────────────────────────────────────────────

    def log_growth(
        self,
        child_id: str,
        height_inches: float | None = None,
        weight_pounds: float | None = None,
        notes: str = "",
    ) -> GrowthRecord:
        """Log a growth measurement for a child.

        Args:
            child_id: The child being measured.
            height_inches: Height in inches.
            weight_pounds: Weight in pounds.
            notes: Additional notes.

        Returns:
            The created GrowthRecord.
        """
        record = GrowthRecord(
            child_id=child_id,
            date=datetime.now(timezone.utc).date().isoformat(),
            height_inches=height_inches,
            weight_pounds=weight_pounds,
            notes=notes,
        )
        data = self._load_data()
        data["growth_records"].append(record.model_dump(mode="json"))
        self._save_data(data)
        return record

    def get_growth_history(self, child_id: str) -> list[GrowthRecord]:
        """Get all growth records for a child, ordered by date.

        Args:
            child_id: The child to look up.

        Returns:
            List of GrowthRecord entries sorted by date ascending.
        """
        data = self._load_data()
        records = [GrowthRecord.model_validate(r) for r in data["growth_records"]]
        records = [r for r in records if r.child_id == child_id]
        records.sort(key=lambda r: r.date)
        return records
