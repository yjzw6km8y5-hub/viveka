"""Write claude-chat/BRIEF.md: the owner's one-page brief for the Claude planning chat.
Run after every cycle (CLAUDE.md section 15):  python scripts/brief.py

Status numbers come from the repo itself (built texts, test results, verse-check results, cycle log, git log).
The screen-by-screen interface description below must be updated whenever scripts/serve_page.html changes.
"""
import csv, datetime, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "claude-chat" / "BRIEF.md"
SHOTS = ROOT / "claude-chat" / "screenshots"
REPO = "https://github.com/yjzw6km8y5-hub/viveka"
RAW = "https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main"

INTERFACE = """### Screen 1: Ask (home)
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
"""


def sh(*a):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.strip()


def gate(set_name):
    p = ROOT / "tests" / "results" / "after" / f"{set_name}.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text(encoding="utf-8"))
    return sum(not x["gate"] for x in r), len(r)


def pct_left(done, total):
    return 100 if not total else round(100 * (total - done) / total)


def main():
    now = datetime.datetime.now().astimezone()
    rows = []
    # Library
    units, reviewed = 0, 0
    for f in ["gita"] + [k for k in json.loads((ROOT / "data/texts.json").read_text(encoding="utf-8")) if not k.startswith("_")]:
        p = ROOT / "data" / f"{f}.json"
        if p.exists():
            recs = json.loads(p.read_text(encoding="utf-8"))
            units += len(recs)
            reviewed += sum(r.get("review_status") in ("reviewed", "approved") for r in recs)
    up_done = sum((ROOT / "data" / f"{t}_upanishad.json").exists() for t in ("isha", "kena", "katha"))
    rows.append(("Upanishads (13 principal)", f"{up_done} of 13 done; paused", pct_left(up_done, 13)))
    niti = sum((ROOT / "data" / f"{t}.json").exists() for t in ("nitishataka", "vidura_niti"))
    rows.append(("Niti texts (8 planned)", f"{niti} of 8 done; paused", pct_left(niti, 8)))
    rows.append(("Sanskrit review by the owner", f"{reviewed} of {units} verses reviewed", pct_left(reviewed, units)))
    vc = len(list((ROOT / "reviews/verse-check/results").glob("batch-*.json")))
    rows.append(("Codex verse check", f"{vc} of 39 batches", pct_left(vc, 39)))
    for s, label in (("situations", "Guidance gate, dev set"), ("heldout", "Guidance gate, held-out v1"),
                     ("heldout2", "Guidance gate, held-out v2"), ("paired", "Guidance gate, paired cases")):
        g = gate(s)
        if g:
            rows.append((label, f"{g[0]} of {g[1]} pass (builder-written; not independent)", pct_left(*g)))
    ind = ROOT / "data/tests/independent.json"
    n_ind = len(json.loads(ind.read_text(encoding="utf-8"))) if ind.exists() else 0
    rows.append(("Independent test set (30 wanted)", f"{n_ind} written by the owner; ChatGPT's 30 requested", pct_left(min(n_ind, 30), 30)))
    rows.append(("Blind comparison vs a general assistant", "not started (needs baseline answers)", 100))
    rows.append(("Privacy decision for the LLM step", "open: zero data retention or a local model (owner)", 100))
    rows.append(("Profile storage", "open: owner decision (2026-10-03)", 100))

    # Runner log, last 24 hours
    since = now - datetime.timedelta(hours=24)
    cyc = [r for r in csv.DictReader(open(ROOT / "logs/cycles.csv", encoding="utf-8", newline=""))
           if r.get("time") and datetime.datetime.fromisoformat(r["time"]) >= since]
    commits = sh("git", "log", "--since=24 hours ago", "--format=%ad  %s", "--date=format:%m-%d %H:%M").splitlines()
    ok = sum(r["result"] == "ok" for r in cyc)
    fail = [r for r in cyc if r["result"] == "failed"]
    unrev = [r for r in cyc if r["result"] in ("ok", "failed") and not r.get("reviewer")]
    by = {}
    for r in cyc:
        by[r.get("builder") or "?"] = by.get(r.get("builder") or "?", 0) + 1

    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    nxt = status.split("## Next step", 1)[1].split("\n## ", 1)[0].strip() if "## Next step" in status else ""
    shots = sorted(SHOTS.glob("*.jpg")) + sorted(SHOTS.glob("*.png"))

    L = [f"# Viveka: brief for the Claude planning chat", "",
         f"_Updated {now:%Y-%m-%d %H:%M %Z} by `scripts/brief.py` after a cycle. Repo: {REPO}_", "",
         "## Current status", "",
         "- **Stage:** prototype. Viveka recommends from verified passages with a pass/fail gate. An LLM writes the final wording (retrieval-augmented generation, prototype on the owner's subscription). Nothing is published; every verse is still a draft.",
         "- **Try it:** on the owner's PC, `python scripts/serve.py`, then open http://127.0.0.1:8765.",
         "- **Next step (from STATUS.md):**", "", "  " + nxt.replace("\n", "\n  "), "",
         "## Remaining, by area", "", "| Area | Where it stands | % remaining |", "|---|---|---:|"]
    L += [f"| {a} | {b} | {c}% |" for a, b, c in rows]
    L += ["", "## Runner log, last 24 hours", "",
          f"- **Cycles:** {len(cyc)} ({ok} ok, {len(fail)} failed); by builder: " + ", ".join(f"{k} {v}" for k, v in by.items()) + ".",
          f"- **Not yet reviewed by the other tool:** {len(unrev)}.",
          f"- **Commits:** {len(commits)}."]
    L += [f"- **Failed:** cycle {r['cycle']}, {r['reason']}" for r in fail]
    L += ["", "<details><summary>Commits</summary>", ""] + [f"- {c}" for c in commits[:60]] + ["", "</details>", "",
          "## The interface, screen by screen", "", INTERFACE, "## Screenshots", ""]
    L += [f"- [{p.stem}]({RAW}/claude-chat/screenshots/{p.name})" for p in shots] or ["(none yet)"]
    L += ["", "## Open owner decisions", "",
          "1. **Profile storage** (Big Five answers and the life map): where, if anywhere, they are kept. Until decided, they stay in the browser for that visit only and are never sent or saved.",
          "2. **Privacy for the LLM step:** a zero-data-retention agreement with a provider, or a local model.",
          "3. **Adopting ChatGPT's roadmap** (with Claude's amendments) as PROJECT_BRIEF.md.", ""]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
