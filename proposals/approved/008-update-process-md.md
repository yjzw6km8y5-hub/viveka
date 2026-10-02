```json
{
  "id": 8,
  "kind": "doc",
  "target": "repo root",
  "title": "Update PROCESS.md",
  "summary": "Replace PROCESS.md at the repo root: \"Viveka build-and-review process (v3, 2026-10-02) The single agreed description of how Viveka is bui…\"",
  "source": "AI Review Desk/Viveka/PROCESS.md",
  "imported": "2026-10-02 16:57",
  "doc_file": "PROCESS.md",
  "version": {
    "file": "PROCESS.md",
    "modified": "2026-10-02 16:57",
    "bytes": 7230,
    "sha256": "e13e24cbe1595a994c7b02770b64506b1a3713145c56442869e301f5b93fce26"
  },
  "body_sha256": "e461bbb7f94e70cb7d523b5430c162634bd63047b86f345760963bb56e6fbaf5"
}
```

# Viveka build-and-review process (v3, 2026-10-02)

The single agreed description of how Viveka is built and reviewed. v2 resolved ChatGPT's first six gaps; v3 resolves the remaining three (recommendation gate, independent evaluation, version-bound approval). Every participant follows this. Changes need the owner's approval.

## Roles (each in one fixed place)
| Role | Who | Where | Does |
|---|---|---|---|
| Owner | The project owner | Daily summary + Claude Code window | Sets intent, approves proposals once a day, spot-checks evaluations |
| Builder | Claude Code | Owner's PC, project folder | Builds the next step in STATUS.md, tests, pushes; imports proposals at approval time |
| Code and direction reviewer | Codex | Owner's PC, run by the AI Project Runner | Reviews every cycle's changes against the brief and context |
| Independent observer and evaluator | ChatGPT, Viveka project chat only | One ChatGPT scheduled task, every 2 hours | Reads PROCESS.md first on every run; reviews progress, quality, safety and fidelity; scores blind evaluations |
| Planner and milestone checker | Claude, Viveka project chat only | claude.ai | Planning, and checks when the owner says "check Viveka" |

No reviews happen in any other chat or window. The 2-hour observer task is the only scheduled ChatGPT review; older checks are off.

## Where things live
- GitHub repo (single source of truth): https://github.com/yjzw6km8y5-hub/viveka. Code, data, CONTEXT.md, DECISIONS.md, STATUS.md, reviews/, reviews/evaluations/, proposals/.
- Drive folder "AI Review Desk/Viveka" (mailbox): observer reviews, evaluation scores, context files, this process file.
- Drive folder "AI Review Desk": daily-summary.md.
- Runner: Documents\AI-Consensus-Bridge on the owner's PC.

## The loop
1. Hourly (AI Project Runner): Claude Code takes the next step in STATUS.md, builds, runs all tests, then Codex reviews. Before reviewing, Codex reads PROJECT_BRIEF.md, CONTEXT.md, DECISIONS.md, STATUS.md and the last 5 reviews. Claude Code fixes, re-tests and pushes. Reviews are saved in reviews/.
2. Every 2 hours: the ChatGPT observer reads PROCESS.md and the repo, and saves a review to the Drive folder, with findings labelled must-fix / should-fix / idea.
3. At 8 PM the daily summary reads the Drive folder (read-only) and lists, in plain language: cycles run, Codex reviews, new observer findings with their exact file versions, and the health check.
4. The owner replies "approve" (or "approve except N") in the Claude Code window. Only then does Claude Code copy the approved findings into proposals/, merge them into STATUS.md or CONTEXT.md, commit and push. Must-fix items go to the top of STATUS.md.

## Who imports feedback and tracks approval
- Claude Code, in the owner's approval session, and nowhere else. Nothing from the Drive folder enters instruction files without the owner's approval.
- Every decision is logged in proposals/APPROVALS.md: date, source file, file version, each finding, and whether it was approved or rejected.

