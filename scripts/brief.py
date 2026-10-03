"""Write claude-chat/BRIEF.md: the owner's one-page brief for the Claude planning chat.
Run after every cycle (CLAUDE.md section 15):  python scripts/brief.py

Status numbers come from the repo itself (built texts, test results, verse-check results, cycle log, git log).
The screen-by-screen interface description below must be updated whenever scripts/serve_page.html changes.
"""
import csv, datetime, json, re, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "claude-chat" / "BRIEF.md"
SHOTS = ROOT / "claude-chat" / "screenshots"
REPO = "https://github.com/yjzw6km8y5-hub/viveka"
RAW = "https://raw.githubusercontent.com/yjzw6km8y5-hub/viveka/main"

INTERFACE = """### Screen 1: Onboarding (first visit only; four steps with a progress bar)
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
"""


def sh(*a):
    exe = shutil.which(a[0]) or (r"C:\Program Files\Git\cmd\git.exe" if a[0] == "git" else a[0])
    return subprocess.run([exe, *a[1:]], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.strip()


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
    rows.append(("Zero-data-retention API before anyone else uses Viveka", "not set up (owner testing uses his subscription)", 100))

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
    L += ["", "## Owner decisions and what is still open", "",
          "- **Decided 2026-10-03:** the profile stays on the device only.",
          "- **Decided 2026-10-03:** the LLM step runs on the owner's subscription for the owner's own testing only. Before anyone else uses Viveka, it needs an API with zero data retention.",
          "- **Open:** ChatGPT's roadmap and business plan (below). The owner decides after the Claude chat reviews it. Claude Code's four amendments are in `AI Review Desk/Viveka/ROADMAP_RESPONSE_claude.md`.", ""]
    road = ROOT.parent / "AI Review Desk" / "Viveka" / "VIVEKA_DESIGN_ROADMAP.md"
    if road.exists():
        L += ["## For review: ChatGPT's roadmap and business plan (in full)", "",
              "_Copied verbatim from `AI Review Desk/Viveka/VIVEKA_DESIGN_ROADMAP.md` each time this brief is written. "
              "The business plan is its section \"Commercial forecast\"; there is no separate business-plan file._", "", "---", ""]
        L += [re.sub(r"^(#+) ", lambda m: "#" * min(len(m.group(1)) + 2, 6) + " ", line)  # nest its headings under this one
              for line in road.read_text(encoding="utf-8").splitlines()]
        L += ["", "---", ""]
    text = "\n".join(L) + "\n"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    # The Claude planning chat reads its own copy on the Drive. Overwrite the contents of that existing file
    # in place (same file, same Drive ID); never delete, rename or recreate it.
    desk = ROOT.parent / "AI Review Desk" / "Viveka" / "BRIEF.md"
    if desk.exists():
        with open(desk, "r+b") as f:
            f.seek(0)
            f.write(text.encode("utf-8"))
            f.truncate()
        print("overwrote AI Review Desk/Viveka/BRIEF.md in place")
    else:
        print("AI Review Desk/Viveka/BRIEF.md not found; not created (Claude chat must create it)")


if __name__ == "__main__":
    main()
