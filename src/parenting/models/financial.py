"""Financial domain models — allowance, savings goals, transactions."""

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class AllowanceConfig(BaseModel):
    """Per-child allowance configuration."""

    child_id: str
    weekly_amount: float = Field(..., ge=0, description="Weekly allowance amount")
    split_save_pct: int = Field(default=40, ge=0, le=100)
    split_spend_pct: int = Field(default=50, ge=0, le=100)
    split_give_pct: int = Field(default=10, ge=0, le=100)
    pay_day: int = Field(
        default=6,
        ge=0,
        le=6,
        description="Day of week for payment, 0=Mon, 6=Sun",
    )
    model: str = Field(
        default="hybrid",
        description="commission, unconditional, or hybrid",
    )


class FinancialTransaction(BaseModel):
    """A financial event — allowance, earning, spending, saving, or giving."""

    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    child_id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
    amount: float = Field(..., description="Transaction amount (always positive)")
    type: str = Field(
        ...,
        description="allowance, earned, spent, saved, given, gift_received",
    )
    jar: str | None = Field(
        default=None,
        description="save, spend, or give",
    )
    description: str = Field(default="")


class SavingsGoal(BaseModel):
    """A savings goal for a child."""

    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    child_id: str
    name: str = Field(..., min_length=1)
    target_amount: float = Field(..., ge=0)
    current_amount: float = Field(default=0, ge=0)
    target_date: str | None = Field(default=None, description="ISO date")
    status: str = Field(default="active", description="active, reached, abandoned")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
