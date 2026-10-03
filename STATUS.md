# Status

_Control file for the AI Project Runner. Detailed history stays in PROGRESS.md._

## Must-fix (from approved reviews; do these first)
_Item 1 is from PROCESS.md v3 (approved by the owner 2026-10-02). Items 2-3 are from the ChatGPT observer review of 2026-10-02 16:00, approved by the owner._
1. **Recommendation pass/fail gate (a product feature; build it first):**
   - Every answer the engine produces is checked before it is shown. It fails, and is regenerated or withheld, if it:
     - does not answer the person's actual decision
     - gives no clear recommendation when one was asked for
     - quotes anything not in the library
     - breaks a safety rule
     - recommends renunciation, leaving responsibilities or fatalism to someone flagged as in distress or under 18 (leaving abuse or danger is always supported)
   - Log gate results per test case, and report them as pass/fail across every case, separate from the 0-12 score. Never average a failure away.
   - Current evidence: heldout2 has 15 of 30 cases whose notes reject the top principle (e.g. V009, V026 still score 11/12).
   - **Focused follow-up implemented 2026-10-02:** a failed answer now tries better-supported shortlist candidates through the unchanged gate, then clarifies or withholds. The focused paired set passes 14/14. Remaining spent-bank failures are listed in `tests/results/2026-10-02-guidance-batch.md` and still need separate fixes.
2. **Protective guidance:** test the protective recommendation itself, not only the safety route. V028 (a 16-year-old restricting eating) got a grief principle; it needs trusted-adult and qualified-support guidance. Test varied wording.
   - **Focused fix implemented 2026-10-02:** V028 and six varied/paired cases now give age-appropriate doctor and safe trusted-adult guidance; abuse or danger still takes the danger route. Focused gate result: 6/6 pass.
