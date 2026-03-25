# Setting Up OpenAuntie with OpenClaw

**For developers already using OpenClaw.** This guide covers adding the parenting skill, not setting up OpenClaw itself.

## Method 1: Drop-in Skill (Simplest)

```bash
# Generate the OpenClaw skill
cd /path/to/openauntie
uv run python -m adapters.generate openclaw

# Copy to your OpenClaw skills directory
cp -r adapters/output/openclaw ~/.openclaw/skills/parenting
```

The skill is loaded automatically at the next session start.

## Method 2: Extra Directory Config

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "load": {
      "extraDirs": ["/path/to/openauntie/adapters/output/openclaw"]
    }
  }
}
```

## Method 3: ClawHub (When Published)

```bash
clawhub install openauntie
```

## MCP Server Configuration

Add to `~/.openclaw/openclaw.json`:

```json
{
  "mcp_servers": {
    "parenting": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/openauntie", "python", "-m", "mcp_server.run_server"]
    }
  }
}
```

## Telegram Command Routing

If using OpenClaw with Telegram, add these routing rules to your workspace's SOUL.md:

```
- Messages starting with "points" → parenting_get_points
- Messages starting with "chores" → parenting_get_chores
- Messages starting with "ask " → parenting_consult
- Messages starting with "summary" → parenting_weekly_summary
```

## Cron Jobs

For daily point resets and morning briefings:

```bash
# Daily point reset at midnight
0 0 * * * uv run --directory /path/to/openauntie parenting points reset

# Weekly summary on Sunday at 8pm
0 20 * * 0 uv run --directory /path/to/openauntie parenting summary --days 7
```
