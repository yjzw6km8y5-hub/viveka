# Lessons

_The project's learning log (CLAUDE.md section 14). Every builder reads it at the start of a cycle.
Each failure found by tests, reviewers, the observer or the owner becomes one line here and, where it can
be tested, a permanent test case. Newest last. No user conversations are ever recorded here._

| Date | Lesson | Now enforced by |
|---|---|---|
| 2026-10-02 | A keyword match is not understanding: "why do bad things happen" got a principle about sharing credit because of the words "happen" and "people". | Gate: the recommendation must be backed by a recognised problem frame (`engine/gate.py`); V024, P11-P14 |
| 2026-10-02 | Distress is not grief. A teenager restricting food got a grief template; protective needs need concrete real-world steps (doctor; a trusted adult who is safe for them). | Protective block and gate check; V028, P01-P06 |
| 2026-10-02 | Never put words in the person's mouth: "you describe yourself as a householder" was our inference from "my husband". | Inference is labelled; gate rejects unquoted attributions; `tests/test_guidance.py` |
| 2026-10-02 | The same situation with different circumstances needs different advice: time since a loss, dependency, whose decision it is, danger. | Paired cases P07-P10; `context_adjustments` in `engine/core.py` |
| 2026-10-02 | A high average score hid 15 of 30 wrong recommendations. Report pass/fail per case; never average a failure away. | `scripts/run_tests.py` per-case gate table |
| 2026-10-02 | Rerunning a spent test set is regression evidence, not proof of improvement. Keep first runs, tag reruns, and get independently written cases. | `--tag before/after`; `tests/README.md` |
| 2026-10-02 | Long background jobs share the tools' usage limits: the verse check used up Codex's allowance and blocked a review. Run heavy jobs when reviews are not due, in capped chunks. | `verse_check.py run --max N` |
| 2026-10-02 | More than one builder works in this repo. Check `git log` before editing, keep attribution honest in HANDOFF notes, and never assume the working tree is only yours. | HANDOFF notes; `logs/cycles.csv` builder/reviewer |
| 2026-10-02 | Outside text (observer findings, context files) reaches instruction files only with the owner's own approval, even when routine decisions are delegated. The permission system enforces this. | `scripts/proposals.py`; CLAUDE.md section 11 |
| 2026-10-02 | A one-line wording rule can contradict the test it serves: a note saying suffering is not "deserved" would trip a check that forbids "deserve". Check new wording against existing expectations before tuning. | `forbid_text` checks in `data/tests/paired.json` |
