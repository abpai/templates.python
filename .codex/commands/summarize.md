### Codex Session Notes

**Command**

* Run: `!summarize [slug]`

**Where to write**

* Path: `./.codex/sessions/[slug]-[date].md`
* `slug`: kebab-case from the session topic (ASCII, ≤40 chars, no spaces).
* `date`: `YYYY-MM-DD` in UTC.

**Update protocol (when `!summarize` is called)**

1. If the file doesn’t exist, create it with the template below and fill all placeholders.
2. Update `last_updated` to the current ISO timestamp.
3. Refresh **TL;DR** (≤120 words) to reflect the latest state.
4. Append a new entry to **Turn log** with: role, timestamp, what changed (bullets), key code refs/paths touched.
5. Extend **Actions taken**, **Decisions & rationale**, **Open questions**, **Next actions** as needed (dedupe; prefer edits over repetition).
6. Keep **Running summary** ≤ \~200 words; compress older detail into Turn log.
7. Never paste long code; reference files/functions/lines instead.

**Style rules**

* Be concise, factual, and action-oriented. No fluff.
* Prefer bullets over prose; present tense; avoid “I”.
* Use explicit file paths (`repo/file.py:func`), commands in single quotes, and UTC timestamps `[YYYY-MM-DD HH:MM]`.
* No PII, secrets, tokens, or full stack traces. Link or reference instead.
* Idempotent edits: do not duplicate prior bullets; update in place.
* Touch only files inside this repo; create directories if missing.

---

### Standard Template (fill all placeholders)

```
The most recent discussion I had with codex was the following. Please use these notes as informative context, so you can catch up and we can re-start the conversation accordingly.

topic: <short topic>
slug: <kebab-case-slug>
date: <YYYY-MM-DD> (UTC)
last_updated: <UTC ISO 8601>
participants: [user, assistant]

# TL;DR (≤120 words)
- <single concise summary capturing goal, current state, next critical step>

# User desires
- <succinct bullets of outcomes the user wants>

# Specifics of user desires (scope & constraints)
- <key constraints, definitions of done, non-goals, acceptance criteria>

# Actions taken (chronological)
1. [YYYY-MM-DD HH:MM] <what was done / command / artifact produced>
2. <next step> …

# Decisions & rationale
- [time] Decision: <decision>. Why: <brief reason/impact/tradeoffs>.

# Helpful hints about conversation & relevant code paths
- Path: <repo/path/file.py:func> — <why it matters>
- Command: '<cli args>' — <purpose>
- Link: <url> — <what it answers>

# Open questions / risks
- <unknown or risk> → <owner/next step to resolve>

# Next actions (checklist)
- [ ] <next concrete task> (owner, expected outcome)
- [ ] …

# Turn log (append-only)
- [YYYY-MM-DD HH:MM] role=assistant — <what changed in this turn; bullets>
- [YYYY-MM-DD HH:MM] role=user — <key asks/clarifications>

# With this context in mind, I have a follow up query:
<one crisp question or instruction that advances the work>
```
---
