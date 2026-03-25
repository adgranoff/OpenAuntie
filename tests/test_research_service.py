"""Tests for the ResearchService."""

import pytest

from parenting.models.research import ResearchUpdate
from parenting.services.research_service import ResearchService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def research_service(tmp_store: JsonStore) -> ResearchService:
    """Provide a ResearchService backed by a temporary store."""
    return ResearchService(store=tmp_store)


def _add_sample_proposal(svc: ResearchService) -> ResearchUpdate:
    """Helper to add a standard sample proposal."""
    return svc.add_update_proposal(
        source="PubMed",
        title="New screen time guidance for toddlers",
        summary="Updated AAP recommendations reduce screen time for ages 2-5",
        relevant_knowledge_file="screen-time.md",
        proposed_change="Lower recommended daily limit from 2h to 1h for ages 2-5",
        evidence_grade="STRONG",
        citation="Smith et al. (2026). Pediatrics, 158(3), e2026012345.",
        source_url="https://pubmed.example.com/12345",
    )


class TestAddProposal:
    def test_add_proposal(self, research_service: ResearchService) -> None:
        # given — empty research store

        # when
        proposal = _add_sample_proposal(research_service)

        # then
        assert proposal.id is not None
        assert len(proposal.id) == 8
        assert proposal.source == "PubMed"
        assert proposal.title == "New screen time guidance for toddlers"
        assert proposal.status == "pending"
        assert proposal.evidence_grade == "STRONG"
        assert proposal.reviewed_at is None


class TestGetProposalsAll:
    def test_get_proposals_all(self, research_service: ResearchService) -> None:
        # given
        _add_sample_proposal(research_service)
        research_service.add_update_proposal(
            source="CDC",
            title="Updated vaccination schedule",
            summary="Minor changes to flu vaccine timing",
            relevant_knowledge_file="health.md",
            proposed_change="Update vaccination timing table",
        )

        # when
        proposals = research_service.get_update_proposals()

        # then
        assert len(proposals) == 2
        assert proposals[0].source == "PubMed"
        assert proposals[1].source == "CDC"


class TestGetProposalsByStatus:
    def test_get_proposals_by_status(
        self, research_service: ResearchService
    ) -> None:
        # given
        p1 = _add_sample_proposal(research_service)
        research_service.add_update_proposal(
            source="WHO",
            title="Breastfeeding duration update",
            summary="Extended recommendation to 2 years",
            relevant_knowledge_file="nutrition.md",
            proposed_change="Update breastfeeding duration guidance",
        )
        research_service.approve_update(p1.id)

        # when
        pending = research_service.get_update_proposals(status="pending")
        approved = research_service.get_update_proposals(status="approved")

        # then
        assert len(pending) == 1
        assert pending[0].source == "WHO"
        assert len(approved) == 1
        assert approved[0].source == "PubMed"


class TestApproveUpdate:
    def test_approve_update(self, research_service: ResearchService) -> None:
        # given
        proposal = _add_sample_proposal(research_service)

        # when
        approved = research_service.approve_update(
            proposal.id, reviewer_notes="Strong evidence, apply immediately"
        )

        # then
        assert approved.status == "approved"
        assert approved.reviewer_notes == "Strong evidence, apply immediately"
        assert approved.reviewed_at is not None

    def test_approve_nonexistent_raises(
        self, research_service: ResearchService
    ) -> None:
        # given — empty store

        # when / then
        with pytest.raises(KeyError, match="not found"):
            research_service.approve_update("nonexistent")


class TestDismissUpdate:
    def test_dismiss_update(self, research_service: ResearchService) -> None:
        # given
        proposal = _add_sample_proposal(research_service)

        # when
        dismissed = research_service.dismiss_update(
            proposal.id, reviewer_notes="Superseded by newer study"
        )

        # then
        assert dismissed.status == "dismissed"
        assert dismissed.reviewer_notes == "Superseded by newer study"
        assert dismissed.reviewed_at is not None

    def test_dismiss_nonexistent_raises(
        self, research_service: ResearchService
    ) -> None:
        # given — empty store

        # when / then
        with pytest.raises(KeyError, match="not found"):
            research_service.dismiss_update("ghost")


class TestGetWatchlistSources:
    def test_get_watchlist_sources(
        self, research_service: ResearchService
    ) -> None:
        # given — no setup needed

        # when
        sources = research_service.get_watchlist_sources()

        # then
        assert isinstance(sources, list)
        assert len(sources) >= 5
        assert "PubMed" in sources
        assert "AAP/HealthyChildren" in sources
        assert "CDC" in sources
        assert "WHO" in sources
        assert "Pediatrics" in sources
