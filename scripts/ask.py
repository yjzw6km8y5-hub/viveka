"""Ask the Viveka answer engine a question (local prototype; nothing is saved or sent anywhere).

Usage: python scripts/ask.py "your situation" [--age N] [--stage student|householder|elder|renunciant]
                                              [--public] [--json] [--region IN|US|UK]
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.core import answer, render  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    profile, mode, region, as_json, text = {}, "internal", None, False, []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--age":
            profile["age"] = int(args[i + 1]); i += 2; continue
        if a == "--stage":
            profile["life_stage"] = args[i + 1]; i += 2; continue
        if a == "--region":
            region = args[i + 1]; i += 2; continue
        if a == "--public":
            mode = "public"; i += 1; continue
        if a == "--json":
            as_json = True; i += 1; continue
        text.append(a); i += 1
    a = answer(" ".join(text), profile, mode=mode, region=region)
    print(json.dumps(a, ensure_ascii=False, indent=1) if as_json else render(a))


if __name__ == "__main__":
    main()
