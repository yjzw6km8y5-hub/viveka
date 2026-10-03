_Imported from the AI Review Desk; owner approved items [23] on 2026-10-03._

# Viveka design roadmap and Claude planning handoff

Version: 2026-10-02 v1
Status: Complete ChatGPT proposal; awaiting Claude planner review and owner adoption of the exact version. This is not a completed cross-model consensus or permission to spend.

## Confirmed owner direction

Viveka is a global conversational guide for real dilemmas. It begins with Indian wisdom, expands to other philosophies, and offers optional thinker and fictional persona lenses. It explains disagreement, recommends by fit to the person's circumstances, preserves agency and gives one practical next step. It is not limited to a verse chatbot or a native mobile app.

Development uses existing subscriptions. Paid model APIs and hosting may be used later where commercially justified, included in forecasts and separately approved before purchase or activation. No services have been purchased or activated by this proposal.

Existing decisions remain in force unless explicitly changed: free access with donations, no ads, no saved conversations or accounts, global audience age 13+, reviewed sources only, protection in abuse or danger, and no divine impersonation. Persistent memory and paid tiers are proposals, not adopted requirements. Do not quietly change these commitments.

## Product design

One conversational interface, with three modes:

1. Guide me: clarify the dilemma, compare relevant perspectives, recommend a next step and state the strongest alternative.
2. Choose a lens: explore through a supported tradition or thinker, with authentic source context.
3. Compare perspectives: show substantive agreement and disagreement, then explain which approach fits the present facts. Never average incompatible philosophies into a false consensus.

Default answer: what I understand; missing fact if it changes the recommendation; relevant perspectives; suggested course and why; strongest alternative; one action; facts that would reverse the advice. Keep it conversational rather than displaying an obligatory form on every turn.

Sources and applications stay distinguishable. Quotes come from approved records, never model recall. A philosopher lens is grounded in works. Einstein or other historical figures are not presumed authorities on every life dilemma: label extrapolations and acknowledge missing evidence. A fictional Harvey-style lens is explicitly fictional interpretation, not evidence or professional advice. Persona tone never overrides safety or source fidelity.

## Architecture

Use a capable LLM for understanding and reasoning, a curated retrieval library for grounding, and software checks for citation identity, source approval, privacy and output routing. Preserve useful existing data and tests. Treat keyword/template logic as supporting infrastructure, not sufficient evidence of situational understanding.

Pipeline: safety and context assessment -> clarification when material -> approved source retrieval -> perspective comparison -> recommendation -> groundedness and appropriateness checks -> bounded revision or useful clarification/withholding.

Start with one main conversational model. Add routing to cheaper supporting models and stronger models only when task-specific evaluation justifies it. Keep a provider adapter so OpenAI, Claude, Gemini or other qualifying providers can be compared without rewriting the product. Do not select a provider on token price alone.

Retrieve only relevant source passages. Limit context growth, retries and simultaneous persona perspectives. Distinguish asynchronous evaluation work from interactive answers. Never run an unbounded model debate for every message.

Initial public interface: responsive hosted web conversation, once release gates pass. Native mobile, voice and messaging integrations follow demonstrated demand. A ChatGPT/Claude-hosted prototype can test interaction design but is not the production hosting architecture.

## Delivery stages and dependencies

| Stage | Deliverable | Exit evidence |
|---|---|---|
| 0: Align | PROJECT_BRIEF.md; decisions and unresolved choices; dependency-ordered STATUS.md | Claude planner review and exact-version owner adoption; reconcile funding, privacy and API rules |
| 1: Prove guidance | LLM reasoning prototype; reviewed starter sources; verified recommendation gate | Actual before/after answers; V028, V001 and V024 addressed; source checks; fresh tests separated from regression; existing release thresholds remain in force |
| 2: Private beta | Hosted web experience; Guide me mode; Indian starter collection; optional small Stoic collection only after expansion approval | Blind comparison, source-visible verification after blind scoring, owner spot-checks; usefulness and return-use evidence; measured conversation cost |
| 3: Broaden | Choose a lens and Compare perspectives; reviewed Greek/Nietzsche collections; limited personas | Each lens grounded and evaluated; disagreement handled honestly; no decrease in guidance quality or safety |
| 4: Operate sustainably | Chosen funding model; controlled usage; support; reliable deployment and recovery | Budget approved; privacy terms verified; unit economics or donation funding adequate; release sign-off |

