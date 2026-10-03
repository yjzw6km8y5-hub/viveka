"""Builder self-check: run before every commit and handoff (CLAUDE.md section 14).

  python scripts/self_check.py

Runs the build, validation, unit tests and every test set with the answer gate on, then compares
each case's gate result with the last accepted run (tests/results/after/). It fails if:
  - build, validation or any unit test fails
  - any safety-path mismatch or use of forbidden material appears
  - any case that passed the gate in the accepted run now fails (a regression)
  - STATUS.md has no HANDOFF note dated today
Newly passing cases are reported as improvements; accept them with --accept, which copies this
run over tests/results/after/. Results of each run go to tests/results/selfcheck/ (not committed).
"""
import datetime, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
SETS = ["situations", "heldout", "heldout2", "paired"]
UNIT = ["tests/test_gate.py", "tests/test_guidance.py", "tests/test_proposals.py"]


def run(args):
    r = subprocess.run([PY, *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    problems, notes = [], []
    for args, name in ((["scripts/build_gita.py"], "build_gita"), (["scripts/build_texts.py"], "build_texts"),
                       (["scripts/validate.py", "--allow-incomplete"], "validate")):
        code, out = run(args)
        if code or (name == "validate" and not out.rstrip().endswith("VALID")):
            problems.append(f"{name} failed: {out.splitlines()[-1] if out else code}")
    for t in UNIT:
        code, out = run([t])
        if code:
            problems.append(f"{t} failed: {out.splitlines()[-1] if out else code}")
    for s in SETS:
        code, out = run(["scripts/run_tests.py", "--set", s, "--tag", "selfcheck", "--no-fail"])
        new = json.loads((ROOT / "tests/results/selfcheck" / f"{s}.json").read_text(encoding="utf-8"))
        for r in new:
            if any("safety expected" in n or "forbid" in n for n in r["notes"]):
                problems.append(f"{s} {r['id']}: {'; '.join(r['notes'])}")
        base_path = ROOT / "tests/results/after" / f"{s}.json"
        if base_path.exists():
            base = {r["id"]: r for r in json.loads(base_path.read_text(encoding="utf-8"))}
            for r in new:
                b = base.get(r["id"])
                if b and not b["gate"] and r["gate"]:
                    problems.append(f"regression {s} {r['id']}: {'; '.join(r['gate'])}")
                elif b and b["gate"] and not r["gate"]:
                    notes.append(f"improved {s} {r['id']}")
        passed = sum(not r["gate"] for r in new)
        notes.append(f"{s}: gate {passed}/{len(new)} pass")
    today = datetime.date.today().isoformat()
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    handoff = status.split("## Handoff", 1)[-1]
    if today not in handoff.split("\n- ", 2)[1] if "\n- " in handoff else True:
        problems.append("STATUS.md has no HANDOFF note dated today at the top of the Handoff section")
    print("\n".join(notes))
    if "--accept" in sys.argv and not problems:
        for s in SETS:
            shutil.copy(ROOT / "tests/results/selfcheck" / f"{s}.json", ROOT / "tests/results/after" / f"{s}.json")
            shutil.copy(ROOT / "tests/results/selfcheck" / f"{s}_summary.md", ROOT / "tests/results/after" / f"{s}_summary.md")
        print("Accepted this run as the new baseline (tests/results/after/).")
    if problems:
        print("\nSELF-CHECK FAILED:\n- " + "\n- ".join(problems))
        sys.exit(1)
    print("\nSELF-CHECK PASSED")


if __name__ == "__main__":
    main()
