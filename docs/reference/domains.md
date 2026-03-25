# Domain Reference

OpenAuntie organizes family data into 10 tracking domains, plus the consultant service. Each domain has its own data model, service, storage file, and set of MCP tools.

---

## 1. Family

**What it tracks:** The family profile -- parents, children, and family metadata.

**Storage file:** `family_data/family_profile.json`

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_setup` | Create a family profile with parents and children |
| `parenting_get_family` | Get the full family profile with computed ages |
| `parenting_get_child` | Get a single child's profile |
| `parenting_update_child` | Update a child's name, temperament, strengths, challenges, or special considerations |
| `parenting_add_child` | Add a new child to an existing family |

### Data Model Fields

**FamilyProfile:**
- `family_name` (str) -- Family last name
- `parents` (list[Parent]) -- Parents/caregivers
- `children` (list[Child]) -- Children in the family
- `timezone` (str) -- Family timezone (IANA format)
- `values` (list[str]) -- Family values and priorities
- `created_at` (datetime)

**Child:**
- `id` (str) -- Unique identifier slug
- `name` (str) -- Display name
- `date_of_birth` (date) -- Date of birth
- `temperament_notes` (str) -- Parent observations about temperament
- `strengths` (list[str]) -- Child's strengths
- `challenges` (list[str]) -- Current growth areas
- `special_considerations` (list[str]) -- Allergies, ADHD, etc.
- `age_description` (computed) -- "X years Y months"

**Parent:**
- `id` (str) -- Unique identifier
- `name` (str) -- Display name
- `role` (str) -- parent, co-parent, guardian, caregiver

---

## 2. Behavior

**What it tracks:** Points, rewards, chores, chore completions, and consequences.

**Storage file:** `family_data/behavior.json`

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_get_points` | Current point balances for one or all children |
| `parenting_add_points` | Award or deduct points with a reason and category |
| `parenting_spend_points` | Redeem points for a reward |
| `parenting_reset_points` | Reset all children to configured starting points |
| `parenting_configure_points` | Update points-per-day, reset schedule, rollover settings |
| `parenting_get_rewards` | List all reward options |
| `parenting_add_reward` | Create a new reward with a point cost |
| `parenting_get_chores` | Chore definitions with today's completion status |
| `parenting_add_chore` | Create a new chore definition |
| `parenting_log_chore` | Log a chore completion (auto-awards points if configured) |
| `parenting_log_consequence` | Log a consequence for a behavior incident |
| `parenting_get_consequence_history` | Get consequence history with optional filtering |
| `parenting_get_behavior_trends` | Compute behavior analytics: ratio, completion rates, trends |

### Data Model Fields

**PointsConfig:**
- `points_per_day` (int, default 3) -- Max points earnable per day
- `reset_schedule` ("daily" | "weekly" | "never")
- `rollover` (bool) -- Whether unused points carry over
- `reset_time` (str, "HH:MM")

**PointsEntry:**
- `id`, `child_id`, `delta` (int -- positive=earned, negative=spent), `reason`, `category` ("general" | "behavior" | "chore" | "academic" | "bonus" | "spent"), `timestamp`

**RewardOption:**
- `id`, `name`, `point_cost` (int), `description`, `active` (bool)

**ChoreDefinition:**
- `id`, `name`, `description`, `frequency` ("daily" | "weekly" | "as_needed"), `assigned_to` (list[str] -- child IDs, empty = all), `point_value` (int -- 0 = family duty, no points), `age_minimum` (int)

**ChoreCompletion:**
- `id`, `chore_id`, `child_id`, `completed_at`, `verified_by`, `notes`

**ConsequenceLog:**
- `id`, `child_id`, `behavior`, `consequence`, `consequence_type` ("natural" | "logical" | "loss_of_privilege" | "other"), `context`, `timestamp`, `follow_up_notes`

### Analytics

- **Points balance:** Current period balance per child
- **Positive-to-negative ratio:** Earned vs. spent/deducted (research target: 5:1)
- **Chore completion rate:** Daily chores completed / expected over period
- **Behavior trends:** Earned, spent, ratio, chore rate over configurable period

---

## 3. Routines

**What it tracks:** Routine definitions (steps, schedules) and daily execution logs.

