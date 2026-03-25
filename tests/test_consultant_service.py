"""Tests for the ConsultantService."""

from pathlib import Path

import pytest

from parenting.models.family import FamilyProfile
from parenting.services.consultant_service import ConsultantService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def knowledge_dir(tmp_path: Path) -> Path:
    """Provide a temp directory with small test knowledge files."""
    kdir = tmp_path / "knowledge"
    kdir.mkdir()

    (kdir / "developmental_stages.md").write_text(
        """\
# Developmental Stages: Age-by-Age Expectations
Last reviewed: 2026-03

---

## Ages 0-2 (Infant / Toddler)

### Executive Function
- Executive function is essentially absent.

### Emotional Regulation
- Infants depend on co-regulation from caregivers.

### Common Parental Over-Expectations
- Expecting toddlers to share.

---

## Ages 3-5 (Preschool)

### Executive Function
- Inhibitory control begins to emerge.

### Emotional Regulation
- Shift from co-regulation to partial self-regulation begins.

### Common Parental Over-Expectations
- Expecting perfect behavior at age 3.

---

## Ages 5-7 (Early Elementary)

### Executive Function
- Working memory and inhibitory control improve significantly.

### Emotional Regulation
- Children can use simple coping strategies independently.

---

## Ages 8-10 (Middle Elementary)

### Executive Function
- Planning and organization emerge as meaningful skills.

---

## Ages 10-12 (Upper Elementary / Pre-Adolescence)

### Executive Function
- Abstract thinking begins to develop.

---

## Ages 13-15 (Early Adolescence)

### Executive Function
- Risk assessment improves but is still unreliable.

---

## Ages 16-18 (Late Adolescence)

### Executive Function
- Approaching adult-level executive function.
""",
        encoding="utf-8",
    )

    (kdir / "homework_and_learning.md").write_text(
        """\
# Homework and Learning
Last reviewed: 2026-03

## Homework Effectiveness
The 10-minute rule: 10 minutes per grade level per night.

## Study Strategies
Active recall and spaced repetition are most effective.
""",
        encoding="utf-8",
    )

    (kdir / "routines_research.md").write_text(
        """\
# Routines Research
Last reviewed: 2026-03

## Bedtime Routines
Consistent bedtime routines improve sleep quality.

## Morning Routines
Visual checklists help children complete morning tasks.
""",
        encoding="utf-8",
    )

    (kdir / "sibling_dynamics.md").write_text(
        """\
# Sibling Dynamics
Last reviewed: 2026-03

## Sibling Conflict
Fighting between siblings is developmentally normal.

## Jealousy
New baby jealousy is universal and temporary.
""",
        encoding="utf-8",
    )

    (kdir / "emotion_coaching.md").write_text(
        """\
# Emotion Coaching
Last reviewed: 2026-03

## Core Steps
1. Notice the emotion
2. See it as a teaching opportunity
3. Listen with empathy
4. Help label the emotion
5. Set limits while problem-solving
""",
        encoding="utf-8",
    )

    return kdir


@pytest.fixture
def consultant_service(
    tmp_store: JsonStore, knowledge_dir: Path
) -> ConsultantService:
    """Provide a ConsultantService with temp store and knowledge dir."""
    return ConsultantService(store=tmp_store, knowledge_dir=knowledge_dir)


@pytest.fixture
def seeded_consultant(
    consultant_service: ConsultantService, sample_family: FamilyProfile
) -> ConsultantService:
    """Provide a ConsultantService with the sample family already saved."""
    consultant_service.family_service.save_family(sample_family)
    return consultant_service


