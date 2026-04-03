# OpenAuntie

**The trusted auntie every parent deserves** — your AI-powered parenting partner, grounded in real research, that tracks your family's day-to-day, spots patterns, and gives research-grounded guidance adapted to each child's developmental stage.

Not a therapist. Not another parent judging you. A knowledgeable family member who's been there, gives honest advice, and helps you keep track of everything.

> **Important:** OpenAuntie provides general parenting information, not medical or psychological advice. Always consult qualified professionals for concerns about your child's health, development, or safety. See [DISCLAIMER.md](DISCLAIMER.md).

---

## What OpenAuntie Does

### Practical Tracking Tools
- **Behavior & Rewards** — Point systems, chore tracking, consequence logging, 5:1 positive ratio monitoring
- **Routines** — Morning/bedtime/homework routines with streak tracking and regression detection
- **Health** — Medication tracking, appointment scheduling, growth records
- **Education** — Reading logs, homework struggle tracking, learning goals with growth mindset integration
- **Emotional Development** — Mood tracking (Zones of Regulation), conflict patterns, developmental milestones
- **Family Activities** — Trip planning (like cruise point systems!), activity suggestions, family meeting agendas
- **Financial Literacy** — Three-jar allowance system (save/spend/give), savings goals

### The Parenting Consultant ("Auntie")
Ask any parenting question and get personalized, evidence-based guidance:
- Knows your family (children's ages, temperaments, strengths, challenges)
- References peer-reviewed research (Triple P, Positive Discipline, Gottman, CPS, growth mindset)
- Follows a collaborative coaching approach — asks "what have you tried?" before suggesting
- Generates weekly summaries, proactive intervention suggestions, and family meeting agendas
- Includes safety boundaries — suggests professional help when appropriate

> **Note:** The ChatGPT setup gives you Auntie's evidence-based advice and research library. For the full tracking experience (behavior points, routine streaks, mood patterns, weekly summaries), use the Claude Desktop setup.

### Evidence-Based Knowledge Base
15 curated reference documents with full citations and evidence grading:
- Every claim includes source, evidence grade (STRONG/MODERATE/EMERGING/CONSENSUS), and review date
- Covers developmental stages, positive discipline, emotion coaching, homework research, screen time guidelines, sibling dynamics, financial literacy, and more

---

## Quick Start

**Two ways to use OpenAuntie:**
- **Quick start (no installs):** Use ChatGPT for evidence-based parenting advice powered by our research library
- **Full experience (some setup):** Use Claude Desktop for advice PLUS tracking tools (points, routines, moods, and more)

### ChatGPT (Easiest — no installs needed)

Follow our [ChatGPT setup guide](docs/setup/chatgpt.md) — it takes about 10-15 minutes and doesn't require any programming.

1. Download the ZIP from GitHub
2. Create a Custom GPT and paste the system prompt
3. Upload the 15 research files from the `knowledge/` folder

You get a parenting consultant with 80% of the value — no tracking tools, but excellent advice.

<details>
<summary>Full-featured setups (Claude Desktop, CLI, developer tools)</summary>

### Claude Desktop (Full experience — some setup required)

1. **Install Claude Desktop** from [claude.ai/download](https://claude.ai/download)
2. **Install UV** (Python package manager):
   - Mac/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: Download from [astral.sh/uv](https://astral.sh/uv)
3. **Download OpenAuntie**: `git clone https://github.com/adgranoff/OpenAuntie.git`
4. **Add to Claude Desktop config** (Settings > Developer > Edit Config):
   ```json
   {
     "mcpServers": {
       "parenting": {
         "command": "uv",
         "args": ["run", "--directory", "/path/to/openauntie", "python", "-m", "mcp_server.run_server"]
       }
     }
   }
   ```
5. **Restart Claude Desktop** — the hammer icon appears
6. **Say**: "Help me set up my family profile"

See the [full Claude Desktop setup guide](docs/setup/claude-desktop.md) for detailed walkthrough.

### Command Line

```bash
git clone https://github.com/adgranoff/OpenAuntie.git
cd openauntie
uv run parenting setup --family-name Smith --parent-name Sarah
uv run parenting consult "My 7-year-old won't do homework without a fight"
```

See [docs/setup/](docs/setup/) for detailed guides for all platforms.

</details>

---

## Supported Platforms

| Platform | Tracking Tools | Consultant | Setup Difficulty | Best For |
|----------|:-:|:-:|:-:|---|
| **ChatGPT** (Custom GPT) | No* | Yes | Easiest | Non-technical parents who want advice |
| **Claude Desktop** | Yes | Yes | Some setup | Parents who want the full experience |
| **claude.ai** (Web) | Yes** | Yes | Moderate | Parents comfortable with some tech |
| **Claude Code** | Yes | Yes | Developer | Developers |
| **OpenAI Codex** | Yes | Yes | Developer | Developers |
| **OpenClaw** | Yes | Yes | Developer | Developers |
| **CLI** | Yes | Yes | Developer | Developers |

\* ChatGPT gets the knowledge base and consultant but not real-time tracking tools
\** Requires hosting the MCP server remotely

---

## Research Foundation

OpenAuntie's knowledge base draws from:

| Framework | Evidence Level | Key Researcher |
|-----------|:-:|---|
| Triple P — Positive Parenting | STRONG | Matthew Sanders |
| Incredible Years | STRONG | Carolyn Webster-Stratton |
| Parent-Child Interaction Therapy | STRONG | Sheila Eyberg |
| Positive Discipline | MODERATE | Jane Nelsen (Adler/Dreikurs) |
| Collaborative & Proactive Solutions | MODERATE | Ross Greene |
| Gottman Emotion Coaching | MODERATE | John Gottman |
| Growth Mindset | MODERATE | Carol Dweck |
| Self-Determination Theory | STRONG | Deci & Ryan |
| AAP Digital Media Guidelines | CONSENSUS | American Academy of Pediatrics |

---

## Contributing

We welcome contributions! See [docs/contributing.md](docs/contributing.md) for guidelines.

**Especially needed:**
- Knowledge base updates with new research citations
- Translations
- Platform adapter improvements
- Documentation and worked examples

---

## Privacy

Your family's stored data (points, routines, health records) is saved as files on your device. OpenAuntie itself never uploads these files. With the **full tracking setup** (Claude Desktop), relevant data snippets may be included in conversation messages sent to the AI provider to give personalized advice. With the **ChatGPT-only setup**, only what you type yourself is sent to OpenAI. For maximum privacy, use nicknames and avoid sharing sensitive medical details.

See [docs/privacy.md](docs/privacy.md) for the full privacy policy.

---

## Architecture

<details>
<summary>Technical details (for developers)</summary>

```
src/parenting/          Core Python library
├── models/             Pydantic v2 data models (source of truth)
├── services/           Business logic (stateless, testable)
└── storage/            JSON file storage (atomic writes)

mcp_server/             Single MCP server (71 tools)
knowledge/              15 evidence-based reference documents
adapters/               Platform config generators
docs/                   Setup guides, how-tos, examples
tests/                  Comprehensive test suite
```

**Key design decisions:**
- Family data stored locally as JSON files — relevant context may be included in AI conversations for personalized advice
- The consultant assembles context for the calling LLM — it does NOT call an LLM internally
- Every knowledge base claim has a source citation, evidence grade, and review date
- v1 is single-family, single-device, local-first

</details>

---

## License

MIT — see [LICENSE](LICENSE).
