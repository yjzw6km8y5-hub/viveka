"""Print a chapter's verses with the opening of each school's commentary.

An authoring and review aid: everything printed comes from data/gita.json and
data/gita_commentaries.json, so writing English or school notes never depends
on memory.

Usage: python scripts/show_chapter.py CHAPTER [FIRST LAST] [--chars N]
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    chars = 450
    if "--chars" in args:
        i = args.index("--chars")
        chars = int(args[i + 1])
        del args[i:i + 2]
    chapter = int(args[0])
    first, last = (int(args[1]), int(args[2])) if len(args) >= 3 else (1, 999)

    records = json.loads((ROOT / "data" / "gita.json").read_text(encoding="utf-8"))
    comms = json.loads((ROOT / "data" / "gita_commentaries.json").read_text(encoding="utf-8"))["verses"]
    seen = {}  # (school, text) -> first verse id, since joint commentaries repeat
    for r in records:
        if r["chapter"] != chapter:
            continue
        in_range = first <= r["verse"] <= last
        if in_range:
            print(f"== {r['id']}  [{r['speaker']}]")
            print(r["devanagari"])
        for school, text in comms.get(r["id"], {}).items():
            text = re.sub(r"^।।[^।]*।।\s*", "", text).replace("\n", " ")
            if (school, text) in seen:
                if in_range:
                    print(f"  -- {school}: (same text as {seen[(school, text)]})")
                continue
            seen[(school, text)] = r["id"]
            if in_range:
                print(f"  -- {school}: {text[:chars]}{'…' if len(text) > chars else ''}")
        if in_range:
            print()


if __name__ == "__main__":
    main()
