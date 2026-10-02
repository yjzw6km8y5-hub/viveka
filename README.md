# Viveka: verse library

Viveka answers a person's life situation with verses from Hindu scripture.
It is free, it is privacy-first, and it stores no user data.

**Rule:** every verse the app quotes must come from this library, never from an
AI model's memory. The model may *choose* verses and *explain* them, but the
Sanskrit, transliteration and translation shown to the user are always read
from `data/`.

Step 1, the Bhagavad Gita (700 verses), is complete and passes strict validation.
The scope now covers Indian wisdom texts from the Vedas to today, built one text
at a time through the same pipeline (see `PROGRESS.md`). Every text is listed in
`data/texts.json`, and the copyright of each source is logged below.
All records are `draft` until a human reviewer checks them (see Review policy).

### Other texts

| Path | What it is |
|---|---|
| `data/<text_id>.json` | built library for each text in `data/texts.json` (fields as below, plus `text`, `ref` and `cross_refs`) |
| `data/commentaries/<text_id>.json` | commentary extracts for checking school notes |
| `data/annotations/<text_id>.json` | editorial fields (hand-written) |
| `data/raw/upanishads/` | Wikisource snapshots |
| `scripts/build_texts.py` | builds every registry text |
| `scripts/fetch_upanishads.py` | refreshes the Upanishad snapshots |
| `scripts/show_text.py` | prints units with commentary, for annotators |

`python scripts/validate.py` checks the Gita and every registry text.

## Layout

```
data/
  raw/ch01.json … ch18.json   Wikisource snapshots (wikitext + revision IDs)
  annotations/ch01-ch18.json  editorial fields, one file per chapter, keyed by verse ID (hand-written)
  speaker_corrections.json    documented fixes where the source omits a speaker line
  vocab.json                  controlled vocabularies (situations, flags, …)
  gita.json                   BUILT: the verse library (do not edit by hand)
  gita_commentaries.json      BUILT: Sanskrit bhāṣyas of Śaṅkara, Rāmānuja, Madhva
scripts/
  fetch_wikisource.py         download the 18 chapter pages into data/raw/
  build_gita.py               raw + annotations -> gita.json
  validate.py                 check gita.json
  translit.py                 Devanagari -> IAST
```

All scripts use only the Python 3 standard library.

## Workflow

```bash
python scripts/fetch_wikisource.py      # only to refresh the source snapshot
python scripts/build_gita.py
python scripts/validate.py              # strict: fails until every verse is written
python scripts/validate.py --allow-incomplete
```

Text fields come **only** from the snapshot. Editorial fields come **only** from
`data/annotations/chNN.json`. The build refuses annotations that try to set a
text field, so a translator can never overwrite the Sanskrit by accident.

## Source and licence

