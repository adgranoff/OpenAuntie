"""Research service — manages the research watchlist and editorial queue."""

from datetime import datetime, timezone

from parenting.models.research import ResearchUpdate
from parenting.storage.store import Store

RESEARCH_DOMAIN = "research_updates"


class ResearchService:
    """Business logic for managing research update proposals.

    Operates on the 'research_updates' domain with structure:
    {"proposals": [...]}
    """

    def __init__(self, store: Store) -> None:
        self._store = store

    def _load_data(self) -> dict:
        """Load the research domain data, initializing if empty."""
        if not self._store.exists(RESEARCH_DOMAIN):
            return {"proposals": []}
        data = self._store.load(RESEARCH_DOMAIN)
        if not data:
            return {"proposals": []}
        return data

    def _save_data(self, data: dict) -> None:
        """Save the research domain data."""
        self._store.save(RESEARCH_DOMAIN, data)

    def add_update_proposal(
        self,
        source: str,
        title: str,
        summary: str,
        relevant_knowledge_file: str,
        proposed_change: str,
        evidence_grade: str = "EMERGING",
        citation: str = "",
        source_url: str = "",
    ) -> ResearchUpdate:
        """Add a research update proposal to the queue.

        Args:
            source: Research source (e.g. PubMed, AAP, CDC).
            title: Title of the research finding.
            summary: Brief summary of the finding.
            relevant_knowledge_file: Which knowledge/ file this relates to.
            proposed_change: What should change in the knowledge base.
            evidence_grade: Evidence strength (STRONG, MODERATE, EMERGING, CONSENSUS).
            citation: Formal citation for the research.
            source_url: URL to the source material.

        Returns:
            The created ResearchUpdate proposal.
        """
        update = ResearchUpdate(
            source=source,
            title=title,
            summary=summary,
            relevant_knowledge_file=relevant_knowledge_file,
            proposed_change=proposed_change,
            evidence_grade=evidence_grade,
            citation=citation,
            source_url=source_url,
        )

        data = self._load_data()
        data["proposals"].append(update.model_dump(mode="json"))
        self._save_data(data)
        return update

    def get_update_proposals(
        self, status: str | None = None
    ) -> list[ResearchUpdate]:
        """Get proposals, optionally filtered by status.

        Args:
            status: Filter by status (pending, approved, dismissed), or None for all.

        Returns:
            List of matching ResearchUpdate proposals.
        """
        data = self._load_data()
        proposals = [
            ResearchUpdate.model_validate(p)
            for p in data.get("proposals", [])
        ]

        if status is not None:
            proposals = [p for p in proposals if p.status == status]

        return proposals

    def _find_and_update(self, update_id: str, data: dict) -> int:
        """Find the index of a proposal by ID.

        Args:
            update_id: The proposal ID to find.
            data: The loaded domain data.

        Returns:
            The index of the proposal.

        Raises:
            KeyError: If the proposal is not found.
        """
        for i, p in enumerate(data.get("proposals", [])):
            if p.get("id") == update_id:
                return i
        raise KeyError(f"Research update '{update_id}' not found.")

    def approve_update(
        self, update_id: str, reviewer_notes: str = ""
    ) -> ResearchUpdate:
        """Approve a proposal (admin action).

        Args:
            update_id: The proposal ID to approve.
            reviewer_notes: Optional notes from the reviewer.

        Returns:
            The updated ResearchUpdate with status 'approved'.

        Raises:
            KeyError: If the proposal is not found.
        """
        data = self._load_data()
        idx = self._find_and_update(update_id, data)

        data["proposals"][idx]["status"] = "approved"
        data["proposals"][idx]["reviewer_notes"] = reviewer_notes
        data["proposals"][idx]["reviewed_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        self._save_data(data)
        return ResearchUpdate.model_validate(data["proposals"][idx])

    def dismiss_update(
        self, update_id: str, reviewer_notes: str = ""
    ) -> ResearchUpdate:
        """Dismiss a proposal with reason (admin action).

        Args:
            update_id: The proposal ID to dismiss.
            reviewer_notes: Reason for dismissal.

        Returns:
            The updated ResearchUpdate with status 'dismissed'.

        Raises:
            KeyError: If the proposal is not found.
        """
        data = self._load_data()
        idx = self._find_and_update(update_id, data)

        data["proposals"][idx]["status"] = "dismissed"
        data["proposals"][idx]["reviewer_notes"] = reviewer_notes
        data["proposals"][idx]["reviewed_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        self._save_data(data)
        return ResearchUpdate.model_validate(data["proposals"][idx])

    def get_watchlist_sources(self) -> list[str]:
        """Return the list of trusted sources being watched.

        Returns:
            A list of source names that the research watchlist monitors.
        """
        return [
            "PubMed",
            "AAP/HealthyChildren",
            "CDC",
            "WHO",
            "NICE",
            "Frontiers in Psychology",
            "Developmental Psychology",
            "Journal of Family Psychology",
            "Pediatrics",
        ]