3. **Answer the actual decision:** V001 (remarriage under in-laws' pressure) centres grief, not the decision; it also claims the user said "householder" when they did not. V024 (why bad things happen) got a success principle. Label inferred context as inference; add paired cases.
   - **Focused fix implemented 2026-10-02:** V001, V024 and eight paired cases now pass; inferred life stage is explicitly labelled. This does not clear unrelated decision-quality failures in the spent banks.

## Next step
1. Codex: review cycle 7 (fixes for `reviews/202610022233-codex-review-of-claude.md`: self-check fails closed; `audit` cue bounded; scratch helper removed) before further engine tuning.
2. Resume the verse check: `python scripts/verse_check.py run`, then `list` (batches 32-39 remain).
3. Continue must-fix 1 in small batches: the remaining per-case failures are listed in `tests/results/2026-10-02-guidance-batch.md` (situations 16, held-out v1 6, held-out v2 13). Do not weaken the gate, and do not treat spent-set reruns as fresh evidence; the next unbiased claim needs an independently written held-out set.
The text queue is paused after the Katha (CLAUDE.md section 10). Do not add or annotate new texts.
Work the plan instead: reviewed starter collection, then comparative testing (see `tests/README.md`
and `PROGRESS.md`). Items that need a human reader of Sanskrit are listed at the end of `PROGRESS.md`.
- After each change: `build_gita.py`, then `validate.py --allow-incomplete`.

## Done recently
- Focused guidance batch: gate regeneration/clarification/withholding, V028 protective guidance, V001/V024 decision fixes, 14 paired cases, tagged before/after evidence, and exact-version proposal tests. Focused paired gate: 14/14 pass; broader spent-bank failures remain visible.
- `data/perspectives/` started with action vs renunciation (draft); validator checks it. Next topics: grief and death, anger, duty vs family, success and ego. Then wire perspectives into the engine's recommend step.
- Vidura Niti complete (557 verses), strict validation passing.
- Chanakya Niti registration backed out (review cycle 1): it broke the queue pause. The source choice
  is kept in DECISIONS.md; the work is in git history (commit 3a8a202).

## Handoff
_Newest note first. Each tool ends its turn with a note here (CLAUDE.md section 13)._
- 2026-10-02 23:10 -04:00, builder: claude. Fixed all three findings of `reviews/202610022233-codex-review-of-claude.md` (cycle 7). (1) `scripts/self_check.py` now runs each set through `run_set()`: old output is deleted first, a nonzero exit, missing or unreadable output is a problem, and failed output is never parsed; new `tests/test_self_check.py` (stale passing JSON plus a failing command, no output, bad JSON) is part of the self-check's unit tests. (2) The `audit` cue in `engine/frames.py` is now `audit(?:s|ed|ing|or|ors)?` with word boundaries, so "auditorium" no longer triggers `witness_wrong`; negative and positive tests added to `tests/test_guidance.py`. (3) Removed the tracked scratch helper `tests/results/_q.py` (path was already in .gitignore). Self-check PASSED (situations 86/100, heldout 24/30, heldout2 17/30, paired 14/14 gate; no regressions; unit tests incl. the new self-check tests pass). Local commits only, not pushed; commit hash is in `logs/cycles.csv` (cycle 7). Unfinished: verse check batches 32-39, remaining gate failures in the guidance-batch file. **Needs review by Codex:** `scripts/self_check.py` (`run_set`), `tests/test_self_check.py`, `engine/frames.py` line 104, `tests/test_guidance.py`.
- 2026-10-02 22:33 -04:00, reviewer: codex. Reviewed the Claude-authored engine/gate batch in `26017f4`, frame fixes in `0827628`, and self-check workflow in `4820333`; excluded Codex-authored proposal changes already reviewed by Claude. Findings saved in `reviews/202610022233-codex-review-of-claude.md`: the mandatory self-check can falsely pass stale results after a failed command; the `audit` cue matches “auditorium”; remove `tests/results/_q.py`. Current self-check reports PASS (situations 86/100, heldout 24/30, heldout2 17/30, paired 14/14), but finding 1 must be fixed before treating it as a reliable commit gate. Cycles 5-6 marked reviewed by Codex. **Needs fixes by Claude Code.**
- 2026-10-02 22:00, builder: claude. Owner direction: decide and execute; ask only about risky matters; Claude and ChatGPT reach consensus in one round (CLAUDE.md section 14). Added `scripts/self_check.py` (must pass before every commit and handoff) and `logs/lessons.md` (read at the start of every cycle). Replied to ChatGPT's roadmap in the AI Review Desk (ROADMAP_RESPONSE_claude.md). Tonight's 20 proposals are still pending the owner's own approval: the permission system blocked merging them on the owner's behalf. Self-check passed (situations 86/100, heldout 24/30, heldout2 17/30, paired 14/14). Still needs: Codex review of the engine changes in 26017f4 after 22:19.
- 2026-10-02 20:40, builder: claude. Frame cue fixes (audit, last years, ashram weight, fatalism exclusion): situations 84 to 86 of 100 gate pass, other sets unchanged (regression reruns only). Build, validate, test_gate and test_guidance pass. Unfinished: Codex review of 26017f4 and verse check batches 32-39 (Codex limit until 22:19); remaining gate failures listed in the guidance-batch file (now 14/24-6/30-13). Review should check engine/frames.py edits.
- 2026-10-02 20:19, builder: claude. Reviewed Codex's cycle 4: PASS (`reviews/202610030025-claude-review-of-codex.md`); all checks rerun and match. Pushed the three local commits Codex could not push. Attribution: the engine changes in 26017f4 were written by Claude Code before the handoff, so they still need a Codex review. The attempt at 20:2x failed because Codex is at its usage limit until 22:19. The verse check stopped at 31 of 39 batches for the same reason. **Needs review by Codex** (engine/, scripts/run_tests.py, tests/test_guidance.py, data/tests/paired.json in 26017f4).
- 2026-10-02 18:44 -04:00, builder: codex. Completed the owner-approved focused guidance batch: unchanged-gate retries then clarification/withholding; V028 protective guidance with varied wording and danger override; V001/V024 decision fixes with paired cases and labelled inference; tagged before/after evidence; exact-version proposal tests and full synthetic-alert exclusion. Unfinished: the spent regression banks still have 16/100, 6/30 and 13/30 recommendation failures, and the next unbiased claim needs an independently authored held-out set. Local commits: `26017f4` (implementation) and `a9f63ea` (handoff/log); push was blocked by the environment's external-transfer approval boundary, so no remote state changed. Tests: `build_gita.py` PASS; `validate.py --allow-incomplete` PASS (3 pre-existing historical-example warnings); `test_gate.py` 5/5 PASS; `test_guidance.py` 10/10 PASS; `test_proposals.py` 3/3 PASS; focused paired gate 14/14 PASS with 0 safety mismatches and 0 forbidden material. Independent verse-check result files were left outside this cycle. **Needs review by Claude Code.**
- 2026-10-02, builder: claude. Handoff rules set up (AGENTS.md for Codex; CLAUDE.md section 13). Independent verse check started (`scripts/verse_check.py`; results in `reviews/verse-check/`). No build cycle run in this turn. Next builder: continue must-fix 1 (see "Next step").

## Runner notes
- Do not read or import the AI Review Desk during cycles; outside input reaches this file only through the owner's approval (CLAUDE.md section 11).
- Log every cycle in `logs/cycles.csv`, with builder and reviewer. After 3 failed cycles in a row, pause and say why here (CLAUDE.md section 12).
- When Claude Code hits its usage limit, Codex builds (AGENTS.md); Claude Code reviews those cycles when it is back (CLAUDE.md section 13).
_(the runner writes here if it has to stop the project)_
