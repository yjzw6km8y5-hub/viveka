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

## Builder handoff (owner instruction, 2026-10-02)
- When Claude Code hits its usage limit, Codex continues as builder from STATUS.md and CONTEXT.md. When Claude's limit resets, Claude Code takes back over.
- A tool never reviews its own work. Codex reviews Claude Code's cycles; Claude Code reviews Codex's cycles when it is back.
- Each tool ends its turn with a short HANDOFF note in STATUS.md. logs/cycles.csv records who built and who reviewed each cycle.

## Independent verse check (owner instruction, 2026-10-02)
- Codex independently checks every verse's English against the Sanskrit (scripts/verse_check.py; results in reviews/verse-check/).
- The owner, who reads Sanskrit, reviews a list of only: verses where Codex disagrees, verses with safety flags, and a fixed 5% random sample. The owner marks them reviewed.

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
