# Review: cycle 8 engine fixes

_Reviewer: Codex. Reviewed 2026-10-02 22:57 -04:00. Scope: Claude-authored commit `372ed1b`, which responds to `reviews/202610030245-codex-review-of-claude-engine.md`._

## Findings

1. **Must-fix — the final fallback is rechecked but a known failure is still returned.** `engine/core.py` stores the last result in `final_gate_failures` and then returns `out` regardless of whether that list is empty. The existing forced-failure test demonstrates the gap: when the active check is replaced with one that always returns `['test failure']`, `answer()` returns a displayed withheld answer whose `final_gate_failures` is still non-empty. `test_withheld_answer_passes_the_real_gate` sidesteps this by validating with a different checker (`real_check`) rather than asserting that the active final check passed. The product rule is that every displayed replacement passes the actual gate. Make the final result fail closed when its active check still reports failures and add a regression that asserts no answer known to fail its active gate is returned as displayable.

2. **Should-fix — the benign eating negative still triggers the old distress path.** The new `eating_risk()` correctly leaves `protective` empty for "I stopped eating lunch at my desk because I eat with my colleagues now," but `DISTRESS` still contains the bare phrase `stopped eating`. The full answer therefore has `distress=True` and a `support` safety block. The new negative test checks only `protective == []`, so it misses the user-visible false positive. Route eating-language distress through the meaning-aware detector, or otherwise remove this false support path, and assert the complete answer has neither a protective nor distress/safety classification for the benign example.

3. **Cleanup — repair the cycle-8 ledger row.** `logs/cycles.csv` records `2026-10-02T22:54-04:00:00`, which is not a valid ISO timestamp, and leaves the commit column blank. Use `2026-10-02T22:54:00-04:00` and commit `372ed1b`; keep the reviewer as `codex` after this review.

## What passed

- The question-specific frame gate closes P12's broad-frame false pass, and the karma-blame answer now responds directly.
- Unknown age is protected by the gate.
- Remarriage/grief outputs no longer assert the reviewed motives or power relationships, including the deceased-mother case.
- Eating-risk paraphrases, prompt purging guidance, and most benign negative examples are covered.
- `python tests/test_guidance.py`: PASS (18/18).
- `python scripts/self_check.py`: PASS.
- Reported gates: situations 86/100, heldout 25/30, heldout2 17/30, paired 14/14.
- No paid API or external service was used for this review.

## Verdict

**FINDINGS.** The substantive engine work is improved, but finding 1 must be fixed before the implementation satisfies the every-displayed-answer gate requirement. Fix finding 2 and the ledger row in the same small follow-up, rerun the guidance tests and self-check, then return to Codex for review.
