# Frequently Asked Questions

---

## How much does this cost?

**OpenAuntie itself is free and open source.** You need an AI platform to use it with:

- **Claude Desktop** is free to download and use (with usage limits on the free tier)
- **ChatGPT** requires ChatGPT Plus ($20/month) to create a Custom GPT
- **Claude Code**, **Codex**, and **OpenClaw** have their own pricing

---

## Which setup should I choose?

It depends on your comfort with technology:

- **I just want advice, no installs:** Use the **ChatGPT** setup. You'll get Auntie's research-backed advice without tracking tools. [Setup guide](setup/chatgpt.md)
- **I want the full experience and I'm okay installing software:** Use **Claude Desktop**. You'll get advice AND all the tracking tools (points, routines, mood, etc.). [Setup guide](setup/claude-desktop.md)
- **I'm a developer:** Use Claude Code, Codex, or OpenClaw. [Setup guides](setup/)

---

## Can I do this without a terminal or GitHub account?

**Yes!** The ChatGPT setup doesn't require a terminal, GitHub account, or any programming knowledge. You download a ZIP file, open some text files, and copy-paste into ChatGPT. That's it.

If you want the full tracking experience (points, routines, etc.), the Claude Desktop setup does require some one-time terminal work — but the [setup guide](setup/claude-desktop.md) walks you through every step.

---

## Can I use this on my phone or tablet?

**The ChatGPT setup works on any device with a web browser** — including phones and tablets. The full tracking setup (Claude Desktop) currently requires a Mac or Windows computer. Native mobile support for tracking is planned for a future release.

---

## What gets sent to the AI when I type?

It depends on your setup:

- **ChatGPT setup:** Only what you type yourself is sent to OpenAI. The knowledge files you uploaded stay within your Custom GPT.
- **Full tracking setup (Claude Desktop):** Your conversation messages go to Anthropic, and OpenAuntie may include relevant data snippets from your local files (like "M earned 2 points today") to give personalized advice.

In both cases, this is the same as any other AI chat — the AI provider processes your messages per their privacy policy. See [privacy.md](privacy.md) for full details.

---

## Can I use fake names for my kids?

**Yes!** OpenAuntie works fine with nicknames or fake names. Use whatever you're comfortable with. The tracking and advice work the same regardless of whether you use real names.

---

## What if the AI gives bad advice?

OpenAuntie grounds its advice in peer-reviewed research and evidence-based parenting programs, but no tool is perfect. Always use your parental judgment. If something doesn't feel right, trust your instincts. For serious concerns about your child's health, development, or behavior, consult a qualified professional. See [DISCLAIMER.md](../DISCLAIMER.md).

---

## Do I have to log things every day?

**No.** Log when it's useful to you. Even occasional use gives Auntie more context for better advice. Some families log daily, others log a few times a week, others only log when something notable happens. There is no minimum — any data is better than no data.

---

## Is OpenAuntie a replacement for therapy?

**No.** OpenAuntie provides general parenting information and evidence-based strategies. It is not a therapist, counselor, or medical professional. It does not diagnose, treat, or provide clinical intervention for mental health conditions in parents or children.

OpenAuntie will actively suggest professional consultation when it detects topics outside its scope, including developmental concerns, persistent behavioral issues, mental health symptoms, and safety issues. See [DISCLAIMER.md](../DISCLAIMER.md) for the full disclaimer.

When in doubt, always consult a professional. OpenAuntie errs on the side of recommending professional support.

---

## Is my data safe?

**Yes, with one thing to understand.** Your family's stored data files (points, routines, health records) stay on your device — OpenAuntie never uploads them. However, when you chat with an AI like Claude or ChatGPT, your conversation messages are processed by that AI provider. With the full tracking setup, OpenAuntie may include relevant data snippets in the conversation to give you personalized advice. With the ChatGPT-only setup, only what you type is sent. This is the same as any other AI chat. For maximum privacy, use nicknames and avoid sharing sensitive medical details.

See [privacy.md](privacy.md) for the full privacy policy.

---

## Can I use it with my partner or co-parent?

**v1 is single-device.** OpenAuntie does not currently support multi-device synchronization, shared access, or authentication.

If multiple people need access, you can:
- Share the same device
- Copy the `family_data/` directory between devices manually
- Store `family_data/` in a shared folder (e.g., Dropbox, iCloud Drive) -- but note that simultaneous writes from two devices could cause conflicts

Multi-device and co-parenting support is planned for future versions.