**Storage file:** `family_data/routines.json`

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_get_routines` | List all routine definitions |
| `parenting_create_routine` | Create a routine with ordered steps and schedule |
| `parenting_update_routine` | Update routine name, steps, schedule, or timing |
| `parenting_delete_routine` | Delete a routine definition |
| `parenting_log_routine` | Log a routine execution with completed/skipped steps and resistance level |
| `parenting_get_routine_trends` | Analytics: completion rate, streak, skipped steps, regression detection |
| `parenting_get_schedule_today` | Today's scheduled routines and completion status |

### Data Model Fields

**RoutineDefinition:**
- `id`, `name`, `child_id` (optional -- None = family-wide)
- `steps` (list[RoutineStep]) -- Ordered steps
- `target_start_time` (str, "HH:MM")
- `target_duration_minutes` (int, default 30)
- `days_of_week` (list[int] -- 0=Monday through 6=Sunday, default = every day)

**RoutineStep:**
- `order` (int, 1-based), `name`, `duration_minutes` (int, default 5), `description`

**RoutineExecution:**
- `id`, `routine_id`, `child_id`, `date` (ISO date)
- `started_at`, `completed_at` (ISO datetimes)
- `steps_completed` (list[int]) -- Step order numbers completed
- `steps_skipped` (list[int]) -- Step order numbers skipped
- `resistance_level` (0=none, 1=mild, 2=moderate, 3=high)
- `notes`

### Analytics

- **Completion rate:** Percentage of executions where all steps were completed
- **Current streak:** Consecutive days of full completion (working backward from today)
- **Skipped steps:** Most commonly skipped step numbers with frequency counts
- **Resistance trend:** Average resistance level over the analysis period
- **Regression flag:** True if completion rate dropped more than 20% between first and second half of the analysis period

---

## 4. Health

**What it tracks:** Medications, medication administration logs, appointments, and growth records.

**Storage file:** `family_data/health.json`

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_get_medications` | List medications, optionally filtered by child |
| `parenting_add_medication` | Add a medication with dosage, frequency, and schedule |
| `parenting_log_medication` | Log a medication administration or skipped dose |
| `parenting_get_appointments` | List upcoming and past appointments |
| `parenting_add_appointment` | Schedule a new appointment |
| `parenting_log_growth` | Record height and/or weight measurement |
| `parenting_get_growth_history` | Get growth records for a child |

### Data Model Fields

**Medication:**
- `id`, `child_id`, `name`, `dosage` (str, e.g. "5mg"), `frequency` ("daily" | "twice_daily" | "as_needed")
- `time_of_day` (list[str] -- "morning", "evening", etc.), `prescriber`, `start_date`, `end_date`
- `notes`, `active` (bool)

**MedicationLog:**
- `id`, `medication_id`, `child_id`, `administered_at`, `administered_by`
- `notes`, `skipped` (bool), `skip_reason`

**Appointment:**
- `id`, `child_id` (optional -- None for family-wide), `provider`, `type` ("pediatrician" | "dentist" | "specialist" | "therapy")
- `date_time`, `location`, `notes`, `completed` (bool), `follow_up_needed` (bool), `follow_up_notes`

**GrowthRecord:**
- `id`, `child_id`, `date`, `height_inches` (float), `weight_pounds` (float), `notes`

---

## 5. Education

**What it tracks:** Reading logs, homework sessions with struggle levels, and learning goals with milestones.

