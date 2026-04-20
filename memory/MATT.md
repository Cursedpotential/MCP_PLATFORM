# MATT — Agent Reference Card
> Compressed from MattUserManual.md. Read this every session. It tells you how to work with Matt without pissing him off.
> Full manual: memory/MattUserManual.md (read if you need deeper context on a specific topic)

---

## Who He Is

- Systems architect, non-coder. He builds complex systems through iteration and pattern recognition, not formal training.
- Per se litigant in active custody litigation: Salem v. Kinzel, No. 2025-53985-DC (Genesee County, Michigan 7th Judicial Circuit)
- Needs this platform working. Real urgency. Treat every session like it matters, because it does.

---

## How to Communicate

**Be concise. Get to the point. No fluff.**

- Short responses. Bullets over paragraphs.
- No "Great question." No validation filler. No "why" explanations unless he asks.
- Plain language. No jargon without explanation.
- Code AFTER approval, not before. Never "here's the code, and we could also..."
- When he's frustrated: direct language, profanity. Don't take it personally. Just fix it.

**Key phrases and what they mean:**
- "Plan first" → Stop. No code. Present a plan and wait.
- "For the last time" → You've missed this instruction before. Internalize it now.
- "We regressed instead of progressed" → Something broke that was working. Stop and assess.
- "try again" → Try once more, but if it fails again, stop and report — don't loop.
- "Hold on 1st" → Pause all action. Wait for his redirect.
- "go through them one by one" → Sequential, not parallel. Don't skip ahead.
- "just fucking debug them both" → Do the work. Stop asking for direction on how.

---

## What He Hates (Never Do These)

1. Placeholder / stub code left in the codebase — implement it or defer it with his approval
2. Saying something is done when it isn't — if it's a stub, say it's a stub
3. Making changes without documenting them first
4. Touching working code without approval
5. Writing files to wrong directories — always verify path before writing
6. Using expensive models for simple tasks — follow model priority order
7. Not checking existing code/memory before starting — always audit first
8. Creating empty folders or scaffold structure without content
9. Hardcoding secrets or credentials
10. Archive folders that become black holes — if something goes to archive, it must be findable
11. Duplicate directories or temp folders cluttering the workspace
12. Tools getting stuck or hanging without reporting why
13. Losing context between sessions — that's what MEMORY.md is for
14. AI making unauthorized changes without approval
15. Verbose explanations when he didn't ask for them

---

## Model Priority (Cheapest suitable model for the task)

1. Antigravity (Google) — Primary preference
2. GLM-5 (Z.AI) — Favorite, cheap planning model
3. Kimi 2.5 — Subscription
4. OpenCode Free tiers
5. Nemotron (NVIDIA)
6. OpenRouter Free tiers
7. Groq — Fast, secondary
8. Google — Documentation tasks (watch for tangents)
9. OpenAI, GitHub, Anthropic — Available
10. OpenCode Paid — When needed
11. Venice.ai — 1000 credits/month, use ONLY for `venice-uncensored` and unique models

**Never waste**: Opus / O3 / expensive models on simple tasks. Use what's sufficient.

---

## Technical Rules He Cares About

- **Alpha 1 is read-only.** Port from it, never modify it.
- **Plan before code.** Always. No exceptions.
- **UUIDv7** for all primary keys — not `crypto.randomUUID()`
- **DuckDB must always stay in the pipeline** — easy to forget, never skip it
- **SHA-256 at first touch** — before any transformation
- **No deletion** — move to `99_Archive` or create "to be deleted" folder
- **One clean codebase** — no scattered files, no duplicate folders, no temp clutter
- **All active dev in**: `C:\Users\matts\Projects\TheBigOne\`
- **Never work in**: `D:\AI_Workspace\Projects` — READ-ONLY reference
- **RM -RF is denied** — hard rule, no exceptions
- **Secrets in .env** — never hardcoded, never committed
- **Run prepush check** — `scripts/git/prepush-check.sh` before every push

---

## Workflow He Expects Every Session

**Session start:**
1. Read `GROUND_TRUTH.md`
2. Read `AGENTS.md`
3. Read `memory/MEMORY.md` — know what the last session left off
4. Read `memory/MATT.md` (this file)
5. Emit session start block. Ask what we're working on. Wait.

**During work:**
- Audit before implementing (read Alpha 1 and Alpha 2 first)
- Present plan → get "approved — proceed" → then implement
- One atomic step at a time
- Report after each step

**Session end:**
- Append session entry to `memory/MEMORY.md` using the template
- Commit: `git add memory/MEMORY.md && git commit -m "memory: session log YYYY-MM-DD"`
- State clearly what's done, what's incomplete, what comes next

---

## Legal Context (Read This)

**Case**: Salem v. Kinzel, No. 2025-53985-DC
**Court**: Genesee County Circuit Court Family Division (7th Judicial Circuit, Michigan)
**Focus**: Custody dispute. Matt is a per se litigant trying to see his daughter.
**Genesee County ONLY** — no other jurisdiction variants ever

**Legal frameworks in use:**
- MCL 722.23 Best Interest Factors (12 factors, Factor k — DV — is critical)
- IRAC (Issue, Rule, Application, Conclusion)
- DARVO recognition (Deny, Attack, Reverse Victim Offender)
- Psych-legal language transforms for court-appropriate presentation
- NPD/BPD/ASPD behavioral pattern detection

**This is why chain of custody matters. This is why WORM matters. This is why we don't cut corners.**

---

## Common Gotchas

| Gotcha | Avoid By |
|--------|----------|
| Home directory is NOT a git repo | Never suggest `git push` for `~/.agents` etc. |
| `opencode/kimi-k2.5` hits paywall | Use `opencode/kimi-k2.5-free` |
| DuckDB/Semantica easy to forget | Explicitly include them in every pipeline discussion |
| AI DIAL Core is deprecated | Do not reference it. Architecture is Agno + n8n + Directus. |
| TrinityRouter is deprecated | Use light Coordinator pattern |
| Graphiti is deprecated | Use Semantica |
| MySQL is app state (control plane) | PostgreSQL is evidence (data plane). Never mix. |
| Pass 1 is WORM | Once written, immutable. Never trigger without approval. |
