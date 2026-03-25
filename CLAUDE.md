# OpenAuntie — Repo Instructions

## What This Is

OpenAuntie is an evidence-based parenting consulting agent. It provides practical tools (behavior tracking, routines, health, education, emotional development, finances) and a collaborative parenting consultant grounded in peer-reviewed research.

## Architecture

- **Core library**: `src/parenting/` — Pydantic v2 models, stateless services, JSON storage
- **MCP server**: `mcp_server/` — single server exposing all tools with `parenting_` prefix
- **Knowledge base**: `knowledge/` — curated evidence-based reference documents with citations
- **Platform adapters**: `adapters/` — generates configs for Claude Desktop, Code, Codex, OpenClaw, ChatGPT
- **CLI**: `uv run parenting ...` — source-of-truth operations

## Key Conventions

- All MCP tool names start with `parenting_`
- Every knowledge base claim must have: source citation, evidence grade (STRONG/MODERATE/EMERGING/CONSENSUS), last-reviewed date
- The consultant personality is "Auntie" — warm, honest, non-judgmental, collaborative coach
- The consultant assembles context for the calling LLM; it does NOT call an LLM internally
- Safety boundaries: never diagnose, never prescribe, always suggest professional help when appropriate
- family_data/ is .gitignored — contains PII, never committed
- v1 is local-first, single-family, single-writer

## Technology

- Python 3.11+, UV, Pydantic v2, Ruff, Black, mypy
- `pyproject.toml` is source of truth
- `uv run` for all execution
- JSON files per domain for storage

## Testing

```bash
python -m py_compile <file>     # Syntax
uv run mypy src/                # Types
uv run ruff check .             # Lint
uv run pytest tests/ -v         # Tests
```
