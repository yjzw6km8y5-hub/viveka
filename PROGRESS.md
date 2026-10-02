# Progress

_Last updated: 2026-10-02_

Repo: https://github.com/yjzw6km8y5-hub/viveka (pushed after every batch)

## Current plan (2026-10-02): prove the guidance before expanding
Sequence: prototype, reviewed starter collection, comparative testing, then library expansion.
The text queue is paused after the Katha.

| Step | Status |
|---|---|
| Finish the Katha | done |
| Safety rule fix (support leaving abuse or danger; help lines) | done |
| Privacy check of the AI provider | done: default API terms keep data up to 30 days, so the engine runs locally (DECISIONS.md) |
| `data/principles/` (165 principles, validated) | done (draft) |
| `data/examples/` (17: 14 stories from the texts, 3 historical cases not yet verified) | done (draft) |
| Answer-engine prototype (`engine/`, `scripts/ask.py`; local only) | done, needs improvement (see below) |
| 100 test situations and scoring (`data/tests/`, `scripts/run_tests.py`) | done |
| Blind comparison with a general assistant and similar apps | tooling ready; blocked on baseline answers and raters |
| Resume the text queue, gaps first (Niti texts) | in progress |

### Text queue (gaps first)
| Text | Units | Status |
|---|---:|---|
| Nitishataka (Bhartrihari) | 109 | done: strict VALID, 9 new principles linked; source lacks verse 7 |
| Vidura Niti | 557 | done: strict VALID; 7 new principles, 2 new frames (family rift, managing people); 2 speaker fixes |
| Chanakya Niti | | next |
| Hitopadesha (stories, as examples) | | |
| Tirukkural | | needs Tamil-script support |

## Test log

The scores are automatic proxies (0-2 per dimension, 12 maximum), not human judgements.

**2026-10-02, development set (100 situations, used while building the engine):** mean 11.38 / 12.

| Dimension | Score |
|---|---:|
| context | 1.85 |
| specificity | 1.63 |
| grounding | 2.00 |
| judgment | 1.91 |
| actionability | 2.00 |
| agency | 1.99 |

- 0 safety-path mismatches.
- 0 uses of forbidden material.
- These numbers are inflated, because the engine's problem types were tuned on this set.

**2026-10-02, held-out set v1 (30 new situations, scored once with no tuning):** mean 9.07 / 12.

| Dimension | Score |
|---|---:|
| context | 1.67 |
| specificity | 1.03 |
| grounding | 2.00 |
| judgment | 0.67 |
| actionability | 2.00 |
| agency | 1.70 |

- **5 safety misses:** a crisis ("no will to live"), online grooming, a shared embarrassing photo, emotional numbness, and karma-shame about a disability.
- **9 answers had no recommendation:** the engine fell back to asking a question.
- **Conclusion:** keyword and problem-type detection does not generalise well. This is the honest estimate of the current prototype.

**2026-10-02, after general fixes made on top of held-out v1** (now spent): development set 11.33, held-out v1 11.23.

**2026-10-02, held-out set v2 (30 new situations, scored once with no tuning):** mean 10.30 / 12.

| Dimension | Score |
|---|---:|
| context | 1.90 |
| specificity | 1.47 |
| grounding | 2.00 |
| judgment | 0.93 |
| actionability | 2.00 |
| agency | 2.00 |

- **4 safety misses:**
  - a crisis: "better off with the insurance money if I wasn't here"
  - elder financial abuse
  - an eating-disorder sign
  - a distress case: drinking every night
- **1 false alarm.**
- **Changes since:**
  - Safety cues were widened, so v2 is now spent: all three sets now show 0 safety mismatches and 0 uses of forbidden material.
  - An **always-on safety footer** now gives help lines on every answer, because detection will miss some people.

**2026-10-02, after adding the Vidura Niti** (regression check only; all sets are spent): development set 11.27, held-out v1 11.23, held-out v2 10.53. 0 safety mismatches and 0 forbidden material on every set.

Grounding (every quote is exact library text, with labels) held at 2.00 on every set.

### What the tests show
1. **Grounding, labelling and safety filtering work.** No forbidden or held passages are quoted, and missing commentaries are always stated.
2. **Understanding is the weak link.** Fresh held-out judgment is about 0.7-0.9 out of 2. Rule-based detection of problem types and of crisis language does not generalise well.
   - The realistic fix is a model-based understanding step. That needs either a zero-data-retention agreement with an AI provider (a cost and contract decision for the owner; see DECISIONS.md) or an on-device model.
   - Either way, a clinically informed review of the crisis-language list is needed.
3. **Content gaps** (situations the library answers only thinly):
   - family hierarchy (in-laws, dowry, inheritance, elder care)
   - practical communication and friendship
   - money management
   - body image and health
   - workplace fairness and prejudice
   - grief for non-human loss
   - sexuality and identity

   The Niti texts (Tirukkural, Vidura Niti, Bhartrihari's Nitishataka, Hitopadesha) speak most directly to the first five. So the text queue resumes with them.

### Blocked or waiting on the owner
- **Blind comparison** with a general assistant and similar apps: tooling is ready (`scripts/make_blind_packet.py`, `tests/README.md`). It needs baseline answers (collected by hand or through a paid API) and human raters.
- **A fresh held-out set** written by someone other than the engine's author.
- **The reviewed starter collection:** a human reviewer who reads Sanskrit must move records from `draft` to `reviewed`. Until then, public mode shows no passages.

## Paused: scope expansion, part a (the 13 principal Upanishads)

The pipeline is generic now (`data/texts.json`, `build_texts.py`, and `validate.py` covering every text).
Snapshots of all 13 Upanishads and 10 Śaṅkara bhāṣyas are in `data/raw/upanishads/`.

| Text | Units | Status |
|---|---:|---|
| Isha | 18 | done (strict VALID) |
| Kena | 35 | done (strict VALID) |
| Katha | 120 | done (strict VALID) |
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
