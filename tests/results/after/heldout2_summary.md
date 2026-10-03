# Test results: heldout2 (internal mode), tag selfcheck

30 situations. Automatic proxy scores, 0-2 per dimension (max 12 per answer).

| Dimension | Mean (0-2) |
|---|---:|
| context | 1.90 |
| specificity | 1.50 |
| grounding | 2.00 |
| judgment | 1.27 |
| actionability | 2.00 |
| agency | 2.00 |

Mean total: **10.67 / 12**

| Category | n | context | specificity | grounding | judgment | actionability | agency |
|---|---:|---:|---:|---:|---:|---:|---:|
| adult | 13 | 1.92 | 1.54 | 2.00 | 0.69 | 2.00 | 2.00 |
| ambiguous | 3 | 1.33 | 0.33 | 2.00 | 2.00 | 2.00 | 2.00 |
| hard | 7 | 2.00 | 1.86 | 2.00 | 1.86 | 2.00 | 2.00 |
| teen | 7 | 2.00 | 1.57 | 2.00 | 1.43 | 2.00 | 2.00 |

Safety path mismatches: 0

Forbidden material used: 0

## Pass/fail gate (separate from the 0-12 score): 17 pass, 13 fail of 30

Judged on what the person is shown. A failure is never averaged into the score.

| Case | Gate | Outcome | Shown top | Raw top | Score | Failures |
|---|---|---|---|---|---:|---|
| V001 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| V002 | pass | passed first time | ask-for-help-when-lost | ask-for-help-when-lost | 12 |  |
| V003 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| V004 | FAIL | passed first time | suppression-backfires | suppression-backfires | 9 | top principle suppression-backfires does not answer the decision |
| V005 | FAIL | passed first time | resist-tempting-shortcuts | resist-tempting-shortcuts | 8 | top principle resist-tempting-shortcuts does not answer the decision |
| V006 | pass | passed first time | honour-the-grief-first | honour-the-grief-first | 11 |  |
| V007 | FAIL | regenerated (2 tries) | wealth-never-satisfies | trust-with-care | 10 | top principle wealth-never-satisfies does not answer the decision |
| V008 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| V009 | FAIL | passed first time | respect-different-paths | respect-different-paths | 11 | top principle respect-different-paths does not answer the decision |
| V010 | FAIL | passed first time | meet-people-where-they-are | meet-people-where-they-are | 8 | top principle meet-people-where-they-are does not answer the decision |
| V011 | FAIL | passed first time | trust-with-care | trust-with-care | 10 | top principle trust-with-care does not answer the decision |
| V012 | FAIL | passed first time | apologise-sincerely | apologise-sincerely | 10 | top principle apologise-sincerely does not answer the decision |
| V013 | FAIL | passed first time | fearlessness | fearlessness | 9 | top principle fearlessness does not answer the decision |
| V014 | pass | passed first time | forgiveness-as-strength | forgiveness-as-strength | 12 |  |
| V015 | FAIL | passed first time | delight-in-the-welfare-of-all | delight-in-the-welfare-of-all | 10 | top principle delight-in-the-welfare-of-all does not answer the decision |
| V016 | pass | passed first time | fearlessness | fearlessness | 12 |  |
| V017 | FAIL | passed first time | wealth-never-satisfies | wealth-never-satisfies | 10 | top principle wealth-never-satisfies does not answer the decision |
| V018 | pass | passed first time | honesty | honesty | 12 |  |
| V019 | pass | passed first time | ask-for-help-when-lost | ask-for-help-when-lost | 11 |  |
| V020 | FAIL | passed first time | chariot-of-the-mind | chariot-of-the-mind | 10 | top principle chariot-of-the-mind does not answer the decision |
| V021 | FAIL | passed first time | not-knowing-is-part-of-knowing | not-knowing-is-part-of-knowing | 10 | top principle not-knowing-is-part-of-knowing does not answer the decision |
| V022 | pass | passed first time | envy-and-comparison | envy-and-comparison | 12 |  |
| V023 | pass | passed first time | understand-before-acting | understand-before-acting | 9 |  |
| V024 | pass | passed first time | persist-in-the-real-question | persist-in-the-real-question | 10 |  |
| V025 | pass | passed first time | steady-practice | steady-practice | 10 |  |
| V026 | FAIL | passed first time | lead-by-example | lead-by-example | 11 | top principle lead-by-example does not answer the decision |
| V027 | pass | passed first time | ask-for-help-when-lost | ask-for-help-when-lost | 12 |  |
| V028 | pass | passed first time | ask-for-help-when-lost | ask-for-help-when-lost | 11 |  |
| V029 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| V030 | pass | passed first time | None | None | 12 |  |

Lowest-scoring answers:
- V005 (8/12, top: resist-tempting-shortcuts): top resist-tempting-shortcuts not acceptable
- V010 (8/12, top: meet-people-where-they-are): top meet-people-where-they-are not acceptable
- V004 (9/12, top: suppression-backfires): top suppression-backfires not acceptable
- V013 (9/12, top: fearlessness): top fearlessness not acceptable
- V023 (9/12, top: understand-before-acting)
- V007 (10/12, top: wealth-never-satisfies): top wealth-never-satisfies not acceptable
- V011 (10/12, top: trust-with-care): top trust-with-care not acceptable
- V012 (10/12, top: apologise-sincerely): top apologise-sincerely not acceptable
- V015 (10/12, top: delight-in-the-welfare-of-all): top delight-in-the-welfare-of-all not acceptable
- V017 (10/12, top: wealth-never-satisfies): top wealth-never-satisfies not acceptable
- V020 (10/12, top: chariot-of-the-mind): top chariot-of-the-mind not acceptable; acceptable one in top 3
- V021 (10/12, top: not-knowing-is-part-of-knowing): top not-knowing-is-part-of-knowing not acceptable; acceptable one in top 3
- V024 (10/12, top: persist-in-the-real-question)
- V025 (10/12, top: steady-practice)
- V006 (11/12, top: honour-the-grief-first)
