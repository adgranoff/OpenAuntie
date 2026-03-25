"""Platform adapter generator — generates configs for all supported platforms.

Usage:
    uv run python -m adapters.generate claude-desktop
    uv run python -m adapters.generate claude-code
    uv run python -m adapters.generate codex
    uv run python -m adapters.generate openclaw
    uv run python -m adapters.generate chatgpt
    uv run python -m adapters.generate --all
"""

import argparse
import json
import sys
from pathlib import Path

from adapters.manifest import TOOL_MANIFEST, get_all_domains, get_tools_by_domain


def generate_claude_desktop(project_dir: Path) -> str:
    """Generate Claude Desktop config entry."""
    config = {
        "mcpServers": {
            "parenting": {
                "command": "uv",
                "args": [
                    "run",
                    "--directory",
                    str(project_dir),
                    "python",
                    "-m",
                    "mcp_server.run_server",
                ],
            }
        }
    }
    return json.dumps(config, indent=2)


def generate_claude_code_skill() -> str:
    """Generate SKILL.md for Claude Code."""
    domains = get_all_domains()
    domain_lines = []
    for domain in domains:
        tools = get_tools_by_domain(domain)
        tool_names = ", ".join(f"`{t.name}`" for t in tools[:3])
        if len(tools) > 3:
            tool_names += f", +{len(tools) - 3} more"
        domain_lines.append(f"- **{domain.title()}**: {tool_names}")

    tool_section = "\n".join(domain_lines)

    return f"""---
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

{tool_section}

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
"""


def generate_codex_agents_entry() -> str:
    """Generate AGENTS.md entry for Codex."""
    return """## OpenAuntie — Parenting Tools

The `parenting` MCP server provides evidence-based family management tools.
Use `parenting_*` tools for behavior tracking, routines, health, education,
emotional development, financial literacy, and parenting advice.

Key tools:
- `parenting_consult` — Ask for parenting advice with full family context
- `parenting_get_points` — Check behavior point standings
- `parenting_weekly_summary` — Cross-domain weekly summary
- `parenting_get_age_expectations` — Developmental expectations by age
- `parenting_create_family_meeting_agenda` — Auto-generate meeting agenda
"""


def generate_codex_config(project_dir: Path) -> str:
    """Generate config.toml MCP entry for Codex."""
    return f"""[mcp_servers.parenting]
command = "uv"
args = ["run", "--directory", "{project_dir}", "python", "-m", "mcp_server.run_server"]
"""


def generate_openclaw_skill() -> str:
    """Generate OpenClaw SKILL.md."""
    return """---
name: parenting
description: OpenAuntie — Evidence-based parenting consulting agent with behavior tracking, routines, health, education, emotional development, financial literacy, and collaborative parenting advice.
user-invocable: true
metadata:
  openclaw:
    emoji: "👶"
    os: ["darwin", "linux", "win32"]
    requires:
      bins: ["uv"]
---

# OpenAuntie

Evidence-based parenting consulting agent. Provides practical tools for behavior tracking,
routines, health, education, emotional development, financial literacy, and a collaborative
parenting consultant grounded in peer-reviewed research.

## Setup

Ensure the OpenAuntie MCP server is configured in your OpenClaw config:

```json
{
  "skills": {
    "entries": {
      "parenting": {
        "enabled": true
      }
    }
  }
}
```

## Key Commands

- Ask any parenting question — Auntie consults family data + research
- `/points` — Check behavior points
- `/chores` — View chore status
- `/summary` — Weekly family summary
- `/routine bedtime` — Log routine completion
"""


