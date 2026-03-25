"""Behavior service — points, rewards, chores, and consequences management."""

from datetime import date, datetime, timedelta, timezone

from parenting.models.behavior import (
    ChoreCompletion,
    ChoreDefinition,
    ConsequenceLog,
    PointsConfig,
    PointsEntry,
    RewardOption,
)
from parenting.services.family_service import FamilyService
from parenting.storage.store import Store

BEHAVIOR_DOMAIN = "behavior"


def _empty_behavior_data() -> dict:
    """Return the default empty behavior data structure."""
    return {
        "config": PointsConfig().model_dump(mode="json"),
        "entries": [],
        "rewards": [],
        "chores": [],
        "chore_completions": [],
        "consequences": [],
    }


class BehaviorService:
    """Business logic for the behavior domain.

    Manages points, rewards, chores, and consequences. Depends on
    FamilyService for child validation.
    """

    def __init__(self, store: Store) -> None:
        self._store = store
        self._family_service = FamilyService(store)

    def _load_data(self) -> dict:
        """Load behavior data from the store, or return defaults."""
        if not self._store.exists(BEHAVIOR_DOMAIN):
            return _empty_behavior_data()
        data = self._store.load(BEHAVIOR_DOMAIN)
        if not data:
            return _empty_behavior_data()
        return data

    def _save_data(self, data: dict) -> None:
        """Save behavior data to the store."""
        self._store.save(BEHAVIOR_DOMAIN, data)

    def _get_config(self, data: dict) -> PointsConfig:
        """Parse the config section from behavior data."""
        return PointsConfig.model_validate(data.get("config", {}))

    def _get_all_child_ids(self) -> list[str]:
        """Get all child IDs from the family profile."""
        profile = self._family_service.get_family()
        if profile is None:
            return []
        return [child.id for child in profile.children]

    def _validate_child_exists(self, child_id: str) -> None:
        """Raise KeyError if the child does not exist in the family profile."""
        child = self._family_service.get_child(child_id)
        if child is None:
            raise KeyError(f"Child '{child_id}' not found.")

    def _entries_for_period(
        self, entries: list[dict], child_id: str | None, config: PointsConfig
    ) -> list[dict]:
        """Filter entries to the current reset period for a child."""
        now = datetime.now(timezone.utc)

        if config.reset_schedule == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif config.reset_schedule == "weekly":
            # Start of current week (Monday)
            days_since_monday = now.weekday()
            period_start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            # "never" — all entries count
            period_start = datetime.min.replace(tzinfo=timezone.utc)

        filtered = []
        for entry in entries:
            if child_id is not None and entry.get("child_id") != child_id:
                continue
            ts = entry.get("timestamp", "")
            if isinstance(ts, str):
                try:
                    entry_time = datetime.fromisoformat(ts)
                except ValueError:
                    continue
            else:
                entry_time = ts
            if entry_time >= period_start:
                filtered.append(entry)
        return filtered

    def _compute_balance(
        self, entries: list[dict], child_id: str, config: PointsConfig
    ) -> int:
        """Compute current point balance for a child in the current period."""
        period_entries = self._entries_for_period(entries, child_id, config)
        total = 0
        for entry in period_entries:
            if entry.get("child_id") == child_id:
                total += entry.get("delta", 0)
        return max(total, 0)

    # -----------------------------------------------------------------
    # Points
    # -----------------------------------------------------------------

    def get_points(self, child_id: str | None = None) -> dict:
        """Get current points.

        Args:
            child_id: If provided, get points for this child only.
                If None, return points for all children.

        Returns:
            Dict with child_id -> balance mapping and config info.
        """
        data = self._load_data()
        config = self._get_config(data)
        entries = data.get("entries", [])

        if child_id is not None:
            balance = self._compute_balance(entries, child_id, config)
            return {
                "points": {child_id: balance},
                "config": config.model_dump(mode="json"),
            }

        child_ids = self._get_all_child_ids()
        points: dict[str, int] = {}
        for cid in child_ids:
            points[cid] = self._compute_balance(entries, cid, config)

        return {
            "points": points,
            "config": config.model_dump(mode="json"),
        }

    def add_points(
        self,
        child_id: str,
        delta: int,
        reason: str,
        category: str = "general",
    ) -> PointsEntry:
        """Add or subtract points for a child.

        Args:
            child_id: The child to modify points for.
            delta: Points to add (positive) or subtract (negative).
            reason: Why points are being modified.
            category: Category of the entry.

        Returns:
            The created PointsEntry.

        Raises:
            KeyError: If the child does not exist.
            ValueError: If the deduction would take the balance below zero.
        """
        self._validate_child_exists(child_id)
        data = self._load_data()
        config = self._get_config(data)
        entries = data.get("entries", [])

        if delta < 0:
            current_balance = self._compute_balance(entries, child_id, config)
            if current_balance + delta < 0:
                raise ValueError(
                    f"Insufficient points: {child_id} has {current_balance} "
                    f"but tried to deduct {abs(delta)}."
                )

        entry = PointsEntry(
            child_id=child_id,
            delta=delta,
            reason=reason,
            category=category,
        )
        entries.append(entry.model_dump(mode="json"))
        data["entries"] = entries
        self._save_data(data)
        return entry

    def reset_points(self) -> dict:
        """Reset all children's points to the configured points_per_day.

        Creates reset entries that zero out current balances and set them
        to the configured starting value.

        Returns:
            Dict summarizing the reset for each child.
        """
        data = self._load_data()
        config = self._get_config(data)
        entries = data.get("entries", [])
        child_ids = self._get_all_child_ids()

        summary: dict[str, dict] = {}
        for cid in child_ids:
            current = self._compute_balance(entries, cid, config)
            # Zero out current balance, then add points_per_day
            if current != 0:
                entries.append(
                    PointsEntry(
                        child_id=cid,
                        delta=-current,
                        reason="Daily reset (zero out)",
                        category="general",
                    ).model_dump(mode="json")
                )
            entries.append(
                PointsEntry(
                    child_id=cid,
                    delta=config.points_per_day,
                    reason="Daily reset (starting points)",
                    category="general",
                ).model_dump(mode="json")
            )
            summary[cid] = {
                "previous_balance": current,
                "new_balance": config.points_per_day,
            }

        data["entries"] = entries
        self._save_data(data)
        return {"reset": summary, "config": config.model_dump(mode="json")}

    def configure_points(self, **kwargs: object) -> PointsConfig:
        """Update points configuration.

        Args:
            **kwargs: Fields to update on PointsConfig.

        Returns:
            The updated PointsConfig.
        """
        data = self._load_data()
        config = self._get_config(data)
        updated_data = config.model_dump()
        updated_data.update(kwargs)
        new_config = PointsConfig.model_validate(updated_data)
        data["config"] = new_config.model_dump(mode="json")
        self._save_data(data)
        return new_config

    # -----------------------------------------------------------------
    # Rewards
    # -----------------------------------------------------------------

    def get_rewards(self) -> list[RewardOption]:
        """Get all reward options.

        Returns:
            List of RewardOption objects.
        """
        data = self._load_data()
        return [
            RewardOption.model_validate(r) for r in data.get("rewards", [])
        ]

    def add_reward(
        self, name: str, point_cost: int, description: str = ""
    ) -> RewardOption:
        """Add a new reward option.

        Args:
            name: Reward name.
            point_cost: Points required to redeem.
            description: Optional description.

        Returns:
            The created RewardOption.
        """
        data = self._load_data()
        reward = RewardOption(
            name=name, point_cost=point_cost, description=description
        )
        rewards = data.get("rewards", [])
        rewards.append(reward.model_dump(mode="json"))
        data["rewards"] = rewards
        self._save_data(data)
        return reward

    def spend_points(self, child_id: str, reward_id: str) -> dict:
        """Redeem points for a reward.

        Args:
            child_id: The child spending points.
            reward_id: The reward to redeem.

        Returns:
            Dict with redemption details.

        Raises:
            KeyError: If child or reward not found.
            ValueError: If insufficient points.
        """
        self._validate_child_exists(child_id)
        data = self._load_data()
        rewards = data.get("rewards", [])

        reward = None
        for r in rewards:
            if r.get("id") == reward_id:
                reward = RewardOption.model_validate(r)
                break
        if reward is None:
            raise KeyError(f"Reward '{reward_id}' not found.")

        config = self._get_config(data)
        entries = data.get("entries", [])
        current_balance = self._compute_balance(entries, child_id, config)

        if current_balance < reward.point_cost:
            raise ValueError(
                f"Insufficient points: {child_id} has {current_balance} "
                f"but '{reward.name}' costs {reward.point_cost}."
            )

        entry = PointsEntry(
            child_id=child_id,
            delta=-reward.point_cost,
            reason=f"Redeemed: {reward.name}",
            category="spent",
        )
        entries.append(entry.model_dump(mode="json"))
        data["entries"] = entries
        self._save_data(data)

        new_balance = self._compute_balance(entries, child_id, config)
        return {
            "status": "ok",
            "child_id": child_id,
            "reward": reward.name,
            "points_spent": reward.point_cost,
            "remaining_balance": new_balance,
        }

    # -----------------------------------------------------------------
    # Chores
    # -----------------------------------------------------------------

    def get_chores(self, child_id: str | None = None) -> dict:
        """List chore definitions and today's completion status.

        Args:
            child_id: If provided, filter to chores assigned to this child.

        Returns:
            Dict with chore definitions and today's completion info.
        """
        data = self._load_data()
        chores = [
            ChoreDefinition.model_validate(c) for c in data.get("chores", [])
        ]
        completions = [
            ChoreCompletion.model_validate(c)
            for c in data.get("chore_completions", [])
        ]

        # Filter chores by child assignment if specified
        if child_id is not None:
            chores = [
                c
                for c in chores
                if not c.assigned_to or child_id in c.assigned_to
            ]

        # Get today's completions (use UTC date for consistency)
        today = datetime.now(timezone.utc).date()
        today_completions: dict[str, list[str]] = {}  # chore_id -> [child_ids]
        for comp in completions:
            comp_date = comp.completed_at.date() if isinstance(comp.completed_at, datetime) else date.fromisoformat(str(comp.completed_at)[:10])
            if comp_date == today:
                if comp.chore_id not in today_completions:
                    today_completions[comp.chore_id] = []
                today_completions[comp.chore_id].append(comp.child_id)

        chore_list = []
        for chore in chores:
            completed_by = today_completions.get(chore.id, [])
            chore_list.append({
                **chore.model_dump(mode="json"),
                "completed_today_by": completed_by,
            })

        return {"chores": chore_list, "today": today.isoformat()}

    def add_chore(
        self,
        name: str,
        frequency: str = "daily",
        assigned_to: list[str] | None = None,
        point_value: int = 0,
    ) -> ChoreDefinition:
        """Add a new chore definition.

        Args:
            name: Chore name.
            frequency: How often: daily, weekly, or as_needed.
            assigned_to: Child IDs, or None for all children.
            point_value: Points earned for completing.

        Returns:
            The created ChoreDefinition.
        """
        data = self._load_data()
        chore = ChoreDefinition(
            name=name,
            frequency=frequency,  # type: ignore[arg-type]
            assigned_to=assigned_to or [],
            point_value=point_value,
        )
        chores = data.get("chores", [])
        chores.append(chore.model_dump(mode="json"))
        data["chores"] = chores
        self._save_data(data)
        return chore

    def log_chore(
        self, chore_id: str, child_id: str, notes: str = ""
    ) -> ChoreCompletion:
        """Log a chore completion.

        Args:
            chore_id: Which chore was completed.
            child_id: Which child completed it.
            notes: Optional notes.

        Returns:
            The created ChoreCompletion.

        Raises:
            KeyError: If the chore or child is not found.
        """
        self._validate_child_exists(child_id)
        data = self._load_data()

        # Validate chore exists
        chores = data.get("chores", [])
        chore = None
        for c in chores:
            if c.get("id") == chore_id:
                chore = ChoreDefinition.model_validate(c)
                break
        if chore is None:
            raise KeyError(f"Chore '{chore_id}' not found.")

        completion = ChoreCompletion(
            chore_id=chore_id,
            child_id=child_id,
            notes=notes,
        )
        completions = data.get("chore_completions", [])
        completions.append(completion.model_dump(mode="json"))
        data["chore_completions"] = completions

        # Auto-award points if the chore has a point value
        if chore.point_value > 0:
            entry = PointsEntry(
                child_id=child_id,
                delta=chore.point_value,
                reason=f"Chore completed: {chore.name}",
                category="chore",
            )
            entries = data.get("entries", [])
            entries.append(entry.model_dump(mode="json"))
            data["entries"] = entries

        self._save_data(data)
        return completion

    # -----------------------------------------------------------------
    # Consequences
    # -----------------------------------------------------------------

    def log_consequence(
        self,
        child_id: str,
        behavior: str,
        consequence: str,
        consequence_type: str = "logical",
        context: str = "",
    ) -> ConsequenceLog:
        """Log a consequence for a behavior incident.

        Args:
            child_id: Which child.
            behavior: The behavior that triggered it.
            consequence: What consequence was applied.
            consequence_type: natural, logical, loss_of_privilege, or other.
            context: Additional context.

        Returns:
            The created ConsequenceLog.

        Raises:
            KeyError: If the child does not exist.
        """
        self._validate_child_exists(child_id)
        data = self._load_data()

        log = ConsequenceLog(
            child_id=child_id,
            behavior=behavior,
            consequence=consequence,
            consequence_type=consequence_type,  # type: ignore[arg-type]
            context=context,
        )
        consequences = data.get("consequences", [])
        consequences.append(log.model_dump(mode="json"))
        data["consequences"] = consequences
        self._save_data(data)
        return log

    def get_consequence_history(
        self, child_id: str | None = None, days: int = 30
    ) -> list[ConsequenceLog]:
        """Get consequence history, optionally filtered.

        Args:
            child_id: If provided, filter to this child.
            days: Number of days to look back.

        Returns:
            List of ConsequenceLog objects within the period.
        """
        data = self._load_data()
        consequences = data.get("consequences", [])
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        result = []
        for c in consequences:
            log = ConsequenceLog.model_validate(c)
            if child_id is not None and log.child_id != child_id:
                continue
            if log.timestamp >= cutoff:
                result.append(log)
        return result

    # -----------------------------------------------------------------
    # Analytics
    # -----------------------------------------------------------------

    def get_behavior_trends(
        self, child_id: str | None = None, days: int = 7
    ) -> dict:
        """Compute behavior analytics over a period.

        Args:
            child_id: If provided, get trends for this child only.
            days: Number of days to analyze.

        Returns:
            Dict with earned, spent, ratio, and chore completion rates.
        """
        data = self._load_data()
        entries = data.get("entries", [])
        completions = data.get("chore_completions", [])
        chores = data.get("chores", [])
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        child_ids = [child_id] if child_id else self._get_all_child_ids()

        trends: dict[str, dict] = {}
        for cid in child_ids:
            earned = 0
            spent = 0
            for entry in entries:
                if entry.get("child_id") != cid:
                    continue
                ts = entry.get("timestamp", "")
                if isinstance(ts, str):
                    try:
                        entry_time = datetime.fromisoformat(ts)
                    except ValueError:
                        continue
                else:
                    entry_time = ts
                if entry_time < cutoff:
                    continue
                delta = entry.get("delta", 0)
                if delta > 0:
                    earned += delta
                else:
                    spent += abs(delta)

            # Positive-to-negative ratio
            ratio = earned / spent if spent > 0 else float(earned) if earned > 0 else 0.0

            # Chore completion rate
            daily_chores = [
                c for c in chores
                if c.get("frequency") == "daily"
                and (
                    not c.get("assigned_to")
                    or cid in c.get("assigned_to", [])
                )
            ]
            expected_completions = len(daily_chores) * days
            actual_completions = 0
            for comp in completions:
                if comp.get("child_id") != cid:
                    continue
                ts = comp.get("completed_at", "")
                if isinstance(ts, str):
                    try:
                        comp_time = datetime.fromisoformat(ts)
                    except ValueError:
                        continue
                else:
                    comp_time = ts
                if comp_time >= cutoff:
                    actual_completions += 1

            chore_rate = (
                actual_completions / expected_completions
                if expected_completions > 0
                else 0.0
            )

            trends[cid] = {
                "total_earned": earned,
                "total_spent": spent,
                "positive_to_negative_ratio": ratio,
                "chore_completion_rate": chore_rate,
                "chores_completed": actual_completions,
                "chores_expected": expected_completions,
            }

        return {"trends": trends, "period_days": days}
