# Review: Claude-authored guidance batch and follow-ups

_Reviewer: Codex. Reviewed 2026-10-02 22:33 -04:00. Scope: Claude-authored engine/gate work in `26017f4`, frame fixes in `0827628`, and self-check/lessons work in `4820333`. Codex-authored proposal-version changes in `26017f4` were excluded; Claude already reviewed those in `reviews/202610030025-claude-review-of-codex.md`._

## Findings

1. **Must-fix — the mandatory self-check can pass stale test results after a test command fails.** In `scripts/self_check.py:41-42`, the return code from `run_tests.py` is assigned but never checked, and the persistent ignored `tests/results/selfcheck/<set>.json` is read immediately. If a later run crashes before rewriting that file, the script reads the previous successful output and can print `SELF-CHECK PASSED`. That defeats CLAUDE.md section 14's commit gate. Remove each set's old output before invoking it, treat any nonzero return as a problem, and do not parse output from a failed command. Add a regression test that pre-populates stale passing JSON and makes the test command fail.

2. **Should-fix — the new audit cue also matches “auditorium.”** `engine/frames.py:104` uses `r"\baudit"`, so `detect_frames("I am anxious about giving a speech in the auditorium tomorrow.")` returns `['witness_wrong']`. This can boost duty-of-protection/honesty advice for an ordinary public-speaking question. Bound the cue to intended audit words (for example, audit/audits/auditor/audit report) and add a negative test for “auditorium.”

3. **Cleanup — remove the committed scratch helper.** `tests/results/_q.py` is a four-line ad hoc inspection script, not a test or result. Remove it; if this scratch location is intentional, ignore the exact path as is already done for `scripts/_q.py`.

## Verification

- `python scripts/self_check.py`: PASS as currently implemented.
- Reported gates: situations 86/100, heldout 24/30, heldout2 17/30, paired 14/14.
- The focused V028/V001/V024 behavior and gate retry/clarify/withhold flow are supported by `tests/test_guidance.py` and the paired cases.
- Frame changes improve the recorded spent-set regression without weakening the gate, but finding 2 shows missing negative coverage.
- No paid API or external service was used for this review.

## Verdict

**FINDINGS.** Fix finding 1 before relying on `self_check.py` as a commit gate. Fix finding 2 and remove the scratch file in the same small follow-up, rerun the self-check, then continue the loop.
