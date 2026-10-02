# Progress

_Last updated: 2026-10-01_

Repo: https://github.com/yjzw6km8y5-hub/viveka (pushed after every batch)

## Current: scope expansion, part a (the 13 principal Upanishads)

The pipeline is generic now (`data/texts.json`, `build_texts.py`, and `validate.py` covering every text).
Snapshots of all 13 Upanishads and 10 Śaṅkara bhāṣyas are in `data/raw/upanishads/`.

| Text | Units | Status |
|---|---:|---|
| Isha | 18 | done (strict VALID) |
| Kena | 35 | done (strict VALID) |
| Katha | 120 | in progress: 1.1.1-1.2.11 annotated (40/120). Next: 1.2.12 onward. Fix: Śaṅkara's comment on 1.2.18 has no 'ए' label, so the parser files the 1.2.19 comment under 1.2.18; split it before writing that note |
| Prashna | | |
| Mundaka | | |
| Mandukya | | |
| Taittiriya | | |
| Aitareya | | |
| Shvetashvatara | | |
| Kaushitaki | | |
| Maitri | | |
| Chandogya | | |
| Brihadaranyaka | | |

Then, in order:
- b. answer-engine prototype
- c. Niti
- d. other Gitas
- e. philosophy
- f. epics and Puranas
- g. bhakti and regional
- h. modern texts (public domain only)
- i. contemporary `view` summaries
- `data/perspectives/`, built up alongside the texts

## Step 1: Bhagavad Gita, complete
All 700 verses of the Bhagavad Gita have English, context, tags, school notes and
safety flags. `python scripts/validate.py` (strict) reports **VALID**.

Every record is `review_status: "draft"`. Nothing has been reviewed by a person yet.

| Ch | Verses | Status |
|---:|---:|---|
| 1 | 47 | done |
| 2 | 72 | done |
| 3 | 43 | done |
| 4 | 42 | done |
| 5 | 29 | done |
| 6 | 47 | done |
| 7 | 30 | done |
| 8 | 28 | done |
| 9 | 34 | done |
| 10 | 42 | done |
| 11 | 55 | done |
| 12 | 20 | done |
| 13 | 34 | done (Rāmānuja commentary realigned, see DECISIONS.md) |
| 14 | 27 | done |
| 15 | 20 | done |
| 16 | 24 | done |
| 17 | 28 | done |
| 18 | 78 | done |

## Library at a glance
- Speakers: Krishna 574, Arjuna 85, Sanjaya 40, Dhritarashtra 1.
- 114 verses have no situation tags (narrative, lists, varna-primary, closing
  verses about the text). They are never offered as advice.
- Safety flags:

  | Flag | Verses |
  |---|---:|
  | war | 81 |
  | death | 55 |
  | under18_hold | 36 |
  | distress_gentle | 25 |
  | caste_gender | 16 |
  | renunciation | 13 |

- Commentary coverage in the source: Śaṅkara 629, Rāmānuja 684, Madhva 398.
  Verses without commentary get no note from that school.

## Done earlier
- Project, source snapshot (Sanskrit Wikisource, pinned revisions), build and validator.
- User decisions of 2026-10-01 applied (see DECISIONS.md):
  - life stages
  - narrative verses
  - under-18 policy
  - the `distress_gentle` flag
  - context and situation limits, now enforced by the validator
- Annotations split into one file per chapter.
- Final sweep: no untranslated epithets remain in the English, except where the
  verse itself uses the name (10.37, "Among the Vrishnis I am Vasudeva").

## Next (needs people, outside this task)
1. Check the 6 verses with irregular metre (2.6, 2.29, 8.10, 11.1, 15.3, 18.51)
   against a printed edition.
2. Human review by someone who reads Sanskrit. This moves records from
   `draft` to `reviewed`, with priority on:
   - verses flagged `under18_hold`, `distress_gentle` or `caste_gender`
   - 7.6, a possible commentary mislabelling in the source
   - chapter 13's realigned Rāmānuja commentary
3. Optionally, a second openly licensed commentary source to fill the gaps in
   school notes (2.59-2.72, 18.78, and the verses where Madhva is sparse).