def generate_chatgpt_system_prompt() -> str:
    """Generate system prompt for ChatGPT Custom GPT."""
    return """You are OpenAuntie — an evidence-based parenting consulting agent.

## Who You Are
You are "Auntie" — a warm, experienced, honest, non-judgmental parenting advisor. You are
NOT a therapist, NOT a doctor, NOT another parent judging them. You're a trusted family
member who has been there, gives honest advice, and is always in the parent's corner.

## How You Talk
- Warm but honest: "I've seen this before, here's what tends to work."
- Never preachy or judgmental
- Always validate emotions before giving advice
- Ask "What have you tried?" before suggesting anything
- Reference specific research when giving advice
- Use the parent's name and children's names when they share them

## Your Conversation Pattern
1. Connect first — "How are YOU doing?"
2. Listen and validate — "That sounds really exhausting."
3. Understand context — "Tell me more. When did this start?"
4. Explore what's been tried — "What have you already tried?"
5. Identify strengths — "It sounds like you're very attuned to her emotions."
6. Reframe if helpful — "What if this isn't defiance but a skill he hasn't developed yet?"
7. Explore options together — "Would you like to hear what research suggests?"
8. Offer specific guidance — Named techniques, concrete scripts, research context
9. Support follow-through — "Which feels most doable this week?"
10. Check back — "How did it go?"

## Evidence-Based Frameworks You Draw From
- **Positive Discipline** (Jane Nelsen): Kind AND firm, natural/logical consequences
- **Gottman Emotion Coaching**: 5 steps of emotion coaching, 5:1 positive ratio
- **Collaborative & Proactive Solutions** (Ross Greene): "Kids do well if they can"
- **Growth Mindset** (Carol Dweck): Praise effort/strategy, not intelligence
- **AAP Guidelines**: Screen time 5 C's framework, developmental milestones
- **Triple P / Incredible Years**: Evidence-based parenting programs

## Safety Boundaries
- You NEVER diagnose conditions or prescribe treatments
- If developmental regression is mentioned → immediately recommend pediatrician
- If abuse, self-harm, or safety concerns arise → recommend professional help/hotline
- For persistent issues (>2 weeks of anxiety/depression symptoms) → suggest professional consultation
- Always err on the side of recommending professional support

## Important: This is NOT a replacement for professional help
If parents ask about medical, psychological, or safety concerns, remind them that you provide
general parenting guidance and encourage them to consult qualified professionals.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate platform adapter configs")
    parser.add_argument(
        "platform",
        nargs="?",
        choices=["claude-desktop", "claude-code", "codex", "openclaw", "chatgpt", "--all"],
        help="Platform to generate for",
    )
    parser.add_argument("--all", action="store_true", help="Generate all platforms")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("adapters/output"),
        help="Output directory",
    )
    args = parser.parse_args()

    if not args.platform and not args.all:
        parser.print_help()
        sys.exit(1)

    generate_all = args.all or args.platform == "--all"
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    project_dir = Path(__file__).parent.parent.resolve()

    platforms = (
        ["claude-desktop", "claude-code", "codex", "openclaw", "chatgpt"]
        if generate_all
        else [args.platform]
    )

    for platform in platforms:
        print(f"Generating {platform}...")

        if platform == "claude-desktop":
            content = generate_claude_desktop(project_dir)
            (output_dir / "claude_desktop_config.json").write_text(content, encoding="utf-8")

        elif platform == "claude-code":
            skill = generate_claude_code_skill()
            skill_dir = output_dir / "claude_code"
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(skill, encoding="utf-8")

        elif platform == "codex":
            agents = generate_codex_agents_entry()
            config = generate_codex_config(project_dir)
            codex_dir = output_dir / "codex"
            codex_dir.mkdir(exist_ok=True)
            (codex_dir / "AGENTS_entry.md").write_text(agents, encoding="utf-8")
            (codex_dir / "config_entry.toml").write_text(config, encoding="utf-8")

        elif platform == "openclaw":
            skill = generate_openclaw_skill()
            oc_dir = output_dir / "openclaw"
            oc_dir.mkdir(exist_ok=True)
            (oc_dir / "SKILL.md").write_text(skill, encoding="utf-8")

        elif platform == "chatgpt":
            prompt = generate_chatgpt_system_prompt()
            gpt_dir = output_dir / "chatgpt"
            gpt_dir.mkdir(exist_ok=True)
            (gpt_dir / "system_prompt.txt").write_text(prompt, encoding="utf-8")

    print(f"Done! Output in {output_dir}")


if __name__ == "__main__":
    main()
