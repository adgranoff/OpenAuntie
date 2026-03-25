"""Feedback service — manages parent feedback on technique effectiveness."""

from datetime import datetime, timezone

from parenting.models.feedback import AdviceFeedback
from parenting.storage.store import Store

FEEDBACK_DOMAIN = "feedback"


class FeedbackService:
    """Business logic for managing parent feedback on parenting techniques.

    Operates on the 'feedback' domain with structure:
    {"entries": [...]}
    """

    def __init__(self, store: Store) -> None:
        self._store = store

    def _load_data(self) -> dict:
        """Load the feedback domain data, initializing if empty."""
        if not self._store.exists(FEEDBACK_DOMAIN):
            return {"entries": []}
        data = self._store.load(FEEDBACK_DOMAIN)
        if not data:
            return {"entries": []}
        return data

    def _save_data(self, data: dict) -> None:
        """Save the feedback domain data."""
        self._store.save(FEEDBACK_DOMAIN, data)

    def rate_advice(
        self,
        child_id: str,
        technique: str,
        outcome: int,
        context: str = "",
        setting: str = "",
        confidence: int = 3,
        used_as_intended: bool = True,
        duration_tried: str = "",
        notes: str = "",
        knowledge_source: str = "",
    ) -> AdviceFeedback:
        """Rate how well a technique worked.

        Args:
            child_id: Which child the technique was used with.
            technique: The technique name.
            outcome: Rating 1-5 (1=made worse, 3=no change, 5=worked great).
            context: Situation context.
            setting: Environmental setting.
            confidence: Confidence in the rating (1-5).
            used_as_intended: Whether the technique was used as described.
            duration_tried: How long the technique was tried.
            notes: Additional notes.
            knowledge_source: Which knowledge file suggested this.

        Returns:
            The created AdviceFeedback entry.
        """
        feedback = AdviceFeedback(
            child_id=child_id,
            technique=technique,
            outcome=outcome,
            context=context,
            setting=setting,
            confidence=confidence,
            used_as_intended=used_as_intended,
            duration_tried=duration_tried,
            notes=notes,
            knowledge_source=knowledge_source,
        )

        data = self._load_data()
        data["entries"].append(feedback.model_dump(mode="json"))
        self._save_data(data)
        return feedback

    def get_feedback_history(
        self,
        child_id: str | None = None,
        technique: str | None = None,
        days: int | None = None,
    ) -> list[AdviceFeedback]:
        """Get feedback entries, optionally filtered.

        Args:
            child_id: Filter to feedback about this child (None returns all).
            technique: Filter to this technique name (None returns all).
            days: Only return entries from the last N days.

        Returns:
            List of matching AdviceFeedback entries, newest first.
        """
        data = self._load_data()
        entries = [
            AdviceFeedback.model_validate(e) for e in data.get("entries", [])
        ]

        if child_id is not None:
            entries = [e for e in entries if e.child_id == child_id]

        if technique is not None:
            entries = [e for e in entries if e.technique == technique]

        if days is not None:
            now = datetime.now(timezone.utc)
            cutoff = now.timestamp() - (days * 86400)
            cutoff_entries = []
            for e in entries:
                ts = datetime.fromisoformat(e.timestamp)
                if ts.timestamp() >= cutoff:
                    cutoff_entries.append(e)
            entries = cutoff_entries

        # Sort newest first
        entries.sort(
            key=lambda e: datetime.fromisoformat(e.timestamp), reverse=True
        )
        return entries

    def get_family_insights(self, child_id: str | None = None) -> dict:
        """Generate insights about what works for each child.

        Groups feedback by child, then by technique, computing statistics
        for each technique's effectiveness.

        Args:
            child_id: Filter to a specific child, or None for all children.

        Returns:
            Dict with per-child insights including technique stats,
            most/least effective techniques, and confidence labels.
        """
        entries = self.get_feedback_history(child_id=child_id)

        if not entries:
            return {
                "children": {},
                "total_feedback_entries": 0,
                "note": "No feedback data yet. Rate techniques to build family insights.",
            }

        # Group by child_id, then by technique
        by_child: dict[str, dict[str, list[AdviceFeedback]]] = {}
        for entry in entries:
            if entry.child_id not in by_child:
                by_child[entry.child_id] = {}
            if entry.technique not in by_child[entry.child_id]:
                by_child[entry.child_id][entry.technique] = []
            by_child[entry.child_id][entry.technique].append(entry)

        children_insights: dict[str, dict] = {}
        now = datetime.now(timezone.utc)

        for cid, techniques in by_child.items():
            technique_stats = []

            for tech_name, tech_entries in techniques.items():
                outcomes = [e.outcome for e in tech_entries]
                avg_outcome = sum(outcomes) / len(outcomes)
                count = len(outcomes)

                # Recency: days since most recent feedback
                most_recent_ts = max(
                    datetime.fromisoformat(e.timestamp) for e in tech_entries
                )
                days_since = (now - most_recent_ts).days

                # Confidence label based on sample size
                if count < 3:
                    confidence_label = "early family signal"
                elif count <= 7:
                    confidence_label = "developing pattern"
                else:
                    confidence_label = "established pattern"

                technique_stats.append({
                    "technique": tech_name,
                    "average_outcome": round(avg_outcome, 2),
                    "sample_size": count,
                    "days_since_last_feedback": days_since,
                    "confidence_level": confidence_label,
                })

            # Sort by average outcome, highest first
            technique_stats.sort(
                key=lambda t: t["average_outcome"], reverse=True
            )

            # Most/least effective
            most_effective = [
                t for t in technique_stats if t["average_outcome"] >= 4.0
            ]
            least_effective = [
                t for t in technique_stats if t["average_outcome"] <= 2.0
            ]

            children_insights[cid] = {
                "techniques": technique_stats,
                "most_effective": most_effective,
                "least_effective": least_effective,
            }

        total_entries = len(entries)
        return {
            "children": children_insights,
            "total_feedback_entries": total_entries,
            "note": f"Based on {total_entries} feedback entries. More data improves accuracy.",
        }

    def get_technique_summary(self, technique: str) -> dict:
        """Get summary for a specific technique across all children.

        Args:
            technique: The technique name to summarize.

        Returns:
            Dict with overall and per-child statistics for the technique.
        """
        entries = self.get_feedback_history(technique=technique)

        if not entries:
            return {
                "technique": technique,
                "total_ratings": 0,
                "note": f"No feedback recorded for '{technique}' yet.",
            }

        outcomes = [e.outcome for e in entries]
        avg_outcome = sum(outcomes) / len(outcomes)

        # Per-child breakdown
        by_child: dict[str, list[int]] = {}
        for e in entries:
            if e.child_id not in by_child:
                by_child[e.child_id] = []
            by_child[e.child_id].append(e.outcome)

        per_child = {
            cid: {
                "average_outcome": round(sum(outs) / len(outs), 2),
                "sample_size": len(outs),
            }
            for cid, outs in by_child.items()
        }

        # Contexts where this technique was used
        contexts = list({e.context for e in entries if e.context})

        return {
            "technique": technique,
            "total_ratings": len(entries),
            "average_outcome": round(avg_outcome, 2),
            "per_child": per_child,
            "contexts_used": contexts,
        }