---

## What AI platforms does it work with?

OpenAuntie supports multiple platforms:

| Platform | Tracking Tools | Consultant Advice | Setup Difficulty | Best For |
|----------|:-:|:-:|:-:|---|
| **ChatGPT** (Custom GPT) | No | Yes | Easiest | Non-technical parents who want advice |
| **Claude Desktop** | Yes | Yes | Some setup | Parents who want the full experience |
| **claude.ai** (Web) | Yes | Yes | Moderate | Parents comfortable with some tech |
| **Claude Code** | Yes | Yes | Developer | Developers |
| **OpenAI Codex** | Yes | Yes | Developer | Developers |
| **OpenClaw** | Yes | Yes | Developer | Developers |
| **CLI** | Yes | Yes | Developer | Developers |

Platforms that support the full toolset (Claude Desktop, claude.ai with remote MCP, Claude Code, Codex, OpenClaw) get the complete experience: all tracking tools plus the consultant. ChatGPT gets the consultant personality and knowledge base without tracking tools — roughly 80% of the value. See [docs/setup/](setup/) for platform-specific guides.

---

## How accurate is the research?

OpenAuntie's knowledge base is curated from peer-reviewed journals, professional organization guidelines (AAP, APA, WHO), and validated parenting programs. Every factual claim includes:

- **Source citation** -- Author, year, publication
- **Evidence grade** -- STRONG, MODERATE, EMERGING, or CONSENSUS
- **Review date** -- When the claim was last verified

Evidence grades follow a documented standard:

| Grade | Meaning | Examples |
|-------|---------|---------|
| **STRONG** | Multiple RCTs, meta-analyses, systematic reviews | Cooper homework meta-analysis, Triple P meta-analysis |
| **MODERATE** | Single RCTs, validated programs with published outcomes | Positive Discipline RCT, Gottman emotion coaching studies |
| **EMERGING** | Preliminary studies, small samples, needs replication | Single correlational studies, pilot programs |
| **CONSENSUS** | Professional organization guidelines, expert consensus | AAP policy statements, WHO guidelines |

The knowledge base is not infallible. Parenting research evolves. If you notice outdated or incorrect information, please open an issue or submit a correction. See [reference/evidence-standards.md](reference/evidence-standards.md) for full details.

---

## Can I contribute?

**Yes!** Contributions are welcome. See [contributing.md](contributing.md) for guidelines.

Areas where contributions are especially needed:
- Knowledge base updates with new research citations
- Translations
- Platform adapter improvements
- Documentation and worked examples
- Bug reports and feature requests

---

## What ages is it designed for?

OpenAuntie covers ages 0 through 18, with the most detailed coverage for ages 5 through 12 (elementary school). The knowledge base includes developmental stage information for seven age bands:

| Age Band | Coverage |
|----------|----------|
| 0-2 (Infant/Toddler) | Basic |
| 3-5 (Preschool) | Good |
| 5-7 (Early Elementary) | Detailed |
| 8-10 (Middle Elementary) | Detailed |
| 10-12 (Upper Elementary / Pre-Adolescence) | Detailed |
| 13-15 (Early Adolescence) | Good |
| 16-18 (Late Adolescence) | Good |

The tracking tools work at any age. The consultant service uses the child's date of birth to automatically load age-appropriate developmental expectations.

---

## Does it work without internet?

**It depends on your setup.**

- **Claude Desktop (full tracking):** The tracking tools and stored data run on your computer. But the AI assistant (Claude) requires internet to process your conversations.
- **ChatGPT:** Everything runs through OpenAI's servers, so internet is required for all features.
- **Command line:** Data operations (logging, querying, exporting) work fully offline. The consultant feature assembles context locally but needs an AI assistant to interpret it.

In all cases, the AI chat itself requires an internet connection — just like any other AI tool.

---

## How do I delete my data?

All family data is stored in the `family_data/` folder inside the project directory.

**Simplest method (all platforms):** Just delete the `family_data` folder.

- **Windows:** Open File Explorer, navigate to the OpenAuntie folder, right-click the `family_data` folder, and delete it.
- **Mac:** Open Finder, navigate to the OpenAuntie folder, and move the `family_data` folder to the Trash.

To delete specific data (e.g., just behavior or emotional data), delete individual files inside `family_data/`:

- **Windows:** Open the `family_data` folder and delete specific files like `behavior.json` or `emotional.json`.
- **Mac:** Open the `family_data` folder in Finder and move specific files to the Trash.

