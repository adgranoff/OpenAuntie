"""Emotional service — mood tracking, conflict resolution, and developmental milestones."""

from collections import Counter
from datetime import datetime, timedelta, timezone

from parenting.models.emotional import ConflictRecord, DevelopmentalMilestone, MoodEntry
from parenting.storage.store import Store

EMOTIONAL_DOMAIN = "emotional"

_EMPTY_DATA: dict = {
    "mood_entries": [],
    "conflicts": [],
    "milestones": [],
}


class EmotionalService:
    """Business logic for managing emotional well-being data.

    Takes a Store backend and operates on the 'emotional' domain.
    """

    def __init__(self, store: Store) -> None:
        self._store = store

    def _load_data(self) -> dict:
        """Load emotional data, returning empty structure if none exists."""
        if not self._store.exists(EMOTIONAL_DOMAIN):
            return {k: list(v) for k, v in _EMPTY_DATA.items()}
        data = self._store.load(EMOTIONAL_DOMAIN)
        if not data:
            return {k: list(v) for k, v in _EMPTY_DATA.items()}
        return data

    def _save_data(self, data: dict) -> None:
        """Save emotional data to the store."""
        self._store.save(EMOTIONAL_DOMAIN, data)

    # ── Mood ─────────────────────────────────────────────────────────

    def log_mood(
        self,
        child_id: str,
        zone: str | None = None,
        intensity: int | None = None,
        emotions: list[str] | None = None,
        context: str = "",
        coping_used: list[str] | None = None,
    ) -> MoodEntry:
        """Log a mood check-in for a child.

        Args:
            child_id: The child being observed.
            zone: Zones of Regulation color (blue, green, yellow, red).
            intensity: Intensity level 1-5.
            emotions: Specific emotion words.
            context: What was happening.
            coping_used: Coping strategies used.

        Returns:
            The created MoodEntry.
        """
        entry = MoodEntry(
            child_id=child_id,
            zone=zone,
            intensity=intensity,
            emotions=emotions or [],
            context=context,
            coping_used=coping_used or [],
        )
        data = self._load_data()
        data["mood_entries"].append(entry.model_dump(mode="json"))
        self._save_data(data)
        return entry

    def get_mood_trends(
        self, child_id: str | None = None, days: int = 14
    ) -> dict:
        """Analyze mood patterns over a time window.

        Args:
            child_id: Filter to a specific child, or None for all.
            days: Number of days to look back.

        Returns:
            Dict with analytics: zone_distribution, average_intensity,
            common_emotions, entries.
        """
        data = self._load_data()
        entries = [MoodEntry.model_validate(e) for e in data["mood_entries"]]

        if child_id is not None:
            entries = [e for e in entries if e.child_id == child_id]

        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        entries = [e for e in entries if e.timestamp >= cutoff]

        # Zone distribution
        zones = [e.zone for e in entries if e.zone is not None]
        zone_counts = Counter(zones)
        total_zones = len(zones)
        zone_distribution = {
            z: round(count / total_zones, 2)
            for z, count in zone_counts.items()
        } if total_zones > 0 else {}

        # Average intensity
        intensities = [e.intensity for e in entries if e.intensity is not None]
        average_intensity = (
            round(sum(intensities) / len(intensities), 1)
            if intensities
            else None
        )

        # Common emotions
        all_emotions: list[str] = []
        for e in entries:
            all_emotions.extend(e.emotions)
        common_emotions = [
            emotion for emotion, _ in Counter(all_emotions).most_common(5)
        ]

        return {
            "entries": [e.model_dump(mode="json") for e in entries],
            "zone_distribution": zone_distribution,
            "average_intensity": average_intensity,
            "common_emotions": common_emotions,
        }

    # ── Conflicts ────────────────────────────────────────────────────

    def log_conflict(
        self,
        children_involved: list[str],
        trigger: str,
        description: str = "",
        resolution: str = "",
        resolution_type: str = "mediated",
        what_worked: str = "",
        what_didnt_work: str = "",
    ) -> ConflictRecord:
        """Log a conflict between children.

        Args:
            children_involved: IDs of children involved.
            trigger: What triggered the conflict.
            description: What happened.
            resolution: How it was resolved.
            resolution_type: Type (mediated, self_resolved, unresolved, escalated).
            what_worked: What worked in resolution.
            what_didnt_work: What did not work.

        Returns:
            The created ConflictRecord.
        """
        record = ConflictRecord(
            children_involved=children_involved,
            trigger=trigger,
            description=description,
            resolution=resolution,
            resolution_type=resolution_type,
            what_worked=what_worked,
            what_didnt_work=what_didnt_work,
        )
        data = self._load_data()
        data["conflicts"].append(record.model_dump(mode="json"))
        self._save_data(data)
        return record

    def get_conflict_patterns(self, days: int = 30) -> dict:
        """Analyze conflict patterns over a time window.

        Args:
            days: Number of days to look back.

        Returns:
            Dict with analytics: total_conflicts, common_triggers,
            resolution_types, children_frequency, entries.
        """
        data = self._load_data()
        records = [ConflictRecord.model_validate(c) for c in data["conflicts"]]

        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        records = [r for r in records if r.timestamp >= cutoff]

        # Common triggers
        triggers = [r.trigger for r in records]
        common_triggers = [t for t, _ in Counter(triggers).most_common(5)]

        # Resolution type distribution
        res_types = Counter(r.resolution_type for r in records)

        # Children frequency
        child_ids: list[str] = []
        for r in records:
            child_ids.extend(r.children_involved)
        children_frequency = dict(Counter(child_ids).most_common())

        return {
            "entries": [r.model_dump(mode="json") for r in records],
            "total_conflicts": len(records),
            "common_triggers": common_triggers,
            "resolution_types": dict(res_types),
            "children_frequency": children_frequency,
        }

    # ── Milestones ───────────────────────────────────────────────────

    def log_milestone(
        self,
        child_id: str,
        description: str,
        category: str = "general",
    ) -> DevelopmentalMilestone:
        """Log a developmental milestone for a child.

        Args:
            child_id: The child who achieved the milestone.
            description: What the milestone is.
            category: Category (cognitive, emotional, social, physical, language).

        Returns:
            The created DevelopmentalMilestone.
        """
        milestone = DevelopmentalMilestone(
            child_id=child_id,
            date=datetime.now(timezone.utc).date().isoformat(),
            category=category,
            description=description,
        )
        data = self._load_data()
        data["milestones"].append(milestone.model_dump(mode="json"))
        self._save_data(data)
        return milestone

    def get_milestones(
        self, child_id: str | None = None
    ) -> list[DevelopmentalMilestone]:
        """List developmental milestones, optionally filtered by child.

        Args:
            child_id: Filter to a specific child, or None for all.

        Returns:
            List of DevelopmentalMilestone objects sorted by date ascending.
        """
        data = self._load_data()
        milestones = [
            DevelopmentalMilestone.model_validate(m) for m in data["milestones"]
        ]
        if child_id is not None:
            milestones = [m for m in milestones if m.child_id == child_id]
        milestones.sort(key=lambda m: m.date)
        return milestones
