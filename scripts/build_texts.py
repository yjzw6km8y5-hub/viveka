"""Build the text libraries listed in data/texts.json (everything except the Gita).

For each text:
  data/<text_id>.json               the built library (do not edit by hand)
  data/commentaries/<text_id>.json  Sanskrit commentary per unit, for checking school notes

Text fields (ref, devanagari, iast, source, licence) come only from the
Wikisource snapshot named in the registry. Editorial fields come only from
data/annotations/<text_id>.json. The build refuses annotations that try to set a
text field.

Usage: python scripts/build_texts.py [TEXT_ID ...]
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

from translit import to_iast

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "data" / "texts.json").read_text(encoding="utf-8"))
ANNOTATIONS_DIR = ROOT / "data" / "annotations"
COMMENTARY_DIR = ROOT / "data" / "commentaries"

EDITORIAL_DEFAULTS = {
    "speaker": "",
    "context": "",
    "english": "",
    "situations": [],
    "life_stages": [],
    "aims": [],
    "school_notes": [],
    "safety_flags": [],
    "cross_refs": [],
    "review_status": "draft",
}
FIELD_ORDER = ["id", "text", "ref", "speaker", "context", "devanagari", "iast", "english",
               "situations", "life_stages", "aims", "school_notes", "safety_flags",
               "cross_refs", "source", "licence", "review_status"]

DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
# A unit ends with a numbered double danda: ॥ १२ ॥ or ॥ १.२.३ ॥
END_MARK = re.compile(r"॥\s*([०-९0-9]+(?:\s*[.\-]\s*[०-९0-9]+)*)\s*॥\s*$")


# ---------------------------------------------------------------- helpers

def clean_lines(wikitext):
    """Wikitext -> plain text lines (markup, templates and categories removed)."""
    text = re.sub(r"\{\{[^{}]*\}\}", "", wikitext, flags=re.S)
    text = re.sub(r"\[\[(?:वर्गः|Category|en):[^\]]*\]\]", "", text)
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("'''", "").replace("''", "").replace("&nbsp;", " ").replace("\xa0", " ")
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        line = line.strip("=").strip()
        if line:
            lines.append(unicodedata.normalize("NFC", line))
    return lines


def number(s):
    return [int(x) for x in re.split(r"\s*[.\-]\s*", s.translate(DIGITS).strip())]


def format_unit(lines):
    """Join a unit's lines; the closing number is dropped, the double danda kept."""
    lines = [ln for ln in lines if ln]
    last = END_MARK.sub("", lines[-1]).rstrip(" ।॥")
    lines = lines[:-1] + [last + " ॥"]
    return "\n".join(lines)


def split_units(lines, start=None, stop=None):
    """Split lines into (number list, unit lines) at each numbered ॥ marker.

    `start` / `stop` are regexes: lines before the first match of `start` and
    from the first match of `stop` onwards are ignored (invocations, colophons).
    """
    if start:
        idx = next(i for i, ln in enumerate(lines) if re.search(start, ln))
        lines = lines[idx + 1:]
    if stop:
        idx = next((i for i, ln in enumerate(lines) if re.search(stop, ln)), len(lines))
        lines = lines[:idx]
    units, current = [], []
    for ln in lines:
        current.append(ln)
        m = END_MARK.search(ln)
        if m:
            units.append((number(m.group(1)), current))
            current = []
    if current:
        raise ValueError(f"unterminated unit: {current}")
    return units


# ---------------------------------------------------------------- parsers
# Each parser returns a list of (ref, lines, page_snapshot).

def parse_isha(raw):
    page = raw["text"][0]
    units = split_units(clean_lines(page["wikitext"]), start=r"अथ ईशोपनिषत्", stop=r"इति ईशोपनिषत्")
    return [(n, lines, page) for n, lines in units]


