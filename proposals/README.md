# Proposals: the owner's approval gate

Text from outside the repo (ChatGPT observer reviews, context files and process documents in the
Drive folder `AI Review Desk/Viveka`) never goes straight into instruction files: STATUS.md,
CONTEXT.md, CLAUDE.md, PROCESS.md, PROJECT_BRIEF.md or `reviews/`. It waits here until the owner approves it.

| Folder | Holds |
|---|---|
| `pending/` | proposals waiting for the owner, one file each, numbered |
| `approved/` | merged proposals |
| `declined/` | proposals the owner left out (`restore N` puts one back) |
| `sources/` | the last imported copy of each desk file, used to detect changes |
| `state.json` | which desk versions were imported and what the last summary showed |

## How it runs
1. `python scripts/proposals.py import`: new or changed desk files become pending proposals.
   - Observer reviews are split into one proposal per must-fix, should-fix or idea item.
   - A changed context file becomes one proposal containing only its new lines.
   - PROCESS.md and PROJECT_BRIEF.md become proposals to add or replace that file at the repo root.
2. At 8 PM, `python scripts/proposals.py summary` lists the pending proposals in plain language.
3. The owner replies "approve" or "approve except 2 5". The builder then runs
   `python scripts/proposals.py approve [--except 2 5] --push`, which:
   - merges exactly the proposals shown in that summary (anything that arrived later waits for the next one)
   - puts must-fix items first in STATUS.md
   - archives the full review in `reviews/` once any of its items is approved
   - commits and pushes

The owner's approval is the only way outside text reaches an instruction file.
