# Viveka — independent observer review

Date: 2026-10-02, 16:17 America/Toronto
Examined commit: e265489ae90b3f5ed297394a94b782f834846b2b
Guidance improvement: UNPROVEN since the preceding review.

## Overall observation

The vision remains sound: understand a real dilemma, weigh competing perspectives, recommend a practical next step and preserve agency. CLAUDE.md section 10 now states that sequence clearly. The most recent commit restores the pause on adding texts after a reviewer challenged Chanakya Niti ingestion. This demonstrates one corrective cycle and improved adherence to direction; it does not demonstrate better advice or a continuously running local builder.

## must-fix

### Central recommendation quality must override aggregate scores

Evidence: tests/results/heldout2.json contains 15 of 30 cases whose notes mark the top principle as unacceptable. V009 and V026 score 11/12 despite that note. The summary reports 10.53/12 and only shows 13 of these failures in its lowest-scoring list. The earlier statement of 13 failures understated the raw-file count; this is a correction to interpretation, not evidence of newly worsened performance.

Impact: the headline score can make unsuitable advice look nearly successful.

Next action: report recommendation acceptability and critical failures separately as pass/fail gates, across every case. Never average those failures away through formatting, exact citations or action-step presence. Rerun spent sets as regression coverage and use independently constructed fresh cases for new quality claims.

### Protective guidance needs more than a generic support template

Evidence: V028 describes a 16-year-old restricting eating to become thinner. The saved answer selects a grief principle and mainly asks the teen to write or talk about feelings. It scores 10/12 even though its own notes reject the top recommendation. Zero safety-path mismatches in the summary do not establish suitability of the resulting guidance.

Impact: a disclosed problem can be detected as distress yet receive a response that misses its concrete support needs.

Next action: make tests assess the protective recommendation itself, including appropriate trusted-adult and qualified support for this kind of disclosure. Test varied wording and changed circumstances; do not treat a generic helpline footer or correct internal route label as sufficient.

### High-scoring answers must address the person's actual decision

Evidence: V001 concerns remarriage two years after a spouse's death and pressure from in-laws. It scores 12/12 but centres grief and journaling rather than weighing remarriage, agency and family pressure. Its explanation says the user described themselves as a householder, although the input supplied no such label. V024 asks why bad things happen to good people but receives an instruction to thank contributors after a success.

Impact: recognising a word or naming a principle is being mistaken for understanding the dilemma.

Next action: evaluate whether the main recommendation answers the actual question; label inferred context as inference. Use paired cases that change dependency, time elapsed, urgency and danger, then assess whether the recommendation changes appropriately.

## should-fix

### Give every reviewer a shared, current intent document

Evidence: CONTEXT.md returned 404 and is absent from the root listing. PROJECT_BRIEF.md is also absent from that listing. README.md still introduces the product mainly as a verse-answer library; the broader owner vision is recorded in CLAUDE.md and Drive context documents.

Impact: different reviewers and builders may judge against different versions of the product intent.

Next action: have the builder reconcile the agreed intent into a canonical project context and cross-link it. Treat proposed changes as proposals until accepted. The observer can use the existing context sources meanwhile; missing files do not justify inventing their contents.

### Keep evaluation records and first-run claims easy to reconcile

Evidence: tests/README.md records a heldout2 first-run score of 10.30/12 and marks the set spent; the saved summary now reports 10.53/12. DECISIONS.md describes subsequent tuning. The spent-set disclosure is good, but the reader must work to distinguish first-run evidence from reruns.

Impact: improvement claims can be overstated or misread.

Next action: retain immutable, dated first-run reports, label reruns explicitly and show full failure counts. Comparative testing still needs baselines, independent cases and raters; these were not demonstrated in the inspected files.

## idea

Use a small decision-focused evaluation set alongside broad coverage: ask whether the user can make a better next decision after the answer, which facts would reverse the advice, and whether the strongest alternative was fairly represented. This is a proposed evaluation improvement, not a newly agreed owner decision.

## Next priority

Keep text expansion paused. Fix the recommendation gate and decision-specific guidance; validate on fresh independently constructed cases while continuing human review of the starter collection.

## Evidence and limits

Read: root listing, STATUS.md, CLAUDE.md, README.md, relevant DECISIONS.md entries, latest reviews/202610021916-viveka-cycle1.md, three recent commits, tests/README.md, heldout summaries and the full saved heldout2.json. This was an observer review of repository evidence, not a fresh engine run, a translation audit, a clinical assessment or independent validation of all outputs. Public scripture approval remains a separate gate.

## Workflow verification

GitHub account and repository reads succeeded. Google Drive context upload and readback succeeded. The two-hour observer task is enabled, with its first scheduled run at 18:15 America/Toronto on 2026-10-02. This review is a manual initial run; scheduled end-to-end execution is pending. Each scheduled review must verify its own save and report failures honestly. The existing hourly progress-check task was left unchanged.
