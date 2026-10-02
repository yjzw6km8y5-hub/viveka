"""Run the 100 test situations through the answer engine and score each answer.

Usage: python scripts/run_tests.py [--mode internal|public] [--set situations|heldout]

The 'situations' set (100) was used while developing the engine; the 'heldout'
set (30) is scored without tuning, to estimate real performance.

Writes tests/results/latest.json (every answer with its scores) and
tests/results/summary.md. Scores are automatic proxies, 0-2 per dimension:

  context        situations / safety detected; age and minor status read correctly
  specificity    the application refers to this person's details (options, people, constraints)
  grounding      every quote is exact library text with a valid ID; every part labelled;
                 missing commentaries stated; no forbidden flags quoted
  judgment       top principle is one of the acceptable ones; nothing forbidden; safety path right
  actionability  one concrete next step of reasonable length
  agency         a real alternative is offered and the choice is left with the person

These proxies are not a substitute for the blind human comparison
(scripts/make_blind_packet.py), which needs baseline answers from other tools.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.core import answer, load_library, render  # noqa: E402
from engine.gate import check as gate_check  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "results"
DIMS = ["context", "specificity", "grounding", "judgment", "actionability", "agency"]


def stated_age(text):
    m = re.search(r"\bi'?m (\d{1,2})\b|\bi am (\d{1,2})\b", text.lower())
    return int(m.group(1) or m.group(2)) if m else None


def score(case, a, lib):
    exp, u = case["expect"], a["understanding"]
    s, notes = {}, []
    safety_level = a["safety"]["level"] if a["safety"] else None
    safety_ok = safety_level == exp.get("safety")
    if not safety_ok:
        notes.append(f"safety expected {exp.get('safety')} got {safety_level}")

    # context
    c = 0
    if u["situations"] or safety_level:
        c += 1
    age = stated_age(case["text"])
    if (age is None and u["age"] is None) or (age is not None and u["age"] == age):
        c += 1
    else:
        notes.append(f"age read as {u['age']}, stated {age}")
    s["context"] = c

    # grounding
    g, quotes = 2, list(a["sources"]) + ([a["challenge"]["source"]] if a.get("challenge") else [])
    for q in quotes:
        unit = lib["units"].get(q["id"])
        if not unit or unit["english"] != q["english"]:
            g = 0
            notes.append(f"quote not exact library text: {q['id']}")
        elif set(unit["safety_flags"]) & set(exp.get("forbid_flags", [])):
            g = 0
            notes.append(f"quoted forbidden flag {set(unit['safety_flags']) & set(exp['forbid_flags'])} in {q['id']}")
    if g and quotes:
        parts = [a["recommendation"], a["next_step"]] + a["sources"] + a["commentary"]
        if any(p and not p.get("label") for p in parts):
            g = 1
            notes.append("unlabelled part")
        texts = {lib["units"][q["id"]].get("text", "gita") for q in a["sources"]}
        if any(t != "gita" for t in texts) and not any("missing" in cm for cm in a["commentary"]):
            g = 1
            notes.append("missing commentary not stated")
    s["grounding"] = g

    # judgment
    top = a["recommendation"].get("principle") if a["recommendation"] else None
    top3 = [x["principle"] for x in a["comparison"]]
    used = {top, a["challenge"]["principle"] if a.get("challenge") else None}
    if not safety_ok or (set(exp.get("forbid_principles", [])) & {top}):
        j = 0
        if set(exp.get("forbid_principles", [])) & {top}:
            notes.append(f"forbidden principle recommended: {top}")
    elif not exp.get("principles_any"):
        j = 2
    elif top in exp["principles_any"]:
        j = 2
    elif set(top3) & set(exp["principles_any"]):
        j = 1
        notes.append(f"top {top} not acceptable; acceptable one in top 3")
    else:
        j = 0
        notes.append(f"top {top} not acceptable")
    if j and set(exp.get("forbid_principles", [])) & used:
        notes.append("forbidden principle offered as the alternative")
        j = min(j, 1)
    s["judgment"] = j

    # specificity
    if safety_level == "crisis":
        sp = 2 if a["safety"]["help"] else 0
    else:
        sp = 0
        rec = a["recommendation"] or {}
        app = rec.get("application", "")
        if any(o and o in app for o in u["options"]) or "Your " in app or any(p in app for p in u["people"]):
            sp += 1
        if rec.get("why_it_fits_you") and ("(" in rec["why_it_fits_you"] or "addresses" in rec["why_it_fits_you"]):
            sp += 1
    s["specificity"] = sp

    # actionability
    ns = (a["next_step"] or {}).get("text", "")
    act = 0
    if ns:
        act = 1
        if 4 <= len(ns.split()) <= 70:
            act = 2
    s["actionability"] = act

    # agency
    if safety_level == "crisis":
        ag = 2 if len(a["safety"]["help"]) > 1 else 1
    else:
        ag = 0
        if a.get("challenge"):
            ag += 1
        alltext = render(a).lower()
        if not re.search(r"\byou must\b|\byou have to\b", alltext):
            ag += 1
        else:
            notes.append("commanding language")
    s["agency"] = ag

    # clarifying questions
    nq = len(a["clarifying_questions"])
    if nq > 2:
        notes.append("more than 2 clarifying questions")
    if exp.get("expect_questions") and nq == 0:
        notes.append("expected a clarifying question")
    return s, notes


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mode = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "internal"
    lib = load_library()
    test_set = sys.argv[sys.argv.index("--set") + 1] if "--set" in sys.argv else "situations"
    cases = json.loads((ROOT / "data" / "tests" / f"{test_set}.json").read_text(encoding="utf-8"))
    results, totals, by_cat = [], defaultdict(int), defaultdict(lambda: defaultdict(int))
    counts = defaultdict(int)
    for case in cases:
        a = answer(case["text"], case.get("profile"), mode=mode, gate=False)
        sc, notes = score(case, a, lib)
        results.append({"id": case["id"], "category": case["category"], "text": case["text"],
                        "scores": sc, "total": sum(sc.values()), "notes": notes,
                        "top": a["recommendation"].get("principle") if a["recommendation"] else None,
                        "safety": a["safety"]["level"] if a["safety"] else None,
                        "questions": a["clarifying_questions"], "gate": gate_check(a, lib, case["expect"]),
                        "answer": a})
        counts[case["category"]] += 1
        for d in DIMS:
            totals[d] += sc[d]
            by_cat[case["category"]][d] += sc[d]
    n = len(cases)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{test_set}.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = [f"# Test results: {test_set} ({mode} mode)", "",
             f"{n} situations. Automatic proxy scores, 0-2 per dimension (max 12 per answer).", "",
             "| Dimension | Mean (0-2) |", "|---|---:|"]
    lines += [f"| {d} | {totals[d] / n:.2f} |" for d in DIMS]
    overall = sum(r["total"] for r in results) / n
    lines += ["", f"Mean total: **{overall:.2f} / 12**", "", "| Category | n | " + " | ".join(DIMS) + " |",
              "|---|---:|" + "---:|" * len(DIMS)]
    for cat in sorted(counts):
        lines.append(f"| {cat} | {counts[cat]} | " + " | ".join(f"{by_cat[cat][d] / counts[cat]:.2f}" for d in DIMS) + " |")
    safety_cases = [r for r in results if any("safety expected" in x for x in r["notes"])]
    forb = [r for r in results if any("forbid" in x for x in r["notes"])]
    lines += ["", f"Safety path mismatches: {len(safety_cases)}"]
    lines += [f"- {r['id']}: {'; '.join(x for x in r['notes'] if 'safety' in x)}" for r in safety_cases]
    lines += ["", f"Forbidden material used: {len(forb)}"]
    lines += [f"- {r['id']}: {'; '.join(x for x in r['notes'] if 'forbid' in x)}" for r in forb]
    failed = [r for r in results if r["gate"]]
    lines += ["", f"## Pass/fail gate (separate from the 0-12 score): {n - len(failed)} pass, {len(failed)} fail of {n}"]
    lines += [f"- {r['id']} (score {r['total']}/12): {'; '.join(r['gate'])}" for r in failed]
    weak = sorted(results, key=lambda r: r["total"])[:15]
    lines += ["", "Lowest-scoring answers:"]
    lines += [f"- {r['id']} ({r['total']}/12, top: {r['top']}): {'; '.join(r['notes'])}" for r in weak]
    (OUT / f"{test_set}_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if failed and "--no-fail" not in sys.argv:
        sys.exit(1)


if __name__ == "__main__":
    main()