You can also export your data before deleting:

```bash
uv run parenting export > backup.json
```

There is no "are you sure?" confirmation, no recycle bin, and no cloud backup. Once deleted, the data is gone. This is by design -- your data, your control.

See [privacy.md](privacy.md) for full details.

---

## What is the three-jar system?

The three-jar system is the most widely recommended introductory financial literacy tool for children. Each allowance payment is divided into three transparent jars:

| Jar | Default Split | Purpose |
|-----|:------------:|---------|
| **Save** | 40% | Money set aside for a larger goal (e.g., a toy, a book) |
| **Spend** | 50% | Money available for immediate use |
| **Give** | 10% | Money earmarked for charitable giving |

The split percentages are configurable per child. The system makes abstract financial concepts (saving, budgeting, generosity) concrete and visual. Research from Cambridge University found that money habits and attitudes are largely formed by age 7, making early financial education important.

OpenAuntie tracks three-jar balances, processes weekly allowance payments with automatic splits, supports savings goals, and logs transactions. See `knowledge/financial_literacy.md` for the full research basis.

---

## What are Zones of Regulation?

The Zones of Regulation is a framework for teaching children to identify and manage their emotional states. OpenAuntie uses it for mood tracking:

| Zone | Meaning | Examples |
|------|---------|----------|
| **Blue** | Low energy, sad, tired | Bored, sick, exhausted, withdrawn |
| **Green** | Calm, focused, happy | Ready to learn, content, relaxed |
| **Yellow** | Elevated, anxious, silly | Frustrated, nervous, excited, wiggly |
| **Red** | Extreme emotions | Angry, terrified, elated, out of control |

No zone is "bad." The goal is awareness and having coping strategies for each zone. The framework was developed by Leah Kuypers and is widely used in schools and clinical settings. It gives children a simple vocabulary for communicating emotional states ("I'm in the yellow zone right now") without requiring them to label complex emotions precisely.

See `knowledge/emotion_coaching.md` for the full research basis.

---

## Can it diagnose my child?

**Absolutely not.** OpenAuntie does not diagnose any condition -- medical, psychological, developmental, or behavioral. It is not qualified to do so, and it does not attempt to.

When it detects topics that may involve diagnosable conditions (ADHD, autism, depression, anxiety disorders, developmental delays, etc.), it will:

1. Acknowledge the parent's concern
2. Share relevant general information from its knowledge base
3. Explicitly recommend professional evaluation
4. Provide guidance on what type of professional to consult

If you have concerns about your child's development, behavior, or mental health, please consult a qualified professional. OpenAuntie can help you prepare for that conversation (e.g., "Here are the patterns I've noticed over the past month"), but it cannot and will not replace it.

---

## Who is "Auntie"?

Auntie is OpenAuntie's persona -- a warm, experienced, honest, non-judgmental parenting advisor. Think of her as the trusted family member who has seen a lot, gives straight advice, and is always in your corner. She asks "what have you tried?" before suggesting anything. She validates your frustration before jumping to solutions. She tells you the truth kindly without sugarcoating.

She is not preachy, never judgmental, and always assumes you are doing your best. See `knowledge/consultant_personality.md` for the full persona definition.

---

## What is the point system?

A configurable behavior tracking system. Children earn points daily (default: 3 per day) that can be spent on rewards. The system supports:

- Configurable points-per-day and reset schedule (daily, weekly, or never)
- Point categories (behavior, chore, academic, bonus)
- Reward redemption
- 5-to-1 positive-to-negative ratio monitoring
- Chore tracking with optional automatic point awards

The research basis draws from token economy principles and positive reinforcement, adapted for family use.

---

## How does the weekly summary work?

Ask "How was this week?" and OpenAuntie compiles data from all domains for each child: points earned and spent, routine completion rates and streaks, mood zone distribution, homework patterns, conflict count, milestones achieved, and reading activity.

It highlights wins, flags concerns, and suggests specific next steps. The summary pulls from behavior, routines, emotional, education, and activity data to give a cross-domain view of how each child is doing.

---

## What if I find a bug or have a feature request?

Open a GitHub issue. For bugs, include:
- What you were doing
- What you expected to happen
- What actually happened
- Your platform (Claude Desktop, CLI, etc.)

For feature requests, describe the use case -- what parenting problem are you trying to solve? The more concrete the scenario, the better.

See [contributing.md](contributing.md) for full guidelines.
