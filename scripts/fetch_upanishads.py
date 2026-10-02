"""Download pinned snapshots of the 13 principal Upanishads and Śaṅkara's bhāṣyas.

Usage: python scripts/fetch_upanishads.py [TEXT_ID ...]

Writes data/raw/upanishads/<text_id>.json: {"text": [page snapshots in reading
order], "bhashya": [page snapshots]}. Page lists are explicit because the
Wikisource pages for these texts use inconsistent titles and subpage names;
the choice of pages is explained in DECISIONS.md.
"""

import json
import sys
from pathlib import Path

from wikisource import fetch_page

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "upanishads"

KATHA = "कठोपनिषत्/{}ोध्यायः/{}वल्ली"
SOURCES = {
    "isha": {
        "text": ["ईशोपनिषत्"],
        "bhashya": ["ईशावास्योपनिषद्भाष्यम्"],
    },
    "kena": {
        "text": ["केनोपनिषद्"],
        "bhashya": ["केनोपनिषद्भाष्यम्"],
    },
    "katha": {
        "text": [KATHA.format(a, v) for a in ("प्रथम", "द्वितीय") for v in ("प्रथम", "द्वितीय", "तृतीय")],
        "bhashya": ["कठोपनिषद्-शाङ्करभाष्यम्"],
    },
    "prashna": {
        "text": [f"प्रश्नोपनिषत्/{n} प्रश्नः" for n in ("प्रथमः", "द्वितीयः", "तृतीयः", "चतुर्थः", "पञ्चमः", "षष्ठः")],
        "bhashya": ["प्रश्नोपनिषद्भाष्यम्"],
    },
    "mundaka": {
        "text": ["मुण्डकोपनिषद्"],
        "bhashya": ["मुण्डकोपनिषद्भाष्यम्"],
    },
    "mandukya": {
        "text": ["माण्डुक्योपनिषत्"],
        "bhashya": ["माण्डूक्योपनिषद्भाष्यम्"],
    },
    "taittiriya": {
        "text": [f"तैत्तिरीयोपनिषदत्/{v}" for v in ("शिक्षावल्ली", "ब्रह्मानन्दवल्ली", "भृगुवल्ली")],
        "bhashya": ["तैत्तरीयोपनिषद्भाष्यम्"],
    },
    "aitareya": {
        "text": ["ऐतरेयोपनिषद्"],
        "bhashya": ["ऐतरेयोपनिषद्भाष्यम्"],
    },
    "chandogya": {
        "text": [f"छान्दोग्योपनिषद्/अध्यायः {n}" for n in "१२३४५६७८"],
        "bhashya": ["छान्दोग्योपनिषद्भाष्यम्"],
    },
    "brihadaranyaka": {
        # The plain (unaccented) Kāṇva text in six adhyāyas, the recension Śaṅkara comments on.
        "text": ["बृहदारण्यक उपनिषद् 1a"] + [f"बृहदारण्यक उपनिषद् {n}p" for n in range(2, 7)],
        "bhashya": ["बृहदारण्यकोपनिषद्भाष्यम्"],
    },
    "shvetashvatara": {
        "text": [f"श्वेताश्वतरोपनिषत्/{n} अध्यायः" for n in ("प्रथमः", "द्वितीयः", "तृतीयः", "चतुर्थः", "पञ्चमः", "षष्ठः")],
        "bhashya": [],
    },
    "kaushitaki": {
        "text": ["कौषीतकिब्राह्मणोपनिषत्"],
        "bhashya": [],
    },
    "maitri": {
        "text": ["मैत्रायण्युपनिषत्"],
        "bhashya": [],
    },
}


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    wanted = sys.argv[1:] or list(SOURCES)
    for text_id in wanted:
        out = {}
        for kind in ("text", "bhashya"):
            out[kind] = []
            for title in SOURCES[text_id][kind]:
                snap = fetch_page(title)
                if snap is None:
                    raise SystemExit(f"{text_id}: missing page {title}")
                out[kind].append(snap)
        (RAW_DIR / f"{text_id}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        sizes = {k: sum(len(p["wikitext"]) for p in v) for k, v in out.items()}
        print(f"{text_id}: {len(out['text'])} text pages ({sizes['text']} chars), "
              f"{len(out['bhashya'])} bhashya pages ({sizes['bhashya']} chars)")


if __name__ == "__main__":
    main()
