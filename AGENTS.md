# Instructions for Codex

Codex has two roles in Viveka (PROCESS.md): code and direction reviewer, and **stand-in builder**
while Claude Code is at its usage limit. The project rules in CLAUDE.md apply to Codex exactly as
they apply to Claude Code. Order of authority: the owner's latest approved decision, DECISIONS.md,
CONTEXT.md, PROCESS.md, STATUS.md.

## As stand-in builder (only when the runner hands over because Claude Code hit its limit)
1. Read STATUS.md (latest HANDOFF note first), CONTEXT.md, DECISIONS.md and CLAUDE.md.
2. Take the next step in STATUS.md. Build, then run `python scripts/build_gita.py` and
   `python scripts/validate.py --allow-incomplete`, and the tests. Commit and push only with the
   repo's configured GitHub no-reply identity.
3. Do not review your own work. Your cycles stay unreviewed until Claude Code is back.
4. Log the cycle in `logs/cycles.csv` with `builder` = `codex` and `reviewer` empty.
5. End your turn with a HANDOFF note at the top of the "Handoff" section of STATUS.md:
   date and time, builder `codex`, what you did, what is unfinished, commits, test results,
   and "Needs review by Claude Code".

## As reviewer
- Review only cycles built by Claude Code. Never review a cycle you built.
- Before reviewing, read PROJECT_BRIEF.md (if present), CONTEXT.md, DECISIONS.md, STATUS.md and the
  last 5 reviews. Save the review in `reviews/` and fill `reviewer` = `codex` for that cycle in
  `logs/cycles.csv`.

## Always
- Never read or import the AI Review Desk, and never copy outside text into STATUS.md, CONTEXT.md,
  CLAUDE.md, PROCESS.md, PROJECT_BRIEF.md or `reviews/` (CLAUDE.md section 11).
- Subscriptions only: no API keys, no paid services. Stop at usage limits and leave a HANDOFF note.
