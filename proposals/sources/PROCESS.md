# Viveka build-and-review process (v1, 2026-10-02)

The single agreed description of how Viveka is built and reviewed. Every participant follows this. Changes need the owner's approval.

## Roles (each in one fixed place)
| Role | Who | Where | Does |
|---|---|---|---|
| Owner | The project owner | Daily summary + Claude Code window | Sets intent, approves proposals once a day |
| Builder | Claude Code | Owner's PC, project folder | Builds the next step in STATUS.md, tests, pushes |
| Code and direction reviewer | Codex | Owner's PC, run by the AI Project Runner | Reviews every cycle's changes against the brief and context |
| Independent observer | ChatGPT, Viveka project chat only | ChatGPT scheduled task, every 2 hours | Reviews progress, quality, safety and fidelity to the vision |
| Planner and milestone checker | Claude, Viveka project chat only | claude.ai | Planning, and checks when the owner says "check Viveka" |

No reviews happen in any other chat or window.

## Where things live
- GitHub repo (single source of truth): https://github.com/yjzw6km8y5-hub/viveka. Code, data, CONTEXT.md, DECISIONS.md, STATUS.md, reviews/, proposals/.
- Drive folder "AI Review Desk/Viveka" (mailbox): observer reviews, context files, this process file.
- Drive folder "AI Review Desk": daily-summary.md.
- Runner: Documents\AI-Consensus-Bridge on the owner's PC.

## The loop
1. Hourly (AI Project Runner): Claude Code takes the next step in STATUS.md, builds, runs all tests, then Codex reviews. Before reviewing, Codex reads PROJECT_BRIEF.md, CONTEXT.md, DECISIONS.md, STATUS.md and the last 5 reviews. Claude Code fixes, re-tests and pushes. Reviews are saved in reviews/.
2. Every 2 hours: the ChatGPT observer reads the repo and saves a review to the Drive folder, with findings labelled must-fix / should-fix / idea.
3. Observer reviews and context updates enter proposals/ as pending. They never go straight into STATUS.md or CONTEXT.md. This is a safety rule: outside text must not become agent instructions without the owner's approval.
4. At 8 PM the daily summary lists cycles run, reviews received, pending proposals in plain language, and a health check.
5. The owner replies "approve" (or "approve except N") in the Claude Code window. Approved items are merged, committed and pushed, and the next hourly cycles act on them, must-fix first.

## Current plan
Prototype, then a reviewed starter collection, then comparative testing, then expanding the library. The text queue is paused after the Katha Upanishad.
Current must-fix items: a pass/fail gate for recommendations; protective guidance (case V028); answering the person's actual decision (cases V001, V024).

## Rules
- Subscriptions only. No API keys, no paid services. Pause when usage limits are hit.
- Work only in the project folder. Publish only to the project's repo.
- Stop a project after 3 failed cycles in a row and say why in STATUS.md.
- Every reviewer judges against CONTEXT.md and DECISIONS.md, not personal preference.