| | |
|---|---|
| Source | Sanskrit Wikisource, [भगवद्गीता](https://sa.wikisource.org/wiki/भगवद्गीता) and its 18 chapter subpages |
| Revisions | pinned per chapter in `data/raw/chNN.json` (`revid`, `permalink`) and in each record's `source` |
| Retrieved | 2026-10-01 |
| Licence | Wikisource text: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The Gita and the classical commentaries are public domain. |

What CC BY-SA requires of us:
- **Attribution:** wherever Viveka shows Sanskrit text, credit "Sanskrit Wikisource" with a link.
- **ShareAlike:** `gita.json` and `gita_commentaries.json` are derived from CC BY-SA text,
  so the whole `data/` folder is released under CC BY-SA 4.0.

**Licences of this repository** (see `LICENSE`):
- **Code** (`scripts/` and any app code): MIT.
- **Data** (`data/`): CC BY-SA 4.0. This covers our English, contexts and notes, and the Wikisource-derived text.

The `english` field is our own wording, translated from the Sanskrit. It is not
copied from any published translation.

## Copyright register

Every source is checked before use. A text goes in only if the work itself is
public domain and the digital edition we copy from is openly licensed.

| Text | Library file | Digital source | Licence of source | Work's status | Checked |
|---|---|---|---|---|---|
| Bhagavad Gita, with Śaṅkara, Rāmānuja and Madhva | `gita.json` | Sanskrit Wikisource (pinned revisions) | CC BY-SA 4.0 | Public domain (ancient/medieval) | 2026-10-01 |
| 13 principal Upanishads | `<name>_upanishad.json` | Sanskrit Wikisource (pinned revisions, `data/raw/upanishads/`) | CC BY-SA 4.0 | Public domain (ancient) | 2026-10-01 |
| Nitishataka of Bhartrihari (109 verses) | `nitishataka.json` | Sanskrit Wikisource, `नीतिशतकम्` (pinned revision, `data/raw/niti/`) | CC BY-SA 4.0 | Public domain (c. 5th century) | 2026-10-02 |
| Vidura Niti (Mahabharata, Udyoga Parva; 557 verses) | `vidura_niti.json` | Sanskrit Wikisource, `विदुरनीतिः` (revision 37534, `data/raw/niti/`) | CC BY-SA 4.0 | Public domain (ancient) | 2026-10-02 |
| Chanakya Niti (Cāṇakyanītidarpaṇa; 343 verses) | `chanakya_niti.json` | Sanskrit Wikisource, `चाणक्यनीतिदर्पणः` (revision 330162, `data/raw/niti/`) | CC BY-SA 4.0 | Public domain (attributed to Chanakya, c. 3rd century BCE to 3rd century CE; this recension is a medieval compilation) | 2026-10-02 |
| Śaṅkara's Upanishad bhāṣyas | `commentaries/<name>_upanishad.json` | Sanskrit Wikisource, `उपनिषद्भाष्यम्` pages | CC BY-SA 4.0 | Public domain (8th century) | 2026-10-01 |

**Not used:**
- **Raṅga Rāmānuja's Upanishad commentaries.** Wikisource has them only as scans of a
  1949 printed edition. We'd need to check that edition's own copyright first.
- **GRETIL and sanskritdocuments.org texts.** Their terms don't clearly allow redistribution under CC BY-SA.

## Record schema (`data/gita.json`)

| Field | Type | From | Notes |
|---|---|---|---|
| `id` | string | source | `BG.<chapter>.<verse>`, e.g. `BG.2.47` |
| `chapter`, `verse` | int | source | |
| `speaker` | string | source | `Dhritarashtra`, `Sanjaya`, `Arjuna`, `Krishna`, taken from the `… उवाच` lines |
| `context` | string | editorial | one sentence, at most 30 words: where we are in the dialogue |
| `devanagari` | string | source | verse lines joined by `\n`, ending `॥` |
| `iast` | string | generated | mechanical transliteration of `devanagari`; the validator checks they match |
| `english` | string | editorial | plain modern English, our own wording |
| `situations` | list | editorial | 1-4 from the vocabulary; empty for narrative, list and varna-primary verses, which are never offered as advice |
| `life_stages` | list | editorial | `student`, `householder`, `elder`, `renunciant` |
| `aims` | list | editorial | `dharma`, `artha`, `kama`, `moksha` |
| `school_notes` | list | editorial | `{school, commentator, note}`; each must have source commentary in `gita_commentaries.json` |
| `safety_flags` | list | editorial | `war`, `death`, `renunciation`, `under18_hold`, `distress_gentle`, `caste_gender`, `fatalism` (definitions in `data/vocab.json`) |
| `source` | object | source | name, page, url, revision, permalink, retrieved |
| `licence` | string | source | |
| `review_status` | string | editorial | `draft` → `reviewed` → `approved` |

Situations: `grief_loss`, `fear_anxiety`, `anger_resentment`, `failure_setback`,
`lack_of_motivation`, `conflict_of_duties`, `relationships_forgiveness`,
`ego_pride_envy`, `temptation_self_control`, `success_wealth`, `purpose_meaning`,
`ageing_death_impermanence`. Definitions are in `data/vocab.json`.

### School notes

Each note summarises what that school's founding commentary actually says on the
verse: Śaṅkara (Advaita), Rāmānuja (Viśiṣṭādvaita) or Madhva (Dvaita). The
Sanskrit commentary is extracted from the same Wikisource pages into
`gita_commentaries.json`, so a reviewer can check every note against its source.
Coverage: Śaṅkara 629 verses, Rāmānuja 684, Madhva 398. Not every commentator
discusses every verse; where one is silent, leave the note out.

## Data notes

- **Chapter 13** follows the 34-verse recension, which has no opening Arjuna verse. Totals are exactly 700.
- **Speaker fix:** the page omits `श्रीभगवानुवाच` before 5.2, so 5.2-5.29 would inherit Arjuna.
  The fix and its evidence are in `data/speaker_corrections.json`.
  Resulting counts: Krishna 574, Arjuna 85, Sanjaya 40, Dhritarashtra 1.
- **Mid-verse speaker changes:** in 1.21 and 1.28, the first line is Sanjaya narrating ("…he said, O king")
  and Arjuna's words begin in the second line. The source credits the whole verse to Arjuna, and so do we.
  Many editions count one of these for Sanjaya, which gives the often-quoted 84/41 split.
  Mention the change in `context` when writing those verses.
- **Irregular metre:** most verses have 32 syllables (anuṣṭubh) or 44 (triṣṭubh).
  The build lists six that don't: 2.6, 2.29, 8.10, 11.1, 15.3, 18.51.
  These are probably genuine irregularities, but check them against a printed edition during review.
- **IAST** keeps sandhi and word-joining exactly as in the Devanagari (`karmaṇyevādhikāraste`).
  It uses `ṃ` for anusvāra.

## Review policy

All records start as `draft`. Before a verse can be shown to users, a human
reviewer who reads Sanskrit should check the `english`, `school_notes` and
`safety_flags` and set `review_status` to `reviewed`. The app should only serve
`reviewed` or `approved` verses.
