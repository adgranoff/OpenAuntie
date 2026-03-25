"""OpenAuntie MCP server — single server exposing all parenting tools.

Uses FastMCP to register tools for family management and consultant services.
All tool names use the `parenting_` prefix per project convention.
"""

import json
import os
from datetime import date
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from parenting.models.family import Child, FamilyProfile, Parent
from parenting.services.activity_service import ActivityService
from parenting.services.behavior_service import BehaviorService
from parenting.services.consultant_service import ConsultantService
from parenting.services.education_service import EducationService
from parenting.services.emotional_service import EmotionalService
from parenting.services.family_service import FamilyService
from parenting.services.feedback_service import FeedbackService
from parenting.services.financial_service import FinancialService
from parenting.services.health_service import HealthService
from parenting.services.journal_service import JournalService
from parenting.services.research_service import ResearchService
from parenting.services.routine_service import RoutineService
from parenting.storage.json_store import JsonStore

mcp = FastMCP(
    "openauntie",
    description="OpenAuntie — Evidence-based parenting consulting agent",
)


def _get_data_dir() -> Path:
    """Resolve the data directory from env var or default."""
    env_dir = os.environ.get("OPENAUNTIE_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path(__file__).parent.parent / "family_data"


def _make_store() -> JsonStore:
    """Create a JsonStore pointed at the configured data directory."""
    return JsonStore(data_dir=_get_data_dir())


def _make_family_service() -> FamilyService:
    """Create a FamilyService with a fresh store."""
    return FamilyService(store=_make_store())


def _make_consultant_service() -> ConsultantService:
    """Create a ConsultantService with a fresh store."""
    return ConsultantService(store=_make_store())


def _make_routine_service() -> RoutineService:
    """Create a RoutineService with a fresh store."""
    return RoutineService(store=_make_store())


def _make_journal_service() -> JournalService:
    """Create a JournalService with a fresh store."""
    return JournalService(store=_make_store())


def _make_behavior_service() -> BehaviorService:
    """Create a BehaviorService with a fresh store."""
    return BehaviorService(store=_make_store())


def _make_health_service() -> HealthService:
    """Create a HealthService with a fresh store."""
    return HealthService(store=_make_store())


def _make_education_service() -> EducationService:
    """Create an EducationService with a fresh store."""
    return EducationService(store=_make_store())


def _make_emotional_service() -> EmotionalService:
    """Create an EmotionalService with a fresh store."""
    return EmotionalService(store=_make_store())


def _make_activity_service() -> ActivityService:
    """Create an ActivityService with a fresh store."""
    return ActivityService(store=_make_store())


def _make_feedback_service() -> FeedbackService:
    """Create a FeedbackService with a fresh store."""
    return FeedbackService(store=_make_store())


def _make_financial_service() -> FinancialService:
    """Create a FinancialService with a fresh store."""
    return FinancialService(store=_make_store())


def _make_research_service() -> ResearchService:
    """Create a ResearchService with a fresh store."""
    return ResearchService(store=_make_store())


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class SetupFamilyInput(BaseModel):
    """Input for creating a family profile."""

    family_name: str = Field(
        ...,
        description="Family last name",
        examples=["Smith", "Garcia"],
        min_length=1,
        max_length=100,
    )
    parent_name: str = Field(
        ...,
        description="Primary parent or caregiver name",
        examples=["Alice", "Bob"],
        min_length=1,
        max_length=100,
    )
    children_json: str = Field(
        ...,
        description=(
            'JSON array of children, each with "id", "name", and '
            '"date_of_birth" (YYYY-MM-DD). Example: '
            '[{"id": "max", "name": "Max", "date_of_birth": "2020-06-15"}]'
        ),
        examples=[
            '[{"id": "max", "name": "Max", "date_of_birth": "2020-06-15"}]'
        ],
    )


class GetChildInput(BaseModel):
    """Input for retrieving a single child."""

    child_id: str = Field(
        ...,
        description="Unique child identifier (slug)",
        examples=["max", "emma"],
        min_length=1,
    )


class UpdateChildInput(BaseModel):
    """Input for updating a child's profile fields."""

    child_id: str = Field(
        ...,
        description="Unique child identifier (slug)",
        examples=["max", "emma"],
        min_length=1,
    )
    name: str | None = Field(
        default=None,
        description="Updated display name",
        examples=["Maxwell"],
    )
    temperament_notes: str | None = Field(
        default=None,
        description="Updated temperament observations",
        examples=["Energetic and curious, loves building things"],
    )
    strengths: list[str] | None = Field(
        default=None,
        description="Updated list of strengths",
        examples=[["creativity", "persistence", "math"]],
    )
    challenges: list[str] | None = Field(
        default=None,
        description="Updated list of growth areas",
        examples=[["transitions", "homework focus"]],
    )
    special_considerations: list[str] | None = Field(
        default=None,
        description="Updated special considerations (allergies, ADHD, etc.)",
        examples=[["dairy allergy", "ADHD"]],
    )


class AddChildInput(BaseModel):
    """Input for adding a new child to the family."""

    id: str = Field(
        ...,
        description="Unique child identifier (slug, lowercase)",
        examples=["zara", "liam"],
        min_length=1,
        max_length=50,
    )
    name: str = Field(
        ...,
        description="Child's display name",
        examples=["Zara", "Liam"],
        min_length=1,
        max_length=100,
    )
    date_of_birth: str = Field(
        ...,
        description="Date of birth in YYYY-MM-DD format",
        examples=["2022-03-15"],
    )


class ConsultInput(BaseModel):
    """Input for the parenting consultant."""

    question: str = Field(
        ...,
        description="Your parenting question — be as specific as you can",
        examples=[
            "My 5-year-old refuses to do homework. What should I try?",
            "How do I handle bedtime battles with a 3-year-old?",
        ],
        min_length=1,
    )


class WeeklySummaryInput(BaseModel):
    """Input for the weekly summary."""

    days: int = Field(
        default=7,
        description="Number of days to include in the summary",
        examples=[7, 14],
        ge=1,
        le=90,
    )


class AgeExpectationsInput(BaseModel):
    """Input for developmental age expectations."""

    child_id: str = Field(
        ...,
        description="Unique child identifier (slug)",
        examples=["max", "emma"],
        min_length=1,
    )


# ---------------------------------------------------------------------------
# Family tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_setup(
    family_name: str,
    parent_name: str,
    children_json: str,
) -> str:
    """Create a family profile for OpenAuntie.

    Sets up the family with a parent and children. This is the first step
    before using any other OpenAuntie tools.
    """
    svc = _make_family_service()

    # Parse children JSON
    try:
        children_raw = json.loads(children_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid children JSON: {e}"})

    if not isinstance(children_raw, list):
        return json.dumps({"error": "children_json must be a JSON array"})

    children = []
    for entry in children_raw:
        try:
            children.append(
                Child(
                    id=entry["id"],
                    name=entry["name"],
                    date_of_birth=date.fromisoformat(entry["date_of_birth"]),
                )
            )
        except (KeyError, ValueError) as e:
            return json.dumps({
                "error": (
                    f"Invalid child entry {entry}: {e}. Each child needs "
                    "'id', 'name', and 'date_of_birth' (YYYY-MM-DD)."
                )
            })

    profile = FamilyProfile(
        family_name=family_name,
        parents=[Parent(id="parent-1", name=parent_name, role="parent")],
        children=children,
    )
    svc.save_family(profile)

    return json.dumps({
        "status": "ok",
        "family_name": family_name,
        "parent": parent_name,
        "children_count": len(children),
        "message": (
            f"Welcome to OpenAuntie, {parent_name}! "
            f"The {family_name} family profile is set up with "
            f"{len(children)} child(ren)."
        ),
    })


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_family() -> str:
    """Get the full family profile including all children with computed ages."""
    svc = _make_family_service()
    profile = svc.get_family()
    if profile is None:
        return json.dumps({
            "error": "No family profile found. Use parenting_setup first."
        })
    return json.dumps(profile.model_dump(mode="json"), indent=2)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_child(child_id: str) -> str:
    """Get a single child's profile with their computed age.

    Returns the child's full profile including strengths, challenges,
    temperament notes, and special considerations.
    """
    svc = _make_family_service()
    child = svc.get_child(child_id)
    if child is None:
        return json.dumps({
            "error": f"Child '{child_id}' not found."
        })
    return json.dumps(child.model_dump(mode="json"), indent=2)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_update_child(
    child_id: str,
    name: str | None = None,
    temperament_notes: str | None = None,
    strengths: list[str] | None = None,
    challenges: list[str] | None = None,
    special_considerations: list[str] | None = None,
) -> str:
    """Update a child's profile fields.

    Only the fields you provide will be updated; others remain unchanged.
    """
    svc = _make_family_service()

    kwargs: dict[str, object] = {}
    if name is not None:
        kwargs["name"] = name
    if temperament_notes is not None:
        kwargs["temperament_notes"] = temperament_notes
    if strengths is not None:
        kwargs["strengths"] = strengths
    if challenges is not None:
        kwargs["challenges"] = challenges
    if special_considerations is not None:
        kwargs["special_considerations"] = special_considerations

    if not kwargs:
        return json.dumps({"error": "No fields provided to update."})

    try:
        updated = svc.update_child(child_id, **kwargs)
    except KeyError as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "status": "ok",
        "child": updated.model_dump(mode="json"),
    })


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_add_child(
    id: str,
    name: str,
    date_of_birth: str,
) -> str:
    """Add a new child to the family profile.

    The family profile must already exist (use parenting_setup first).
    """
    svc = _make_family_service()

    try:
        dob = date.fromisoformat(date_of_birth)
    except ValueError as e:
        return json.dumps({
            "error": f"Invalid date_of_birth: {e}. Use YYYY-MM-DD format."
        })

    child = Child(id=id, name=name, date_of_birth=dob)
    try:
        updated = svc.add_child(child)
    except (ValueError, RuntimeError) as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "status": "ok",
        "children_count": len(updated.children),
        "added": child.model_dump(mode="json"),
    })


