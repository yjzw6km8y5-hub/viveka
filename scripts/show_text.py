"""Print units of a built text with the opening of each commentary, for annotating.

Usage: python scripts/show_text.py TEXT_ID [FIRST_INDEX LAST_INDEX] [--chars N]
Indexes are 1-based positions in the built file (not mantra numbers).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    chars = 600
    if "--chars" in sys.argv:
        chars = int(sys.argv[sys.argv.index("--chars") + 1])
        args = [a for a in args if a != str(chars)]
    text_id = args[0]
    first = int(args[1]) if len(args) > 1 else 1
    last = int(args[2]) if len(args) > 2 else 10**9
    records = json.loads((ROOT / "data" / f"{text_id}.json").read_text(encoding="utf-8"))
    comm = json.loads((ROOT / "data" / "commentaries" / f"{text_id}.json").read_text(encoding="utf-8"))["units"]
    seen = {}
    for i, r in enumerate(records[first - 1:last], start=first):
        print(f"== {r['id']}  (#{i})")
        print(r["devanagari"])
        for school, text in comm.get(r["id"], {}).items():
            key = (school, text)
            if key in seen:
                print(f"  -- {school}: (same text as {seen[key]})")
                continue
            seen[key] = r["id"]
            body = " ".join(text.split())
            print(f"  -- {school}: {body[:chars]}{'…' if len(body) > chars else ''}")
        print()


if __name__ == "__main__":
    main()