Expansion remains paused until the current prerequisite gates are satisfied and approved. Adding a Stoic starter collection is a future proposal, not authority to ingest it now. Roadmap stages are evidence-based; no completion dates are invented.

## Improvement and evaluation

Personalisation within a session is separate from product improvement and model training. Retaining user memory would require a deliberate new privacy decision. Do not store private conversations, traces or feedback containing personal data under the current promise.

The improvement loop uses fictional cases, explicit consent where appropriate under an adopted policy, reviewer findings and safely aggregated operational measures. AI may propose retrieval/prompt/code changes and run evaluations. An independent reviewer assesses the builder's changes. Promotion requires the existing process; do not let AI self-approval replace it.

Keep a fresh evaluation set; log first-run failures before tuning. Freeze blind usefulness/judgment scores before revealing sources for source verification. Compare against general assistants and selected spiritual/philosophy products on identical cases. A bad central recommendation fails irrespective of attractive prose. Add paired cases changing age, danger, dependency, urgency and options.

No public guidance until required human source review, safety checks and owner release approval are complete. Prioritise the latest confirmed urgent findings before new product capabilities.

## Commercial forecast

Forecast monthly active users, sessions per active user, messages per session, input/output tokens including context, model mix, checks/retries, retrieval, hosting, monitoring, payment fees, support, review costs and acquisition costs. Separate fixed costs, variable costs and development time. Model low/base/high use, long conversations, abuse of free usage and currency exposure.

Cost per completed useful session is the main model-cost measure. Contribution equals net revenue or funding less variable delivery cost. Break-even volume equals fixed monthly costs divided by positive contribution per funded/paying unit, using internally consistent units. Donations require conversion and average-gift assumptions rather than subscription assumptions.

Current baseline remains free access with donations. Alternatives to compare, not silently adopt: sponsorship without access to user conversations; optional premium capabilities with free basic access; institution-funded access. No advertising or sale of personal data. Label every untested price/conversion estimate as an assumption. Purchase caps and operational pause conditions must be set before API activation.

For multiple ventures, reuse provider access code, evaluation tools and deployment patterns while separating project data, secrets, budgets, user promises and performance. Give each venture a capped experiment budget and evidence-based continue/pause decision. Do not let the portfolio obscure loss-making projects.

## Seamless coding handoff

After adoption, builders import this exact version into PROJECT_BRIEF.md and record the source file ID, modified time and content hash in proposals/APPROVALS.md under the existing process. Update CONTEXT.md and DECISIONS.md for confirmed choices; STATUS.md carries only the next executable batch with acceptance evidence and dependencies. Avoid competing master roadmaps.

Already-approved safety, source-review and recommendation work continues while this planning review is pending. This document does not authorise an architecture rewrite or spending. A planning limit should not erase the current approved queue.

One builder at a time. At subscription limits use the approved stand-in rule. Codex-built changes wait for Claude review; Claude-built changes receive Codex review. Persist an honest handoff with changed files, tests, pending review and next action. Do not claim an automatic handoff is operational without runner evidence.

## Claude planner review request

When available, read this complete proposal alongside current PROCESS.md, CONTEXT.md, DECISIONS.md, STATUS.md and latest reviews. Review as the planner, not as your own code reviewer. Reply in AI Review Desk/Viveka as ROADMAP_RESPONSE_claude.md, referencing this filename and version. Include: agreement; substantive disagreements with reasons; missing dependencies; proposed revised text; and decisions requiring the owner. Explicitly assess API architecture, funding, no-storage constraints, teen audience, persona fidelity, costs and achievable evaluation evidence.

Do not claim consensus until the response is actually read and disagreements reconciled. Do not treat this request as evidence that Claude has been notified or executed. The ChatGPT observer may discover and reconcile the saved response on its existing cadence; it cannot detect Claude's account reset or start the Claude planning chat.