**Storage file:** `family_data/education.json`

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_log_reading` | Log a reading session with book, pages, duration, and enjoyment |
| `parenting_get_reading_log` | Get reading history for a child |
| `parenting_log_homework` | Log a homework session with subject, duration, and struggle level |
| `parenting_get_homework_trends` | Homework analytics: duration and struggle patterns by subject |
| `parenting_set_learning_goal` | Create a learning goal with milestones |
| `parenting_get_learning_goals` | Get learning goals and progress for a child |

### Data Model Fields

**ReadingEntry:**
- `id`, `child_id`, `date`, `book_title`
- `pages_read` (int), `minutes_read` (int)
- `finished_book` (bool), `enjoyment` (1-5), `notes`

**HomeworkEntry:**
- `id`, `child_id`, `date`, `subject` (str -- math, reading, science, etc.)
- `duration_minutes` (int), `struggle_level` (0=easy, 1=moderate, 2=hard, 3=meltdown)
- `completed` (bool), `help_needed` (str), `notes`

**LearningGoal:**
- `id`, `child_id`, `goal` (str), `category` (str -- reading, math, writing, etc.)
- `target_date`, `milestones` (list[str]), `milestones_completed` (list[int])
- `status` ("active" | "completed" | "paused" | "abandoned")
- `created_at`, `completed_at`, `reflection`

### Analytics

- **Homework trends:** Average duration and struggle level per subject, patterns over time
- **Reading trends:** Books read, total minutes, enjoyment distribution

---

## 6. Emotional

**What it tracks:** Mood check-ins using the Zones of Regulation framework, conflict records, and developmental milestones.

**Storage file:** `family_data/emotional.json`

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_log_mood` | Log a mood check-in with zone, intensity, emotions, and coping strategies |
| `parenting_get_mood_trends` | Mood analytics: zone distribution, intensity trend, common emotions |
| `parenting_log_conflict` | Log a conflict between children with trigger and resolution |
| `parenting_get_conflict_patterns` | Conflict analytics: frequency, triggers, resolution types |
| `parenting_log_milestone` | Record a developmental milestone |
| `parenting_get_milestones` | Get developmental milestones for a child |

### Data Model Fields

**MoodEntry:**
- `id`, `child_id`, `timestamp`
- `zone` ("blue" | "green" | "yellow" | "red")
- `intensity` (1-5), `emotions` (list[str] -- happy, frustrated, anxious, etc.)
- `context` (str -- what was happening), `coping_used` (list[str] -- deep breathing, walk, etc.), `notes`

**ConflictRecord:**
- `id`, `children_involved` (list[str]), `timestamp`
- `trigger` (str), `description`, `resolution`
- `resolution_type` ("mediated" | "self_resolved" | "unresolved" | "escalated")
- `what_worked`, `what_didnt_work`

**DevelopmentalMilestone:**
- `id`, `child_id`, `date`
- `category` ("cognitive" | "emotional" | "social" | "physical" | "language")
- `description`, `notes`

### Zones of Regulation Reference

| Zone | Color | Meaning | Examples |
|------|-------|---------|----------|
| Blue | Blue | Low energy, sad, tired | Bored, sick, exhausted, withdrawn |
| Green | Green | Calm, focused, happy | Ready to learn, content, relaxed |
| Yellow | Yellow | Elevated, anxious, silly | Frustrated, nervous, excited, wiggly |
| Red | Red | Extreme emotions | Angry, terrified, elated, out of control |

### Analytics

- **Mood trends:** Zone distribution over time, average intensity, most common emotions
- **Conflict patterns:** Frequency per time period, common triggers, resolution type distribution

---

## 7. Activities

**What it tracks:** Family events and outings, trip plans, activity suggestions, and family meeting agendas.

**Storage file:** `family_data/activities.json`

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_log_activity` | Record a family activity with rating and category |
| `parenting_get_activity_history` | Get activity history with optional filtering |
| `parenting_plan_trip` | Create a trip plan with dates, destination, activities, and packing list |
| `parenting_get_trip` | Get trip details by ID or list all trips |
| `parenting_suggest_activity` | Get activity suggestions based on children's ages and preferences |
| `parenting_create_family_meeting_agenda` | Auto-generate a family meeting agenda from recent data across all domains |

### Data Model Fields

**FamilyEvent:**
- `id`, `name`, `date`, `time` (optional), `location`
- `children_involved` (list[str] -- child IDs, empty = all)
- `category` ("outdoor" | "educational" | "social" | "creative" | "physical")
- `notes`, `rating` (1-5), `would_repeat` (bool)

**TripPlan:**
- `id`, `name`, `start_date`, `end_date`, `destination`
- `activities` (list[str]), `packing_list` (list[str])
- `behavior_plan` (str -- point system or expectations for the trip)
- `notes`, `active` (bool)

**ActivitySuggestion:**
- `id`, `name`, `category`, `age_range` (str, e.g. "5-10"), `description`
- `indoor_outdoor` ("indoor" | "outdoor" | "either")
- `energy_level` ("low" | "medium" | "high")
- `timestamp`

---

## 8. Financial

**What it tracks:** Allowance configuration with three-jar splits, financial transactions, and savings goals.

**Storage file:** `family_data/financial.json`

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_configure_allowance` | Set up allowance with weekly amount, jar split percentages, and pay day |
| `parenting_get_allowance` | Get allowance configuration for one or all children |
| `parenting_pay_allowance` | Process weekly allowance payment with automatic three-jar splits |
| `parenting_log_transaction` | Log a financial event (earned, spent, saved, given, gift received) |
| `parenting_get_financial_summary` | Get financial summary with jar balances |
| `parenting_set_savings_goal` | Create a savings goal with target amount and optional deadline |
| `parenting_get_savings_goals` | Get savings goals and progress for a child |

