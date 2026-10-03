"""Local try-it page for Viveka (owner and testers only; nothing is published).

  python scripts/serve.py            then open http://127.0.0.1:8765   (add ?dev=1 for the test-case form)

Conversation flow (owner decisions 2026-10-03):
  1. Onboarding once: age and country, kept on the device only (browser storage), never sent anywhere except with
     each question to this local server.
  2. The person writes. /triage reflects the situation back, shows safety or health help at once if needed, and
     asks a few context questions (who they live with, constraints, timing). "Just answer" skips them.
  3. /answer runs the engine with the gate on the message plus the context, then (if AI writing is on in
     settings) the LLM writing step rewrites it in plain words from the same checked material. One answer is shown.
Questions are answered in memory and never written anywhere. AI writing sends the text to Anthropic through the
owner's subscription: owner testing only, until there is a zero-data-retention API (DECISIONS.md).
Listens on 127.0.0.1 only.
"""
import json, sys, threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine import llm  # noqa: E402
from engine.core import SITUATION_LABEL, answer, help_lines, load_library  # noqa: E402

PAGE = Path(__file__).with_name("serve_page.html")
CASES = ROOT / "data" / "tests" / "independent.json"
LOCK = threading.Lock()
COUNTRIES = {"CA": "CA", "IN": "IN", "US": "US", "UK": "UK"}
FRAME_LABEL = {"study_focus": "focus and study", "outcome_anxiety": "worry about results", "family_care": "caring for family",
               "hurt_by_someone": "being hurt", "i_hurt_someone": "having hurt someone", "pride_credit": "credit and pride",
               "witness_wrong": "seeing wrongdoing", "peer_pressure": "peer pressure", "fear_courage": "fear",
               "parent_child": "parents and children", "death_question": "questions about death", "spiritual_doubt": "faith and doubt",
               "coercive_authority": "pressure from authority", "friendship_hurt": "a friendship", "risky_choice": "a risky choice",
               "difficult_conversation": "a hard conversation", "family_shame": "family shame", "why_suffering": "why suffering happens",
               "karma_blame": "karma and blame", "eating": "eating and your body", "remarriage": "remarriage",
               "family_rift": "a family rift", "managing": "managing people", "worry_control": "worry", "career": "work and career",
               "money": "money", "grief": "a loss", "anger": "anger", "envy": "comparison", "loneliness": "loneliness"}
QUESTIONS = [
    {"id": "live", "text": "Who do you live with?",
     "options": ["On my own", "With family", "With a partner", "With roommates or friends", "I'd rather not say"]},
    {"id": "limits", "text": "What's limiting your options right now?", "multi": True,
     "options": ["Money", "Time", "Family expectations", "Health", "Nothing major"]},
    {"id": "when", "text": "How soon do you need to act?", "options": ["Today", "This week", "No rush"]},
]
CONTEXT_TEXT = {
    "live": {"On my own": "I live on my own.", "With family": "I live with my family.", "With a partner": "I live with my partner.",
             "With roommates or friends": "I live with roommates."},
    "when": {"Today": "I need to act today.", "This week": "I need to decide this week."},
}


def profile_of(b):
    p = b.get("profile") or {}
    prof = {"age": int(p["age"])} if str(p.get("age", "")).isdigit() else {}
    return prof, COUNTRIES.get(p.get("country"))


def themes_of(a):
    u = a["understanding"]
    t = [FRAME_LABEL.get(f, f.replace("_", " ")) for f in u.get("frames", []) if f not in ("distress", "danger", "decision")]
    t += [SITUATION_LABEL[s] for s in u.get("situations", [])[:2] if s in SITUATION_LABEL]
    return list(dict.fromkeys(t))[:3]


def reflection(a):
    themes = themes_of(a)
    if "a friendship" in themes or "parents and children" in themes or "a family rift" in themes:
        themes = [t for t in themes if t != "a relationship"]
    people = a["understanding"].get("people", [])
    people = [p for p in people if not any(p != q and p in q for q in people)][:2]  # "best friend" covers "friend"
    if not themes and not people:
        return "Thank you for telling me this."
    s = "It sounds like this is about " + (" and ".join(themes) if themes else "something that matters to you")
    if people:
        s += ", and it involves your " + " and ".join(people)
    return s + "."


def safety_cards(a):
    cards = []
    s = a.get("safety")
    if s and s["level"] in ("crisis", "danger", "support"):
        title = {"crisis": "Please reach out now", "danger": "Your safety first", "support": "You don't have to carry this alone"}[s["level"]]
        cards.append({"kind": s["level"], "title": title, "text": s["message"], "help": s["help"]})
    if a.get("protective"):
        cards.append({"kind": "health", "title": "Your health first", "text": a["protective"]["text"], "help": a["protective"]["help"]})
    return cards


