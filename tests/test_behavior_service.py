"""Tests for the BehaviorService."""

from datetime import datetime, timedelta, timezone

import pytest

from parenting.models.family import FamilyProfile
from parenting.services.behavior_service import BehaviorService
from parenting.services.family_service import FamilyService
from parenting.storage.json_store import JsonStore


@pytest.fixture
def behavior_service(tmp_store: JsonStore, sample_family: FamilyProfile) -> BehaviorService:
    """Provide a BehaviorService with the sample family already saved."""
    FamilyService(store=tmp_store).save_family(sample_family)
    return BehaviorService(store=tmp_store)


# ---------------------------------------------------------------------------
# Points — get
# ---------------------------------------------------------------------------


class TestGetPoints:
    def test_get_points_empty_returns_zero_for_all_children(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — no points entries exist

        # when
        result = behavior_service.get_points()

        # then
        assert result["points"]["max"] == 0
        assert result["points"]["emma"] == 0

    def test_get_points_for_specific_child(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        behavior_service.add_points("max", 2, "Good behavior", "behavior")

        # when
        result = behavior_service.get_points(child_id="max")

        # then
        assert result["points"]["max"] == 2
        assert "emma" not in result["points"]


# ---------------------------------------------------------------------------
# Points — add
# ---------------------------------------------------------------------------


class TestAddPoints:
    def test_add_points_creates_entry(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — max starts with 0 points

        # when
        entry = behavior_service.add_points("max", 2, "Helped with dishes", "chore")

        # then
        assert entry.child_id == "max"
        assert entry.delta == 2
        assert entry.reason == "Helped with dishes"
        assert entry.category == "chore"
        result = behavior_service.get_points(child_id="max")
        assert result["points"]["max"] == 2

    def test_add_points_wont_go_below_zero(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — max has 0 points

        # when / then
        with pytest.raises(ValueError, match="Insufficient points"):
            behavior_service.add_points("max", -1, "Deduction", "behavior")

    def test_add_points_validates_child_exists(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — no child "ghost"

        # when / then
        with pytest.raises(KeyError, match="not found"):
            behavior_service.add_points("ghost", 1, "Test", "general")

    def test_add_points_allows_deduction_within_balance(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        behavior_service.add_points("max", 5, "Earned", "behavior")

        # when
        entry = behavior_service.add_points("max", -3, "Spent", "spent")

        # then
        assert entry.delta == -3
        result = behavior_service.get_points(child_id="max")
        assert result["points"]["max"] == 2


# ---------------------------------------------------------------------------
# Points — reset
# ---------------------------------------------------------------------------


class TestResetPoints:
    def test_reset_points_resets_all_children(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — max has 5 points, emma has 0
        behavior_service.add_points("max", 5, "Earned", "behavior")

        # when
        result = behavior_service.reset_points()

        # then — both should now have points_per_day (default=3)
        assert result["reset"]["max"]["new_balance"] == 3
        assert result["reset"]["emma"]["new_balance"] == 3
        assert result["reset"]["max"]["previous_balance"] == 5
        assert result["reset"]["emma"]["previous_balance"] == 0

        # Verify via get_points
        points = behavior_service.get_points()
        assert points["points"]["max"] == 3
        assert points["points"]["emma"] == 3


# ---------------------------------------------------------------------------
# Points — configure
# ---------------------------------------------------------------------------


class TestConfigurePoints:
    def test_configure_points_updates_config(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — default config

        # when
        config = behavior_service.configure_points(points_per_day=5, rollover=True)

        # then
        assert config.points_per_day == 5
        assert config.rollover is True
        assert config.reset_schedule == "daily"  # unchanged

    def test_configure_points_persists(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        behavior_service.configure_points(reset_schedule="weekly")

        # when
        result = behavior_service.get_points()

        # then
        assert result["config"]["reset_schedule"] == "weekly"


# ---------------------------------------------------------------------------
# Rewards
# ---------------------------------------------------------------------------


class TestRewards:
    def test_get_rewards_empty(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — no rewards defined

        # when
        rewards = behavior_service.get_rewards()

        # then
        assert rewards == []

    def test_add_and_get_reward(
        self, behavior_service: BehaviorService
    ) -> None:
        # given / when
        reward = behavior_service.add_reward("Extra screen time", 5, "30 min extra")

        # then
        assert reward.name == "Extra screen time"
        assert reward.point_cost == 5
        assert reward.description == "30 min extra"
        rewards = behavior_service.get_rewards()
        assert len(rewards) == 1
        assert rewards[0].id == reward.id


# ---------------------------------------------------------------------------
# Spend points
# ---------------------------------------------------------------------------


class TestSpendPoints:
    def test_spend_points_deducts_correctly(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        behavior_service.add_points("max", 10, "Earned", "behavior")
        reward = behavior_service.add_reward("Movie night", 3)

        # when
        result = behavior_service.spend_points("max", reward.id)

        # then
        assert result["status"] == "ok"
        assert result["points_spent"] == 3
        assert result["remaining_balance"] == 7

    def test_spend_points_fails_insufficient(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — max has 0 points
        reward = behavior_service.add_reward("Expensive reward", 100)

        # when / then
        with pytest.raises(ValueError, match="Insufficient points"):
            behavior_service.spend_points("max", reward.id)

    def test_spend_points_fails_bad_reward(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        behavior_service.add_points("max", 10, "Earned", "behavior")

        # when / then
        with pytest.raises(KeyError, match="not found"):
            behavior_service.spend_points("max", "nonexistent")


# ---------------------------------------------------------------------------
# Chores
# ---------------------------------------------------------------------------


class TestChores:
    def test_add_chore(
        self, behavior_service: BehaviorService
    ) -> None:
        # given / when
        chore = behavior_service.add_chore(
            "Make bed", frequency="daily", assigned_to=["max"], point_value=1
        )

        # then
        assert chore.name == "Make bed"
        assert chore.frequency == "daily"
        assert chore.assigned_to == ["max"]
        assert chore.point_value == 1

    def test_log_chore_completion(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        chore = behavior_service.add_chore("Feed dog", point_value=2)

        # when
        completion = behavior_service.log_chore(chore.id, "max", "Fed on time")

        # then
        assert completion.chore_id == chore.id
        assert completion.child_id == "max"
        assert completion.notes == "Fed on time"

        # Points should have been auto-awarded
        points = behavior_service.get_points(child_id="max")
        assert points["points"]["max"] == 2

    def test_get_chores_shows_today_completion(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        chore = behavior_service.add_chore("Clean room")
        behavior_service.log_chore(chore.id, "max")

        # when
        result = behavior_service.get_chores()

        # then
        assert len(result["chores"]) == 1
        assert "max" in result["chores"][0]["completed_today_by"]

    def test_get_chores_filters_by_child(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        behavior_service.add_chore("Max only chore", assigned_to=["max"])
        behavior_service.add_chore("Everyone chore")

        # when
        result = behavior_service.get_chores(child_id="emma")

        # then — emma sees the "everyone" chore but not the "max only" chore
        chore_names = [c["name"] for c in result["chores"]]
        assert "Everyone chore" in chore_names
        assert "Max only chore" not in chore_names

    def test_log_chore_fails_for_nonexistent_chore(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — no chores defined

        # when / then
        with pytest.raises(KeyError, match="not found"):
            behavior_service.log_chore("nonexistent", "max")


# ---------------------------------------------------------------------------
# Consequences
# ---------------------------------------------------------------------------


class TestConsequences:
    def test_log_consequence(
        self, behavior_service: BehaviorService
    ) -> None:
        # given / when
        log = behavior_service.log_consequence(
            child_id="max",
            behavior="Hitting sibling",
            consequence="Time out and apology",
            consequence_type="logical",
            context="During playtime",
        )

        # then
        assert log.child_id == "max"
        assert log.behavior == "Hitting sibling"
        assert log.consequence == "Time out and apology"
        assert log.consequence_type == "logical"
        assert log.context == "During playtime"

    def test_log_consequence_fails_for_nonexistent_child(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — no child "ghost"

        # when / then
        with pytest.raises(KeyError, match="not found"):
            behavior_service.log_consequence(
                "ghost", "Bad behavior", "Consequence"
            )

    def test_get_consequence_history_filters_by_days(
        self, behavior_service: BehaviorService, tmp_store: JsonStore
    ) -> None:
        # given — one recent consequence and one old one
        behavior_service.log_consequence(
            "max", "Recent behavior", "Recent consequence"
        )

        # Manually insert an old entry
        data = tmp_store.load("behavior")
        old_entry = data["consequences"][-1].copy()
        old_entry["id"] = "old-entry"
        old_entry["behavior"] = "Old behavior"
        old_entry["timestamp"] = (
            datetime.now(timezone.utc) - timedelta(days=60)
        ).isoformat()
        data["consequences"].append(old_entry)
        tmp_store.save("behavior", data)

        # when — get last 30 days
        results = behavior_service.get_consequence_history(days=30)

        # then — only the recent one
        assert len(results) == 1
        assert results[0].behavior == "Recent behavior"

    def test_get_consequence_history_filters_by_child(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        behavior_service.log_consequence("max", "Max behavior", "Max consequence")
        behavior_service.log_consequence("emma", "Emma behavior", "Emma consequence")

        # when
        results = behavior_service.get_consequence_history(child_id="max")

        # then
        assert len(results) == 1
        assert results[0].child_id == "max"


# ---------------------------------------------------------------------------
# Trends
# ---------------------------------------------------------------------------


class TestBehaviorTrends:
    def test_behavior_trends_positive_negative_ratio(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — max earns 6 and spends 2
        behavior_service.add_points("max", 6, "Earned", "behavior")
        behavior_service.add_points("max", -2, "Spent", "spent")

        # when
        result = behavior_service.get_behavior_trends(child_id="max", days=7)

        # then
        trends = result["trends"]["max"]
        assert trends["total_earned"] == 6
        assert trends["total_spent"] == 2
        assert trends["positive_to_negative_ratio"] == 3.0  # 6/2

    def test_behavior_trends_no_negatives_ratio(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — max earns 5, spends nothing
        behavior_service.add_points("max", 5, "Earned", "behavior")

        # when
        result = behavior_service.get_behavior_trends(child_id="max", days=7)

        # then — ratio is just the earned amount (no denominator)
        trends = result["trends"]["max"]
        assert trends["positive_to_negative_ratio"] == 5.0

    def test_behavior_trends_chore_completion_rate(
        self, behavior_service: BehaviorService
    ) -> None:
        # given — one daily chore for everyone, max completes it once
        chore = behavior_service.add_chore("Daily chore", frequency="daily")
        behavior_service.log_chore(chore.id, "max")

        # when
        result = behavior_service.get_behavior_trends(child_id="max", days=7)

        # then — 1 completion out of 7 expected (1 chore * 7 days)
        trends = result["trends"]["max"]
        assert trends["chores_completed"] == 1
        assert trends["chores_expected"] == 7
        assert abs(trends["chore_completion_rate"] - 1 / 7) < 0.01

    def test_behavior_trends_all_children(
        self, behavior_service: BehaviorService
    ) -> None:
        # given
        behavior_service.add_points("max", 3, "Earned", "behavior")
        behavior_service.add_points("emma", 1, "Earned", "behavior")

        # when
        result = behavior_service.get_behavior_trends(days=7)

        # then
        assert "max" in result["trends"]
        assert "emma" in result["trends"]
        assert result["trends"]["max"]["total_earned"] == 3
        assert result["trends"]["emma"]["total_earned"] == 1