### Data Model Fields

**AllowanceConfig:**
- `child_id`, `weekly_amount` (float)
- `split_save_pct` (int, default 40), `split_spend_pct` (int, default 50), `split_give_pct` (int, default 10)
- `pay_day` (int -- 0=Monday through 6=Sunday, default Sunday)
- `model` ("commission" | "unconditional" | "hybrid")

**FinancialTransaction:**
- `id`, `child_id`, `timestamp`, `amount` (float, always positive)
- `type` ("allowance" | "earned" | "spent" | "saved" | "given" | "gift_received")
- `jar` ("save" | "spend" | "give" | None)
- `description`

**SavingsGoal:**
- `id`, `child_id`, `name`, `target_amount` (float), `current_amount` (float)
- `target_date` (optional), `status` ("active" | "reached" | "abandoned")
- `created_at`

### The Three-Jar System

The three-jar (or three-envelope) system divides each allowance payment into three categories:

| Jar | Default % | Purpose |
|-----|----------:|---------|
| **Save** | 40% | Money set aside for a larger goal |
| **Spend** | 50% | Money available for immediate use |
| **Give** | 10% | Money earmarked for charitable giving |

Split percentages are configurable per child and must sum to 100. The allowance model can be "commission" (earn by chores), "unconditional" (given regardless), or "hybrid" (base + commission).

---

## 9. Journal

**What it tracks:** Free-form parenting observations and reflections, tagged and filterable.

**Storage file:** `family_data/journal.json`

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_journal_entry` | Add a journal entry about a child or the family, with optional tags |
| `parenting_get_journal` | Retrieve journal entries filtered by child, recency, or tags |

### Data Model Fields

**JournalEntry:**
- `id` (str)
- `timestamp` (datetime)
- `child_id` (str, optional -- None for family-level entries)
- `content` (str) -- The journal entry text
- `tags` (list[str]) -- Categorization tags (e.g., "milestone", "concern", "win", "behavior", "medical")

---

## 10. Consultant

**What it provides:** Evidence-based parenting advice assembled from family context, developmental expectations, and curated research.

The consultant does not store its own data. It reads from all other domains and the knowledge base to assemble context for the calling LLM.

### MCP Tools

| Tool | Description |
|------|-------------|
| `parenting_consult` | Ask a parenting question -- assembles full family context, relevant research, developmental expectations, and safety checks |
| `parenting_weekly_summary` | Generate a cross-domain weekly summary with per-child behavior, routine, and emotional data |
| `parenting_get_age_expectations` | Get developmental expectations for a child's current age band |

### How It Works

1. **Topic detection** -- Maps question keywords to relevant knowledge files
2. **Family context** -- Loads full family profile with children's details
3. **Developmental context** -- Extracts age-band expectations from developmental_stages.md
4. **Knowledge loading** -- Reads matched evidence-based research documents
5. **Safety check** -- Scans for topics requiring professional referral (hard: crisis resources; soft: suggest professional consultation)

The assembled context is returned to the calling LLM, which uses it to generate a personalized, evidence-based response. The consultant does NOT call an LLM itself.

---

## Tool Count Summary

| Domain | Tools |
|--------|------:|
| Family | 5 |
| Behavior | 13 |
| Routines | 7 |
| Health | 7 |
| Education | 6 |
| Emotional | 6 |
| Activities | 6 |
| Financial | 7 |
| Journal | 2 |
| Consultant | 3 |
| **Total** | **62** |