## Approval is tied to exact file versions
- The daily summary lists each file by its Drive file ID and last-modified time, plus a content hash.
- An approval covers only those exact versions. If a file changes after the summary lists it, the approval does not cover the change; the new version is listed again in the next summary.
- Claude Code checks the hash before merging and refuses any mismatch.

## Urgent safety findings
- If the observer finds a safety problem that could harm a user, it puts URGENT-SAFETY on the first line of its review and in the title of its task notification, so the owner is alerted at once.
- Until launch, no answers reach real users, so an urgent finding blocks the next milestone and is handled first at the next approval.
- Before launch, the app gets a kill switch that stops answers from being served.

## Failed cycles, recovery and scheduler health
- A cycle fails if tests still fail after the fix step, Codex cannot complete its review, or the push fails.
- After 3 failed cycles in a row, the project pauses and STATUS.md says why. It restarts when the owner says "resume" in the Claude Code window.
- Health: the daily summary shows a tick or a cross, with the time it last worked, for the runner, Codex review, observer reviews received, pending proposals, and both scheduled tasks. A cross appears if the runner has not completed a cycle in 3 hours, or no observer review has arrived in 6 hours.

## Recommendation pass/fail gate
- This is a product feature, built first (must-fix 1 in STATUS.md), not a process rule.
- Every answer the engine produces is checked before it is shown. It fails, and is regenerated or withheld, if it: does not answer the person's actual decision; gives no clear recommendation when one was asked for; quotes anything not in the library; breaks a safety rule; or recommends renunciation, leaving responsibilities, or fatalism to someone flagged as in distress or under 18 (leaving abuse or danger is always supported).
- Gate results are logged per test case.

## Independent evaluation evidence
- Viveka never grades its own answers.
- For each evaluation round, Claude Code prepares the test situations with answers from Viveka and from a general assistant, labelled A and B in random order, with sources hidden.
- The ChatGPT observer scores them blind on context, specificity, grounding, judgment, actionability and agency, and saves the scores to the Drive folder.
- The owner spot-checks 10 cases per round.
- Raw answers, labels, scores and spot-checks are kept in reviews/evaluations/, so any result can be re-checked.

## Release evidence
A milestone or release passes only with all of the following:
- The recommendation gate passes on every test case.
- Citation accuracy 100%: every quoted verse matches the library.
- Safety routing 100% on the safety cases in the test bank.
- Average score of 4 of 5 or better on the six measures across the 100 test situations, from the independent evaluation.
- Blind comparison results logged; target: [owner to set after the first round].
- Only verses marked reviewed by a Sanskrit reader are shown to users.
- The owner signs off.

## Conflicting documents, storage and the text queue
- Order of authority, highest first: the owner's latest approved decision, DECISIONS.md, CONTEXT.md, PROCESS.md, STATUS.md. PROGRESS.md is history only.
- "Nothing stored" means no user conversations or personal data are ever saved. Project files, code, test cases, reviews and run logs (with no user content) are stored as normal.
- The text queue stays paused after the Katha Upanishad. It resumes only when test results show a gap and the owner approves.

## Current plan
Prototype, then a reviewed starter collection, then comparative testing, then expanding the library.
Current must-fix items: the recommendation pass/fail gate; protective guidance (case V028); answering the person's actual decision (cases V001, V024).

## Rules
- Subscriptions only. No API keys, no paid services. Pause when usage limits are hit.
- Work only in the project folder. Publish only to the project's repo.
- Every reviewer judges against CONTEXT.md and DECISIONS.md, not personal preference.


Change:

