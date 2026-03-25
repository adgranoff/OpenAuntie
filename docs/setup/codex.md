# Setting Up OpenAuntie with Codex

**For developers who use OpenAI's Codex CLI.**

## Setup

```bash
# Clone the repo
git clone https://github.com/adgranoff/OpenAuntie.git
cd openauntie

# Install dependencies
uv sync

# Generate Codex config
uv run python -m adapters.generate codex

# Add the MCP server to your Codex config (~/.codex/config.toml):
cat adapters/output/codex/config_entry.toml >> ~/.codex/config.toml

# Add the agent description to your AGENTS.md:
cat adapters/output/codex/AGENTS_entry.md >> ~/.codex/AGENTS.md
```

## Usage

```bash
codex exec "How many points does Max have?"
codex exec --full-auto "Set up a bedtime routine for Emma with 4 steps"
```
