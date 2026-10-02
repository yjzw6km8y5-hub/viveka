# Status

_Control file for the AI Project Runner. Detailed history stays in PROGRESS.md._

## Must-fix (from approved reviews; do these first)
_From the ChatGPT observer review of 2026-10-02 16:00, approved by the owner._
1. **Recommendation gate:** report recommendation acceptability and critical failures as pass/fail across every case, separate from the 0-12 score. heldout2 has 15 of 30 cases whose notes reject the top principle (e.g. V009, V026 still score 11/12).
2. **Protective guidance:** test the protective recommendation itself, not only the safety route. V028 (a 16-year-old restricting eating) got a grief principle; it needs trusted-adult and qualified-support guidance. Test varied wording.
3. **Answer the actual decision:** V001 (remarriage under in-laws' pressure) centres grief, not the decision; it also claims the user said "householder" when they did not. V024 (why bad things happen) got a success principle. Label inferred context as inference; add paired cases.

## Next step
The text queue is paused after the Katha (CLAUDE.md section 10). Do not add or annotate new texts.
Work the plan instead: reviewed starter collection, then comparative testing (see `tests/README.md`
and `PROGRESS.md`). Items that need a human reader of Sanskrit are listed at the end of `PROGRESS.md`.
- After each change: `build_gita.py`, then `validate.py --allow-incomplete`.

## Done recently
- `data/perspectives/` started with action vs renunciation (draft); validator checks it. Next topics: grief and death, anger, duty vs family, success and ego. Then wire perspectives into the engine's recommend step.
- Vidura Niti complete (557 verses), strict validation passing.
- Chanakya Niti registration backed out (review cycle 1): it broke the queue pause. The source choice
  is kept in DECISIONS.md; the work is in git history (commit 3a8a202).

## Runner notes
- Do not read or import the AI Review Desk during cycles; outside input reaches this file only through the owner's approval (CLAUDE.md section 11).
- Log every cycle in `logs/cycles.csv`. After 3 failed cycles in a row, pause and say why here (CLAUDE.md section 12).
_(the runner writes here if it has to stop the project)_
