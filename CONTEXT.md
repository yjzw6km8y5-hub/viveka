# Viveka: shared context for builders and reviewers

_Updated: 2026-10-02. Merged from `AI Review Desk/Viveka/CONTEXT_claude.md` and `CONTEXT_chatgpt.md`, plus the repo's CLAUDE.md and DECISIONS.md._

Read this before judging any Viveka work, together with STATUS.md, DECISIONS.md and the latest files in `reviews/`.
Owner decisions are marked as decisions. Reviewer suggestions stay proposals until the owner accepts them.

## Vision (owner)
- A guide for tough times. A person aged 13 to 80+ describes their real situation. Viveka understands it, weighs the relevant wisdom, explains disagreements, recommends a course of action and suggests one next step, while preserving the person's agency.
- Grounded first in Indian wisdom, from the Vedas to contemporary thinkers. Later: other philosophies (Greek first), then optional persona lenses.
- Not Krishna-centric. Viveka quotes and explains texts; it never speaks as Krishna or any deity.
- Not a guru, therapist or substitute for professional help.

## Fixed decisions (owner)
- **Name:** Viveka (a small same-name app exists; mitigate with distinctive handles and a trademark search before launch).
- **Audience:** global, minimum age 13. Users aged 13-17 get gentler framing and no verses on war or renunciation.
- **Funding:** free with donations, no ads. Existing subscriptions only: no paid APIs, extra billing or paid services without the owner's approval.
- **Privacy:** no accounts, no saved conversations. Session context may exist temporarily but is never stored. The AI provider's data terms must match this (see DECISIONS.md; the engine currently runs locally).
- **Open library:** the verse library is published under CC BY-SA 4.0 so anyone can verify every verse.
- **Sources:** Sanskrit from Sanskrit Wikisource at pinned revisions. English renderings are our own. GRETIL is for cross-checking only.
- **Schools:** pluralist. If a school's commentary is missing for a text, say so; never present uneven coverage as consensus.
- **Editorial:** four traditional life stages, kept separate from age. Narrative verses get no situations and are never offered as advice. Context is one sentence of at most 30 words; 1-4 situations per verse.
- **Safety flags:** war, death, renunciation, under18_hold, distress_gentle, caste_gender, fatalism (definitions in `data/vocab.json`). Varna and gender verses are never offered as advice.

## Conflicting views (owner)
- Explain why views conflict, then recommend the one that fits this person's situation and say why, then name the strongest alternative. Recommend by fit, never by declaring one school true. Never average philosophies into one answer.
- **Safety overrides fit:** never recommend renunciation, abandoning responsibilities or fatalism to anyone in distress or under 18. Always support leaving abuse or danger and point to help; leaving an unsafe home is never framed as abandoning duty.

## Guardrails (owner)
- Quote only library text, with an automated citation check.
- Safety screen before scripture: risk signs route to human help (localised help lines) first.
- Never tell anyone their suffering is deserved karma.
- Label every part of an answer: source text / commentator's view / historical example / Viveka's application.
- Users see only reviewed or approved material; drafts stay internal.

## Current plan (owner, 2026-10-02)
- **Sequence:** prototype, then a reviewed starter collection, then comparative testing, then library expansion. The text queue is paused after the Katha Upanishad. (Nitishataka and Vidura Niti were added before review cycle 1 enforced the pause; Chanakya Niti was backed out.)
- **Engine steps:** understand (dilemma, emotions, people, obligations, options; constraints such as power imbalance, dependency, money, urgency, reversibility), clarify (at most 1-2 questions, only if they change the advice), retrieve, compare, recommend, challenge, act.
- **Tests:** 100 fictional situations plus held-out sets, scored on context, specificity, grounding, judgment, actionability and agency. Blind comparison with a general assistant and similar apps is still to come.
- **Personas** only after the prototype passes its tests. Fictional lenses are clearly labelled, never evidence, and never quote copyrighted dialogue. Chanakya and Kautilya are one person.

## Evaluation principles (agreed with the ChatGPT observer, 2026-10-02)
- An inappropriate central recommendation fails an answer, whatever its formatting or citations.
- Use paired cases where age, dependency, urgency, danger or available options change the decision.
- Keep first-run results separate from reruns after fixes. Automatic proxy scores are not independent evidence of judgment quality.

## Open proposals (not yet owner decisions)
- Decision-focused evaluation set: can the user make a better next decision, what facts would reverse the advice, was the strongest alternative fairly represented? (observer, 2026-10-02)

## Known open items
- Every record is draft. A Sanskrit reader must review before anything goes live (priority: flagged verses, Gita 7.6, Gita chapter 13's realigned Ramanuja commentary, 6 irregular-metre verses).
- Upanishad school notes are mostly Shankara; this must be disclosed.
- PROJECT_BRIEF.md does not exist yet. Until it does, this file and CLAUDE.md section 10 are the brief.

## Review process
- All reviews are stored in `reviews/` (builder-cycle reviews) or `AI Review Desk/Viveka/` (observer reviews), labelled must-fix / should-fix / idea.
- Before every review, read PROJECT_BRIEF.md (if present), CONTEXT.md, DECISIONS.md, STATUS.md and the latest reviews.
- Update this file only for newly confirmed owner decisions.
