# Viveka: brief for the Claude planning chat

_Updated 2026-10-03 01:30 Eastern Daylight Time by `scripts/brief.py` after a cycle. Repo: https://github.com/yjzw6km8y5-hub/viveka_

## Current status

- **Stage:** prototype. Viveka recommends from verified passages with a pass/fail gate. An LLM writes the final wording (retrieval-augmented generation, prototype on the owner's subscription). Nothing is published; every verse is still a draft.
- **Try it:** on the owner's PC, `python scripts/serve.py`, then open http://127.0.0.1:8765.
- **Next step (from STATUS.md):**

  0. **Owner decisions of 2026-10-03, build now** (CONTEXT.md):
     - **Context-first answer flow:** before recommending, ask about who they live with, where they are and their constraints. Offer a "just answer" option. Show safety and health help at once, and never delay them.
     - **Visual onboarding on the try-it page:**
       - a short Big Five questionnaire, using public-domain IPIP items
       - a Dharma / Artha / Kama / Moksha life map, with Ikigai as an alternative
       - the profile stays in the browser for the visit only; never send or save it
     - Use the profile to tailor answers; add tests; update `claude-chat/BRIEF.md`.
  1. Resume the verse check: `python scripts/verse_check.py run`, then `list` (batches 32-39 remain).
  2. Continue must-fix 1 in small batches: the remaining per-case failures are listed in `tests/results/2026-10-02-guidance-batch.md` (situations 16, held-out v1 5, held-out v2 13). Do not weaken the gate, and do not treat spent-set reruns as fresh evidence; the next unbiased claim needs an independently written held-out set.
  The text queue is paused after the Katha (CLAUDE.md section 10). Do not add or annotate new texts.
  Work the plan instead: reviewed starter collection, then comparative testing (see `tests/README.md`
  and `PROGRESS.md`). Items that need a human reader of Sanskrit are listed at the end of `PROGRESS.md`.
  - After each change: `build_gita.py`, then `validate.py --allow-incomplete`.

## Remaining, by area

| Area | Where it stands | % remaining |
|---|---|---:|
| Upanishads (13 principal) | 3 of 13 done; paused | 77% |
| Niti texts (8 planned) | 2 of 8 done; paused | 75% |
| Sanskrit review by the owner | 0 of 1539 verses reviewed | 100% |
| Codex verse check | 39 of 39 batches | 0% |
| Guidance gate, dev set | 86 of 100 pass (builder-written; not independent) | 14% |
| Guidance gate, held-out v1 | 25 of 30 pass (builder-written; not independent) | 17% |
| Guidance gate, held-out v2 | 17 of 30 pass (builder-written; not independent) | 43% |
| Guidance gate, paired cases | 14 of 14 pass (builder-written; not independent) | 0% |
| Independent test set (30 wanted) | 0 written by the owner; ChatGPT's 30 requested | 100% |
| Blind comparison vs a general assistant | not started (needs baseline answers) | 100% |
| Privacy decision for the LLM step | open: zero data retention or a local model (owner) | 100% |
| Profile storage | open: owner decision (2026-10-03) | 100% |

## Runner log, last 24 hours

- **Cycles:** 6 (5 ok, 1 failed); by builder: codex 1, claude 5.
- **Not yet reviewed by the other tool:** 0.
- **Commits:** 34.
- **Failed:** cycle 4, push blocked by external-transfer approval boundary; local commits ready

<details><summary>Commits</summary>

- 10-03 01:20  Visual try-it page with voice input; LLM writing step (RAG on existing subscription, checked before shown); friend-fight detection; UI screenshots for review
- 10-03 00:49  Local try-it page (scripts/serve.py) with an 'Add a test case' form for the independent test set
- 10-03 00:47  Merge owner-approved proposals [10, 13, 14, 18, 20, 22, 23]; rejected [2, 3, 4, 5, 6, 7, 9, 12, 15, 16, 17, 19, 21]
- 10-02 23:08  Codex review cycle 9 follow-up
- 10-02 23:04  Log cycle 9 (fixes for Codex review of cycle 8)
- 10-02 23:03  Fix Codex review of cycle 8: final fallback fails closed, eating distress by meaning
- 10-02 22:59  Codex review cycle 8 engine fixes
- 10-02 22:54  Fix Codex review of the engine batch: recheck withheld answers, question-specific gate, karma answer, no invented power or motives, meaning-based eating risk, unknown age protected
- 10-02 22:49  Codex review cycle 7 fixes
- 10-02 22:44  Log cycle 7 (fixes for Codex review of Claude)
- 10-02 22:44  Fix Codex review findings: fail-closed self-check, bounded audit cue, remove scratch helper
- 10-02 22:37  Codex review of Claude guidance and self-check changes
- 10-02 22:02  Self-check script, lessons log, CLAUDE.md section 14 (execute, consensus, learn); handoff note
- 10-02 20:29  Frame cue fixes for wrong-principle gate failures (situations 86/100 pass)
- 10-02 20:19  Claude review of Codex cycle 4 (PASS); cycle log; verse check 31/39 batches and owner list; next steps
- 10-02 18:46  Record blocked push in Codex handoff
- 10-02 18:45  Log Codex cycle for Claude review
- 10-02 18:44  Focused gate retries and decision-specific guidance
- 10-02 17:32  Verse check: first results and owner review list (safety-flagged + 5% sample; Codex disagreements added as batches finish)
- 10-02 17:31  Builder handoff rules (AGENTS.md, CLAUDE.md section 13, PROCESS.md); builder/reviewer in cycle log and Health; independent Codex verse check; exact-version check before approval
- 10-02 17:27  Wire gate into answer(), fix minor flag, nonzero exit on gate failure; keep exact review versions by hash; gate unit tests; cycle 3 review response
- 10-02 17:19  Add recommendation pass/fail gate and report it per test case; ignore stray scratch file
- 10-02 17:03  Adopt PROCESS.md v3 (owner approved, 7230 bytes): version-bound approvals with hashes; recommendation pass/fail gate is must-fix 1
- 10-02 16:59  Adopt PROCESS.md v2 (owner approved); APPROVALS.md log; health check in 8 PM summary; cycle log, pause rule and order of authority
- 10-02 16:50  Owner approval gate for outside input: proposals/, scripts/proposals.py, CLAUDE.md section 11
- 10-02 16:46  Add CONTEXT.md (merged reviewer context) and observer must-fix items in STATUS.md (approved by owner)
- 10-02 16:19  Start perspectives: action vs renunciation (draft) with validator checks
- 10-02 15:25  Back out Chanakya Niti (text queue paused after the Katha); builder response to review cycle 1; build and validate (allow-incomplete) pass
- 10-02 15:18  Chanakya Niti: source snapshot, parser, registry and copyright entry (343 verses built)
- 10-02 15:15  Add STATUS.md control file for the AI Project Runner; log decision
- 10-02 10:31  Vidura Niti complete (557 verses); 7 new principles; family-rift and managing frames; commentary danda fix
- 10-02 10:10  Nitishataka complete (109 verses); 9 Niti principles; fatalism flag; nukta transliteration
- 10-02 10:02  Held-out v2 results, always-on safety footer, safety cue fixes, blind comparison tooling
- 10-02 09:57  Answer-engine prototype, 100 test situations, held-out set, examples; honest test log

</details>

## The interface, screen by screen

### Screen 1: Ask (home)
- Header: round "V" logo, title **Viveka**, line "Wisdom for real situations · local test page · not saved".
- Tabs: **Ask** (selected) | **Add a test case**.
- Text box, placeholder: "What's on your mind? Type or tap the mic." Enter sends; Shift+Enter adds a line.
- Under the box, left to right:
  - **Microphone button.** Tap to speak, tap again to stop; the button turns red while recording. On first use a note appears: "Voice is turned into text by your browser's speech service, which may send the audio to its provider."
  - **Age** field (number, optional).
  - **AI-written** checkbox (on by default).
  - **Ask** button.
- Example buttons (tap to ask at once):
  - "I'm nervous about my exam tomorrow"
  - "I had a fight with my best friend"
  - "Should I take the new job or stay?"
  - "I can't get myself to start working"
  - "My parents want me to study medicine but I love art"
  - "I feel jealous of my colleague's promotion"

  They hide after the first question and come back when the box is cleared.
- No onboarding yet, and no follow-up questions before answering (both decided 2026-10-03, not built yet).

### Screen 2: Answer (same page, below the box; it scrolls into view)
1. **Safety card** (red), only for danger or crisis. Title "Your safety first" or "Please reach out now", a message, and help lines with numbers.
2. **Health card** (red), only when eating risk is found. Title "Your health first", then the guidance (a doctor; for under-18s a trusted adult who is safe for them).
3. **"Viveka suggests" card:**
   - a headline (the principle's name)
   - one short paragraph
   - the line "AI is writing a warmer version…", which changes to "✓ written by AI from the passages above, then checked" or to the reason the AI text was not used
   - a green box, **ONE NEXT STEP**, with one action

   When the AI version arrives (40-70 s), it replaces the headline, the paragraph and the next step.
4. **Two cards side by side** (stacked on phones):
   - **YOUR SITUATION:** theme tags (e.g. "fear and anxiety", "focus and study"), "Involves: …", and an **Urgency ring 1-10** with a label ("Time to reflect" 3, "Soon, not rushed" 6, "Health matters soon" 7, "Safety comes first" 9, "Reach out today" 10).
   - **PERSPECTIVES COMPARED (FIT, 1-10):** three bars with the principle names and scores; the top one is orange. Note: "Engine's relative estimate, not a verdict."
5. **Details card** (folding sections):
   - "The text (ID)": open by default, with the English in quotes and the Sanskrit in Devanagari.
   - "Why this fits you", "The other view", "What the commentators say", "A story from the texts".
6. **Footer:** red badge "Draft · N of M quoted verses reviewed by a Sanskrit reader", then the help-line footer (India 112, 14416, 1098, 181; US 988; UK 116 123).

### Screen 3: Add a test case
- Card "Independent test set" with the text: "Write a realistic situation the engine has never seen, and what a good answer must do. Each case is scored once before anyone tunes against it."
- Fields:
  - the situation (text)
  - category: adult / teen / ambiguous / hard
  - safety route: none / support / danger / crisis
  - "What a good answer must do (and must not do)"
  - "Your name or initials"
- Button **Save test case**. The confirmation reads "Saved as I00N · N independent cases so far."

## Screenshots

- [2026-10-03-answer-exam-phone](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/2026-10-03-answer-exam-phone.jpg)
- [2026-10-03-answer-friend-details](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/2026-10-03-answer-friend-details.jpg)
- [2026-10-03-answer-friend-top](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/2026-10-03-answer-friend-top.jpg)
- [2026-10-03-home](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/2026-10-03-home.jpg)

## Open owner decisions

1. **Profile storage** (Big Five answers and the life map): where, if anywhere, they are kept. Until decided, they stay in the browser for that visit only and are never sent or saved.
2. **Privacy for the LLM step:** a zero-data-retention agreement with a provider, or a local model.
3. **Adopting ChatGPT's roadmap** (with Claude's amendments) as PROJECT_BRIEF.md.

