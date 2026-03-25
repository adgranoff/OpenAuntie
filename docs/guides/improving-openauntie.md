# How OpenAuntie Improves Over Time

OpenAuntie has two systems that help it get better at helping your family:

1. **Research Watchlist** — stays up-to-date with new parenting research
2. **Parent Feedback** — learns what works specifically for YOUR kids

---

## Research Watchlist

Parenting research is always evolving. OpenAuntie monitors trusted sources for new findings:

- PubMed (peer-reviewed journals)
- American Academy of Pediatrics (AAP)
- CDC developmental guidelines
- WHO recommendations
- Major psychology journals

### How It Works

When new research is found that's relevant to OpenAuntie's knowledge base, it creates a **proposal** — not an automatic update. A human reviews every proposed change before it's applied.

This matters because OpenAuntie gives advice about your children. We don't want an automated system changing advice without careful review.

**To check for research updates:**
> "Are there any new research updates for OpenAuntie?"

**To see pending proposals:**
> "Show me the research update proposals"

### For Contributors

If you find new parenting research that should be included:

> "Add a research proposal: A 2026 study in [Journal] found that [finding]. This is relevant to [knowledge file]. The proposed change is [what should be updated]."

See [docs/reference/evidence-standards.md](../reference/evidence-standards.md) for citation format and evidence grading.

---

## Parent Feedback Loop

Every family is different. A technique that works brilliantly for one child might not work for another. OpenAuntie tracks what works for YOUR family.

### Rating Advice

After trying a technique Auntie suggested, let her know how it went:

> "The logical consequences approach worked great for homework with Emma — I'd rate it 5 out of 5"

Or:

> "We tried the reward chart for bedtime with Max but it actually made things worse — 2 out of 5"

### What OpenAuntie Tracks

For each rating, OpenAuntie records:
- **Which child** — techniques work differently for different kids
- **Which technique** — the specific approach you tried
- **The context** — homework, bedtime, sibling conflict, etc.
- **The setting** — calm weekend vs. rushed school morning
- **How well it worked** — 1 (made worse) to 5 (worked great)
- **Your confidence** — how sure you are about the rating
- **Whether you used it as described** — did you follow the approach fully?
- **How long you tried** — one time, a few days, a week, ongoing

### How Auntie Uses Your Feedback

When you ask for advice, Auntie now considers your family's track record:

> "For Emma during homework, logical consequences have worked well for you (4.5/5 average across 6 tries). Reward charts haven't been as effective (2/5 across 2 tries — though that's a small sample). Let's lean into what's working."

### Important: Research Still Comes First

Your feedback never overrides research evidence. If research says a technique is effective but it's not working for your family, Auntie will:

1. First check if the implementation might need adjusting
2. Then offer alternative evidence-based approaches
3. Never force a technique that consistently fails for your family

### Checking Your Insights

> "What techniques work best for Emma?"

> "Show me the feedback history for bedtime approaches"

> "What's our family's experience with emotion coaching?"

---

## Privacy

- Your stored feedback data stays on your device — OpenAuntie never sends it anywhere. Your conversation messages are processed by the AI provider (like Claude or ChatGPT) — the same as any other AI chat.
- No data is shared with other families in v1
- You can delete feedback anytime: just delete `family_data/feedback.json`

---

## Tips for Better Feedback

1. **Rate after trying for a few days** — one-time results aren't reliable
2. **Be honest** — if something didn't work, say so. That helps Auntie suggest better alternatives
3. **Note the context** — "worked on Saturday but not on school nights" is more useful than just a number
4. **Rate even when things work** — positive feedback is just as valuable as negative
5. **Update over time** — what works at age 6 might not work at age 8
