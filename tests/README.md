# Testing Viveka's answers

## Test sets (in `data/tests/`)

| Set | Size | Role |
|---|---:|---|
| `situations.json` | 100 | Development set: adult, teen, ambiguous and hard cases. Used while building the engine, so its scores are optimistic. |
| `heldout.json` | 30 | Held-out v1. Scored once before any tuning, then used for tuning, so it is now spent. |
| `heldout2.json` | 30 | Held-out v2. Scored once (10.30 / 12), then used for safety-cue fixes, so it is now spent. |

The next unbiased check needs a **new held-out set written by someone other than the engine's author**. A model writing both the tests and the engine is a known source of bias.

Each case lists what an acceptable answer looks like:
- `safety`: the expected safety path (`crisis`, `danger`, `support` or none)
- `principles_any`: acceptable top principles
- `forbid_principles`: principles that must not be recommended
- `forbid_flags`: verse flags that must never be quoted

## Automatic scores (`python scripts/run_tests.py --set NAME`)

Each dimension is scored 0-2:
- **context:** the situation, age and minor status are read correctly
- **specificity:** the application refers to this person's details
- **grounding:**
  - every quote is exact library text
  - every part is labelled
  - missing commentaries are stated
  - nothing forbidden is quoted
- **judgment:**
  - the top principle is acceptable
  - nothing forbidden is used
  - the safety path is right
- **actionability:** one concrete next step
- **agency:** a real alternative is offered, and the choice stays with the person

These are proxies. They can tell a broken answer from a working one, but not a good answer from a great one.

## Blind comparison (`python scripts/make_blind_packet.py NAME`)

1. **Collect baseline answers.** For each situation, paste the exact text into each comparison tool (e.g. a general assistant, or similar wisdom or advice apps) in a fresh chat with no other context. Save the answers as `tests/baselines/<tool>/<set>.json` in the form `{"T001": "answer text", ...}`.
2. **Build the packet.** Run the script. It shuffles the answers into anonymous A/B/C labels and strips Viveka's draft banner. The key goes in `key.json`.
3. **Rate.** At least two raters, who don't see `key.json`, fill in `ratings.csv`. A good mix is someone who knows the texts and someone who doesn't.
4. **Score.** Unblind using the key and compare the mean per dimension. Report where raters disagreed.

Collecting baselines through a paid API, or paying raters, costs money, so it needs the project owner's approval.
