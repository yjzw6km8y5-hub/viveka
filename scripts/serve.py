"""Local try-it page for Viveka (owner and testers only; nothing is published).

  python scripts/serve.py            then open http://127.0.0.1:8765

- "Ask": runs the engine with the pass/fail gate exactly as a user would see it (internal mode: drafts are
  marked DRAFT), plus a visual summary. With "AI-written" on, the LLM writing step (engine/llm.py) then
  rewrites the answer in plain words from the same checked material. Questions are answered in memory and
  never written anywhere. AI writing sends the text to Anthropic through the owner's subscription.
- "Add a test case": for the independent test set; saved to data/tests/independent.json (test data,
  deliberately kept). Scored once on the engine as it stands before anyone tunes against it.
Listens on 127.0.0.1 only.
"""
import json, sys, threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine import llm  # noqa: E402
from engine.core import SITUATION_LABEL, answer, load_library  # noqa: E402

PAGE = Path(__file__).with_name("serve_page.html")
CASES = ROOT / "data" / "tests" / "independent.json"
LOCK = threading.Lock()
FRAME_LABEL = {"study_focus": "focus and study", "outcome_anxiety": "worry about results", "family_care": "caring for family",
               "hurt_by_someone": "being hurt", "i_hurt_someone": "having hurt someone", "pride_credit": "credit and pride",
               "renounce_wish": "wanting to leave it all", "witness_wrong": "seeing wrongdoing", "peer_pressure": "peer pressure",
               "fear_courage": "fear", "parent_child": "parents and children", "death_question": "questions about death",
               "spiritual_doubt": "faith and doubt", "coercive_authority": "pressure from authority", "friendship_hurt": "friendship",
               "risky_choice": "a risky choice", "difficult_conversation": "a hard conversation", "family_shame": "family shame",
               "why_suffering": "why suffering happens", "karma_blame": "karma and blame", "eating": "eating and body",
               "remarriage": "remarriage", "family_rift": "family rift", "managing": "managing people", "worry_control": "worry"}


def visual(a):
    """Short, visual summary of an answer. Numbers are the engine's own estimates, labelled as such."""
    u, rec = a["understanding"], a["recommendation"] or {}
    themes = [SITUATION_LABEL[s] for s in u.get("situations", [])[:3] if s in SITUATION_LABEL]
    themes += [FRAME_LABEL.get(f, f.replace("_", " ")) for f in u.get("frames", []) if f not in ("distress", "danger", "decision")]
    themes = list(dict.fromkeys(themes))[:5]
    scores = {c["id"]: c["score"] for c in a.get("shortlist", [])}
    top = max(scores.values(), default=0) or 1
    persp = [{"name": c["name"], "fit": max(1, min(10, round(10 * scores.get(c["principle"], 0) / top)))}
             for c in a.get("comparison", [])]
    level = (a.get("safety") or {}).get("level")
    if level == "crisis":
        urg, lab = 10, "Reach out today"
    elif level == "danger":
        urg, lab = 9, "Safety comes first"
    elif a.get("protective"):
        urg, lab = 7, "Health matters soon"
    elif u["constraints"].get("urgency") or level == "support":
        urg, lab = 6, "Soon, not rushed"
    else:
        urg, lab = 3, "Time to reflect"
    quoted = list(a.get("sources", [])) + ([a["challenge"]["source"]] if a.get("challenge") else [])
    lib = load_library()
    reviewed = sum(lib["units"].get(q["id"], {}).get("review_status") in ("reviewed", "approved") for q in quoted)
    meaning = rec.get("text", "")
    if rec.get("name") and meaning.startswith(rec["name"]):
        meaning = meaning[len(rec["name"]):].lstrip(". ")
    return {"headline": rec.get("name") or rec.get("text", ""), "summary": meaning if rec.get("name") else "",
            "themes": themes, "people": u.get("people", []), "perspectives": persp, "urgency": urg,
            "urgency_label": lab, "quoted": len(quoted), "reviewed": reviewed}


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
        if self.path in ("/", "/index.html"):
            self.send(200, PAGE.read_text(encoding="utf-8"), "text/html; charset=utf-8")
        else:
            self.send(404, json.dumps({"error": "not found"}))

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(min(n, 20000)) or b"{}")

    def build(self, b):
        profile = {"age": int(b["age"])} if str(b.get("age", "")).isdigit() else {}
        return answer(str(b.get("q", ""))[:4000], profile, mode="internal")

    def do_POST(self):
        try:
            b = self.body()
            if self.path == "/ask":
                a = self.build(b)
                v = visual(a)
                a.pop("question", None)
                self.send(200, json.dumps({"answer": a, "visual": v, "ai_ok": llm.available()}, ensure_ascii=False, default=str))
            elif self.path == "/write":
                written, note = llm.write(self.build(b))
                self.send(200, json.dumps({"written": written, "note": note}, ensure_ascii=False))
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
