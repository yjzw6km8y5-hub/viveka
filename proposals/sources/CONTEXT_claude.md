# Viveka: context from the Claude project chat (as of 2026-10-02)

Every reviewer reads this before judging any Viveka work. It records the owner's intent and every decision made in the Claude planning chat.

## Vision (owner's words, condensed)
- A guide for tough times. A person (13 to 80+) describes their real situation; Viveka understands it, weighs the relevant wisdom, recommends a course of action, explains disagreements, and suggests a next step.
- Grounded in Indian wisdom from the Vedas to contemporary thinkers, not only ancient texts. Later: other philosophies (Greek first), then optional persona lenses.
- Not Krishna-centric. Viveka quotes and explains texts; it never speaks as Krishna or any deity.
- Wisdom is eternal; the intent is pure: help people, store nothing.

## Fixed decisions
- Name: Viveka, kept even though a small same-name app exists ("Viveka - Ancient Wisdom", Product Hunt, early 2026). Mitigation: distinctive domain/handles and a trademark search before launch.
- Audience: global; minimum age 13. Users aged 13-17 get gentler framing and no verses on war or renunciation.
- Funding: free with donations. No ads.
- Privacy: no accounts, no saved conversations. Session context may exist temporarily but is never stored. Confirm the AI provider's data terms (including for under-18 users) match this promise.
- Verse library is published openly under CC BY-SA 4.0 so anyone can verify every verse.
- Sources: Sanskrit from Sanskrit Wikisource (pinned revisions). English renderings are our own, cross-checked against public-domain translations (Telang 1882, Hume 1921 edition, Max Muller). GRETIL is cross-check only (non-commercial licence).
- Schools: pluralist (Advaita, Vishishtadvaita, Dvaita and others). If a school's commentary is missing for a text, say so; never present uneven coverage as consensus.
- Life stages: the four traditional stages, kept separate from age.
- Narrative verses: no situation tags; never offered as advice.
- Safety flags: war, death, renunciation, under18_hold, distress_gentle, caste_gender. under18_hold applies when a verse presents death as harmless, urges fighting, or urges leaving family or the world. distress_gentle marks verses that could deepen self-blame.
- Context field: one sentence, max 30 words. Situations: 1 to 4 per verse.
- Varna and gender verses are never offered as advice; where relevant, svadharma is framed as one's own nature and duty, never birth-based hierarchy.

## Conflicting views (owner's explicit instruction)
- It is not a matter of belief. The app explains why views conflict, then RECOMMENDS the view that fits this person's situation and says why, then names the strongest alternative: "If your conscience leans the other way, here is the other view."
- Recommend by fit to the situation, never by declaring one school true.
- Safety overrides: never recommend renunciation or abandoning responsibilities to someone in distress or under 18. Always support leaving abuse or danger and point to help.

## Guardrails
- No invented verses: quote only library text; automated citation check on every answer.
- Safety screen before scripture: risk signs route to human help (localised helplines) first.
- Never tell anyone their suffering is deserved karma.
- Not a guru, therapist or substitute for professional help.
- Every answer labels its parts: source text / commentator's view / historical example / Viveka's application.
- Users see only reviewed or approved material; drafts stay internal.

## Plan adopted on 2026-10-02 (from the ChatGPT review, agreed by owner)
- Sequence: prototype -> reviewed starter collection -> comparative testing -> expand library. Text queue paused after the Katha Upanishad.
- Answer engine steps: understand (dilemma, emotions, people, obligations, options, constraints such as power imbalance, dependency, money, urgency, reversibility) -> clarify (max 1-2 questions, only if they change the advice) -> retrieve (short list) -> compare -> recommend -> challenge (strongest alternative) -> act (one next step). Never average philosophies into one answer.
- Tests: 100 fictional situations (adult and teen, ambiguous, hard exceptions), scored on context, specificity, grounding, judgment, actionability, agency; blind comparison with a general assistant and similar apps.
- data/principles/ (~150 principles) and data/examples/ (stories and historical cases with limits of the analogy).
- Personas only after the prototype passes tests: thinker lenses grounded in their works; fictional lenses clearly labelled, never evidence, never quoting copyrighted dialogue; Chanakya and Kautilya are one person.

## Full scope (after tests, prioritised by what tests show is missing)
13 principal Upanishads; Niti texts (Chanakya Niti, Vidura Niti, Bhartrihari, Shukra Niti, selected Arthashastra, Panchatantra, Hitopadesha, Subhashitas); other Gitas (Uddhava, Anu, Ashtavakra, Avadhuta, Shiva, Devi, Sanatsujatiya); philosophy (Yoga Sutras, Brahma Sutras, Samkhya Karika, Vivekachudamani); epics and Puranas (Mahabharata and Ramayana selections, Bhagavata Purana Book 11 first, Devi Mahatmya, Yoga Vasishtha, Vedic suktas); bhakti and regional (Ramcharitmanas, Dnyaneshwari, Tirukkural, Surdas, Mirabai); modern public-domain (Vivekananda, Tilak, Gandhi, Tagore, Aurobindo); contemporary thinkers as paraphrased "view" records only.
Excluded: Dharmashastras, Tantra/Agama ritual texts, Jyotish texts.

## Known open items
- All records are draft; a Sanskrit reader must review before anything goes live (priority: flagged verses, Gita 7.6, Gita chapter 13 realigned Ramanuja commentary, 6 irregular-metre verses).
- Upanishad school notes are mostly Shankara; disclose this.

## Review process
- Reviews happen only in the designated place for each tool; all reviews are stored in reviews/.
- Before every review, the reviewer reads: PROJECT_BRIEF.md, CONTEXT.md, DECISIONS.md, STATUS.md and the latest reviews.