# ---------------------------------------------------------------------------
# Consultant tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_consult(question: str) -> str:
    """Ask OpenAuntie a parenting question.

    This is the crown jewel of OpenAuntie. It assembles full family context,
    relevant research from the evidence base, developmental expectations for
    your children's ages, and safety checks — all so the AI can give you
    personalized, evidence-based advice.

    Be as specific as you can: mention the child's name, the situation,
    what you've tried, and what you're hoping for.
    """
    svc = _make_consultant_service()
    result = svc.consult(question)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_weekly_summary(days: int = 7) -> str:
    """Generate a cross-domain weekly summary for the family.

    Shows behavior trends, routine completion, emotional patterns,
    highlights, and concerns for each child over the specified period.
    """
    svc = _make_consultant_service()
    result = svc.weekly_summary(period_days=days)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_age_expectations(child_id: str) -> str:
    """Get developmental expectations for a child's current age.

    Returns evidence-based information about what is developmentally
    typical and realistic for this child's age band, including executive
    function, emotional regulation, social development, and common
    parental over-expectations.
    """
    svc = _make_consultant_service()
    try:
        result = svc.get_age_expectations(child_id)
    except KeyError as e:
        return json.dumps({"error": str(e)})
    return json.dumps(result, indent=2, default=str)


# ---------------------------------------------------------------------------
# Behavior tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_points(child_id: str | None = None) -> str:
    """Get current points balance for one or all children.

    If child_id is provided, returns that child's balance only.
    Otherwise returns balances for all children in the family.
    """
    svc = _make_behavior_service()
    try:
        result = svc.get_points(child_id=child_id)
    except KeyError as e:
        return json.dumps({"error": str(e)})
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_add_points(
    child_id: str,
    delta: int,
    reason: str,
    category: str = "general",
) -> str:
    """Add or subtract points for a child.

    Use positive delta to award points and negative delta to deduct.
    Points will not go below zero.
    """
    svc = _make_behavior_service()
    try:
        entry = svc.add_points(
            child_id=child_id, delta=delta, reason=reason, category=category
        )
    except (KeyError, ValueError) as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "entry": entry.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_spend_points(child_id: str, reward_id: str) -> str:
    """Redeem a child's points for a reward.

    Deducts the reward's point cost from the child's balance.
    Fails if the child has insufficient points.
    """
    svc = _make_behavior_service()
    try:
        result = svc.spend_points(child_id=child_id, reward_id=reward_id)
    except (KeyError, ValueError) as e:
        return json.dumps({"error": str(e)})
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_reset_points() -> str:
    """Reset all children's points to the configured starting value.

    Creates reset entries that zero out current balances and set them
    to points_per_day.
    """
    svc = _make_behavior_service()
    result = svc.reset_points()
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_configure_points(
    points_per_day: int | None = None,
    reset_schedule: str | None = None,
    rollover: bool | None = None,
) -> str:
    """Update points system configuration.

    Only the fields you provide will be updated; others remain unchanged.
    """
    svc = _make_behavior_service()
    kwargs: dict[str, object] = {}
    if points_per_day is not None:
        kwargs["points_per_day"] = points_per_day
    if reset_schedule is not None:
        kwargs["reset_schedule"] = reset_schedule
    if rollover is not None:
        kwargs["rollover"] = rollover

    if not kwargs:
        return json.dumps({"error": "No fields provided to update."})

    try:
        config = svc.configure_points(**kwargs)
    except Exception as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "config": config.model_dump(mode="json"),
    })


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_rewards() -> str:
    """Get all available reward options that children can redeem points for."""
    svc = _make_behavior_service()
    rewards = svc.get_rewards()
    return json.dumps(
        [r.model_dump(mode="json") for r in rewards], indent=2, default=str
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_add_reward(
    name: str,
    point_cost: int,
    description: str = "",
) -> str:
    """Add a new reward option that children can redeem points for."""
    svc = _make_behavior_service()
    try:
        reward = svc.add_reward(
            name=name, point_cost=point_cost, description=description
        )
    except Exception as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "reward": reward.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_chores(child_id: str | None = None) -> str:
    """List chore definitions and today's completion status.

    If child_id is provided, filters to chores assigned to that child.
    """
    svc = _make_behavior_service()
    result = svc.get_chores(child_id=child_id)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_add_chore(
    name: str,
    frequency: str = "daily",
    assigned_to: str | None = None,
    point_value: int = 0,
) -> str:
    """Add a new chore definition.

    assigned_to is a comma-separated list of child IDs, or omit for all children.
    """
    svc = _make_behavior_service()
    child_ids = (
        [cid.strip() for cid in assigned_to.split(",") if cid.strip()]
        if assigned_to
        else None
    )
    try:
        chore = svc.add_chore(
            name=name,
            frequency=frequency,
            assigned_to=child_ids,
            point_value=point_value,
        )
    except Exception as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "chore": chore.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_chore(
    chore_id: str,
    child_id: str,
    notes: str = "",
) -> str:
    """Log that a child completed a chore.

    Automatically awards points if the chore has a point value.
    """
    svc = _make_behavior_service()
    try:
        completion = svc.log_chore(
            chore_id=chore_id, child_id=child_id, notes=notes
        )
    except KeyError as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "completion": completion.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_consequence(
    child_id: str,
    behavior: str,
    consequence: str,
    consequence_type: str = "logical",
    context: str = "",
) -> str:
    """Log a consequence for a behavior incident.

    Records what behavior occurred, what consequence was applied,
    and optional context for future reference and pattern analysis.
    """
    svc = _make_behavior_service()
    try:
        log = svc.log_consequence(
            child_id=child_id,
            behavior=behavior,
            consequence=consequence,
            consequence_type=consequence_type,
            context=context,
        )
    except KeyError as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "consequence": log.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_consequence_history(
    child_id: str | None = None,
    days: int = 30,
) -> str:
    """Get consequence history, optionally filtered by child and time period.

    Returns logged consequences within the specified number of days.
    """
    svc = _make_behavior_service()
    results = svc.get_consequence_history(child_id=child_id, days=days)
    return json.dumps(
        [c.model_dump(mode="json") for c in results], indent=2, default=str
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_behavior_trends(
    child_id: str | None = None,
    days: int = 7,
) -> str:
    """Get behavior analytics: points earned/spent, ratios, chore completion rates.

    Analyzes behavior patterns over the specified period to help identify
    trends and areas for encouragement.
    """
    svc = _make_behavior_service()
    result = svc.get_behavior_trends(child_id=child_id, days=days)
    return json.dumps(result, indent=2, default=str)


# ---------------------------------------------------------------------------
# Routine tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_routines() -> str:
    """Get all routine definitions for the family.

    Returns all configured routines including steps, schedule,
    and target times.
    """
    svc = _make_routine_service()
    routines = svc.get_routines()
    return json.dumps(
        [r.model_dump(mode="json") for r in routines], indent=2
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_create_routine(
    name: str,
    steps_json: str,
    child_id: str | None = None,
    target_start_time: str | None = None,
    target_duration_minutes: int = 30,
) -> str:
    """Create a new routine with ordered steps.

    Steps should be a JSON array of objects with 'order', 'name',
    and optionally 'duration_minutes' and 'description'.
    Example: [{"order": 1, "name": "Brush teeth", "duration_minutes": 3}]
    """
    svc = _make_routine_service()

    try:
        steps = json.loads(steps_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid steps JSON: {e}"})

    if not isinstance(steps, list):
        return json.dumps({"error": "steps_json must be a JSON array"})

    try:
        routine = svc.create_routine(
            name=name,
            steps=steps,
            child_id=child_id,
            target_start_time=target_start_time,
            target_duration_minutes=target_duration_minutes,
        )
    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "status": "ok",
        "routine": routine.model_dump(mode="json"),
    })


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_update_routine(
    routine_id: str,
    name: str | None = None,
    steps_json: str | None = None,
    target_start_time: str | None = None,
    target_duration_minutes: int | None = None,
) -> str:
    """Update an existing routine's fields.

    Only the fields you provide will be updated; others remain unchanged.
    """
    svc = _make_routine_service()

    kwargs: dict[str, object] = {}
    if name is not None:
        kwargs["name"] = name
    if steps_json is not None:
        try:
            kwargs["steps"] = json.loads(steps_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid steps JSON: {e}"})
    if target_start_time is not None:
        kwargs["target_start_time"] = target_start_time
    if target_duration_minutes is not None:
        kwargs["target_duration_minutes"] = target_duration_minutes

    if not kwargs:
        return json.dumps({"error": "No fields provided to update."})

    try:
        updated = svc.update_routine(routine_id, **kwargs)
    except KeyError as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "status": "ok",
        "routine": updated.model_dump(mode="json"),
    })


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_delete_routine(routine_id: str) -> str:
    """Delete a routine definition permanently.

    This removes the routine template. Existing execution logs are preserved.
    """
    svc = _make_routine_service()
    try:
        svc.delete_routine(routine_id)
    except KeyError as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "status": "ok",
        "message": f"Routine '{routine_id}' deleted.",
    })


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_routine(
    routine_id: str,
    child_id: str,
    steps_completed: list[int],
    steps_skipped: list[int] | None = None,
    resistance_level: int = 0,
    notes: str = "",
) -> str:
    """Log a routine execution for a child.

    Record which steps were completed, which were skipped,
    and the child's resistance level (0=none, 1=mild, 2=moderate, 3=high).
    """
    svc = _make_routine_service()
    try:
        execution = svc.log_routine(
            routine_id=routine_id,
            child_id=child_id,
            steps_completed=steps_completed,
            steps_skipped=steps_skipped,
            resistance_level=resistance_level,
            notes=notes,
        )
    except KeyError as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "status": "ok",
        "execution": execution.model_dump(mode="json"),
    })


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_routine_trends(
    routine_id: str | None = None,
    child_id: str | None = None,
    days: int = 14,
) -> str:
    """Get analytics and trends for routine executions.

    Shows completion rates, streak tracking, commonly skipped steps,
    resistance trends, and regression detection over the specified period.
    """
    svc = _make_routine_service()
    result = svc.get_routine_trends(
        routine_id=routine_id, child_id=child_id, days=days
    )
    return json.dumps(result, indent=2)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_schedule_today() -> str:
    """Get today's scheduled routines and their completion status.

    Shows which routines are scheduled for today's day of the week
    and whether they have been completed.
    """
    svc = _make_routine_service()
    result = svc.get_schedule_today()
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Journal tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_journal_entry(
    content: str,
    child_id: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Add a journal entry about a child or the family.

    Use tags to categorize entries (e.g. 'milestone', 'concern', 'win',
    'behavior', 'medical'). Leave child_id empty for family-level entries.
    """
    svc = _make_journal_service()
    entry = svc.add_entry(content=content, child_id=child_id, tags=tags)
    return json.dumps({
        "status": "ok",
        "entry": entry.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_journal(
    child_id: str | None = None,
    days: int | None = None,
    tags: list[str] | None = None,
) -> str:
    """Retrieve journal entries with optional filtering.

    Filter by child, recency (days), or tags. Returns entries newest first.
    """
    svc = _make_journal_service()
    entries = svc.get_entries(child_id=child_id, days=days, tags=tags)
    return json.dumps(
        [e.model_dump(mode="json") for e in entries],
        indent=2,
        default=str,
    )


# ---------------------------------------------------------------------------
# Health tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_medications(child_id: str | None = None) -> str:
    """Get active medications for one or all children.

    Returns a list of current medications with dosage, frequency,
    and time-of-day information.
    """
    svc = _make_health_service()
    meds = svc.get_medications(child_id=child_id)
    return json.dumps(
        [m.model_dump(mode="json") for m in meds], indent=2, default=str
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_add_medication(
    child_id: str,
    name: str,
    dosage: str = "",
    frequency: str = "daily",
    time_of_day: list[str] | None = None,
) -> str:
    """Add a new medication for a child.

    Records the medication name, dosage, frequency, and when it should
    be administered (morning, evening, etc.).
    """
    svc = _make_health_service()
    med = svc.add_medication(
        child_id=child_id,
        name=name,
        dosage=dosage,
        frequency=frequency,
        time_of_day=time_of_day,
    )
    return json.dumps({
        "status": "ok",
        "medication": med.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_medication(
    medication_id: str,
    child_id: str,
    skipped: bool = False,
    skip_reason: str = "",
    notes: str = "",
) -> str:
    """Log a medication administration or skip event.

    Records whether the medication was given or skipped,
    with an optional reason and notes.
    """
    svc = _make_health_service()
    log = svc.log_medication(
        medication_id=medication_id,
        child_id=child_id,
        skipped=skipped,
        skip_reason=skip_reason,
        notes=notes,
    )
    return json.dumps({
        "status": "ok",
        "log": log.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_appointments(child_id: str | None = None) -> str:
    """Get upcoming appointments for one or all children.

    Returns future, uncompleted appointments with provider,
    type, and location details.
    """
    svc = _make_health_service()
    appts = svc.get_appointments(child_id=child_id)
    return json.dumps(
        [a.model_dump(mode="json") for a in appts], indent=2, default=str
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_add_appointment(
    provider: str,
    date_time: str,
    child_id: str | None = None,
    type: str = "pediatrician",
    location: str = "",
) -> str:
    """Add a new appointment.

    Schedule a medical or other appointment with a provider.
    Use ISO datetime format for date_time (e.g. 2026-04-15T10:00:00).
    """
    svc = _make_health_service()
    appt = svc.add_appointment(
        provider=provider,
        date_time=date_time,
        child_id=child_id,
        type=type,
        location=location,
    )
    return json.dumps({
        "status": "ok",
        "appointment": appt.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_growth(
    child_id: str,
    height_inches: float | None = None,
    weight_pounds: float | None = None,
    notes: str = "",
) -> str:
    """Log a growth measurement for a child.

    Record height in inches and/or weight in pounds.
    At least one measurement should be provided.
    """
    svc = _make_health_service()
    record = svc.log_growth(
        child_id=child_id,
        height_inches=height_inches,
        weight_pounds=weight_pounds,
        notes=notes,
    )
    return json.dumps({
        "status": "ok",
        "record": record.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_growth_history(child_id: str) -> str:
    """Get all growth records for a child, ordered by date.

    Returns height and weight measurements over time to
    track growth trends.
    """
    svc = _make_health_service()
    records = svc.get_growth_history(child_id=child_id)
    return json.dumps(
        [r.model_dump(mode="json") for r in records], indent=2, default=str
    )


# ---------------------------------------------------------------------------
# Education tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_reading(
    child_id: str,
    book_title: str,
    pages_read: int | None = None,
    minutes_read: int | None = None,
    finished_book: bool = False,
    enjoyment: int | None = None,
) -> str:
    """Log a reading session for a child.

    Track what was read, how much, and how the child enjoyed it.
    Enjoyment is rated 1-5.
    """
    svc = _make_education_service()
    entry = svc.log_reading(
        child_id=child_id,
        book_title=book_title,
        pages_read=pages_read,
        minutes_read=minutes_read,
        finished_book=finished_book,
        enjoyment=enjoyment,
    )
    return json.dumps({
        "status": "ok",
        "entry": entry.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_reading_log(
    child_id: str,
    days: int | None = None,
) -> str:
    """Get reading log entries with summary statistics.

    Returns entries and stats including books completed,
    total pages, total minutes, and reading streak.
    """
    svc = _make_education_service()
    result = svc.get_reading_log(child_id=child_id, days=days)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_homework(
    child_id: str,
    subject: str,
    duration_minutes: int,
    struggle_level: int = 0,
    completed: bool = True,
    help_needed: str = "",
) -> str:
    """Log a homework session for a child.

    Records subject, duration, difficulty (0=easy to 3=meltdown),
    completion status, and what help was needed.
    """
    svc = _make_education_service()
    entry = svc.log_homework(
        child_id=child_id,
        subject=subject,
        duration_minutes=duration_minutes,
        struggle_level=struggle_level,
        completed=completed,
        help_needed=help_needed,
    )
    return json.dumps({
        "status": "ok",
        "entry": entry.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_homework_trends(
    child_id: str | None = None,
    days: int = 14,
) -> str:
    """Analyze homework patterns over a time window.

    Shows subjects by struggle level, completion rate,
    average duration, and individual entries.
    """
    svc = _make_education_service()
    result = svc.get_homework_trends(child_id=child_id, days=days)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_set_learning_goal(
    child_id: str,
    goal: str,
    category: str = "",
    milestones: list[str] | None = None,
    target_date: str | None = None,
) -> str:
    """Create a new learning goal for a child.

    Set academic or developmental goals with optional milestones
    and a target date. Goals start as 'active'.
    """
    svc = _make_education_service()
    lg = svc.set_learning_goal(
        child_id=child_id,
        goal=goal,
        category=category,
        milestones=milestones,
        target_date=target_date,
    )
    return json.dumps({
        "status": "ok",
        "goal": lg.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_learning_goals(
    child_id: str | None = None,
    status: str | None = None,
) -> str:
    """List learning goals, optionally filtered by child and status.

    Status can be: active, completed, paused, or abandoned.
    """
    svc = _make_education_service()
    goals = svc.get_learning_goals(child_id=child_id, status=status)
    return json.dumps(
        [g.model_dump(mode="json") for g in goals], indent=2, default=str
    )


# ---------------------------------------------------------------------------
# Emotional tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_mood(
    child_id: str,
    zone: str | None = None,
    intensity: int | None = None,
    emotions: list[str] | None = None,
    context: str = "",
    coping_used: list[str] | None = None,
) -> str:
    """Log a mood check-in for a child.

    Uses Zones of Regulation colors (blue, green, yellow, red),
    intensity (1-5), specific emotions, and coping strategies used.
    """
    svc = _make_emotional_service()
    entry = svc.log_mood(
        child_id=child_id,
        zone=zone,
        intensity=intensity,
        emotions=emotions,
        context=context,
        coping_used=coping_used,
    )
    return json.dumps({
        "status": "ok",
        "entry": entry.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_mood_trends(
    child_id: str | None = None,
    days: int = 14,
) -> str:
    """Analyze mood patterns over a time window.

    Shows zone distribution, average intensity, common emotions,
    and individual mood entries.
    """
    svc = _make_emotional_service()
    result = svc.get_mood_trends(child_id=child_id, days=days)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_conflict(
    children_involved: list[str],
    trigger: str,
    description: str = "",
    resolution: str = "",
    resolution_type: str = "mediated",
) -> str:
    """Log a conflict between children.

    Records who was involved, what triggered it, and how it was
    resolved. Resolution types: mediated, self_resolved, unresolved, escalated.
    """
    svc = _make_emotional_service()
    record = svc.log_conflict(
        children_involved=children_involved,
        trigger=trigger,
        description=description,
        resolution=resolution,
        resolution_type=resolution_type,
    )
    return json.dumps({
        "status": "ok",
        "conflict": record.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_conflict_patterns(days: int = 30) -> str:
    """Analyze conflict patterns over a time window.

    Shows total conflicts, common triggers, resolution type
    distribution, and which children are most frequently involved.
    """
    svc = _make_emotional_service()
    result = svc.get_conflict_patterns(days=days)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_milestone(
    child_id: str,
    description: str,
    category: str = "general",
) -> str:
    """Log a developmental milestone for a child.

    Categories: cognitive, emotional, social, physical, language, or general.
    """
    svc = _make_emotional_service()
    milestone = svc.log_milestone(
        child_id=child_id,
        description=description,
        category=category,
    )
    return json.dumps({
        "status": "ok",
        "milestone": milestone.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_milestones(child_id: str | None = None) -> str:
    """List developmental milestones, optionally filtered by child.

    Returns milestones sorted by date ascending.
    """
    svc = _make_emotional_service()
    milestones = svc.get_milestones(child_id=child_id)
    return json.dumps(
        [m.model_dump(mode="json") for m in milestones], indent=2, default=str
    )


# ---------------------------------------------------------------------------
# Activities tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_activity(
    name: str,
    date: str,
    time: str | None = None,
    location: str = "",
    category: str = "",
    rating: int | None = None,
    would_repeat: bool | None = None,
) -> str:
    """Log a family activity or outing.

    Record what the family did, where, and how it went.
    Rating is 1-5, and would_repeat helps track favorites.
    """
    svc = _make_activity_service()
    event = svc.log_activity(
        name=name,
        date=date,
        time=time,
        location=location,
        category=category,
        rating=rating,
        would_repeat=would_repeat,
    )
    return json.dumps({
        "status": "ok",
        "event": event.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_activity_history(
    days: int | None = None,
    category: str | None = None,
) -> str:
    """Get past family activities, optionally filtered.

    Filter by number of days and/or category (outdoor, educational,
    social, creative, physical).
    """
    svc = _make_activity_service()
    events = svc.get_activity_history(days=days, category=category)
    return json.dumps(
        [e.model_dump(mode="json") for e in events], indent=2, default=str
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_plan_trip(
    name: str,
    start_date: str,
    end_date: str,
    destination: str = "",
    behavior_plan: str = "",
) -> str:
    """Create a trip plan for the family.

    Plan a vacation or outing with dates, destination, and an
    optional behavior plan for the trip.
    """
    svc = _make_activity_service()
    trip = svc.plan_trip(
        name=name,
        start_date=start_date,
        end_date=end_date,
        destination=destination,
        behavior_plan=behavior_plan,
    )
    return json.dumps({
        "status": "ok",
        "trip": trip.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_trip(trip_id: str | None = None) -> str:
    """Get a specific trip by ID or list all active trips.

    If trip_id is provided, returns that trip's details.
    Otherwise returns all active trip plans.
    """
    svc = _make_activity_service()
    try:
        result = svc.get_trip(trip_id=trip_id)
    except KeyError as e:
        return json.dumps({"error": str(e)})
    if isinstance(result, list):
        return json.dumps(
            [t.model_dump(mode="json") for t in result], indent=2, default=str
        )
    return json.dumps(result.model_dump(mode="json"), indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_suggest_activity(
    ages: list[int] | None = None,
    category: str | None = None,
    energy_level: str | None = None,
) -> str:
    """Get activity suggestions based on children's ages and preferences.

    Returns context about past activities and the request criteria
    for the consultant to generate personalized suggestions.
    """
    svc = _make_activity_service()
    result = svc.suggest_activity(
        ages=ages,
        category=category,
        energy_level=energy_level,
    )
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_create_family_meeting_agenda() -> str:
    """Generate a family meeting agenda pulling from all domains.

    Creates a structured agenda with appreciations, calendar items,
    old and new business, chore review, and fun planning.
    """
    store = _make_store()
    svc = ActivityService(store=store)
    result = svc.create_family_meeting_agenda(store=store)
    return json.dumps(result, indent=2, default=str)


# ---------------------------------------------------------------------------
# Financial tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_configure_allowance(
    child_id: str,
    weekly_amount: float,
    split_save_pct: int = 40,
    split_spend_pct: int = 50,
    split_give_pct: int = 10,
    model: str = "hybrid",
) -> str:
    """Set up or update allowance configuration for a child.

    Uses a three-jar system (save, spend, give). Splits must sum to 100.
    Model can be: commission, unconditional, or hybrid.
    """
    svc = _make_financial_service()
    try:
        config = svc.configure_allowance(
            child_id=child_id,
            weekly_amount=weekly_amount,
            split_save_pct=split_save_pct,
            split_spend_pct=split_spend_pct,
            split_give_pct=split_give_pct,
            model=model,
        )
    except ValueError as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "config": config.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_allowance(child_id: str | None = None) -> str:
    """Get allowance configuration and current jar balances.

    Shows save/spend/give balances and the allowance config
    for one or all children.
    """
    svc = _make_financial_service()
    result = svc.get_allowance(child_id=child_id)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_pay_allowance(child_id: str) -> str:
    """Distribute weekly allowance across jars based on the child's config.

    Splits the weekly amount into save, spend, and give jars
    according to the configured percentages.
    """
    svc = _make_financial_service()
    try:
        transactions = svc.pay_allowance(child_id=child_id)
    except KeyError as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "transactions": [t.model_dump(mode="json") for t in transactions],
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_log_transaction(
    child_id: str,
    amount: float,
    type: str,
    jar: str | None = None,
    description: str = "",
) -> str:
    """Record a financial transaction for a child.

    Types: allowance, earned, spent, saved, given, gift_received.
    Jar: save, spend, or give (optional).
    """
    svc = _make_financial_service()
    txn = svc.log_transaction(
        child_id=child_id,
        amount=amount,
        type=type,
        jar=jar,
        description=description,
    )
    return json.dumps({
        "status": "ok",
        "transaction": txn.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_financial_summary(child_id: str | None = None) -> str:
    """Get a financial overview: balances, recent transactions, savings goals.

    Provides a comprehensive financial picture for one or all children.
    """
    svc = _make_financial_service()
    result = svc.get_financial_summary(child_id=child_id)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_set_savings_goal(
    child_id: str,
    name: str,
    target_amount: float,
    target_date: str | None = None,
) -> str:
    """Create a savings goal for a child.

    Set a target amount and optional target date.
    Goals start as 'active'.
    """
    svc = _make_financial_service()
    goal = svc.set_savings_goal(
        child_id=child_id,
        name=name,
        target_amount=target_amount,
        target_date=target_date,
    )
    return json.dumps({
        "status": "ok",
        "goal": goal.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_savings_goals(
    child_id: str | None = None,
    status: str | None = None,
) -> str:
    """List savings goals, optionally filtered by child and status.

    Status can be: active, reached, or abandoned.
    """
    svc = _make_financial_service()
    goals = svc.get_savings_goals(child_id=child_id, status=status)
    return json.dumps(
        [g.model_dump(mode="json") for g in goals], indent=2, default=str
    )


# ---------------------------------------------------------------------------
# Research watchlist tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_research_sources() -> str:
    """List the trusted research sources being monitored.

    Returns the names of journals, organizations, and databases
    that OpenAuntie watches for new parenting research.
    """
    svc = _make_research_service()
    sources = svc.get_watchlist_sources()
    return json.dumps({"sources": sources}, indent=2)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_add_research_proposal(
    source: str,
    title: str,
    summary: str,
    relevant_knowledge_file: str,
    proposed_change: str,
    evidence_grade: str = "EMERGING",
    citation: str = "",
    source_url: str = "",
) -> str:
    """Add a research update proposal to the editorial queue.

    Proposes a change to the knowledge base based on new research.
    The proposal enters a 'pending' state until reviewed.
    """
    svc = _make_research_service()
    proposal = svc.add_update_proposal(
        source=source,
        title=title,
        summary=summary,
        relevant_knowledge_file=relevant_knowledge_file,
        proposed_change=proposed_change,
        evidence_grade=evidence_grade,
        citation=citation,
        source_url=source_url,
    )
    return json.dumps({
        "status": "ok",
        "proposal": proposal.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_research_proposals(status: str | None = None) -> str:
    """View research update proposals in the editorial queue.

    Optionally filter by status: 'pending', 'approved', or 'dismissed'.
    Returns all proposals if no status filter is provided.
    """
    svc = _make_research_service()
    proposals = svc.get_update_proposals(status=status)
    return json.dumps(
        [p.model_dump(mode="json") for p in proposals], indent=2, default=str
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_approve_research_update(
    update_id: str,
    reviewer_notes: str = "",
) -> str:
    """Approve a research update proposal (admin action).

    Marks the proposal as approved, indicating the knowledge base
    should be updated accordingly.
    """
    svc = _make_research_service()
    try:
        updated = svc.approve_update(
            update_id=update_id, reviewer_notes=reviewer_notes
        )
    except KeyError as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "proposal": updated.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_dismiss_research_update(
    update_id: str,
    reviewer_notes: str = "",
) -> str:
    """Dismiss a research update proposal with reason (admin action).

    Marks the proposal as dismissed. Include reviewer_notes to explain why.
    """
    svc = _make_research_service()
    try:
        updated = svc.dismiss_update(
            update_id=update_id, reviewer_notes=reviewer_notes
        )
    except KeyError as e:
        return json.dumps({"error": str(e)})
    return json.dumps({
        "status": "ok",
        "proposal": updated.model_dump(mode="json"),
    }, default=str)


# ---------------------------------------------------------------------------
# Parent feedback tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def parenting_rate_advice(
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
) -> str:
    """Rate how well a parenting technique worked for your child.

    Outcome scale: 1=made things worse, 2=didn't help, 3=no change,
    4=helped somewhat, 5=worked great.
    """
    svc = _make_feedback_service()
    feedback = svc.rate_advice(
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
    return json.dumps({
        "status": "ok",
        "feedback": feedback.model_dump(mode="json"),
    }, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_feedback_history(
    child_id: str | None = None,
    technique: str | None = None,
    days: int | None = None,
) -> str:
    """Get history of technique ratings, optionally filtered.

    Filter by child, technique name, or recency (days).
    Returns entries newest first.
    """
    svc = _make_feedback_service()
    entries = svc.get_feedback_history(
        child_id=child_id, technique=technique, days=days
    )
    return json.dumps(
        [e.model_dump(mode="json") for e in entries], indent=2, default=str
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_family_insights(child_id: str | None = None) -> str:
    """Get insights about what parenting techniques work for each child.

    Analyzes feedback data to show per-child technique effectiveness,
    most/least effective approaches, and confidence levels based on
    sample size.
    """
    svc = _make_feedback_service()
    result = svc.get_family_insights(child_id=child_id)
    return json.dumps(result, indent=2, default=str)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def parenting_get_technique_summary(technique: str) -> str:
    """Get a summary of how a specific technique has worked across all children.

    Shows overall and per-child statistics, plus the contexts where
    the technique has been tried.
    """
    svc = _make_feedback_service()
    result = svc.get_technique_summary(technique=technique)
    return json.dumps(result, indent=2, default=str)
