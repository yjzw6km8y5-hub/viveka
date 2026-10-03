_Reviewer: Codex (read-only run requested by Claude Code, 2026-10-02 22:36-22:47 -04:00). Scope: the Claude-authored engine, gate, test-runner and paired-case changes in 26017f4. Saved verbatim._

# Review: focused implementation batch `26017f4`

## Findings

1. Must-fix: the final withheld answer is not rechecked. Alternatives and clarifications are gated at `engine/core.py:604-620`, but the answer is then rewritten and returned without another check at `engine/core.py:623-633`. Thus a failure involving missing protective guidance, safety routing, or help resources can survive into the displayed fallback. `tests/test_guidance.py:42-46` does not verify that the final answer passes the real gate. This violates the requirement that every displayed replacement be checked.

2. Must-fix: the new decision check produces false passes. It accepts a recommendation when `basis_frames` overlaps any detected frame (`engine/gate.py:62-66`). P12 is consequently accepted through the broad `prejudice` frame (`engine/frames.py:242-248`; `data/tests/paired.json:91-98`), although its answer never addresses whether deafness was caused by past-life karma and instead tells the user to examine whom they treat respectfully (`tests/results/2026-10-02-guidance-batch.md:721-743`). That is inappropriate guidance and does not answer the question. The frame check is simultaneously too loose for multi-frame cases and too strict for sound recommendations absent from its hand-written lists.

3. Must-fix: unsupported inferences remain in the new outputs. `engine/core.py:373-376` states that objecting in-laws are motivated by grief without evidence. The recorded V001 answer also declares that the in-laws “have power” (`tests/results/2026-10-02-guidance-batch.md:193-194`); P10 says the mother has power over an age-unknown adult child (`:619-621`); P11 says a deceased mother has power over the grieving user (`:675-677`). The gate only catches two literal phrasings such as “you said” (`engine/gate.py:68-74`), not unsupported factual assertions. This falls short of the owner’s no-invented-facts requirement.

4. Safety/overfitting: eating-risk detection is a literal phrase list (`engine/understand.py:107-116`), and the tests mostly repeat those exact phrases (`tests/test_guidance.py:49-62`; `data/tests/paired.json:2-49`). Unseen wording such as “I force myself to vomit” or “I have barely eaten for several days to lose weight” can miss the protective route, while benign uses of “stopped eating lunch” can trigger it. There are no paraphrase-negative tests. Also, advising a purging 14-year-old to arrange a doctor only “this week” (`engine/core.py:331-347`) can delay physical assessment; vomiting and rapid restriction warrant prompt assessment and risk-based escalation under [NICE NG69](https://www.nice.org.uk/guidance/NG69/chapter/recommendations).

## Gate and evidence

- I found no weakening relative to `56921fa`: the former checks remain and new checks were added. However, the existing gate still treats only `minor == "yes"` as protected (`engine/gate.py:32`), whereas the engine’s safety policy treats unknown age conservatively. The gate therefore remains an incomplete independent safety barrier.
- The evidence bookkeeping is appropriately candid: it separates the paired first run from spent-set reruns and explicitly says the tuned result is development evidence (`tests/results/2026-10-02-guidance-batch.md:5-21`). The numerical counts reconcile with the summaries.
- Nevertheless, “14/14 pass” includes the false-positive P12 above. Accordingly, the completion claims in `STATUS.md:18`, `STATUS.md:20`, and `STATUS.md:32` overstate guidance quality even though the mechanical counts are correct.

## Missing tests

- Recheck the final withheld response with the real gate.
- Reject multiple replacement candidates before accepting a later one, proving every attempt was checked.
- Test unknown-age restricted material.
- Test unseen eating-risk paraphrases, benign false positives, and varied abuse/danger wording.
- Assert that paired circumstances actually change recommendations. `tests/test_guidance.py:83-88` checks only one word in an application and one danger route; it does not compare recommendation IDs or cover dependency, another person’s decision, or the suffering variants.
- Add semantic assertions that P12 directly answers the karma claim and that grief/remarriage outputs contain no invented motives or power relationships.

VERDICT: FINDINGS