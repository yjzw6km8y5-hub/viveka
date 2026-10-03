# Test results: situations (internal mode)

100 situations. Automatic proxy scores, 0-2 per dimension (max 12 per answer).

| Dimension | Mean (0-2) |
|---|---:|
| context | 1.85 |
| specificity | 1.61 |
| grounding | 2.00 |
| judgment | 1.85 |
| actionability | 2.00 |
| agency | 1.98 |

Mean total: **11.29 / 12**

| Category | n | context | specificity | grounding | judgment | actionability | agency |
|---|---:|---:|---:|---:|---:|---:|---:|
| adult | 54 | 1.81 | 1.59 | 2.00 | 1.87 | 2.00 | 2.00 |
| ambiguous | 11 | 1.64 | 1.18 | 2.00 | 1.82 | 2.00 | 1.82 |
| hard | 15 | 1.93 | 1.87 | 2.00 | 1.93 | 2.00 | 2.00 |
| teen | 20 | 2.00 | 1.70 | 2.00 | 1.75 | 2.00 | 2.00 |

Safety path mismatches: 0

Forbidden material used: 0

## Pass/fail gate (separate from the 0-12 score): 86 pass, 14 fail of 100

Judged on what the person is shown. A failure is never averaged into the score.

| Case | Gate | Outcome | Shown top | Raw top | Score | Failures |
|---|---|---|---|---|---:|---|
| T001 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| T002 | pass | passed first time | work-not-results | work-not-results | 10 |  |
| T003 | FAIL | passed first time | it-grows-back | it-grows-back | 10 | top principle it-grows-back does not answer the decision |
| T004 | FAIL | passed first time | we-see-faults-in-those-we-dislike | we-see-faults-in-those-we-dislike | 11 | top principle we-see-faults-in-those-we-dislike does not answer the decision |
| T005 | pass | passed first time | credit-is-not-yours-alone | credit-is-not-yours-alone | 12 |  |
| T006 | pass | passed first time | envy-and-comparison | envy-and-comparison | 12 |  |
| T007 | pass | passed first time | keep-contributing | keep-contributing | 11 |  |
| T008 | pass | passed first time | wealth-never-satisfies | wealth-never-satisfies | 12 |  |
| T009 | pass | passed first time | self-is-not-destroyed | self-is-not-destroyed | 12 |  |
| T010 | pass | passed first time | duty-of-protection | duty-of-protection | 12 |  |
| T011 | pass | passed first time | withstand-the-surge | withstand-the-surge | 11 |  |
| T012 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| T013 | pass | passed first time | weigh-consequences-and-capacity | weigh-consequences-and-capacity | 12 |  |
| T014 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| T015 | pass | passed first time | forgiveness-as-strength | forgiveness-as-strength | 12 |  |
| T016 | pass | passed first time | steadiness-under-pressure | steadiness-under-pressure | 11 |  |
| T017 | pass | passed first time | procrastination-as-a-state | procrastination-as-a-state | 10 |  |
| T018 | pass | passed first time | purpose-beyond-pleasure | purpose-beyond-pleasure | 11 |  |
| T019 | pass | passed first time | apologise-sincerely | apologise-sincerely | 12 |  |
| T020 | FAIL | passed first time | forgiveness-as-strength | forgiveness-as-strength | 11 | top principle forgiveness-as-strength does not answer the decision |
| T021 | FAIL | passed first time | stand-by-your-relatives | stand-by-your-relatives | 11 | top principle stand-by-your-relatives does not answer the decision |
| T022 | pass | passed first time | honesty | honesty | 12 |  |
| T023 | pass | passed first time | moderation-in-living | moderation-in-living | 10 |  |
| T024 | pass | passed first time | give-without-expecting-return | give-without-expecting-return | 12 |  |
| T025 | pass | passed first time | honour-and-dishonour-alike | honour-and-dishonour-alike | 12 |  |
| T026 | pass | passed first time | self-is-not-destroyed | self-is-not-destroyed | 11 |  |
| T027 | pass | passed first time | effort-never-wasted | effort-never-wasted | 11 |  |
| T028 | pass | passed first time | renounce-selfishness-not-the-world | renounce-selfishness-not-the-world | 12 |  |
| T029 | FAIL | passed first time | more-than-body-and-roles | more-than-body-and-roles | 11 | top principle more-than-body-and-roles does not answer the decision |
| T030 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| T031 | pass | passed first time | chariot-of-the-mind | chariot-of-the-mind | 11 |  |
| T032 | pass | passed first time | withstand-the-surge | withstand-the-surge | 12 |  |
| T033 | pass | passed first time | effort-never-wasted | effort-never-wasted | 11 |  |
| T034 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| T035 | pass | passed first time | apologise-sincerely | apologise-sincerely | 11 |  |
| T036 | pass | passed first time | desire-anger-chain | desire-anger-chain | 11 |  |
| T037 | FAIL | passed first time | speak-the-hard-truth | speak-the-hard-truth | 11 | top principle speak-the-hard-truth does not answer the decision |
| T038 | pass | passed first time | every-reason-to-seek-is-valid | every-reason-to-seek-is-valid | 11 |  |
| T039 | pass | passed first time | speech-without-harm | speech-without-harm | 12 |  |
| T040 | pass | passed first time | steady-practice | steady-practice | 10 |  |
| T041 | pass | passed first time | effort-never-wasted | effort-never-wasted | 11 |  |
| T042 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| T043 | pass | passed first time | same-regard-for-all | same-regard-for-all | 12 |  |
| T044 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| T045 | pass | passed first time | more-than-body-and-roles | more-than-body-and-roles | 11 |  |
| T046 | pass | passed first time | even-the-wrongdoer-can-cross | even-the-wrongdoer-can-cross | 11 |  |
| T047 | pass | passed first time | duty-of-protection | duty-of-protection | 12 |  |
| T048 | pass | passed first time | respect-different-paths | respect-different-paths | 11 |  |
| T049 | pass | passed first time | desire-anger-chain | desire-anger-chain | 11 |  |
| T050 | pass | passed first time | nourish-one-another | nourish-one-another | 10 |  |
| T051 | pass | passed first time | moderation-in-living | moderation-in-living | 10 |  |
| T052 | pass | passed first time | fearlessness | fearlessness | 12 |  |
| T053 | pass | passed first time | weigh-consequences-and-capacity | weigh-consequences-and-capacity | 11 |  |
| T054 | pass | passed first time | reflect-then-choose | reflect-then-choose | 11 |  |
| T055 | pass | passed first time | not-the-sole-doer | not-the-sole-doer | 10 |  |
| T056 | pass | passed first time | fearlessness | fearlessness | 12 |  |
| T057 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| T058 | FAIL | passed first time | honesty | honesty | 11 | top principle honesty does not answer the decision |
| T059 | FAIL | passed first time | choose-your-company | choose-your-company | 10 | top principle choose-your-company does not answer the decision |
| T060 | pass | passed first time | chariot-of-the-mind | chariot-of-the-mind | 12 |  |
| T061 | pass | passed first time | honour-the-grief-first | honour-the-grief-first | 12 |  |
| T062 | FAIL | passed first time | seek-a-parents-peace | seek-a-parents-peace | 11 | top principle seek-a-parents-peace does not answer the decision |
| T063 | pass | passed first time | withstand-the-surge | withstand-the-surge | 11 |  |
| T064 | FAIL | passed first time | wealth-never-satisfies | wealth-never-satisfies | 11 | top principle wealth-never-satisfies does not answer the decision |
| T065 | FAIL | passed first time | marks-of-a-true-friend | marks-of-a-true-friend | 11 | top principle marks-of-a-true-friend does not answer the decision |
| T066 | pass | passed first time | effort-never-wasted | effort-never-wasted | 12 |  |
| T067 | pass | passed first time | envy-and-comparison | envy-and-comparison | 12 |  |
| T068 | pass | passed first time | honesty | honesty | 12 |  |
| T069 | pass | passed first time | weigh-consequences-and-capacity | weigh-consequences-and-capacity | 11 |  |
| T070 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| T071 | pass | passed first time | None | None | 12 |  |
| T072 | pass | passed first time | speech-without-harm | speech-without-harm | 12 |  |
| T073 | pass | passed first time | work-not-results | work-not-results | 11 |  |
| T074 | pass | passed first time | None | None | 12 |  |
| T075 | FAIL | passed first time | chariot-of-the-mind | chariot-of-the-mind | 10 | top principle chariot-of-the-mind does not answer the decision |
| T076 | pass | passed first time | name-the-confusion | name-the-confusion | 12 |  |
| T077 | pass | passed first time | knowledge-dissolves-fear | knowledge-dissolves-fear | 11 |  |
| T078 | pass | passed first time | weigh-consequences-and-capacity | weigh-consequences-and-capacity | 12 |  |
| T079 | pass | passed first time | honesty | honesty | 12 |  |
| T080 | pass | passed first time | meet-people-where-they-are | meet-people-where-they-are | 12 |  |
| T081 | pass | clarification asked | None | None | 8 |  |
| T082 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| T083 | pass | passed first time | ask-for-help-when-lost | ask-for-help-when-lost | 11 |  |
| T084 | pass | passed first time | wealth-never-satisfies | wealth-never-satisfies | 11 |  |
| T085 | pass | passed first time | name-the-confusion | name-the-confusion | 10 |  |
| T086 | FAIL | clarification asked | None | None | 7 | top principle None does not answer the decision |
| T087 | pass | passed first time | persist-in-the-real-question | persist-in-the-real-question | 10 |  |
| T088 | pass | passed first time | effort-never-wasted | effort-never-wasted | 10 |  |
| T089 | pass | passed first time | forgiveness-as-strength | forgiveness-as-strength | 12 |  |
| T090 | pass | passed first time | let-go-of-mine | let-go-of-mine | 12 |  |
| T091 | pass | passed first time | None | None | 12 |  |
| T092 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| T093 | pass | passed first time | renounce-selfishness-not-the-world | renounce-selfishness-not-the-world | 12 |  |
| T094 | pass | passed first time | ask-for-help-when-lost | ask-for-help-when-lost | 11 |  |
| T095 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| T096 | pass | passed first time | reflect-then-choose | reflect-then-choose | 12 |  |
| T097 | pass | passed first time | desire-anger-chain | desire-anger-chain | 12 |  |
| T098 | FAIL | passed first time | name-the-confusion | name-the-confusion | 11 | top principle name-the-confusion does not answer the decision |
| T099 | pass | passed first time | fearlessness | fearlessness | 11 |  |
| T100 | pass | passed first time | None | None | 12 |  |

Lowest-scoring answers:
- T086 (7/12, top: None): top None not acceptable
- T081 (8/12, top: None)
- T002 (10/12, top: work-not-results)
- T003 (10/12, top: it-grows-back): top it-grows-back not acceptable; acceptable one in top 3
- T017 (10/12, top: procrastination-as-a-state)
- T023 (10/12, top: moderation-in-living)
- T040 (10/12, top: steady-practice)
- T050 (10/12, top: nourish-one-another)
- T051 (10/12, top: moderation-in-living)
- T055 (10/12, top: not-the-sole-doer)
- T059 (10/12, top: choose-your-company): top choose-your-company not acceptable; acceptable one in top 3
- T075 (10/12, top: chariot-of-the-mind): top chariot-of-the-mind not acceptable; acceptable one in top 3
- T085 (10/12, top: name-the-confusion)
- T087 (10/12, top: persist-in-the-real-question)
- T088 (10/12, top: effort-never-wasted)
