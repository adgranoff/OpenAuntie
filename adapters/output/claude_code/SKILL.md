---
name: parenting
description: |
  OpenAuntie — Evidence-based parenting consulting agent.
  Provides behavior tracking, routine management, health tracking, education support,
  emotional development tools, financial literacy, and AI-powered parenting consultation.
  All tools are exposed via the parenting MCP server.
  Use when: user mentions kids, parenting, points, chores, routines, homework, bedtime,
  allowance, mood, behavior, screen time, or asks for parenting advice.
  Triggers: kids, parenting, points, chores, homework, bedtime, routine, allowance,
  parenting advice, behavior, mood, screen time, family meeting, sibling, emotion
---

# OpenAuntie — Parenting Agent

## MCP Server

All parenting tools are available via the `parenting` MCP server.
Tools are prefixed with `parenting_` and cover these domains:

- **Activities**: `parenting_log_activity`, `parenting_plan_trip`, `parenting_suggest_activity`, +1 more
- **Behavior**: `parenting_get_points`, `parenting_add_points`, `parenting_reset_points`, +3 more
- **Consultant**: `parenting_consult`, `parenting_weekly_summary`, `parenting_get_age_expectations`
- **Education**: `parenting_log_reading`, `parenting_log_homework`, `parenting_get_homework_trends`
- **Emotional**: `parenting_log_mood`, `parenting_log_conflict`, `parenting_get_mood_trends`
- **Family**: `parenting_setup`, `parenting_get_family`, `parenting_get_child`, +2 more
- **Financial**: `parenting_configure_allowance`, `parenting_get_allowance`, `parenting_pay_allowance`, +2 more
- **Health**: `parenting_get_medications`, `parenting_log_medication`, `parenting_get_appointments`
- **Journal**: `parenting_journal_entry`, `parenting_get_journal`
- **Routines**: `parenting_get_routines`, `parenting_create_routine`, `parenting_log_routine`, +1 more

## Key Usage Patterns

### Ask Auntie for advice
Use `parenting_consult` with any parenting question. The tool assembles
full family context with evidence-based research automatically.

### Quick point check
Use `parenting_get_points` to see current standings.

### Log an observation
Use `parenting_journal_entry` for anything that doesn't fit a specific domain.

### Weekly review
Use `parenting_weekly_summary` to see trends across all domains.

### Family meeting prep
Use `parenting_create_family_meeting_agenda` to auto-generate an agenda.