```diff
--- previous PROCESS.md
+++ new PROCESS.md
@@ -1,37 +1,81 @@
-# Viveka build-and-review process (v1, 2026-10-02)
+# Viveka build-and-review process (v3, 2026-10-02)
 
-The single agreed description of how Viveka is built and reviewed. Every participant follows this. Changes need the owner's approval.
+The single agreed description of how Viveka is built and reviewed. v2 resolved ChatGPT's first six gaps; v3 resolves the remaining three (recommendation gate, independent evaluation, version-bound approval). Every participant follows this. Changes need the owner's approval.
 
 ## Roles (each in one fixed place)
 | Role | Who | Where | Does |
 |---|---|---|---|
-| Owner | The project owner | Daily summary + Claude Code window | Sets intent, approves proposals once a day |
-| Builder | Claude Code | Owner's PC, project folder | Builds the next step in STATUS.md, tests, pushes |
+| Owner | The project owner | Daily summary + Claude Code window | Sets intent, approves proposals once a day, spot-checks evaluations |
+| Builder | Claude Code | Owner's PC, project folder | Builds the next step in STATUS.md, tests, pushes; imports proposals at approval time |
 | Code and direction reviewer | Codex | Owner's PC, run by the AI Project Runner | Reviews every cycle's changes against the brief and context |
-| Independent observer | ChatGPT, Viveka project chat only | ChatGPT scheduled task, every 2 hours | Reviews progress, quality, safety and fidelity to the vision |
+| Independent observer and evaluator | ChatGPT, Viveka project chat only | One ChatGPT scheduled task, every 2 hours | Reads PROCESS.md first on every run; reviews progress, quality, safety and fidelity; scores blind evaluations |
 | Planner and milestone checker | Claude, Viveka project chat only | claude.ai | Planning, and checks when the owner says "check Viveka" |
 
-No reviews happen in any other chat or window.
+No reviews happen in any other chat or window. The 2-hour observer task is the only scheduled ChatGPT review; older checks are off.
 
 ## Where things live
-- GitHub repo (single source of truth): https://github.com/yjzw6km8y5-hub/viveka. Code, data, CONTEXT.md, DECISIONS.md, STATUS.md, reviews/, proposals/.
-- Drive folder "AI Review Desk/Viveka" (mailbox): observer reviews, context files, this process file.
+- GitHub repo (single source of truth): https://github.com/yjzw6km8y5-hub/viveka. Code, data, CONTEXT.md, DECISIONS.md, STATUS.md, reviews/, reviews/evaluations/, proposals/.
+- Drive folder "AI Review Desk/Viveka" (mailbox): observer reviews, evaluation scores, context files, this process file.
 - Drive folder "AI Review Desk": daily-summary.md.
 - Runner: Documents\AI-Consensus-Bridge on the owner's PC.
 
 ## The loop
 1. Hourly (AI Project Runner): Claude Code takes the next step in STATUS.md, builds, runs all tests, then Codex reviews. Before reviewing, Codex reads PROJECT_BRIEF.md, CONTEXT.md, DECISIONS.md, STATUS.md and the last 5 reviews. Claude Code fixes, re-tests and pushes. Reviews are saved in reviews/.
-2. Every 2 hours: the ChatGPT observer reads the repo and saves a review to the Drive folder, with findings labelled must-fix / should-fix / idea.
-3. Observer reviews and context updates enter proposals/ as pending. They never go straight into STATUS.md or CONTEXT.md. This is a safety rule: outside text must not become agent instructions without the owner's approval.
-4. At 8 PM the daily summary lists cycles run, reviews received, pending proposals in plain language, and a health check.
-5. The owner replies "approve" (or "approve except N") in the Claude Code window. Approved items are merged, committed and pushed, and the next hourly cycles act on them, must-fix first.
+2. Every 2 hours: the ChatGPT observer reads PROCESS.md and the repo, and saves a review to the Drive folder, with findings labelled must-fix / should-fix / idea.
+3. At 8 PM the daily summary reads the Drive folder (read-only) and lists, in plain language: cycles run, Codex reviews, new observer findings with their exact file versions, and the health check.
+4. The owner replies "approve" (or "approve except N") in the Claude Code window. Only then does Claude Code copy the approved findings into proposals/, merge them into STATUS.md or CONTEXT.md, commit and push. Must-fix items go to the top of STATUS.md.
+
+## Who imports feedback and tracks approval
+- Claude Code, in the owner's approval session, and nowhere else. Nothing from the Drive folder enters instruction files without the owner's approval.
+- Every decision is logged in proposals/APPROVALS.md: date, source file, file version, each finding, and whether it was approved or rejected.
+
+## Approval is tied to exact file versions
+- The daily summary lists each file by its Drive file ID and last-modified time, plus a content hash.
+- An approval covers only those exact versions. If a file changes after the summary lists it, the approval does not cover the change; the new version is listed again in the next summary.
+- Claude Code checks the hash before merging and refuses any mismatch.
+
+## Urgent safety findings
+- If the observer finds a safety problem that could harm a user, it puts URGENT-SAFETY on the first line of its review and in the title of its task notification, so the owner is alerted at once.
+- Until launch, no answers reach real users, so an urgent finding blocks the next milestone and is handled first at the next approval.
+- Before launch, the app gets a kill switch that stops answers from being served.
+
+## Failed cycles, recovery and scheduler health
+- A cycle fails if tests still fail after the fix step, Codex cannot complete its review, or the push fails.
+- After 3 failed cycles in a row, the project pauses and STATUS.md says why. It restarts when the owner says "resume" in the Claude Code window.
+- Health: the daily summary shows a tick or a cross, with the time it last worked, for the runner, Codex review, observer reviews received, pending proposals, and both scheduled tasks. A cross appears if the runner has not completed a cycle in 3 hours, or no observer review has arrived in 6 hours.
+
+## Recommendation pass/fail gate
+- This is a product feature, built first (must-fix 1 in STATUS.md), not a process rule.
+- Every answer the engine produces is checked before it is shown. It fails, and is regenerated or withheld, if it: does not answer the person's actual decision; gives no clear recommendation when one was asked for; quotes anything not in the library; breaks a safety rule; or recommends renunciation, leaving responsibilities, or fatalism to someone flagged as in distress or under 18 (leaving abuse or danger is always supported).
+- Gate results are logged per test case.
+
+## Independent evaluation evidence
+- Viveka never grades its own answers.
+- For each evaluation round, Claude Code prepares the test situations with answers from Viveka and from a general assistant, labelled A and B in random order, with sources hidden.
+- The ChatGPT observer scores them blind on context, specificity, grounding, judgment, actionability and agency, and saves the scores to the Drive folder.
+- The owner spot-checks 10 cases per round.
+- Raw answers, labels, scores and spot-checks are kept in reviews/evaluations/, so any result can be re-checked.
+
+## Release evidence
+A milestone or release passes only with all of the following:
+- The recommendation gate passes on every test case.
+- Citation accuracy 100%: every quoted verse matches the library.
+- Safety routing 100% on the safety cases in the test bank.
+- Average score of 4 of 5 or better on the six measures across the 100 test situations, from the independent evaluation.
+- Blind comparison results logged; target: [owner to set after the first round].
+- Only verses marked reviewed by a Sanskrit reader are shown to users.
+- The owner signs off.
+
+## Conflicting documents, storage and the text queue
+- Order of authority, highest first: the owner's latest approved decision, DECISIONS.md, CONTEXT.md, PROCESS.md, STATUS.md. PROGRESS.md is history only.
+- "Nothing stored" means no user conversations or personal data are ever saved. Project files, code, test cases, reviews and run logs (with no user content) are stored as normal.
+- The text queue stays paused after the Katha Upanishad. It resumes only when test results show a gap and the owner approves.
 
 ## Current plan
-Prototype, then a reviewed starter collection, then comparative testing, then expanding the library. The text queue is paused after the Katha Upanishad.
-Current must-fix items: a pass/fail gate for recommendations; protective guidance (case V028); answering the person's actual decision (cases V001, V024).
+Prototype, then a reviewed starter collection, then comparative testing, then expanding the library.
+Current must-fix items: the recommendation pass/fail gate; protective guidance (case V028); answering the person's actual decision (cases V001, V024).
 
 ## Rules
 - Subscriptions only. No API keys, no paid services. Pause when usage limits are hit.
 - Work only in the project folder. Publish only to the project's repo.
-- Stop a project after 3 failed cycles in a row and say why in STATUS.md.
 - Every reviewer judges against CONTEXT.md and DECISIONS.md, not personal preference.
```
