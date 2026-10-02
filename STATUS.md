# Status

_Control file for the AI Project Runner. Detailed history stays in PROGRESS.md._

## Next step
The text queue is paused after the Katha (CLAUDE.md section 10). Do not add or annotate new texts.
Work the plan instead: reviewed starter collection, then comparative testing (see `tests/README.md`
and `PROGRESS.md`). Items that need a human reader of Sanskrit are listed at the end of `PROGRESS.md`.
- After each change: `build_gita.py`, then `validate.py --allow-incomplete`.

## Done recently
- Vidura Niti complete (557 verses), strict validation passing.
- Chanakya Niti registration backed out (review cycle 1): it broke the queue pause. The source choice
  is kept in DECISIONS.md; the work is in git history (commit 3a8a202).

## Runner notes
_(the runner writes here if it has to stop the project)_
