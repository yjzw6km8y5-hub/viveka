```json
{
  "id": 11,
  "kind": "doc",
  "target": "repo root",
  "title": "Add PROCESS.md v2",
  "summary": "PROCESS.md v2 (the version the owner approved in chat)",
  "source": "AI Review Desk/Viveka/PROCESS (1).md",
  "imported": "2026-10-02 16:58",
  "doc_file": "PROCESS.md",
  "version": "2026-10-02 16:52, 5605 bytes, sha256 0ab0b1b8ba4f"
}
```

# Viveka build-and-review process (v2, 2026-10-02)

The single agreed description of how Viveka is built and reviewed. Version 2 resolves the six gaps ChatGPT raised in PROCESS_AGREEMENT_chatgpt.md. Every participant follows this. Changes need the owner's approval.

## Roles (each in one fixed place)
| Role | Who | Where | Does |
|---|---|---|---|
| Owner | The project owner | Daily summary + Claude Code window | Sets intent, approves proposals once a day |
| Builder | Claude Code | Owner's PC, project folder | Builds the next step in STATUS.md, tests, pushes; imports proposals at approval time |
| Code and direction reviewer | Codex | Owner's PC, run by the AI Project Runner | Reviews every cycle's changes against the brief and context |
| Independent observer | ChatGPT, Viveka project chat only | One ChatGPT scheduled task, every 2 hours | Reads PROCESS.md first on every run, then reviews progress, quality, safety and fidelity to the vision |
| Planner and milestone checker | Claude, Viveka project chat only | claude.ai | Planning, and checks when the owner says "check Viveka" |

No reviews happen in any other chat or window. Any older or overlapping scheduled checks are switched off; the 2-hour observer task is the only scheduled ChatGPT review.

## Where things live
- GitHub repo (single source of truth): https://github.com/yjzw6km8y5-hub/viveka. Code, data, CONTEXT.md, DECISIONS.md, STATUS.md, reviews/, proposals/.
- Drive folder "AI Review Desk/Viveka" (mailbox): observer reviews, context files, this process file.
- Drive folder "AI Review Desk": daily-summary.md.
- Runner: Documents\AI-Consensus-Bridge on the owner's PC.

## The loop
1. Hourly (AI Project Runner): Claude Code takes the next step in STATUS.md, builds, runs all tests, then Codex reviews. Before reviewing, Codex reads PROJECT_BRIEF.md, CONTEXT.md, DECISIONS.md, STATUS.md and the last 5 reviews. Claude Code fixes, re-tests and pushes. Reviews are saved in reviews/.
2. Every 2 hours: the ChatGPT observer reads PROCESS.md and the repo, and saves a review to the Drive folder, with findings labelled must-fix / should-fix / idea.
3. At 8 PM the daily summary reads the Drive folder (read-only) and lists, in plain language: cycles run, Codex reviews, new observer findings, and the health check.
4. The owner replies "approve" (or "approve except N") in the Claude Code window. Only then does Claude Code copy the approved findings into proposals/, merge them into STATUS.md or CONTEXT.md, commit and push. Must-fix items go to the top of STATUS.md.

## Who imports feedback and tracks approval (gap 2)
- Claude Code, in the owner's approval session, and nowhere else. Nothing from the Drive folder enters instruction files without the owner's approval.
- Every decision is logged in proposals/APPROVALS.md: date, source file, each finding, and whether it was approved or rejected.

## Urgent safety findings (gap 3)
- If the observer finds a safety problem that could harm a user, it puts URGENT-SAFETY on the first line of its review and in the title of its task notification, so the owner is alerted at once rather than at 8 PM.
- Until launch, no answers reach real users, so an urgent finding blocks the next milestone and is handled first at the next approval.
- Before launch, the app gets a kill switch that stops answers from being served.

## Failed cycles, recovery and scheduler health (gap 4)
- A cycle fails if tests still fail after the fix step, Codex cannot complete its review, or the push fails.
- After 3 failed cycles in a row, the project pauses and STATUS.md says why. It restarts when the owner says "resume" in the Claude Code window.
- Health: the daily summary shows a tick or a cross, with the time it last worked, for the runner, Codex review, observer reviews received, pending proposals, and both scheduled tasks. A cross appears if the runner has not completed a cycle in 3 hours, or no observer review has arrived in 6 hours.

## Evidence for guidance quality and release (gap 5)
A milestone or release passes only with all of the following:
- Citation accuracy 100%: every quoted verse matches the library.
- Safety routing 100% on the safety cases in the test bank.
- Average score of 4 of 5 or better on context, specificity, grounding, judgment, actionability and agency across the 100 test situations.
- A blind comparison against a general assistant, with the results logged and target: [owner to set after the first round].
- Only verses marked reviewed by a Sanskrit reader are shown to users.
- The owner signs off.

## Conflicting documents, storage and the text queue (gap 6)
- Order of authority, highest first: the owner's latest approved decision, DECISIONS.md, CONTEXT.md, PROCESS.md, STATUS.md. PROGRESS.md is history only.
- "Nothing stored" means no user conversations or personal data are ever saved. Project files, code, test cases, reviews and run logs (with no user content) are stored as normal.
- The text queue stays paused after the Katha Upanishad. It resumes only when test results show a gap and the owner approves.

## Current plan
Prototype, then a reviewed starter collection, then comparative testing, then expanding the library.
Current must-fix items: a pass/fail gate for recommendations; protective guidance (case V028); answering the person's actual decision (cases V001, V024).

## Rules
- Subscriptions only. No API keys, no paid services. Pause when usage limits are hit.
- Work only in the project folder. Publish only to the project's repo.
- Every reviewer judges against CONTEXT.md and DECISIONS.md, not personal preference.
