# Proposals: the owner's approval gate

Text from outside the repo (ChatGPT observer reviews, context files and process documents in the
Drive folder `AI Review Desk/Viveka`) never goes straight into instruction files: STATUS.md,
CONTEXT.md, CLAUDE.md, PROCESS.md, PROJECT_BRIEF.md or `reviews/`. It waits for the owner's
approval (PROCESS.md v3).

| Path | Holds | In git? |
|---|---|---|
| `pending/` | items waiting for the owner, one numbered file each | no: unapproved text stays local |
| `sources/` | the last imported copy of each desk file, used to detect changes | no |
| `declined/` | items the owner rejected (`restore N` puts one back) | no |
| `state.json` | imported versions, and what the last summary showed | no |
| `approved/` | merged items | yes |
| `APPROVALS.md` | every decision: date, source file, finding, approved or rejected | yes |

## How it runs
1. **8 PM:** `python scripts/proposals.py import`, then `python scripts/proposals.py summary`.
   - The summary starts with the Health section, then lists the pending items in plain language,
     each with the exact desk file version it came from (name, modified time, size, SHA-256).
   - An approval covers only those versions; `approve` refuses any item whose content no longer
     matches its hash. Every decision is logged with its version in APPROVALS.md.
   - Import splits observer reviews into one item per must-fix, should-fix or idea finding.
   - A changed context file becomes one item containing only its new lines.
   - PROCESS.md and PROJECT_BRIEF.md become items to add or replace that file at the repo root. Drive re-upload names such as "PROCESS (1).md" are treated as the same file.
2. **The owner replies** "approve" or "approve except 2 5". The builder then runs
   `python scripts/proposals.py approve [--except 2 5] --push`, which:
   - merges exactly the items shown in that summary (anything that arrived later waits for the next one)
   - puts must-fix items first in STATUS.md
   - archives the full review in `reviews/` once any of its items is approved
   - logs every decision in APPROVALS.md, then commits and pushes
3. `approve --only N` approves single items and leaves the rest pending. `decline N --reason "..."` rejects one.

The owner's approval is the only way outside text reaches an instruction file.
