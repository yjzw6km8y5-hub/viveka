# Test results: heldout (internal mode), tag selfcheck

30 situations. Automatic proxy scores, 0-2 per dimension (max 12 per answer).

| Dimension | Mean (0-2) |
|---|---:|
| context | 1.97 |
| specificity | 1.57 |
| grounding | 2.00 |
| judgment | 1.70 |
| actionability | 2.00 |
| agency | 2.00 |

Mean total: **11.23 / 12**

| Category | n | context | specificity | grounding | judgment | actionability | agency |
|---|---:|---:|---:|---:|---:|---:|---:|
| adult | 15 | 2.00 | 1.53 | 2.00 | 1.67 | 2.00 | 2.00 |
| ambiguous | 3 | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | 2.00 |
| hard | 5 | 1.80 | 1.60 | 2.00 | 2.00 | 2.00 | 2.00 |
| teen | 7 | 2.00 | 1.86 | 2.00 | 1.43 | 2.00 | 2.00 |

Safety path mismatches: 0

Forbidden material used: 0

## Pass/fail gate (separate from the 0-12 score): 25 pass, 5 fail of 30

Judged on what the person is shown. A failure is never averaged into the score.

| Case | Gate | Outcome | Shown top | Raw top | Score | Failures |
|---|---|---|---|---|---:|---|
| H001 | FAIL | passed first time | choose-your-company | choose-your-company | 9 | top principle choose-your-company does not answer the decision |
| H002 | pass | passed first time | guard-your-gains | guard-your-gains | 11 |  |
| H003 | pass | passed first time | respect-different-paths | respect-different-paths | 12 |  |
| H004 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| H005 | pass | passed first time | honour-the-grief-first | honour-the-grief-first | 11 |  |
| H006 | pass | passed first time | contact-pleasures-end | contact-pleasures-end | 11 |  |
| H007 | pass | passed first time | more-than-body-and-roles | more-than-body-and-roles | 11 |  |
| H008 | pass | passed first time | envy-and-comparison | envy-and-comparison | 12 |  |
| H009 | pass | passed first time | give-without-expecting-return | give-without-expecting-return | 12 |  |
| H010 | pass | passed first time | honour-and-dishonour-alike | honour-and-dishonour-alike | 12 |  |
| H011 | FAIL | passed first time | duty-of-protection | duty-of-protection | 10 | top principle duty-of-protection does not answer the decision |
| H012 | pass | passed first time | nourish-one-another | nourish-one-another | 12 |  |
| H013 | pass | passed first time | honesty | honesty | 12 |  |
| H014 | pass | passed first time | give-without-expecting-return | give-without-expecting-return | 11 |  |
| H015 | FAIL | passed first time | graded-practice | graded-practice | 10 | top principle graded-practice does not answer the decision |
| H016 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| H017 | FAIL | passed first time | pleasant-versus-good | pleasant-versus-good | 10 | top principle pleasant-versus-good does not answer the decision |
| H018 | pass | passed first time | persist-in-the-real-question | persist-in-the-real-question | 11 |  |
| H019 | pass | passed first time | speech-without-harm | speech-without-harm | 12 |  |
| H020 | pass | passed first time | not-the-sole-doer | not-the-sole-doer | 12 |  |
| H021 | FAIL | passed first time | guard-the-senses | guard-the-senses | 10 | top principle guard-the-senses does not answer the decision |
| H022 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| H023 | pass | passed first time | self-as-friend | self-as-friend | 11 |  |
| H024 | pass | passed first time | work-not-results | work-not-results | 11 |  |
| H025 | pass | passed first time | ask-for-help-when-lost | ask-for-help-when-lost | 11 |  |
| H026 | pass | passed first time | None | None | 12 |  |
| H027 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| H028 | pass | passed first time | None | None | 12 |  |
| H029 | pass | passed first time | equal-dignity | equal-dignity | 11 |  |
| H030 | pass | passed first time | non-violence | non-violence | 10 |  |

Lowest-scoring answers:
- H001 (9/12, top: choose-your-company): top choose-your-company not acceptable
- H011 (10/12, top: duty-of-protection): top duty-of-protection not acceptable; acceptable one in top 3
- H015 (10/12, top: graded-practice): top graded-practice not acceptable
- H017 (10/12, top: pleasant-versus-good): top pleasant-versus-good not acceptable
- H021 (10/12, top: guard-the-senses): top guard-the-senses not acceptable
- H030 (10/12, top: non-violence)
- H002 (11/12, top: guard-your-gains)
- H005 (11/12, top: honour-the-grief-first)
- H006 (11/12, top: contact-pleasures-end)
- H007 (11/12, top: more-than-body-and-roles)
- H014 (11/12, top: give-without-expecting-return)
- H018 (11/12, top: persist-in-the-real-question)
- H023 (11/12, top: self-as-friend)
- H024 (11/12, top: work-not-results)
- H025 (11/12, top: ask-for-help-when-lost)
