"""Tests for the financial service."""

import pytest

from parenting.services.financial_service import FinancialService


class TestConfigureAllowance:
    def test_configure_allowance(self, tmp_store):
        # given
        service = FinancialService(tmp_store)

        # when
        config = service.configure_allowance(
            child_id="max",
            weekly_amount=7.00,
            split_save_pct=40,
            split_spend_pct=50,
            split_give_pct=10,
        )

        # then
        assert config.child_id == "max"
        assert config.weekly_amount == 7.00
        assert config.model == "hybrid"

    def test_configure_allowance_splits_must_sum_100(self, tmp_store):
        # given
        service = FinancialService(tmp_store)

        # when / then
        with pytest.raises(ValueError, match="sum to 100"):
            service.configure_allowance(
                child_id="max",
                weekly_amount=7.00,
                split_save_pct=40,
                split_spend_pct=40,
                split_give_pct=10,
            )

    def test_update_existing_config(self, tmp_store):
        # given
        service = FinancialService(tmp_store)
        service.configure_allowance(child_id="max", weekly_amount=5.00)

        # when
        service.configure_allowance(child_id="max", weekly_amount=10.00)
        result = service.get_allowance("max")

        # then
        assert result["max"]["config"]["weekly_amount"] == 10.00


class TestPayAllowance:
    def test_pay_allowance_creates_jar_transactions(self, tmp_store):
        # given
        service = FinancialService(tmp_store)
        service.configure_allowance(
            child_id="emma",
            weekly_amount=10.00,
            split_save_pct=40,
            split_spend_pct=50,
            split_give_pct=10,
        )

        # when
        transactions = service.pay_allowance("emma")

        # then
        assert len(transactions) == 3
        jars = {t.jar: t.amount for t in transactions}
        assert jars["save"] == 4.00
        assert jars["spend"] == 5.00
        assert jars["give"] == 1.00

    def test_pay_allowance_no_config_raises(self, tmp_store):
        # given
        service = FinancialService(tmp_store)

        # when / then
        with pytest.raises(KeyError, match="No allowance configured"):
            service.pay_allowance("unknown")


class TestGetAllowance:
    def test_get_allowance_with_balances(self, tmp_store):
        # given
        service = FinancialService(tmp_store)
        service.configure_allowance(child_id="max", weekly_amount=10.00)
        service.pay_allowance("max")

        # when
        result = service.get_allowance("max")

        # then
        assert result["max"]["total"] == 10.00
        assert result["max"]["balances"]["save"] == 4.00
        assert result["max"]["balances"]["spend"] == 5.00
        assert result["max"]["balances"]["give"] == 1.00


class TestLogTransaction:
    def test_log_spending(self, tmp_store):
        # given
        service = FinancialService(tmp_store)
        service.configure_allowance(child_id="max", weekly_amount=10.00)
        service.pay_allowance("max")

        # when
        txn = service.log_transaction(
            child_id="max",
            amount=3.00,
            type="spent",
            jar="spend",
            description="Bought candy",
        )

        # then
        assert txn.type == "spent"
        result = service.get_allowance("max")
        assert result["max"]["balances"]["spend"] == 2.00  # 5.00 - 3.00


class TestSavingsGoals:
    def test_set_savings_goal(self, tmp_store):
        # given
        service = FinancialService(tmp_store)

        # when
        goal = service.set_savings_goal(
            child_id="emma",
            name="New bike",
            target_amount=50.00,
        )

        # then
        assert goal.name == "New bike"
        assert goal.target_amount == 50.00
        assert goal.status == "active"

    def test_update_savings_goal(self, tmp_store):
        # given
        service = FinancialService(tmp_store)
        goal = service.set_savings_goal(
            child_id="emma", name="Lego set", target_amount=30.00
        )

        # when
        updated = service.update_savings_goal(
            goal.id, current_amount=15.00
        )

        # then
        assert updated.current_amount == 15.00

    def test_get_savings_goals_by_status(self, tmp_store):
        # given
        service = FinancialService(tmp_store)
        goal = service.set_savings_goal(
            child_id="max", name="Game", target_amount=20.00
        )
        service.update_savings_goal(goal.id, status="reached")
        service.set_savings_goal(
            child_id="max", name="Book", target_amount=10.00
        )

        # when
        active = service.get_savings_goals(child_id="max", status="active")
        reached = service.get_savings_goals(child_id="max", status="reached")

        # then
        assert len(active) == 1
        assert active[0].name == "Book"
        assert len(reached) == 1
        assert reached[0].name == "Game"


class TestFinancialSummary:
    def test_summary_structure(self, tmp_store):
        # given
        service = FinancialService(tmp_store)
        service.configure_allowance(child_id="max", weekly_amount=7.00)
        service.pay_allowance("max")

        # when
        summary = service.get_financial_summary("max")

        # then
        assert "balances" in summary
        assert "recent_transactions" in summary
        assert "savings_goals" in summary
