# Status

_Control file for the AI Project Runner. Detailed history stays in PROGRESS.md._

## Next step
Annotate Chanakya Niti (`data/annotations/chanakya_niti.json`, 343 verses, ids
`CN.<chapter>.<n>`), about one chapter per cycle, following CLAUDE.md sections 1 to 7
and the Nitishataka/Vidura model.
- After each batch: run strict validation on that batch's verses.
- Verses come from `data/`, never from memory. The source gives no speaker; decide and log it.

## Done recently
- Vidura Niti complete (557 verses), strict validation passing.
- Chanakya Niti: source chosen, copyright logged, snapshot in `data/raw/niti/`, parser and
  registry added (343 verses built, none annotated yet).

## Runner notes
_(the runner writes here if it has to stop the project)_
