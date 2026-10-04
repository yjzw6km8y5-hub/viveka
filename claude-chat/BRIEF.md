# Viveka: brief for the Claude planning chat

_Updated 2026-10-04 01:46 Eastern Daylight Time by `scripts/brief.py` after a cycle. Repo: https://github.com/yjzw6km8y5-hub/viveka_

## Current status

- **Stage:** prototype. Viveka recommends from verified passages with a pass/fail gate. An LLM writes the final wording (retrieval-augmented generation, prototype on the owner's subscription). Nothing is published; every verse is still a draft.
- **Try it:** on the owner's PC, `python scripts/serve.py`, then open http://127.0.0.1:8765.
- **Next step (from STATUS.md):**

  0. **Owner decisions of 2026-10-03, build now** (CONTEXT.md):
     - **Context-first answer flow:** before recommending, ask about who they live with, where they are and their constraints. Offer a "just answer" option. Show safety and health help at once, and never delay them.
     - **Visual onboarding on the try-it page** (done 2026-10-03: age, country, Big Five, life map):
       - a short Big Five questionnaire, using public-domain IPIP items
       - a Dharma / Artha / Kama / Moksha life map, with Ikigai as an alternative
       - the profile stays in the browser for the visit only; never send or save it
     - Use the profile to tailor answers; add tests; update `claude-chat/BRIEF.md`.
  1. Verse check complete (39/39). The owner's list is ready in `reviews/verse-check/OWNER_REVIEW.md`: 484 verses listed (1539/1539 checked by Codex, 127 disagreements).
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
| Guidance gate, dev set | 91 of 100 pass (builder-written; not independent) | 9% |
| Guidance gate, held-out v1 | 25 of 30 pass (builder-written; not independent) | 17% |
| Guidance gate, held-out v2 | 17 of 30 pass (builder-written; not independent) | 43% |
| Guidance gate, paired cases | 14 of 14 pass (builder-written; not independent) | 0% |
| Independent test set (30 wanted) | 0 written by the owner; ChatGPT's 30 requested | 100% |
| Blind comparison vs a general assistant | not started (needs baseline answers) | 100% |
| Zero-data-retention API before anyone else uses Viveka | not set up (owner testing uses his subscription) | 100% |

## Runner log, last 24 hours

- **Cycles:** 1 (1 ok, 0 failed); by builder: claude 1.
- **Not yet reviewed by the other tool:** 1.
- **Commits:** 4.

<details><summary>Commits</summary>

- 10-04 01:38  Remove stray scratch scripts; ignore scratch_*.py so the build leaves a clean tree
- 10-04 00:32  Cycle 10: new frames (identity loss, credit taken, preparing for death), family-care and family-rift fixes; situations gate 91/100
- 10-03 23:37  Fix cycle-8 review findings: no age to AI writer, invented-number check, removed-baseline check, full proposal merge text
- 10-03 01:58  Big Five (Mini-IPIP) and life-map onboarding, kept on the device; profile note; AI writer keeps message and context apart; Desk screenshots tool

</details>

## The interface, screen by screen

### Screen 1: Onboarding (first visit only; four steps with a progress bar)
1. **Before we start:** "So the help lines and answers fit you. Everything you enter stays on this device."
   - **Your age**: number, placeholder "e.g. 34".
   - **Where are you?**: Canada (default) / India / United States / United Kingdom / Somewhere else.
   - **Next**.
2. **How you tend to be:** "20 quick statements (a public-domain Big Five measure). How accurately does each describe you? Not a test or a diagnosis."
   - The 20 Mini-IPIP statements, each with buttons 1-5 ("1 = very inaccurate", "5 = very accurate"):
     - "I am the life of the party."
     - "I sympathize with others' feelings."
     - "I get chores done right away."
     - "I have frequent mood swings."
     - "I have a vivid imagination."
     - "I don't talk a lot."
     - "I am not interested in other people's problems."
     - "I often forget to put things back in their proper place."
     - "I am relaxed most of the time."
     - "I am not interested in abstract ideas."
     - "I talk to a lot of different people at parties."
     - "I feel others' emotions."
     - "I like order."
     - "I get upset easily."
     - "I have difficulty understanding abstract ideas."
     - "I keep in the background."
     - "I am not really interested in others."
     - "I make a mess of things."
     - "I seldom feel blue."
     - "I do not have a good imagination."
   - A counter ("N of 20 answered"). **Next** and **Skip**.
3. **Your life map:** "How settled or fulfilled does each part of your life feel right now? 1 = not at all, 10 = completely."
   - A switch: **Dharma · Artha · Kama · Moksha** | **Ikigai**.
   - Four tiles, each with a 1-10 slider:
     - Dharma "duty, values, doing right by others", Artha "work, money, security", Kama "joy, love, beauty, pleasure", Moksha "inner freedom, meaning, peace".
     - Or, for Ikigai: "What you love", "What you're good at", "What the world needs", "What you can be paid for".
   - **Next** and **Skip**.
4. **Your profile:** "Kept only on this device. It shapes how Viveka frames its suggestions, never what is true."
   - Five trait bars: Openness, Conscientiousness, Extraversion, Agreeableness, Emotional sensitivity. Each has a short description and is marked lower / middle / higher.
   - The life map as four tiles with N/10 bars.
   - **Start**.
- Everything stays in the browser on this device. The profile itself is never sent to the server or to the AI.

### Screen 2: Conversation (home)
- Header: "V" logo, **Viveka**, **⚙ Settings**. (A **Test case** button appears only with `?dev=1`.)
- First message from Viveka: "Hello. Tell me what's on your mind, in your own words. I'll ask a few questions first, then suggest one way forward."
- Example buttons:
  - "I'm nervous about my exam tomorrow"
  - "I had a fight with my best friend"
  - "Should I take the new job or stay?"
  - "I can't get myself to start working"
- Bottom bar: **microphone** button, a text box "What's on your mind?", and a round **send** button (➤). Enter sends.
- Under the bar: "Local test page · not published · nothing you write is saved". After an answer, this line shows the person's own country's help lines.
- While recording, it shows: "Listening… Voice is turned into text by your browser's speech service, which may send the audio to its provider."

### Screen 3: Context questions (after the person writes)
- The person's message appears as a green bubble on the right.
- **Safety first:** if there is danger, crisis or an eating risk, a red card appears at once, before any questions:
  - "Your safety first", "Please reach out now" or "Your health first", with the message and help lines for their country.
  - A crisis ends here, with a "Right now" step.
  - Gentle distress shows a card titled "You don't have to carry this alone".
- **Viveka's reply** first reflects the situation back, e.g. "It sounds like this is about a friendship, and it involves your best friend. Before I suggest anything, a few quick questions:". Then:
  - **Who do you live with?** On my own / With family / With a partner / With roommates or friends / I'd rather not say
  - **What's limiting your options right now?** (pick any) Money / Time / Family expectations / Health / Nothing major
  - **How soon do you need to act?** Today / This week / No rush
  - Sometimes one more free-text question from the engine (e.g. "What are the main options you are choosing between?")
  - Buttons **Continue** and **Just answer**.
- While Viveka thinks: "<the reflection> Let me think this through carefully (this can take up to a minute)." with three pulsing dots.

### Screen 4: The answer (one answer only)
- **Opening:** one sentence to the person, in large text, e.g. "After a fight with someone close, it can help to look at what a true friend does."
- **Body:** a short paragraph (AI-written from the checked passages, or Viveka's own text if AI is off or fails the check).
- **ONE NEXT STEP:** a green box with one action.
- **THROUGH YOUR PROFILE (ON THIS DEVICE):** a sand-coloured note worked out in the browser. For example, "This touches **Dharma** (duty, values, doing right by others), which you rated 7/10." It adds one tip from the Big Five when relevant: low conscientiousness gives "make the next step small and give it a time"; high emotional sensitivity gives "take the next step slowly…"; low extraversion gives "a written message is a fine first step".
- **CLOSEST FIT:** the principle, as an orange tag.
- **ALSO WORTH CONSIDERING:** one or two principles, as tags.
- **Folded sections:**
  - "The text (ID)": the English first, then a further fold, "Sanskrit".
  - "Why this fits you", "The other view", "What the commentators say", "A story from the texts".
- **Footer line:** "Draft · N of M verses reviewed by a Sanskrit reader · written by AI, from the passages shown, then checked" (or "written by Viveka").

### Screen 5: Settings (⚙)
- **Age**, **Country (for help lines)**.
- **AI-written answers** checkbox, labelled "uses Claude through the owner's subscription; your text leaves this device; testing only".
- Buttons **Your profile** (shows the profile summary) and **Redo personality and life map**.
- Buttons **Save**, **Cancel**, **Forget me** (clears the device profile and shows onboarding again).

### Screen 6: Add a test case (developer only, `?dev=1`)
- Explanation, then fields:
  - the situation
  - category: adult / teen / ambiguous / hard
  - safety route: none / support / danger / crisis
  - "What a good answer must do (and must not do)"
  - "Your name or initials"
- Buttons **Save** and **Close**. Confirmation: "Saved as I00N · N so far."

## Screenshots

- [1-onboarding-profile](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/1-onboarding-profile.jpg)
- [2-home](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/2-home.jpg)
- [3-context-questions](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/3-context-questions.jpg)
- [4-answer](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/4-answer.jpg)
- [5-answer-details](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/5-answer-details.jpg)
- [6-answer-phone](https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main/claude-chat/screenshots/6-answer-phone.jpg)

## Owner decisions and what is still open

- **Decided 2026-10-03:** the profile stays on the device only.
- **Decided 2026-10-03:** the LLM step runs on the owner's subscription for the owner's own testing only. Before anyone else uses Viveka, it needs an API with zero data retention.
- **Open:** ChatGPT's roadmap and business plan (below). The owner decides after the Claude chat reviews it. Claude Code's four amendments are in `AI Review Desk/Viveka/ROADMAP_RESPONSE_claude.md`.

## For review: ChatGPT's roadmap and business plan (in full)

_Copied verbatim from `AI Review Desk/Viveka/VIVEKA_DESIGN_ROADMAP.md` each time this brief is written. The business plan is its section "Commercial forecast"; there is no separate business-plan file._

---

### Viveka design roadmap and Claude planning handoff

Version: 2026-10-02 v1
Status: Complete ChatGPT proposal; awaiting Claude planner review and owner adoption of the exact version. This is not a completed cross-model consensus or permission to spend.

#### Confirmed owner direction

Viveka is a global conversational guide for real dilemmas. It begins with Indian wisdom, expands to other philosophies, and offers optional thinker and fictional persona lenses. It explains disagreement, recommends by fit to the person's circumstances, preserves agency and gives one practical next step. It is not limited to a verse chatbot or a native mobile app.

Development uses existing subscriptions. Paid model APIs and hosting may be used later where commercially justified, included in forecasts and separately approved before purchase or activation. No services have been purchased or activated by this proposal.

Existing decisions remain in force unless explicitly changed: free access with donations, no ads, no saved conversations or accounts, global audience age 13+, reviewed sources only, protection in abuse or danger, and no divine impersonation. Persistent memory and paid tiers are proposals, not adopted requirements. Do not quietly change these commitments.

#### Product design

One conversational interface, with three modes:

1. Guide me: clarify the dilemma, compare relevant perspectives, recommend a next step and state the strongest alternative.
2. Choose a lens: explore through a supported tradition or thinker, with authentic source context.
3. Compare perspectives: show substantive agreement and disagreement, then explain which approach fits the present facts. Never average incompatible philosophies into a false consensus.

Default answer: what I understand; missing fact if it changes the recommendation; relevant perspectives; suggested course and why; strongest alternative; one action; facts that would reverse the advice. Keep it conversational rather than displaying an obligatory form on every turn.

Sources and applications stay distinguishable. Quotes come from approved records, never model recall. A philosopher lens is grounded in works. Einstein or other historical figures are not presumed authorities on every life dilemma: label extrapolations and acknowledge missing evidence. A fictional Harvey-style lens is explicitly fictional interpretation, not evidence or professional advice. Persona tone never overrides safety or source fidelity.

#### Architecture

Use a capable LLM for understanding and reasoning, a curated retrieval library for grounding, and software checks for citation identity, source approval, privacy and output routing. Preserve useful existing data and tests. Treat keyword/template logic as supporting infrastructure, not sufficient evidence of situational understanding.

Pipeline: safety and context assessment -> clarification when material -> approved source retrieval -> perspective comparison -> recommendation -> groundedness and appropriateness checks -> bounded revision or useful clarification/withholding.

Start with one main conversational model. Add routing to cheaper supporting models and stronger models only when task-specific evaluation justifies it. Keep a provider adapter so OpenAI, Claude, Gemini or other qualifying providers can be compared without rewriting the product. Do not select a provider on token price alone.

Retrieve only relevant source passages. Limit context growth, retries and simultaneous persona perspectives. Distinguish asynchronous evaluation work from interactive answers. Never run an unbounded model debate for every message.

Initial public interface: responsive hosted web conversation, once release gates pass. Native mobile, voice and messaging integrations follow demonstrated demand. A ChatGPT/Claude-hosted prototype can test interaction design but is not the production hosting architecture.

#### Delivery stages and dependencies

| Stage | Deliverable | Exit evidence |
|---|---|---|
| 0: Align | PROJECT_BRIEF.md; decisions and unresolved choices; dependency-ordered STATUS.md | Claude planner review and exact-version owner adoption; reconcile funding, privacy and API rules |
| 1: Prove guidance | LLM reasoning prototype; reviewed starter sources; verified recommendation gate | Actual before/after answers; V028, V001 and V024 addressed; source checks; fresh tests separated from regression; existing release thresholds remain in force |
| 2: Private beta | Hosted web experience; Guide me mode; Indian starter collection; optional small Stoic collection only after expansion approval | Blind comparison, source-visible verification after blind scoring, owner spot-checks; usefulness and return-use evidence; measured conversation cost |
| 3: Broaden | Choose a lens and Compare perspectives; reviewed Greek/Nietzsche collections; limited personas | Each lens grounded and evaluated; disagreement handled honestly; no decrease in guidance quality or safety |
| 4: Operate sustainably | Chosen funding model; controlled usage; support; reliable deployment and recovery | Budget approved; privacy terms verified; unit economics or donation funding adequate; release sign-off |

Expansion remains paused until the current prerequisite gates are satisfied and approved. Adding a Stoic starter collection is a future proposal, not authority to ingest it now. Roadmap stages are evidence-based; no completion dates are invented.

#### Improvement and evaluation

Personalisation within a session is separate from product improvement and model training. Retaining user memory would require a deliberate new privacy decision. Do not store private conversations, traces or feedback containing personal data under the current promise.

The improvement loop uses fictional cases, explicit consent where appropriate under an adopted policy, reviewer findings and safely aggregated operational measures. AI may propose retrieval/prompt/code changes and run evaluations. An independent reviewer assesses the builder's changes. Promotion requires the existing process; do not let AI self-approval replace it.

Keep a fresh evaluation set; log first-run failures before tuning. Freeze blind usefulness/judgment scores before revealing sources for source verification. Compare against general assistants and selected spiritual/philosophy products on identical cases. A bad central recommendation fails irrespective of attractive prose. Add paired cases changing age, danger, dependency, urgency and options.

No public guidance until required human source review, safety checks and owner release approval are complete. Prioritise the latest confirmed urgent findings before new product capabilities.

#### Commercial forecast

Forecast monthly active users, sessions per active user, messages per session, input/output tokens including context, model mix, checks/retries, retrieval, hosting, monitoring, payment fees, support, review costs and acquisition costs. Separate fixed costs, variable costs and development time. Model low/base/high use, long conversations, abuse of free usage and currency exposure.

Cost per completed useful session is the main model-cost measure. Contribution equals net revenue or funding less variable delivery cost. Break-even volume equals fixed monthly costs divided by positive contribution per funded/paying unit, using internally consistent units. Donations require conversion and average-gift assumptions rather than subscription assumptions.

Current baseline remains free access with donations. Alternatives to compare, not silently adopt: sponsorship without access to user conversations; optional premium capabilities with free basic access; institution-funded access. No advertising or sale of personal data. Label every untested price/conversion estimate as an assumption. Purchase caps and operational pause conditions must be set before API activation.

For multiple ventures, reuse provider access code, evaluation tools and deployment patterns while separating project data, secrets, budgets, user promises and performance. Give each venture a capped experiment budget and evidence-based continue/pause decision. Do not let the portfolio obscure loss-making projects.

#### Seamless coding handoff

After adoption, builders import this exact version into PROJECT_BRIEF.md and record the source file ID, modified time and content hash in proposals/APPROVALS.md under the existing process. Update CONTEXT.md and DECISIONS.md for confirmed choices; STATUS.md carries only the next executable batch with acceptance evidence and dependencies. Avoid competing master roadmaps.

Already-approved safety, source-review and recommendation work continues while this planning review is pending. This document does not authorise an architecture rewrite or spending. A planning limit should not erase the current approved queue.

One builder at a time. At subscription limits use the approved stand-in rule. Codex-built changes wait for Claude review; Claude-built changes receive Codex review. Persist an honest handoff with changed files, tests, pending review and next action. Do not claim an automatic handoff is operational without runner evidence.

#### Claude planner review request

When available, read this complete proposal alongside current PROCESS.md, CONTEXT.md, DECISIONS.md, STATUS.md and latest reviews. Review as the planner, not as your own code reviewer. Reply in AI Review Desk/Viveka as ROADMAP_RESPONSE_claude.md, referencing this filename and version. Include: agreement; substantive disagreements with reasons; missing dependencies; proposed revised text; and decisions requiring the owner. Explicitly assess API architecture, funding, no-storage constraints, teen audience, persona fidelity, costs and achievable evaluation evidence.

Do not claim consensus until the response is actually read and disagreements reconciled. Do not treat this request as evidence that Claude has been notified or executed. The ChatGPT observer may discover and reconcile the saved response on its existing cadence; it cannot detect Claude's account reset or start the Claude planning chat.

---