def triage(b):
    prof, region = profile_of(b)
    a = answer(str(b.get("q", ""))[:4000], prof, mode="internal", region=region)
    crisis = (a.get("safety") or {}).get("level") == "crisis"
    extra = [q for q in a.get("clarifying_questions", []) if not (prof.get("age") and "18 or older" in q)]
    qs = [] if crisis else QUESTIONS + [{"id": f"x{i}", "text": q, "free": True} for i, q in enumerate(extra[:1])]
    return {"reflection": reflection(a), "cards": safety_cards(a), "questions": qs, "final": crisis,
            "next_step": (a.get("next_step") or {}).get("text") if crisis else None}


def compose(q, ctx):
    parts = [q.strip()]
    for k, v in (ctx or {}).items():
        if k in CONTEXT_TEXT and v in CONTEXT_TEXT[k]:
            parts.append(CONTEXT_TEXT[k][v])
        elif k == "limits" and v:
            lim = [x.lower() for x in (v if isinstance(v, list) else [v]) if x != "Nothing major"]
            if lim:
                parts.append("What limits me: " + ", ".join(lim) + ".")
        elif k.startswith("x") and isinstance(v, str) and v.strip():
            parts.append(v.strip())
    return " ".join(parts)


def respond(b):
    prof, region = profile_of(b)
    q = str(b.get("q", ""))[:4000]
    a = answer(compose(q, b.get("context"))[:6000], prof, mode="internal", region=region)
    a["user_message"] = q  # the AI writer sees the message and the context answers separately
    a["background"] = [x for x in compose("", b.get("context")).split(". ") if x.strip()]
    written, note = (llm.write(a) if b.get("ai") else (None, "AI writing is off in settings"))
    rec = a.get("recommendation") or {}
    meaning = rec.get("text", "")
    if rec.get("name") and meaning.startswith(rec["name"]):
        meaning = meaning[len(rec["name"]):].lstrip(". ")
    comp = a.get("comparison", [])
    lib = load_library()
    minor = a["understanding"].get("minor") != "no"
    footer = help_lines(lib, ["self_harm", "danger"] + (["under18"] if minor else []), region)
    return {
        "notice": a["notice"], "cards": safety_cards(a),
        "opening": (written or {}).get("opening") or ("Here's one way to look at what you're facing." if rec.get("name") else rec.get("text", "")),
        "body": (written or {}).get("answer") or meaning,
        "next_step": (written or {}).get("next_step") or (a.get("next_step") or {}).get("text"),
        "closest": rec.get("name"), "also": [c["name"] for c in comp[1:3]],
        "aims": lib["principles"].get(rec.get("principle"), {}).get("aims", []),
        "why": rec.get("why_it_fits_you"), "application": rec.get("application"),
        "sources": [{"id": s["id"], "english": s["english"], "devanagari": s["devanagari"]} for s in a.get("sources", [])],
        "alternative": (written or {}).get("alternative") or (a.get("challenge") or {}).get("text"),
        "alternative_source": (a.get("challenge") or {}).get("source"),
        "commentary": a.get("commentary", []), "example": a.get("example"),
        "written_by": "AI, from the passages shown, then checked" if written else "Viveka" + (f" ({note})" if b.get("ai") else ""),
        "outcome": "withheld" if a.get("withheld") else "clarifying question" if a.get("clarify") else
                   "passed after a replacement" if a.get("regenerated") else "passed",
        "reviewed": sum(lib["units"].get(s["id"], {}).get("review_status") in ("reviewed", "approved") for s in a.get("sources", [])),
        "footer": footer,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # no request logging: questions are never written anywhere
        pass

    def send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/index.html"):
            self.send(200, PAGE.read_text(encoding="utf-8"), "text/html; charset=utf-8")
        else:
            self.send(404, json.dumps({"error": "not found"}))

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(min(n, 30000)) or b"{}")

    def do_POST(self):
        try:
            b = self.body()
            if self.path == "/triage":
                self.send(200, json.dumps(triage(b), ensure_ascii=False, default=str))
            elif self.path == "/answer":
                self.send(200, json.dumps(respond(b), ensure_ascii=False, default=str))
            elif self.path == "/case":
                with LOCK:
                    cases = json.loads(CASES.read_text(encoding="utf-8")) if CASES.exists() else []
                    cid = f"I{len(cases) + 1:03d}"
                    cases.append({"id": cid, "category": b.get("category", "adult"), "text": str(b["text"])[:4000],
                                  "profile": {}, "author": str(b["author"])[:80],
                                  "written": datetime.now().astimezone().isoformat(timespec="minutes"),
                                  "good_answer": str(b["good_answer"])[:4000],
                                  "expect": {"safety": b.get("safety") or None}})
                    CASES.write_text(json.dumps(cases, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
                self.send(200, json.dumps({"id": cid, "count": len(cases)}))
            else:
                self.send(404, json.dumps({"error": "not found"}))
        except Exception as e:  # report, never crash the page
            self.send(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))


def main():
    load_library()
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8765
    print(f"Viveka local page: http://127.0.0.1:{port}  (Ctrl+C to stop)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
