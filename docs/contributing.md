# Contributing to OpenAuntie

Thank you for helping make OpenAuntie better for families everywhere.

## Ways to Contribute

### Report Issues
- Found a bug? Open a GitHub issue with steps to reproduce.
- Outdated research? Open an issue citing the newer source.
- Unclear documentation? Tell us what confused you.

### Improve the Knowledge Base

The knowledge base (`knowledge/`) is OpenAuntie's backbone. Every claim must be evidence-based and properly cited.

**Citation format:**
```
> [Claim text] [Author, Year, Publication] [Evidence Grade] [Reviewed: YYYY-MM]
```

**Evidence grades:**
| Grade | Meaning | Examples |
|-------|---------|---------|
| **STRONG** | Multiple RCTs, meta-analyses, systematic reviews | Triple P meta-analysis (55 studies), Cooper homework meta-analysis |
| **MODERATE** | Single RCTs, validated programs with positive outcomes | Positive Discipline RCT (258 parents), PCIT 2024 trial |
| **EMERGING** | Preliminary studies, small samples, promising but needs replication | Single correlational studies, pilot programs |
| **CONSENSUS** | Professional organization guidelines, expert consensus | AAP policy statements, APA position papers |

**Review process:**
1. Each knowledge file has a `Last reviewed:` date at the top
2. Claims should be reviewed annually
3. When updating, check if the source has been superseded by newer research
4. If contradictory evidence exists, note both sides

### Contribute Code

1. Fork the repository
2. Create a feature branch
3. Follow the coding conventions in `CLAUDE.md`
4. Add tests for new functionality
5. Run the test suite: `uv run pytest tests/ -v`
6. Submit a pull request

### Add Platform Adapters

Want to support a new AI platform? See `adapters/manifest.py` for the tool manifest and create a new adapter following the patterns in existing adapters.

## Code of Conduct

OpenAuntie is a project about supporting families. We expect all contributors to:

- Be respectful and constructive
- Prioritize child safety and wellbeing in all design decisions
- Acknowledge that parenting is culturally diverse — avoid one-size-fits-all assumptions
- Respect privacy — never commit example data containing real family information
