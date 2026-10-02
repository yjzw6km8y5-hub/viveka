# Viveka: standing rules

Viveka answers a person's life situation with verified verses from Hindu
scripture. See README.md for the data layout and schema.

## 1. Validate after every change
- After every change, run `python scripts/build_gita.py`, then `python scripts/validate.py`.
- Fix any failure yourself before moving on or reporting back.
- While the library is still being written, use `python scripts/validate.py --allow-incomplete`.
  In that mode, empty `english`/`context` on not-yet-written verses are warnings.
  Every other check must pass, and so must all verses you have written.
- Before saying a batch is finished, run strict mode on the verses in that batch.
- If `python` is not on PATH, use `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`.

## 2. Review before showing anything
Before showing the user any verse, record or summary, check it against these rules:
- **Verses come from `data/`, never from memory.**
  - Copy Sanskrit and IAST from `data/gita.json`; never retype or recall them.
  - Never edit `devanagari`, `iast`, `speaker` or `source` by hand. They come from
    `data/raw/` through the build. Speaker fixes go in `data/speaker_corrections.json`
    with evidence from the snapshot.
  - `school_notes` must summarise the commentary text in `data/gita_commentaries.json`
    for that verse. If that commentator has nothing on the verse, leave the note out.
- **Speaker and context must be correct.**
  - Check the speaker against the `… उवाच` lines and the dialogue.
  - `context` must describe where the verse sits in the dialogue, and must be
    accurate for that exact verse.
  - Note mid-verse speaker changes (e.g. 1.21, 1.28) in `context`.
- **English must be plain and faithful to the Sanskrit.**
  - Use modern, everyday words, in our own wording. Don't copy published translations.
  - Add nothing the Sanskrit doesn't say, and leave out nothing it does say.
  - Don't soften or modernise the meaning. Interpretation belongs in `school_notes`, not `english`.

## 3. Technical choices: decide, don't ask
- Don't ask the user about technical choices (code, file formats, tooling, schema
  mechanics, validation rules).
- Make the call and record it in `DECISIONS.md`: date, decision, why.

## 4. Don't stop to ask; keep going
- Don't stop to ask the user anything. Decide using these rules and the project
  principles (verified verses only, faithful English, privacy, user safety).
- Log every decision in `DECISIONS.md`, including ones that change what users see.
- Keep working in batches until all 700 verses are done and strict validation passes.
- **Only stop if something costs money or publishes** (paid services, purchases,
  posting, sharing or deploying anything).

## Editorial standards (user-approved, 2026-10-01)
- **context:** one sentence, at most 30 words.
- **situations:**
  - Narrative verses (scene-setting, lists of warriors, Sanjaya's reporting) get none
    and are never offered as advice.
  - Every other verse gets 1-4.
- **life_stages:** the four traditional stages only: `student`, `householder`, `elder`, `renunciant`.
- **under18_hold:** whenever a verse presents death as harmless, urges fighting, or
  urges leaving family or the world.
- **distress_gentle:** verses that could deepen self-blame in someone who is
  struggling (e.g. 6.5, "you alone are your own enemy").
- The five sample records (1.1, 2.20, 2.37, 2.47, 6.5) are the approved model for style and depth.

## 5. Keep PROGRESS.md current
After each piece of work, update `PROGRESS.md` with what's done and what's next.
