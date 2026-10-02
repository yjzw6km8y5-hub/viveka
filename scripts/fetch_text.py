"""Download pinned Wikisource snapshots for a text listed in data/texts.json.

Usage: python scripts/fetch_text.py TEXT_ID [TEXT_ID ...]

The registry entry must have "source_pages": {"text": [titles in reading order],
"bhashya": [commentary page titles]} and "raw": the output path. Writes
{"text": [snapshots], "bhashya": [snapshots]} in the same format as
fetch_upanishads.py, so build_texts.py can read either.
"""

import json
import sys
from pathlib import Path

from wikisource import fetch_page

ROOT = Path(__file__).resolve().parent.parent


def main():
    registry = json.loads((ROOT / "data" / "texts.json").read_text(encoding="utf-8"))
    for text_id in sys.argv[1:]:
        meta = registry[text_id]
        pages = meta["source_pages"]
        out = {}
        for kind in ("text", "bhashya"):
            out[kind] = []
            for title in pages.get(kind, []):
                snap = fetch_page(title)
                if snap is None:
                    raise SystemExit(f"{text_id}: missing page {title}")
                out[kind].append(snap)
        path = ROOT / meta["raw"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{text_id}: {len(out['text'])} text pages, {len(out['bhashya'])} commentary pages -> {meta['raw']}")


if __name__ == "__main__":
    main()
