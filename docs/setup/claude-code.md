# Setting Up OpenAuntie with Claude Code

**For developers who use Claude Code CLI.**

## Setup

```bash
# Clone the repo
git clone https://github.com/adgranoff/OpenAuntie.git
cd openauntie

# Install dependencies
uv sync

# The .mcp.json in the repo root auto-configures the MCP server
# Claude Code will detect it when you run in this directory

# Or install globally:
uv run python -m adapters.generate --install claude-code
```

## Usage

```bash
# Start Claude Code in the repo directory
claude

# Or from anywhere with the global skill installed
claude
> "How many points does Max have?"
> "Log bedtime routine for Emma — all steps completed, no resistance"
```

## All Available Tools

Run `claude` and ask: "List all parenting tools"

Or check `adapters/manifest.py` for the complete tool manifest.
