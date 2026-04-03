# OpenAuntie — Repo Instructions

## What This Is

OpenAuntie is an evidence-based parenting consulting agent. It provides practical tools (behavior tracking, routines, health, education, emotional development, finances) and a collaborative parenting consultant grounded in peer-reviewed research.

## Architecture

```
src/parenting/           Core library — Pydantic v2 models, stateless services, JSON storage
  models/                11 model files, 26 Pydantic types (source of truth for all domains)
  services/              12 stateless services (~3,500 LOC), one per domain
  storage/               Atomic JSON file persistence (store protocol + JsonStore impl)
  cli.py                 CLI entry point (setup, consult, summary, export)
mcp_server/              Single FastMCP server — 71 tools, all parenting_* prefixed
knowledge/               15 evidence-based reference documents with citations
adapters/                Platform config generators (Claude Desktop, Code, Codex, OpenClaw, ChatGPT)
  generate.py            Generator script — run: uv run python -m adapters.generate --all
  manifest.py            Single source of truth for tool definitions
  output/                Generated output (gitignored — contains machine-specific paths)
tests/                   13 test files, 181 tests (pytest)
docs/                    Setup guides (6), user guides (8), examples (5), reference docs
```

## Domains (all fully implemented)

| Domain | Model | Service | MCP Tools | Tests |
|--------|-------|---------|-----------|-------|
| Family | `family.py` | `family_service.py` | 4 tools | `test_family_service.py` |
| Behavior & Rewards | `behavior.py` | `behavior_service.py` | 13 tools | `test_behavior_service.py` |
| Routines | `routines.py` | `routine_service.py` | 7 tools | `test_routine_service.py` |
| Health | `health.py` | `health_service.py` | 7 tools | `test_health_service.py` |
| Education | `education.py` | `education_service.py` | 6 tools | `test_education_service.py` |
| Emotional | `emotional.py` | `emotional_service.py` | 6 tools | `test_emotional_service.py` |
| Activities | `activities.py` | `activity_service.py` | 6 tools | `test_activity_service.py` |
| Financial | `financial.py` | `financial_service.py` | 7 tools | `test_financial_service.py` |
| Journal | `journal.py` | `journal_service.py` | 2 tools | `test_journal_service.py` |
| Consultant | — | `consultant_service.py` | 3 tools | `test_consultant_service.py` |
| Research | `research.py` | `research_service.py` | 5 tools | `test_research_service.py` (in test_feedback) |
| Feedback | `feedback.py` | `feedback_service.py` | 5 tools | `test_feedback_service.py` |

## Key Conventions

- All MCP tool names start with `parenting_`
- Every knowledge base claim must have: source citation, evidence grade (STRONG/MODERATE/EMERGING/CONSENSUS), last-reviewed date
- The consultant personality is "Auntie" — warm, honest, non-judgmental, collaborative coach
- The consultant assembles context for the calling LLM; it does NOT call an LLM internally
- Safety boundaries: never diagnose, never prescribe, always suggest professional help when appropriate
- `family_data/` is .gitignored — contains PII, never committed
- `adapters/output/` is .gitignored — contains machine-specific generated paths
- v1 is local-first, single-family, single-writer

## Technology

- Python 3.11+, UV, Pydantic v2, Ruff, Black, mypy (strict)
- `pyproject.toml` is source of truth
- `uv run` for all execution
- JSON files per domain for storage (atomic writes via temp file + os.replace)

## Testing

```bash
python -m py_compile <file>     # Syntax
uv run mypy src/                # Types
uv run ruff check .             # Lint
uv run pytest tests/ -v         # Tests (181 tests across 13 files)
```

## Generating Adapter Configs

```bash
uv run python -m adapters.generate --all          # All platforms
uv run python -m adapters.generate claude-desktop  # Single platform
```

Output goes to `adapters/output/` (gitignored). Users must regenerate for their own paths.

## Learned Lessons

- Make privacy and safety architecture a Phase 0 deliverable before collecting family data or building adapters; define storage boundaries, PII handling, and parent-facing disclosures up front.
- Document platform capability differences explicitly; separate advice-only adapters from full local-tracking setups in prompts, setup guides, and FAQs.
- Generated adapter output files must never be committed — they embed machine-specific absolute paths. Keep `adapters/output/` in `.gitignore`.
- If this repo uses package-level `__init__.py` exports for models or services, keep those re-exports synchronized with the actual implemented modules.

## LLM Anti-Patterns

- Parent-facing privacy copy must be platform-qualified: do not say data 'stays on your device' or is 'never sent anywhere' without also stating that the chosen AI platform may process conversation context.
