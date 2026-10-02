"""Build a blind rating packet comparing Viveka with other assistants.

Usage: python scripts/make_blind_packet.py SET [--seed N]

Inputs:
  tests/results/<SET>.json                Viveka answers (from scripts/run_tests.py)
  tests/baselines/<tool>/<SET>.json       {"<case id>": "<answer text>", ...} for each other tool
Outputs (in tests/blind/<SET>/):
  packet.md     every case with its answers labelled A, B, C… in random order
  ratings.csv   one row per case x answer, with 0-2 columns for the six dimensions
  key.json      which label is which tool (keep this away from raters until scoring is done)

Baseline answers must be collected by a person (pasting each situation into the
other tool) or through that tool's paid API; this script never calls any service.
"""

import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.core import render  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["context", "specificity", "grounding", "judgment", "actionability", "agency"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    test_set = sys.argv[1]
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 7
    rng = random.Random(seed)
    viveka = {r["id"]: (r["text"], render(r["answer"])) for r in
              json.loads((ROOT / "tests" / "results" / f"{test_set}.json").read_text(encoding="utf-8"))}
    base_dir = ROOT / "tests" / "baselines"
    tools = {}
    if base_dir.exists():
        for d in sorted(p for p in base_dir.iterdir() if p.is_dir()):
            f = d / f"{test_set}.json"
            if f.exists():
                tools[d.name] = json.loads(f.read_text(encoding="utf-8"))
    if not tools:
        raise SystemExit(f"No baseline answers found in tests/baselines/<tool>/{test_set}.json. "
                         "Collect them first (see tests/README.md).")
    out = ROOT / "tests" / "blind" / test_set
    out.mkdir(parents=True, exist_ok=True)
    key, md, rows = {}, [f"# Blind rating packet: {test_set}", "",
                         "Rate each answer 0-2 on: " + ", ".join(DIMS) + ". See tests/README.md for definitions.", ""], []
    for cid, (text, v_answer) in viveka.items():
        answers = [("viveka", v_answer)] + [(t, a[cid]) for t, a in tools.items() if cid in a]
        if len(answers) < 2:
            continue
        rng.shuffle(answers)
        labels = [chr(65 + i) for i in range(len(answers))]
        key[cid] = {lab: tool for lab, (tool, _) in zip(labels, answers)}
        # Strip Viveka's DRAFT banner so raters cannot identify it.
        md += [f"## {cid}", "", f"> {text}", ""]
        for lab, (tool, ans) in zip(labels, answers):
            ans = ans.replace("[DRAFT: internal test answer using unreviewed material. Not for users.]", "").strip()
            md += [f"### Answer {lab}", "", ans, ""]
            rows.append([cid, lab] + [""] * len(DIMS) + [""])
    (out / "packet.md").write_text("\n".join(md), encoding="utf-8")
    (out / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    with open(out / "ratings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "answer"] + DIMS + ["comment"])
        w.writerows(rows)
    print(f"Wrote {out}: {len(key)} cases, tools: viveka + {', '.join(tools)}")


if __name__ == "__main__":
    main()
