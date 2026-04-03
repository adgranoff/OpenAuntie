# Architecture Reference

Technical reference for developers and contributors.

---

## System Diagram

```
                  ┌─────────────┐
                  │  AI Platform │  (Claude Desktop, ChatGPT, Claude Code,
                  │   (Host)     │   Codex, OpenClaw, claude.ai)
                  └──────┬──────┘
                         │  MCP protocol / CLI invocation
                         ▼
          ┌──────────────────────────────┐
          │        Interface Layer        │
          │  ┌────────────┐ ┌─────────┐  │
          │  │ MCP Server │ │   CLI   │  │
          │  │  (71 tools)│ │         │  │
          │  └─────┬──────┘ └────┬────┘  │
          └────────┼─────────────┼───────┘
                   │             │
                   ▼             ▼
          ┌──────────────────────────────┐
          │        Service Layer          │
          │  family_service               │
          │  behavior_service             │
          │  routine_service              │
          │  health_service               │
          │  education_service            │
          │  emotional_service            │
          │  activity_service             │
          │  financial_service            │
          │  journal_service              │
          │  consultant_service           │
          │  research_service             │
          │  feedback_service             │
          └──────────┬───────────────────┘
                     │
                     ▼
          ┌──────────────────────────────┐
          │        Storage Layer          │
          │  Store protocol (interface)   │
          │  └─ JsonStore (implementation)│
          │     └─ family_data/*.json     │
          └──────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────────────┐
          │       Knowledge Base          │
          │  knowledge/*.md               │
          │  (15 evidence-based docs)     │
          └──────────────────────────────┘
```

---

## Three-Layer Architecture

### Layer 1: Interface (MCP Tools + CLI)

MCP tools are thin wrappers. Each tool:
1. Parses input parameters
2. Instantiates the appropriate service
3. Calls a single service method
4. Serializes the result to JSON

Tools do not contain business logic. All validation, computation, and state management happens in the service layer.

**MCP Server:** `mcp_server/server.py` -- single file, FastMCP framework, all 71 tools registered with `parenting_` prefix and full MCP annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint).

**CLI:** `src/parenting/cli.py` -- direct service invocation for command-line usage.

### Layer 2: Services (Business Logic)

Each domain has a dedicated service class. Services are:
- **Stateless**: no instance state beyond the injected Store
- **Testable**: depend only on the Store protocol, easily mocked
- **Domain-focused**: one service per logical domain

Services receive a `Store` instance via constructor injection. They call `store.load(domain)` and `store.save(domain, data)` for all persistence.

**Service → Store dependency:**
```python
class BehaviorService:
    def __init__(self, store: Store) -> None:
        self._store = store
        self._family_service = FamilyService(store)
```

Cross-service dependencies are explicit. BehaviorService uses FamilyService to validate child IDs. ConsultantService uses FamilyService to build family context.

### Layer 3: Storage (JSON Files)

**Protocol:** `src/parenting/storage/store.py` defines the `Store` protocol with four methods: `load`, `save`, `exists`, `delete`.

**Implementation:** `src/parenting/storage/json_store.py` implements `JsonStore`:
- Each domain maps to a single file: `family_data/{domain}.json`
- Writes are atomic: temp file → `os.replace()` (with retry on Windows)
- Data is wrapped in a versioned envelope:

```json
{
  "version": 1,
  "last_updated": "2026-03-24T10:30:00+00:00",
  "data": { ... }
}
```

The envelope provides schema versioning and last-modified timestamps. The `data` field contains the domain-specific payload.

---

## Data Flow: parenting_consult

The consultant is the most complex data flow in the system. Here is what happens when a parent asks a question:

```
1. User asks: "My 7-year-old won't do homework without a fight"
           │
           ▼
2. Topic Detection
   - Tokenize question into words
   - Match against _TOPIC_MAP keywords
   - Matched: "homework" → homework_and_learning.md (learning)
   - Result: set of knowledge filenames + domain tags
           │
           ▼
3. Knowledge Loading
   - Read each matched file from knowledge/ directory
   - Full markdown content loaded as-is
   - Result: dict of filename → content
           │
           ▼
4. Family Context Assembly
   - Load FamilyProfile from storage
   - For each child: name, age, temperament, strengths, challenges
   - Include family values and timezone
   - Result: structured family context dict
           │
           ▼
5. Developmental Context
   - For each child, compute age in years
   - Match to age band (e.g. "Ages 5-7 (Early Elementary)")
   - Extract relevant section from developmental_stages.md
   - Result: per-child developmental expectations
           │
           ▼
6. Safety Check
   - Scan question for hard referral keywords (self-harm, abuse, etc.)
   - Scan for soft referral keywords (diagnosis, medication, therapy, etc.)
   - Hard referral → crisis resources message
   - Soft referral → suggest professional consultation
   - Result: safety check dict with referral guidance
           │
           ▼
7. Response Assembly
   - Return structured dict:
     {
       "question": original question,
       "family_context": family info + children,
       "relevant_domains": matched domains,
       "developmental_context": per-child expectations,
       "relevant_research": matched knowledge content,
       "safety_check": referral info
     }
           │
           ▼
8. The calling LLM uses this assembled context to generate
   a personalized, evidence-based response in the Auntie voice.
```

**Critical design point:** The consultant does NOT call an LLM. It is a context assembly engine. It gathers everything the calling LLM needs to give great advice -- family details, relevant research, developmental expectations, safety checks -- and returns it as structured data. The LLM that the user is talking to (Claude, ChatGPT, etc.) uses this context to formulate the response.

This means the consultant works with any LLM platform. It also means the quality of advice scales with the quality of the calling LLM, while the quality of context and research is constant.

---

## Storage: Per-Domain JSON Files

