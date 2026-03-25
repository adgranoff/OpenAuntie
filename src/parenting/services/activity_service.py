"""Activity service — family events, trip planning, meeting agenda generation."""

from datetime import datetime, timezone

from parenting.models.activities import ActivitySuggestion, FamilyEvent, TripPlan
from parenting.storage.store import Store


class ActivityService:
    """Manages family activities, trips, and event history."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def _load(self) -> dict:
        data = self.store.load("activities")
        if not data:
            return {"events": [], "trips": [], "suggestions": []}
        return data

    def _save(self, data: dict) -> None:
        self.store.save("activities", data)

    # --- Events ---

    def log_activity(
        self,
        name: str,
        date: str,
        time: str | None = None,
        location: str = "",
        children_involved: list[str] | None = None,
        category: str = "",
        rating: int | None = None,
        would_repeat: bool | None = None,
        notes: str = "",
    ) -> FamilyEvent:
        """Record a family activity."""
        event = FamilyEvent(
            name=name,
            date=date,
            time=time,
            location=location,
            children_involved=children_involved or [],
            category=category,
            rating=rating,
            would_repeat=would_repeat,
            notes=notes,
        )
        data = self._load()
        data["events"].append(event.model_dump())
        self._save(data)
        return event

    def get_activity_history(
        self,
        days: int | None = None,
        category: str | None = None,
    ) -> list[FamilyEvent]:
        """Get past activities, optionally filtered."""
        data = self._load()
        events = [FamilyEvent.model_validate(e) for e in data.get("events", [])]

        if category:
            events = [e for e in events if e.category == category]

        if days is not None:
            cutoff = datetime.now(timezone.utc).isoformat()[:10]
            # Simple date filtering - events within last N days
            from datetime import timedelta

            cutoff_date = (
                datetime.now(timezone.utc) - timedelta(days=days)
            ).strftime("%Y-%m-%d")
            events = [e for e in events if e.date >= cutoff_date]

        return events

    # --- Trips ---

    def plan_trip(
        self,
        name: str,
        start_date: str,
        end_date: str,
        destination: str = "",
        activities: list[str] | None = None,
        behavior_plan: str = "",
        notes: str = "",
    ) -> TripPlan:
        """Create a trip plan."""
        trip = TripPlan(
            name=name,
            start_date=start_date,
            end_date=end_date,
            destination=destination,
            activities=activities or [],
            behavior_plan=behavior_plan,
            notes=notes,
        )
        data = self._load()
        data["trips"].append(trip.model_dump())
        self._save(data)
        return trip

    def get_trip(self, trip_id: str | None = None) -> TripPlan | list[TripPlan]:
        """Get a specific trip or all active trips."""
        data = self._load()
        trips = [TripPlan.model_validate(t) for t in data.get("trips", [])]

        if trip_id:
            for trip in trips:
                if trip.id == trip_id:
                    return trip
            raise KeyError(f"Trip not found: {trip_id}")

        return [t for t in trips if t.active]

    # --- Suggestions ---

    def suggest_activity(
        self,
        ages: list[int] | None = None,
        category: str | None = None,
        energy_level: str | None = None,
        indoor_outdoor: str | None = None,
    ) -> list[dict]:
        """Suggest activities based on criteria. Returns context for LLM to generate suggestions."""
        data = self._load()
        past_events = [FamilyEvent.model_validate(e) for e in data.get("events", [])]

        # Build context for the consultant LLM
        past_categories = {}
        highly_rated = []
        for event in past_events:
            cat = event.category or "uncategorized"
            past_categories[cat] = past_categories.get(cat, 0) + 1
            if event.rating and event.rating >= 4:
                highly_rated.append(event.name)

        return {
            "request": {
                "ages": ages,
                "preferred_category": category,
                "energy_level": energy_level,
                "indoor_outdoor": indoor_outdoor,
            },
            "family_history": {
                "total_activities_logged": len(past_events),
                "category_counts": past_categories,
                "highly_rated_activities": highly_rated[-10:],
            },
        }

    def create_family_meeting_agenda(self, store: Store) -> dict:
        """Generate a family meeting agenda pulling from all domains.

        Returns structured data the consultant LLM uses to present the agenda.
        """
        from parenting.services.family_service import FamilyService

        family_service = FamilyService(store)
        family = family_service.get_family()

        agenda = {
            "appreciations": [],
            "calendar": [],
            "old_business": [],
            "new_business": [],
            "chore_review": [],
            "fun_planning": [],
        }

        if not family:
            return agenda

        # Pull recent milestones for appreciations
        emotional_data = store.load("emotional")
        if emotional_data:
            milestones = emotional_data.get("milestones", [])
            recent = milestones[-5:] if milestones else []
            agenda["appreciations"] = [
                {"child_id": m.get("child_id"), "description": m.get("description")}
                for m in recent
            ]

        # Pull recent conflicts for new business
        if emotional_data:
            conflicts = emotional_data.get("conflicts", [])
            unresolved = [
                c for c in conflicts if c.get("resolution_type") == "unresolved"
            ]
            agenda["new_business"] = [
                {"trigger": c.get("trigger"), "children": c.get("children_involved")}
                for c in unresolved[-3:]
            ]

        # Pull behavior trends for chore review
        behavior_data = store.load("behavior")
        if behavior_data:
            completions = behavior_data.get("chore_completions", [])
            agenda["chore_review"] = {
                "total_completions_this_week": len(completions[-7:]),
            }

        # Pull activity suggestions for fun planning
        agenda["fun_planning"] = self.suggest_activity()

        return agenda
