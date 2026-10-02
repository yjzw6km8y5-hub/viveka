"""Validate data/gita.json.

Checks:
  - exactly 700 records, no duplicate IDs, IDs match chapter/verse
  - verses per chapter = 47,72,43,42,29,47,30,28,34,42,55,20,34,27,20,24,28,78
    and verse numbers in each chapter run 1..n without gaps
  - every required field present and non-empty
  - tag fields are lists using only the controlled vocabulary in data/vocab.json
  - iast is exactly the transliteration of devanagari
  - every school note points to a commentary present in data/gita_commentaries.json
  - context is one sentence of at most 30 words; at most 4 situations
  - narrative verses (no situations) have no stage/aim tags; other verses have both

Usage: python scripts/validate.py [path] [--allow-incomplete]
  --allow-incomplete  report empty context/english as warnings, not errors
                      (useful while the library is still being written)
Exit code 0 if valid, 1 otherwise.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from translit import to_iast

ROOT = Path(__file__).resolve().parent.parent
VOCAB = json.loads((ROOT / "data" / "vocab.json").read_text(encoding="utf-8"))

EXPECTED_TOTAL = 700
VERSES_PER_CHAPTER = [47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 34, 27, 20, 24, 28, 78]

FIELDS = ["id", "chapter", "verse", "speaker", "context", "devanagari", "iast", "english",
          "situations", "life_stages", "aims", "school_notes", "safety_flags", "source",
          "licence", "review_status"]
# Must be non-empty. The list fields may legitimately be empty (e.g. a verse
# naming warriors has no life situation), but must be present and be lists.
REQUIRED_NON_EMPTY = ["id", "chapter", "verse", "speaker", "context", "devanagari", "iast",
                      "english", "source", "licence", "review_status"]
EDITORIAL_TEXT = {"context", "english"}
LIST_VOCAB = {
    "situations": VOCAB["situations"],
    "life_stages": VOCAB["life_stages"],
    "aims": VOCAB["aims"],
    "safety_flags": VOCAB["safety_flags"],
}
SOURCE_KEYS = ["name", "page", "url", "revision", "permalink", "retrieved"]
MAX_CONTEXT_WORDS = 30
MAX_SITUATIONS = 4


def is_empty(value):
    return value is None or value == "" or value == [] or value == {}


def validate(records, commentaries, allow_incomplete=False):
    errors = defaultdict(list)    # check name -> examples
    warnings = defaultdict(list)

    if not isinstance(records, list):
        errors["file is not a JSON list"].append(type(records).__name__)
        return errors, warnings

    if len(records) != EXPECTED_TOTAL:
        errors["record count"].append(f"{len(records)} records, expected {EXPECTED_TOTAL}")

    ids = Counter(r.get("id") for r in records if isinstance(r, dict))
    for vid, n in ids.items():
        if n > 1:
            errors["duplicate id"].append(f"{vid} x{n}")

    by_chapter = defaultdict(list)
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            errors["record is not an object"].append(f"index {i}")
            continue
        vid = r.get("id") or f"index {i}"

        missing = [f for f in FIELDS if f not in r]
        extra = [f for f in r if f not in FIELDS]
        if missing:
            errors["missing field"].append(f"{vid}: {', '.join(missing)}")
        if extra:
            errors["unknown field"].append(f"{vid}: {', '.join(extra)}")

        for f in REQUIRED_NON_EMPTY:
            if f in r and is_empty(r[f]):
                bucket = warnings if (allow_incomplete and f in EDITORIAL_TEXT) else errors
                bucket[f"empty {f}"].append(vid)

        ch, vs = r.get("chapter"), r.get("verse")
        if not (isinstance(ch, int) and isinstance(vs, int)):
            errors["chapter/verse not integers"].append(vid)
        else:
            by_chapter[ch].append(vs)
            if r.get("id") != f"BG.{ch}.{vs}":
                errors["id does not match chapter/verse"].append(f"{vid} vs BG.{ch}.{vs}")

        if r.get("speaker") not in VOCAB["speakers"]:
            errors["unknown speaker"].append(f"{vid}: {r.get('speaker')!r}")
        if r.get("review_status") not in VOCAB["review_status"]:
            errors["unknown review_status"].append(f"{vid}: {r.get('review_status')!r}")

        for f, allowed in LIST_VOCAB.items():
            value = r.get(f)
            if f not in r:
                continue
            if not isinstance(value, list):
                errors[f"{f} is not a list"].append(vid)
                continue
            bad = [v for v in value if v not in allowed]
            if bad:
                errors[f"unknown {f} value"].append(f"{vid}: {bad}")
            if len(set(value)) != len(value):
                errors[f"repeated {f} value"].append(vid)

        ctx = r.get("context") or ""
        if ctx:
            if len(ctx.split()) > MAX_CONTEXT_WORDS:
                errors[f"context over {MAX_CONTEXT_WORDS} words"].append(f"{vid} ({len(ctx.split())})")
            if re.search(r"[.!?]\s+\S", ctx.strip()):
                errors["context is more than one sentence"].append(vid)

        sits = r.get("situations")
        if isinstance(sits, list):
            if len(sits) > MAX_SITUATIONS:
                errors[f"more than {MAX_SITUATIONS} situations"].append(vid)
            # Narrative verses carry no situations and must not be retrievable as
            # advice by any other tag; teaching verses need a stage and an aim.
            if r.get("english"):
                others = [f for f in ("life_stages", "aims") if r.get(f)]
                if not sits and others:
                    errors["narrative verse (no situations) has stage/aim tags"].append(vid)
                if sits and len(others) < 2:
                    errors["verse with situations lacks life_stages or aims"].append(vid)

        dev = r.get("devanagari") or ""
        if dev and not re.search(r"[ऀ-ॿ]", dev):
            errors["devanagari has no Devanagari text"].append(vid)
        if dev and r.get("iast"):
            try:
                if to_iast(dev) != r["iast"]:
                    errors["iast does not match devanagari"].append(vid)
            except ValueError as e:
                errors["devanagari not transliterable"].append(f"{vid}: {e}")

        src = r.get("source")
        if isinstance(src, dict):
            gaps = [k for k in SOURCE_KEYS if is_empty(src.get(k))]
            if gaps:
                errors["incomplete source"].append(f"{vid}: {', '.join(gaps)}")
        elif src is not None and src != "":
            errors["source is not an object"].append(vid)

        notes = r.get("school_notes")
        if isinstance(notes, list):
            for n in notes:
                if not isinstance(n, dict) or is_empty(n.get("note")):
                    errors["malformed school note"].append(vid)
                    continue
                school = n.get("school")
                if school not in VOCAB["schools"]:
                    errors["unknown school"].append(f"{vid}: {school!r}")
                elif school not in commentaries.get(vid, {}):
                    errors["school note without source commentary"].append(f"{vid}: {school}")
        elif "school_notes" in r:
            errors["school_notes is not a list"].append(vid)

    for idx, expected in enumerate(VERSES_PER_CHAPTER, start=1):
        got = sorted(by_chapter.get(idx, []))
        if got != list(range(1, expected + 1)):
            errors["verses per chapter"].append(
                f"chapter {idx}: {len(got)} verses, expected {expected}"
                + ("" if got == list(range(1, len(got) + 1)) else " (numbering has gaps or repeats)"))
    stray = sorted(set(by_chapter) - set(range(1, len(VERSES_PER_CHAPTER) + 1)))
    if stray:
        errors["unexpected chapter"].append(str(stray))

    return errors, warnings


def report(title, problems, limit=8):
    total = sum(len(v) for v in problems.values())
    print(f"{title}: {total}")
    for check, examples in sorted(problems.items()):
        shown = ", ".join(examples[:limit]) + (f", ... (+{len(examples) - limit} more)" if len(examples) > limit else "")
        print(f"  [{len(examples)}] {check}: {shown}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    allow_incomplete = "--allow-incomplete" in sys.argv
    path = Path(args[0]) if args else ROOT / "data" / "gita.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    comm_path = ROOT / "data" / "gita_commentaries.json"
    commentaries = json.loads(comm_path.read_text(encoding="utf-8"))["verses"] if comm_path.exists() else {}

    errors, warnings = validate(records, commentaries, allow_incomplete)
    print(f"Validating {path.name}: {len(records) if isinstance(records, list) else '?'} records")
    if warnings:
        report("Warnings", warnings)
    if errors:
        report("Errors", errors)
        print("INVALID")
        sys.exit(1)
    print("VALID")


if __name__ == "__main__":
    main()