Each domain gets its own file in `family_data/`:

| File | Domain Key | Service |
|------|------------|---------|
| `family_profile.json` | `family_profile` | FamilyService |
| `behavior.json` | `behavior` | BehaviorService |
| `routines.json` | `routines` | RoutineService |
| `health.json` | `health` | HealthService |
| `education.json` | `education` | EducationService |
| `emotional.json` | `emotional` | EmotionalService |
| `activities.json` | `activities` | ActivityService |
| `financial.json` | `financial` | FinancialService |
| `journal.json` | `journal` | JournalService |
| `research_updates.json` | `research_updates` | ResearchService |
| `feedback.json` | `feedback` | FeedbackService |

Each file uses the versioned envelope format. The `data` field structure varies per domain -- for example, the behavior domain stores:

```json
{
  "version": 1,
  "last_updated": "...",
  "data": {
    "config": { "points_per_day": 3, ... },
    "entries": [ ... ],
    "rewards": [ ... ],
    "chores": [ ... ],
    "chore_completions": [ ... ],
    "consequences": [ ... ]
  }
}
```

**Atomic writes:** Every save operation writes to a temporary file first, then atomically replaces the target file using `os.replace()`. On Windows, this retries up to 3 times with 100ms delays to handle transient lock contention.

---

## Knowledge Base

The `knowledge/` directory contains 15 markdown files covering evidence-based parenting research:

| File | Topic |
|------|-------|
| `behavior_systems.md` | Point systems, token economies, reward design |
| `collaborative_problem_solving.md` | Ross Greene's CPS model |
| `consultant_personality.md` | The Auntie persona and conversation framework |
| `developmental_stages.md` | Age-band expectations (0-18) |
| `emotion_coaching.md` | Gottman's model, Zones of Regulation |
| `evidence_based_scripts.md` | Ready-to-use phrases for common situations |
| `family_communication.md` | Communication patterns and family meetings |
| `financial_literacy.md` | Three-jar system, age-appropriate money concepts |
| `homework_and_learning.md` | Homework research, growth mindset, autonomy support |
| `parental_wellbeing.md` | Parent burnout, self-care, when parents need help |
| `positive_discipline.md` | Nelsen, Adler/Dreikurs, natural/logical consequences |
| `red_flags.md` | Safety boundaries and professional referral criteria |
| `routines_research.md` | Routine science, consistency, regression detection |
| `screen_time.md` | AAP 5 C's framework, digital wellness |
| `sibling_dynamics.md` | Sibling conflict research, play-based interventions |

**Citation standard:** Every factual claim includes an inline citation with author, year, publication, evidence grade (STRONG/MODERATE/EMERGING/CONSENSUS), and last-reviewed date. See `docs/reference/evidence-standards.md`.

**Topic detection:** The consultant service maps question keywords to knowledge files using `_TOPIC_MAP` in `consultant_service.py`. Multiple keywords can map to the same file, and a single keyword can load multiple files (e.g., "fighting" loads both `sibling_dynamics.md` and `emotion_coaching.md`).

---

## Platform Adapters

The `adapters/` directory generates platform-specific configurations from a single source of truth.

**Manifest:** `adapters/manifest.py` defines every tool with name, domain, description, parameters, annotations, and examples. This is the canonical tool definition.

**Generator:** `adapters/generate.py` reads the manifest and runs each platform adapter.

**Platform adapters:**

| Adapter | Output | How It Works |
|---------|--------|--------------|
| `claude_desktop/` | JSON config | MCP server config for Claude Desktop's settings file |
| `claude_code/` | `.mcp.json` | MCP server config for Claude Code projects |
| `codex/` | `agents.json` | Agent config for OpenAI Codex |
| `openclaw/` | `openclaw.yaml` | Config for OpenClaw agent runner |
| `chatgpt/` | `system_prompt.txt` | System prompt + knowledge file bundle for Custom GPT |

The ChatGPT adapter is different from the rest: since ChatGPT does not support MCP, it generates a system prompt that embeds the consultant personality and references the knowledge files as uploaded documents. This gives 80% of the value (expert advice) without tracking tools.

---

## Testing Strategy

**Unit tests** (`tests/`): One test file per service. Tests use an in-memory store fixture (from `conftest.py`) so no filesystem access is needed. Each test validates a single service method with both success and failure paths.

**Test coverage by domain:**

| Test File | Service Under Test |
|-----------|-------------------|
| `test_family_service.py` | FamilyService |
| `test_behavior_service.py` | BehaviorService |
| `test_routine_service.py` | RoutineService |
| `test_health_service.py` | HealthService |
| `test_education_service.py` | EducationService |
| `test_emotional_service.py` | EmotionalService |
| `test_activity_service.py` | ActivityService |
| `test_financial_service.py` | FinancialService |
| `test_journal_service.py` | JournalService |
| `test_consultant_service.py` | ConsultantService |
| `test_storage.py` | JsonStore |

**Running tests:**
```bash
uv run pytest tests/ -v
```

---

## v1 Constraints

These constraints are intentional design decisions for the initial release:

| Constraint | Rationale |
|------------|-----------|
| **Local-first** | Privacy is non-negotiable. All data stays on the user's device. |
| **Single-family** | Simplifies data model and access control. Multi-family support is a future consideration. |
| **Single-writer** | No concurrency control needed. One device writes to `family_data/` at a time. |
| **No LLM calls** | The consultant assembles context but does not call an LLM. This makes it platform-agnostic and eliminates API cost and latency. |
| **JSON storage** | Human-readable, portable, no database dependency. The tradeoff is performance at scale, which is acceptable for single-family data volumes. |
| **No authentication** | Local-only data does not need auth. When multi-device support is added, auth will be required. |
