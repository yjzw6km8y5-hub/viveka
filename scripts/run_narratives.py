"""Run the long-narrative development cases (data/tests/narratives.json) through the story flow and check them.

  python scripts/run_narratives.py --tag first-run     (keep the first run; never overwrite it)
  python scripts/run_narratives.py --tag after          (reruns)

Per case: safety route; the core dilemma found (the two expected pulls); the reflection uses only the person's
words and names the people; follow-up questions are relevant and not repeated; the advice addresses the core
dilemma, not the side detail, and refers to the person's specifics; forbidden principles are not recommended;
the engine's own pass/fail gate. Engine wording only (no LLM), so runs are fast and repeatable.
Results: tests/results/<tag>/narratives.json and narratives_summary.md.
"""
import json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine import narrative as N  # noqa: E402
from engine.core import load_library  # noqa: E402
from engine.gate import check as gate_check  # noqa: E402


def run_case(c, lib):
    e, text = c["expect"], c["text"]
    t0 = time.time()
    an = N.analyse(text)
    refl = N.reflection(an)
    qs = N.followups(an, [], 0)
    t_listen = time.time() - t0
    a, an, whole = N.advise(text)
    adv = N.compose_advice(a, an)
    level = (a.get("safety") or {}).get("level")
    fails = []
    if level != e.get("safety"):
        fails.append(f"safety: expected {e.get('safety')}, got {level}")
    special = level in ("danger", "crisis") or a.get("protective")
    if not special and set(e["core_pulls"]) != set(an["core"]):
        fails.append(f"core dilemma: expected {'/'.join(e['core_pulls'])}, found {'/'.join(an['core'])}")
    side = e.get("side_detail")
    spec = [w for g in e.get("specifics", []) for w in g]
    if side and any(side.lower() in p["quote"].lower() and not any(w in p["quote"].lower() for w in spec) for p in an["pulls"]):
        fails.append(f"reflection centres a side detail ({side})")
    found = [p for p in e.get("people", []) if any(p in q or q in p for q in refl["people"])]
    if len(found) < min(2, len(e.get("people", []))):
        fails.append(f"reflection misses the people (expected {e.get('people')}, named {refl['people']})")
    fails += N.check_reflection(refl, text)
    fails += N.check_questions(qs, [], an)
    if level != "crisis":
        fails += N.check_advice(a, an, adv["text"], lib)
        low = adv["text"].lower()
        for group in e.get("specifics", []):
            if not any(w in low for w in group):
                fails.append("advice misses specifics: " + " / ".join(group))
    top = (a.get("recommendation") or {}).get("principle")
    if top in e.get("forbid_principles", []):
        fails.append(f"forbidden principle: {top}")
    fails += [f"gate: {g}" for g in gate_check(a, lib)]
    return {"id": c["id"], "category": c["category"], "style": c["style"], "words": len(text.split()),
            "listen_seconds": round(t_listen, 3), "safety": level, "core": an["core"], "top": top,
            "questions": [q["text"] for q in qs], "reflection": refl["text"], "advice": adv, "fails": fails}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "latest"
    out = ROOT / "tests" / "results" / tag
    if (out / "narratives.json").exists() and tag == "first-run":
        sys.exit("A first run already exists; it is never overwritten. Use another tag for reruns.")
    lib = load_library()
    cases = json.loads((ROOT / "data/tests/narratives.json").read_text(encoding="utf-8"))
    res = [run_case(c, lib) for c in cases]
    out.mkdir(parents=True, exist_ok=True)
    (out / "narratives.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = [r for r in res if not r["fails"]]
    L = [f"# Long-narrative cases ({tag})", "",
         f"{len(res)} cases (builder-written development set: not independent). Pass: {len(ok)}, fail: {len(res) - len(ok)}. "
         f"Slowest listening turn: {max(r['listen_seconds'] for r in res):.2f} s.", "",
         "| Case | Kind | Words | Safety | Core found | Top principle | Result |", "|---|---|---:|---|---|---|---|"]
    for r in res:
        L.append(f"| {r['id']} | {r['category']}, {r['style']} | {r['words']} | {r['safety']} | {'/'.join(r['core'])} | "
                 f"{r['top']} | {'pass' if not r['fails'] else 'FAIL: ' + '; '.join(r['fails']).replace('|', '/')} |")
    (out / "narratives_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    if len(ok) < len(res) and "--no-fail" not in sys.argv:
        sys.exit(1)


if __name__ == "__main__":
    main()