def bhashya_isha(raw, refs):
    """Śaṅkara's comment on mantra N follows the marker 'शा.भा.N'."""
    text = "\n".join(clean_lines(raw["bhashya"][0]["wikitext"]))
    parts = re.split(r"^शा\.भा\.\s*([०-९]+)\s*$", text, flags=re.M)
    out = {}
    for num, body in zip(parts[1::2], parts[2::2]):
        n = int(num.translate(DIGITS))
        # The comment ends where the next mantra's heading number begins.
        body = re.split(r"^[०-९]+\s*$", body, maxsplit=1, flags=re.M)[0].strip()
        out[(n,)] = {"advaita": body}
    return out


PARSERS = {
    "isha_upanishad": (parse_isha, bhashya_isha),
}


# ---------------------------------------------------------------- build

def build(text_id):
    meta = REGISTRY[text_id]
    raw = json.loads((ROOT / meta["raw"]).read_text(encoding="utf-8"))
    parse, parse_bhashya = PARSERS[text_id]
    units = parse(raw)
    prefix = meta["id_prefix"]

    records, seen = [], set()
    for ref, lines, page in units:
        uid = prefix + "." + ".".join(map(str, ref))
        if uid in seen:
            raise SystemExit(f"{text_id}: duplicate unit {uid}")
        seen.add(uid)
        dev = unicodedata.normalize("NFC", format_unit(lines))
        records.append({
            "id": uid,
            "text": text_id,
            "ref": list(ref),
            "devanagari": dev,
            "iast": to_iast(dev),
            "source": {
                "name": "Sanskrit Wikisource",
                "page": page["title"],
                "url": page["url"],
                "revision": page["revid"],
                "permalink": page["permalink"],
                "retrieved": page["retrieved"],
            },
            "licence": page["licence"],
        })

    commentaries = {}
    if parse_bhashya and raw.get("bhashya"):
        for ref, by_school in parse_bhashya(raw, [r["ref"] for r in records]).items():
            uid = prefix + "." + ".".join(map(str, ref))
            if uid not in seen:
                raise SystemExit(f"{text_id}: commentary for unknown unit {uid}")
            commentaries[uid] = {k: unicodedata.normalize("NFC", v) for k, v in by_school.items() if v}

    ann_path = ANNOTATIONS_DIR / f"{text_id}.json"
    annotations = json.loads(ann_path.read_text(encoding="utf-8")) if ann_path.exists() else {}
    unknown = sorted(set(annotations) - seen)
    if unknown:
        raise SystemExit(f"{text_id}: annotations for unknown ids: {unknown}")

    out = []
    for rec in records:
        merged = {**EDITORIAL_DEFAULTS, **rec}
        for key, value in annotations.get(rec["id"], {}).items():
            if key not in EDITORIAL_DEFAULTS:
                raise SystemExit(f"{rec['id']}: annotation may not set source-derived field {key!r}")
            merged[key] = value
        out.append({k: merged[k] for k in FIELD_ORDER})

    (ROOT / "data" / f"{text_id}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    COMMENTARY_DIR.mkdir(exist_ok=True)
    bhashya_pages = [{"page": p["title"], "url": p["url"], "revision": p["revid"], "permalink": p["permalink"]}
                     for p in raw.get("bhashya", [])]
    (COMMENTARY_DIR / f"{text_id}.json").write_text(json.dumps({
        "note": f"Sanskrit commentary extracted from Wikisource for data/{text_id}.json.",
        "licence": "CC BY-SA 4.0 (Wikisource text); underlying works are public domain",
        "schools": meta.get("commentaries", {}),
        "sources": bhashya_pages,
        "units": commentaries,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    done = sum(1 for r in out if r["english"])
    cov = {s: sum(1 for c in commentaries.values() if s in c) for s in meta.get("commentaries", {})}
    print(f"{text_id}: {len(out)} units, {done} annotated, commentary {cov}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    wanted = sys.argv[1:] or [k for k in REGISTRY if not k.startswith("_")]
    for text_id in wanted:
        build(text_id)


if __name__ == "__main__":
    main()
