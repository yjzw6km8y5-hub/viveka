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

## Owner decisions, 2026-10-03
- **Later phase (after the first tests pass):** widen scope to Greek, Roman, Chinese and modern Western philosophy (e.g. Nietzsche), seen as the main paying audience. Public-domain works may be quoted; thinkers under copyright get paraphrased "view" records only. Not now: the first test stays on the current plan.
- **Now: context first.** Viveka asks follow-up questions about context (who they live with, where they are, constraints) before answering, never up front. The person can say "just answer". Safety help is never delayed by these questions.
- **Now: visual onboarding in the prototype UI:** a short Big Five questionnaire (public-domain IPIP items, not MBTI or 16Personalities) and a visual life map on Dharma, Artha, Kama and Moksha, with Ikigai as an alternative.
- **Open (owner decision): where the profile is stored.** Until decided, it stays in the browser for that visit only and is never sent or saved.
- **Owner decisions, 2026-10-03 (later):**
  - The profile stays on the device only.
  - The LLM step runs on the owner's subscription for his own testing only; anyone else needs a zero-data-retention API first.
  - The roadmap is decided after the Claude chat reviews it.
  - Push to the project's repo is pre-approved.

- **Owner decision, 2026-10-03: real-life dilemmas told as a story.**
  - Viveka is for weighty, tangled situations with competing duties, told in full, not one-line trivial questions.
  - The flow: listen and reflect back (only their facts, correctable), then ask 1-3 questions that would change the advice, then advise (the core dilemma, the competing pulls across Dharma / Artha / Kama / Moksha, a recommendation, the other view, one next step).
  - "Just listen" and "Just give me advice" are always available.
  - The tone is a wise friend who listens, never a therapist. Safety help always comes first.
  - It replaces the earlier fixed context questions.

## Review process
- The build-and-review loop is in PROCESS.md (v3, approved 2026-10-02).
- Order of authority, highest first: the owner's latest approved decision, DECISIONS.md, CONTEXT.md, PROCESS.md, STATUS.md. PROGRESS.md is history only.
- Outside input waits in proposals/ for the owner's approval; every decision is logged in proposals/APPROVALS.md.
- All reviews are stored in `reviews/` (builder-cycle reviews) or `AI Review Desk/Viveka/` (observer reviews), labelled must-fix / should-fix / idea.
- Before every review, read PROJECT_BRIEF.md (if present), CONTEXT.md, DECISIONS.md, STATUS.md and the latest reviews.
- Update this file only for newly confirmed owner decisions.

## Approved ideas from reviews
- **Use a small decision-focused evaluation set alongside broad coverage: ask wheth…** (2026-10-02-16_observer_chatgpt.md, approved 2026-10-03): Use a small decision-focused evaluation set alongside broad coverage: ask whether the user can make a better next decision after the answer, which facts would reverse the advice, and whether the strongest alternative was fairly represented. This is a proposed evaluation improvement, not a newly agreed owner decision.

## Approved context updates
### From CONTEXT_chatgpt.md (approved 2026-10-03)
**Confirmed updates — 2026-10-02, 17:03 America/Toronto**
- The older overlapping hourly Viveka check is disabled; verified from automation configuration. The two-hour observer reads the current Drive PROCESS.md first on every run.
- Owner requested PROCESS v3 evaluation boundaries and a one-time synthetic urgent-notification test. The synthetic finding is excluded from scores, approval proposals and ordinary safety counts; notification receipt remains unverified.
- Repository approvals at f498735ba134dca4f16181e282b914289df4db3a confirm the prior three must-fix findings and shared-context merge were approved. CONTEXT.md now exists. Earlier setup notes about the hourly check remaining unchanged and CONTEXT.md missing are historical, superseded by these observations.
- Drive PROCESS.md v3 (file 1Wr38FfMZ_BWThvB4vMyS1fv4gyf1v47c) guides this observer; repository adoption is still v2, with v3 explicitly pending separate owner approval. Do not infer that agreement by this observer authorises builder import.
- Guidance improvement remains unproven; the new review's recommendations remain pending feedback, not newly approved owner decisions.
**Confirmed updates — 2026-10-02, 18:20 America/Toronto**
- At repository commit 56921fa6ca7e60457e9145586c712461fa6c6377, proposals/APPROVALS.md records owner approval of PROCESS.md v3 (source modified 16:57 Toronto, 7230 bytes, recorded hash prefix e13e24cbe159). Repository adoption is no longer pending; the earlier note is superseded.
- The same approval log records the owner's builder-handoff decision: Codex builds at Claude's usage limit, Claude resumes after reset, and no tool reviews its own work. It also records independent Codex verse checking with the Sanskrit-reading owner reviewing disagreements, safety-flagged verses and a fixed 5% sample. Unmarked verses remain draft unless the owner decides otherwise.
- These are confirmed recorded owner decisions, not evidence that automatic runner handoff has executed. DECISIONS.md explicitly places that implementation outside the repository session's permitted scope; no successful takeover cycle is established here.
- The 18:20 observer review carries forward the real V028 protective-guidance defect and distinguishes ordinary gate checks from test-only decision-fit expectations. Its recommendations remain pending proposals. The synthetic notification test is excluded from findings, approval records and evaluations.