class TestConsult:
    def test_consult_returns_family_context(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given — family profile is saved

        # when
        result = seeded_consultant.consult("How do I handle bedtime?")

        # then
        assert "family_context" in result
        assert result["family_context"] is not None
        assert result["family_context"]["family_name"] == "TestFamily"
        assert len(result["family_context"]["children"]) == 2

    def test_consult_loads_relevant_knowledge_for_homework_question(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given — knowledge dir contains homework_and_learning.md

        # when
        result = seeded_consultant.consult(
            "My kid won't do his homework. Help!"
        )

        # then
        assert "relevant_research" in result
        assert "homework_and_learning.md" in result["relevant_research"]
        research = result["relevant_research"]["homework_and_learning.md"]
        assert "10-minute rule" in research

    def test_consult_loads_relevant_knowledge_for_bedtime_question(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given — knowledge dir contains routines_research.md

        # when
        result = seeded_consultant.consult(
            "Bedtime battles every night. What do I do?"
        )

        # then
        assert "relevant_research" in result
        assert "routines_research.md" in result["relevant_research"]
        research = result["relevant_research"]["routines_research.md"]
        assert "Bedtime" in research

    def test_consult_returns_developmental_context(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given — family has children with DOBs

        # when
        result = seeded_consultant.consult("General parenting question")

        # then
        assert "developmental_context" in result
        dev_ctx = result["developmental_context"]
        assert len(dev_ctx) == 2
        # Max (born 2020) should have an age band
        max_ctx = next(c for c in dev_ctx if c["child_id"] == "max")
        assert "age_band" in max_ctx
        assert "expectations" in max_ctx

    def test_consult_includes_question(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given
        question = "How do I handle tantrums?"

        # when
        result = seeded_consultant.consult(question)

        # then
        assert result["question"] == question

    def test_consult_with_no_family_returns_null_context(
        self, consultant_service: ConsultantService
    ) -> None:
        # given — no family saved

        # when
        result = consultant_service.consult("Any question")

        # then
        assert result["family_context"] is None
        assert result["developmental_context"] == []


class TestSafetyCheck:
    def test_safety_check_detects_regression(
        self, consultant_service: ConsultantService
    ) -> None:
        # given
        text = "My child has been regressing lately"

        # when
        result = consultant_service.check_safety(text)

        # then
        assert result["needs_referral"] is True
        assert result["referral_type"] == "soft"
        assert "professional" in result["referral_message"].lower()

    def test_safety_check_detects_self_harm(
        self, consultant_service: ConsultantService
    ) -> None:
        # given
        text = "I'm worried my teenager is thinking about self-harm"

        # when
        result = consultant_service.check_safety(text)

        # then
        assert result["needs_referral"] is True
        assert result["referral_type"] == "hard"
        assert "988" in result["referral_message"]

    def test_safety_check_returns_clean_for_normal_question(
        self, consultant_service: ConsultantService
    ) -> None:
        # given
        text = "How do I get my kid to eat vegetables?"

        # when
        result = consultant_service.check_safety(text)

        # then
        assert result["needs_referral"] is False
        assert result["referral_type"] is None
        assert result["referral_reason"] is None

    def test_safety_check_detects_abuse(
        self, consultant_service: ConsultantService
    ) -> None:
        # given
        text = "I'm concerned about possible abuse at daycare"

        # when
        result = consultant_service.check_safety(text)

        # then
        assert result["needs_referral"] is True
        assert result["referral_type"] == "hard"


class TestGetAgeExpectations:
    def test_get_age_expectations_returns_correct_band(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given — Max was born 2020-06-15, so around 5-6 years old
        # Should fall into "Ages 5-7 (Early Elementary)"

        # when
        result = seeded_consultant.get_age_expectations("max")

        # then
        assert result["child_id"] == "max"
        assert result["child_name"] == "Max"
        assert "age_band" in result
        assert "Early Elementary" in result["age_band"]
        assert "expectations" in result
        assert "Working memory" in result["expectations"]

    def test_get_age_expectations_for_young_child(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given — Emma was born 2023-01-10, so around 3 years old
        # Should fall into "Ages 3-5 (Preschool)"

        # when
        result = seeded_consultant.get_age_expectations("emma")

        # then
        assert "Preschool" in result["age_band"]

    def test_get_age_expectations_raises_for_unknown_child(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given — no child "ghost"

        # when / then
        with pytest.raises(KeyError, match="not found"):
            seeded_consultant.get_age_expectations("ghost")


class TestWeeklySummary:
    def test_weekly_summary_structure(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given — family with 2 children

        # when
        result = seeded_consultant.weekly_summary(period_days=7)

        # then
        assert result["period_days"] == 7
        assert result["family_name"] == "TestFamily"
        assert "children" in result
        assert "max" in result["children"]
        assert "emma" in result["children"]

        # Check per-child structure
        max_summary = result["children"]["max"]
        assert max_summary["name"] == "Max"
        assert "behavior" in max_summary
        assert "routines" in max_summary
        assert "emotional" in max_summary
        assert "highlights" in max_summary
        assert "concerns" in max_summary

    def test_weekly_summary_with_no_family(
        self, consultant_service: ConsultantService
    ) -> None:
        # given — no family profile

        # when
        result = consultant_service.weekly_summary()

        # then
        assert "error" in result

    def test_weekly_summary_custom_period(
        self, seeded_consultant: ConsultantService
    ) -> None:
        # given — family exists

        # when
        result = seeded_consultant.weekly_summary(period_days=14)

        # then
        assert result["period_days"] == 14
