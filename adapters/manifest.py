"""Tool manifest — single source of truth for all platform adapter generation.

This manifest defines every OpenAuntie MCP tool with platform-agnostic metadata.
Platform adapters use this to generate their specific configurations.
"""

from dataclasses import dataclass, field


@dataclass
class Annotations:
    read_only: bool = False
    destructive: bool = False
    idempotent: bool = False
    open_world: bool = False


@dataclass
class ParamDef:
    name: str
    type: str  # "string", "int", "float", "bool", "list[str]"
    required: bool = True
    description: str = ""
    default: str | None = None


@dataclass
class ToolDef:
    name: str
    domain: str
    description: str
    parameters: list[ParamDef] = field(default_factory=list)
    annotations: Annotations = field(default_factory=Annotations)
    examples: list[str] = field(default_factory=list)


# ============================================================
# TOOL MANIFEST
# ============================================================

TOOL_MANIFEST: list[ToolDef] = [
    # --- Family ---
    ToolDef(
        name="parenting_setup",
        domain="family",
        description="Create your family profile with children and parents",
        parameters=[
            ParamDef("family_name", "string", description="Family last name"),
            ParamDef("parent_name", "string", description="Your name"),
            ParamDef("children_json", "string", False, "JSON array of children with name and date_of_birth"),
        ],
        examples=["Set up my family", "Create a family profile"],
    ),
    ToolDef(
        name="parenting_get_family",
        domain="family",
        description="Get your full family profile",
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["Show my family", "Who's in our family?"],
    ),
    ToolDef(
        name="parenting_get_child",
        domain="family",
        description="Get details about a specific child including age and profile",
        parameters=[ParamDef("child_id", "string", description="Child's ID")],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["Tell me about Max", "Show Emma's profile"],
    ),
    ToolDef(
        name="parenting_update_child",
        domain="family",
        description="Update a child's profile information",
        parameters=[
            ParamDef("child_id", "string", description="Child's ID"),
            ParamDef("name", "string", False, "New name"),
            ParamDef("temperament_notes", "string", False, "Temperament notes"),
            ParamDef("strengths", "string", False, "JSON array of strengths"),
            ParamDef("challenges", "string", False, "JSON array of challenges"),
        ],
        annotations=Annotations(idempotent=True),
        examples=["Update Max's strengths", "Add a note about Emma"],
    ),
    ToolDef(
        name="parenting_add_child",
        domain="family",
        description="Add a new child to the family",
        parameters=[
            ParamDef("id", "string", description="Unique ID for the child"),
            ParamDef("name", "string", description="Child's name"),
            ParamDef("date_of_birth", "string", description="Date of birth (YYYY-MM-DD)"),
        ],
        examples=["Add a new child", "We have a new baby"],
    ),

    # --- Consultant ---
    ToolDef(
        name="parenting_consult",
        domain="consultant",
        description="Ask Auntie a parenting question — assembles full family context with evidence-based research",
        parameters=[ParamDef("question", "string", description="Your parenting question")],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=[
            "My kid won't do homework", "Bedtime is a struggle",
            "How do I handle sibling fighting?", "Is this normal for a 7 year old?",
        ],
    ),
    ToolDef(
        name="parenting_weekly_summary",
        domain="consultant",
        description="Generate a weekly summary across all domains for each child",
        parameters=[ParamDef("days", "int", False, "Number of days to summarize", "7")],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["Weekly summary", "How was this week?"],
    ),
    ToolDef(
        name="parenting_get_age_expectations",
        domain="consultant",
        description="Get developmental expectations for a child's current age",
        parameters=[ParamDef("child_id", "string", description="Child's ID")],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["What should I expect from a 7 year old?", "Is this normal for Max's age?"],
    ),

    # --- Behavior ---
    ToolDef(
        name="parenting_get_points",
        domain="behavior",
        description="Get current point totals for one or all children",
        parameters=[ParamDef("child_id", "string", False, "Child ID or omit for all")],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["How many points does Max have?", "Show points"],
    ),
    ToolDef(
        name="parenting_add_points",
        domain="behavior",
        description="Award or deduct points for a child with a reason",
        parameters=[
            ParamDef("child_id", "string", description="Child's ID"),
            ParamDef("delta", "int", description="Points to add (positive) or subtract (negative)"),
            ParamDef("reason", "string", description="Why points are being given/taken"),
            ParamDef("category", "string", False, "Category: behavior, chore, academic, bonus", "general"),
        ],
        examples=["Give Max a point for cleaning his room", "Take a point from Emma"],
    ),
    ToolDef(
        name="parenting_reset_points",
        domain="behavior",
        description="Reset all children's points to the daily maximum",
        annotations=Annotations(idempotent=True),
        examples=["Reset points", "New day, new points"],
    ),
    ToolDef(
        name="parenting_get_chores",
        domain="behavior",
        description="List chore assignments and today's completion status",
        parameters=[ParamDef("child_id", "string", False, "Filter by child")],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["Show chores", "What chores does Max have today?"],
    ),
    ToolDef(
        name="parenting_log_chore",
        domain="behavior",
        description="Mark a chore as completed for a child",
        parameters=[
            ParamDef("chore_id", "string", description="Chore ID"),
            ParamDef("child_id", "string", description="Child's ID"),
        ],
        examples=["Max finished his chore", "Log chore completion"],
    ),
    ToolDef(
        name="parenting_get_behavior_trends",
        domain="behavior",
        description="Analytics: points earned/spent, positive-to-negative ratio, chore completion rates",
        parameters=[
            ParamDef("child_id", "string", False, "Filter by child"),
            ParamDef("days", "int", False, "Number of days to analyze", "7"),
        ],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["How's behavior this week?", "Show behavior trends"],
    ),

    # --- Routines ---
    ToolDef(
        name="parenting_get_routines",
        domain="routines",
        description="List all defined routines (morning, bedtime, homework, etc.)",
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["Show our routines", "What routines do we have?"],
    ),
    ToolDef(
        name="parenting_create_routine",
        domain="routines",
        description="Define a new routine with steps",
        parameters=[
            ParamDef("name", "string", description="Routine name (e.g., 'Bedtime')"),
            ParamDef("steps_json", "string", description="JSON array of steps with name and duration_minutes"),
            ParamDef("child_id", "string", False, "Assign to specific child, or omit for family-wide"),
        ],
        examples=["Create a bedtime routine", "Set up a morning routine for Max"],
    ),
    ToolDef(
        name="parenting_log_routine",
        domain="routines",
        description="Record how a routine went — which steps were completed, resistance level",
        parameters=[
            ParamDef("routine_id", "string", description="Routine ID"),
            ParamDef("child_id", "string", description="Child's ID"),
            ParamDef("steps_completed", "string", description="JSON array of completed step numbers"),
            ParamDef("resistance_level", "int", False, "0=none, 1=mild, 2=moderate, 3=high", "0"),
        ],
        examples=["Log bedtime routine", "Max did his morning routine with mild resistance"],
    ),
    ToolDef(
        name="parenting_get_routine_trends",
        domain="routines",
        description="Analytics: completion rates, streaks, which steps get skipped, resistance trends",
        parameters=[
            ParamDef("routine_id", "string", False, "Filter by routine"),
            ParamDef("child_id", "string", False, "Filter by child"),
            ParamDef("days", "int", False, "Number of days", "14"),
        ],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["How's the bedtime routine going?", "Show routine trends"],
    ),

    # --- Health ---
    ToolDef(
        name="parenting_get_medications",
        domain="health",
        description="List active medications and schedules",
        parameters=[ParamDef("child_id", "string", False, "Filter by child")],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["What medications is Max on?", "Show medications"],
    ),
    ToolDef(
        name="parenting_log_medication",
        domain="health",
        description="Record that a medication was given or skipped",
        parameters=[
            ParamDef("medication_id", "string", description="Medication ID"),
            ParamDef("child_id", "string", description="Child's ID"),
            ParamDef("skipped", "bool", False, "Was this dose skipped?", "false"),
        ],
        examples=["Max took his allergy pill", "Log medication"],
    ),
    ToolDef(
        name="parenting_get_appointments",
        domain="health",
        description="List upcoming appointments",
        parameters=[ParamDef("child_id", "string", False, "Filter by child")],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["When is the next doctor appointment?", "Show appointments"],
    ),

    # --- Education ---
    ToolDef(
        name="parenting_log_reading",
        domain="education",
        description="Record a reading session",
        parameters=[
            ParamDef("child_id", "string", description="Child's ID"),
            ParamDef("book_title", "string", description="Book being read"),
            ParamDef("minutes_read", "int", False, "Minutes spent reading"),
            ParamDef("finished_book", "bool", False, "Did they finish the book?", "false"),
        ],
        examples=["Max read Percy Jackson for 30 minutes", "Log reading"],
    ),
    ToolDef(
        name="parenting_log_homework",
        domain="education",
        description="Record a homework session with struggle level",
        parameters=[
            ParamDef("child_id", "string", description="Child's ID"),
            ParamDef("subject", "string", description="Subject"),
            ParamDef("duration_minutes", "int", description="Minutes spent"),
            ParamDef("struggle_level", "int", False, "0=easy, 1=moderate, 2=hard, 3=meltdown", "0"),
        ],
        examples=["Max did 20 minutes of math homework", "Log homework"],
    ),
    ToolDef(
        name="parenting_get_homework_trends",
        domain="education",
        description="Analytics: which subjects are hard, duration trends, struggle patterns",
        parameters=[
            ParamDef("child_id", "string", False, "Filter by child"),
            ParamDef("days", "int", False, "Number of days", "14"),
        ],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["How's homework going?", "Show homework trends"],
    ),

    # --- Emotional ---
    ToolDef(
        name="parenting_log_mood",
        domain="emotional",
        description="Record a child's mood using Zones of Regulation (blue/green/yellow/red)",
        parameters=[
            ParamDef("child_id", "string", description="Child's ID"),
            ParamDef("zone", "string", False, "blue, green, yellow, or red"),
            ParamDef("intensity", "int", False, "1-5 intensity level"),
            ParamDef("emotions", "string", False, "Comma-separated emotion words"),
            ParamDef("context", "string", False, "What was happening"),
        ],
        examples=["Max is in the yellow zone", "Emma seems sad today", "Log mood"],
    ),
    ToolDef(
        name="parenting_log_conflict",
        domain="emotional",
        description="Record a sibling or peer conflict with resolution",
        parameters=[
            ParamDef("children_involved", "string", description="Comma-separated child IDs"),
            ParamDef("trigger", "string", description="What started the conflict"),
            ParamDef("resolution_type", "string", False, "mediated, self_resolved, unresolved, escalated", "mediated"),
        ],
        examples=["Max and Emma fought over a toy", "Log sibling conflict"],
    ),
    ToolDef(
        name="parenting_get_mood_trends",
        domain="emotional",
        description="Analytics: mood patterns, zone distribution, common emotions",
        parameters=[
            ParamDef("child_id", "string", False, "Filter by child"),
            ParamDef("days", "int", False, "Number of days", "14"),
        ],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["How's Max's mood been?", "Show mood trends"],
    ),

    # --- Activities ---
    ToolDef(
        name="parenting_log_activity",
        domain="activities",
        description="Record a family activity or outing",
        parameters=[
            ParamDef("name", "string", description="Activity name"),
            ParamDef("date", "string", description="Date (YYYY-MM-DD)"),
            ParamDef("category", "string", False, "outdoor, educational, social, creative, physical"),
            ParamDef("rating", "int", False, "How did it go? 1-5"),
        ],
        examples=["We went to the park today", "Log family activity"],
    ),
    ToolDef(
        name="parenting_plan_trip",
        domain="activities",
        description="Create a trip plan with optional behavior system",
        parameters=[
            ParamDef("name", "string", description="Trip name"),
            ParamDef("start_date", "string", description="Start date"),
            ParamDef("end_date", "string", description="End date"),
            ParamDef("destination", "string", False, "Destination"),
            ParamDef("behavior_plan", "string", False, "Point system or behavior expectations"),
        ],
        examples=["Plan a spring break trip", "Set up a cruise vacation"],
    ),
    ToolDef(
        name="parenting_suggest_activity",
        domain="activities",
        description="Get activity suggestions based on children's ages and interests",
        parameters=[
            ParamDef("category", "string", False, "Preferred category"),
            ParamDef("energy_level", "string", False, "low, medium, or high"),
        ],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["What should we do this weekend?", "Suggest an outdoor activity"],
    ),
    ToolDef(
        name="parenting_create_family_meeting_agenda",
        domain="activities",
        description="Auto-generate a family meeting agenda from recent data across all domains",
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["Create a family meeting agenda", "What should we discuss at our family meeting?"],
    ),

    # --- Financial ---
    ToolDef(
        name="parenting_configure_allowance",
        domain="financial",
        description="Set up the allowance system for a child (three-jar: save/spend/give)",
        parameters=[
            ParamDef("child_id", "string", description="Child's ID"),
            ParamDef("weekly_amount", "float", description="Weekly allowance amount"),
            ParamDef("split_save_pct", "int", False, "Percentage to save jar", "40"),
            ParamDef("split_spend_pct", "int", False, "Percentage to spend jar", "50"),
            ParamDef("split_give_pct", "int", False, "Percentage to give jar", "10"),
            ParamDef("model", "string", False, "commission, unconditional, or hybrid", "hybrid"),
        ],
        examples=["Set up allowance for Max", "Configure allowance"],
    ),
    ToolDef(
        name="parenting_get_allowance",
        domain="financial",
        description="Get allowance configuration and current jar balances",
        parameters=[ParamDef("child_id", "string", False, "Filter by child")],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["How much is in Max's save jar?", "Show allowance status"],
    ),
    ToolDef(
        name="parenting_pay_allowance",
        domain="financial",
        description="Distribute weekly allowance across jars",
        parameters=[ParamDef("child_id", "string", description="Child's ID")],
        examples=["Pay Max's allowance", "It's allowance day"],
    ),
    ToolDef(
        name="parenting_set_savings_goal",
        domain="financial",
        description="Create a savings goal for a child",
        parameters=[
            ParamDef("child_id", "string", description="Child's ID"),
            ParamDef("name", "string", description="What they're saving for"),
            ParamDef("target_amount", "float", description="Target amount in dollars"),
        ],
        examples=["Max wants to save for a Lego set", "Set a savings goal"],
    ),
    ToolDef(
        name="parenting_get_savings_goals",
        domain="financial",
        description="View savings goals and progress",
        parameters=[
            ParamDef("child_id", "string", False, "Filter by child"),
            ParamDef("status", "string", False, "active, reached, or abandoned"),
        ],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["How close is Max to his savings goal?", "Show savings progress"],
    ),

    # --- Journal ---
    ToolDef(
        name="parenting_journal_entry",
        domain="journal",
        description="Write a free-form parenting observation",
        parameters=[
            ParamDef("content", "string", description="Your observation"),
            ParamDef("child_id", "string", False, "About which child (omit for family-level)"),
            ParamDef("tags", "string", False, "Comma-separated tags"),
        ],
        examples=["Max had a great day at school", "Write a parenting note"],
    ),
    ToolDef(
        name="parenting_get_journal",
        domain="journal",
        description="View journal entries with optional filters",
        parameters=[
            ParamDef("child_id", "string", False, "Filter by child"),
            ParamDef("days", "int", False, "Last N days"),
        ],
        annotations=Annotations(read_only=True, idempotent=True),
        examples=["Show recent journal entries", "What did I note about Max?"],
    ),
]


def get_tools_by_domain(domain: str) -> list[ToolDef]:
    """Get all tools for a specific domain."""
    return [t for t in TOOL_MANIFEST if t.domain == domain]


def get_all_domains() -> list[str]:
    """Get list of unique domain names."""
    return sorted(set(t.domain for t in TOOL_MANIFEST))


def get_tool_count() -> int:
    """Total number of tools."""
    return len(TOOL_MANIFEST)
