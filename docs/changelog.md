# Changelog

All notable changes to OpenAuntie will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## v0.1.0 (2026-03-24) -- Initial Release

### Added

**Core System**
- 10 tracking domains: family, behavior, routines, health, education, emotional, activities, financial, journal, consultant
- 62 MCP tools covering all domains with full annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
- JSON file storage with atomic writes and versioned envelope format
- CLI entry point (`uv run parenting ...`)

**Knowledge Base**
- 15 evidence-based reference documents with full citations
- Evidence grading system (STRONG/MODERATE/EMERGING/CONSENSUS)
- Review dates on all claims
- Sources include: AAP, PubMed, Triple P, Positive Discipline, Gottman, CPS, Dweck, Deci & Ryan

**Parenting Consultant ("Auntie")**
- Collaborative coaching approach (GROW model, Motivational Interviewing, CPS)
- Context assembly engine -- loads family data + relevant research for each question
- Safety boundaries -- hard and soft referral triggers
- Topic detection -- matches questions to relevant knowledge files
- Age-appropriate developmental expectations

**Platform Support**
- Claude Desktop (recommended for non-technical parents)
- ChatGPT Custom GPT (no-code option with system prompt + knowledge upload)
- Claude Code CLI
- OpenAI Codex CLI
- OpenClaw
- Platform adapter generator (`uv run python -m adapters.generate --all`)

**Documentation**
- Setup guides for all supported platforms
- Getting started guide
- 5 worked examples (week-in-the-life, homework struggles, sibling fighting, screen time, new baby)
- Architecture and domain reference
- FAQ, privacy policy, evidence standards, contributing guidelines
- DISCLAIMER with clear boundaries

**Testing**
- 164 tests across all services and storage
- Coverage: family, behavior, routines, health, education, emotional, activities, financial, journal, consultant, storage
