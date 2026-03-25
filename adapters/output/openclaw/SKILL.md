---
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
