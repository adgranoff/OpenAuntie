"""Financial service — allowance, three-jar system, savings goals, spending."""

from datetime import datetime, timezone

from parenting.models.financial import AllowanceConfig, FinancialTransaction, SavingsGoal
from parenting.storage.store import Store


class FinancialService:
    """Manages children's financial literacy tools: allowance, savings, spending."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def _load(self) -> dict:
        data = self.store.load("financial")
        if not data:
            return {"configs": [], "transactions": [], "savings_goals": []}
        return data

    def _save(self, data: dict) -> None:
        self.store.save("financial", data)

    # --- Allowance Config ---

    def configure_allowance(
        self,
        child_id: str,
        weekly_amount: float,
        split_save_pct: int = 40,
        split_spend_pct: int = 50,
        split_give_pct: int = 10,
        pay_day: int = 6,
        model: str = "hybrid",
    ) -> AllowanceConfig:
        """Set up or update allowance configuration for a child."""
        if split_save_pct + split_spend_pct + split_give_pct != 100:
            raise ValueError(
                f"Splits must sum to 100, got {split_save_pct + split_spend_pct + split_give_pct}"
            )

        config = AllowanceConfig(
            child_id=child_id,
            weekly_amount=weekly_amount,
            split_save_pct=split_save_pct,
            split_spend_pct=split_spend_pct,
            split_give_pct=split_give_pct,
            pay_day=pay_day,
            model=model,
        )

        data = self._load()
        configs = data.get("configs", [])
        # Replace existing config for this child
        configs = [c for c in configs if c.get("child_id") != child_id]
        configs.append(config.model_dump())
        data["configs"] = configs
        self._save(data)
        return config

    def get_allowance(self, child_id: str | None = None) -> dict:
        """Get allowance config and current balances."""
        data = self._load()
        configs = data.get("configs", [])
        transactions = data.get("transactions", [])

        if child_id:
            configs = [c for c in configs if c.get("child_id") == child_id]

        result = {}
        for config_data in configs:
            config = AllowanceConfig.model_validate(config_data)
            cid = config.child_id

            # Compute balances per jar
            child_txns = [t for t in transactions if t.get("child_id") == cid]
            balances = {"save": 0.0, "spend": 0.0, "give": 0.0}
            for txn in child_txns:
                jar = txn.get("jar")
                txn_type = txn.get("type")
                amount = txn.get("amount", 0)
                if jar and jar in balances:
                    if txn_type in ("allowance", "earned", "gift_received", "saved"):
                        balances[jar] += amount
                    elif txn_type in ("spent", "given"):
                        balances[jar] -= amount

            result[cid] = {
                "config": config.model_dump(),
                "balances": balances,
                "total": sum(balances.values()),
            }

        return result

    # --- Transactions ---

    def pay_allowance(self, child_id: str) -> list[FinancialTransaction]:
        """Distribute weekly allowance across jars based on config."""
        data = self._load()
        configs = data.get("configs", [])
        config_data = next(
            (c for c in configs if c.get("child_id") == child_id), None
        )
        if not config_data:
            raise KeyError(f"No allowance configured for child: {child_id}")

        config = AllowanceConfig.model_validate(config_data)
        amount = config.weekly_amount

        transactions = []
        for jar, pct in [
            ("save", config.split_save_pct),
            ("spend", config.split_spend_pct),
            ("give", config.split_give_pct),
        ]:
            if pct > 0:
                jar_amount = round(amount * pct / 100, 2)
                txn = FinancialTransaction(
                    child_id=child_id,
                    amount=jar_amount,
                    type="allowance",
                    jar=jar,
                    description=f"Weekly allowance ({pct}% to {jar})",
                )
                transactions.append(txn)

        data.setdefault("transactions", [])
        for txn in transactions:
            data["transactions"].append(txn.model_dump())
        self._save(data)
        return transactions

    def log_transaction(
        self,
        child_id: str,
        amount: float,
        type: str,
        jar: str | None = None,
        description: str = "",
    ) -> FinancialTransaction:
        """Record a financial transaction."""
        txn = FinancialTransaction(
            child_id=child_id,
            amount=amount,
            type=type,
            jar=jar,
            description=description,
        )
        data = self._load()
        data.setdefault("transactions", [])
        data["transactions"].append(txn.model_dump())
        self._save(data)
        return txn

    def get_financial_summary(self, child_id: str | None = None) -> dict:
        """Balances, recent transactions, savings goal progress."""
        data = self._load()
        transactions = [
            FinancialTransaction.model_validate(t)
            for t in data.get("transactions", [])
        ]

        if child_id:
            transactions = [t for t in transactions if t.child_id == child_id]

        return {
            "balances": self.get_allowance(child_id),
            "recent_transactions": [
                t.model_dump() for t in transactions[-10:]
            ],
            "savings_goals": self.get_savings_goals(child_id),
        }

    # --- Savings Goals ---

    def set_savings_goal(
        self,
        child_id: str,
        name: str,
        target_amount: float,
        target_date: str | None = None,
    ) -> SavingsGoal:
        """Create a savings goal."""
        goal = SavingsGoal(
            child_id=child_id,
            name=name,
            target_amount=target_amount,
            target_date=target_date,
        )
        data = self._load()
        data.setdefault("savings_goals", [])
        data["savings_goals"].append(goal.model_dump())
        self._save(data)
        return goal

    def update_savings_goal(self, goal_id: str, **kwargs: object) -> SavingsGoal:
        """Update a savings goal."""
        data = self._load()
        goals = data.get("savings_goals", [])

        for i, g in enumerate(goals):
            if g.get("id") == goal_id:
                g.update(kwargs)
                goals[i] = g
                data["savings_goals"] = goals
                self._save(data)
                return SavingsGoal.model_validate(g)

        raise KeyError(f"Savings goal not found: {goal_id}")

    def get_savings_goals(
        self, child_id: str | None = None, status: str | None = None
    ) -> list[SavingsGoal]:
        """Get savings goals, optionally filtered."""
        data = self._load()
        goals = [
            SavingsGoal.model_validate(g) for g in data.get("savings_goals", [])
        ]

        if child_id:
            goals = [g for g in goals if g.child_id == child_id]
        if status:
            goals = [g for g in goals if g.status == status]

        return goals
