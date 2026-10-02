"""Validate every text library: data/gita.json and each text in data/texts.json.

Checks on every record:
  - no duplicate IDs; every required field present and non-empty
  - tag fields are lists using only the controlled vocabulary in data/vocab.json
  - iast is exactly the transliteration of devanagari
  - every school note points to commentary present for that unit
  - context is one sentence of at most 30 words; at most 4 situations
  - narrative units (no situations) have no stage/aim tags; other units have both
  - cross_refs point to existing IDs in any library

Gita: exactly 700 records; verses per chapter = 47,72,43,42,29,47,30,28,34,42,55,20,34,27,20,24,28,78.
Other texts: unit numbering under each parent runs 1..n with the counts in
data/texts.json ("expected_units"); IDs match prefix + ref; speaker is listed for the text.

Usage: python scripts/validate.py [--allow-incomplete] [--only TEXT_ID]
  --allow-incomplete  report empty context/english as warnings, not errors
                      (useful while a library is still being written)
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
REGISTRY = {k: v for k, v in json.loads((ROOT / "data" / "texts.json").read_text(encoding="utf-8")).items()
            if not k.startswith("_")}

EXPECTED_TOTAL = 700
VERSES_PER_CHAPTER = [47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 34, 27, 20, 24, 28, 78]

GITA_FIELDS = ["id", "chapter", "verse", "speaker", "context", "devanagari", "iast", "english",
               "situations", "life_stages", "aims", "school_notes", "safety_flags", "source",
               "licence", "review_status"]
TEXT_FIELDS = ["id", "text", "ref", "speaker", "context", "devanagari", "iast", "english",
               "situations", "life_stages", "aims", "school_notes", "safety_flags", "cross_refs",
               "source", "licence", "review_status"]
# Must be non-empty. The list fields may legitimately be empty (e.g. a verse
# naming warriors has no life situation), but must be present and be lists.
REQUIRED_NON_EMPTY = ["id", "speaker", "context", "devanagari", "iast", "english", "source",
                      "licence", "review_status"]
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


def check_record(r, vid, fields, speakers, commentary, errors, warnings, allow_incomplete):
    missing = [f for f in fields if f not in r]
    extra = [f for f in r if f not in fields]
    if missing:
        errors["missing field"].append(f"{vid}: {', '.join(missing)}")
    if extra:
        errors["unknown field"].append(f"{vid}: {', '.join(extra)}")

    for f in REQUIRED_NON_EMPTY:
        if f in r and is_empty(r[f]):
            editorial = f in EDITORIAL_TEXT or (f == "speaker" and "text" in r)
            bucket = warnings if (allow_incomplete and editorial) else errors
            bucket[f"empty {f}"].append(vid)

    if r.get("speaker") and r.get("speaker") not in speakers:
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
        # Narrative units carry no situations and must not be retrievable as
        # advice by any other tag; teaching units need a stage and an aim.
        if r.get("english"):
            others = [f for f in ("life_stages", "aims") if r.get(f)]
            if not sits and others:
                errors["narrative unit (no situations) has stage/aim tags"].append(vid)
            if sits and len(others) < 2:
                errors["unit with situations lacks life_stages or aims"].append(vid)

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
            elif school not in commentary:
                errors["school note without source commentary"].append(f"{vid}: {school}")
    elif "school_notes" in r:
        errors["school_notes is not a list"].append(vid)


def check_ids(records, errors):
    ids = Counter(r.get("id") for r in records if isinstance(r, dict))
    for vid, n in ids.items():
        if n > 1:
            errors["duplicate id"].append(f"{vid} x{n}")


def validate_gita(records, commentaries, allow_incomplete=False):
    errors, warnings = defaultdict(list), defaultdict(list)
    if not isinstance(records, list):
        errors["file is not a JSON list"].append(type(records).__name__)
        return errors, warnings
    if len(records) != EXPECTED_TOTAL:
        errors["record count"].append(f"{len(records)} records, expected {EXPECTED_TOTAL}")
    check_ids(records, errors)

    by_chapter = defaultdict(list)
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            errors["record is not an object"].append(f"index {i}")
            continue
        vid = r.get("id") or f"index {i}"
        check_record(r, vid, GITA_FIELDS, VOCAB["speakers"], commentaries.get(vid, {}),
                     errors, warnings, allow_incomplete)
        ch, vs = r.get("chapter"), r.get("verse")
        if not (isinstance(ch, int) and isinstance(vs, int)):
            errors["chapter/verse not integers"].append(vid)
        else:
            by_chapter[ch].append(vs)
            if r.get("id") != f"BG.{ch}.{vs}":
                errors["id does not match chapter/verse"].append(f"{vid} vs BG.{ch}.{vs}")

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


def validate_text(text_id, meta, records, commentaries, allow_incomplete=False):
    errors, warnings = defaultdict(list), defaultdict(list)
    if not isinstance(records, list):
        errors["file is not a JSON list"].append(type(records).__name__)
        return errors, warnings
    check_ids(records, errors)
    depth = len(meta["levels"])
    by_parent = defaultdict(list)
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            errors["record is not an object"].append(f"index {i}")
            continue
        vid = r.get("id") or f"index {i}"
        check_record(r, vid, TEXT_FIELDS, meta["speakers"], commentaries.get(vid, {}),
                     errors, warnings, allow_incomplete)
        ref = r.get("ref")
        if r.get("text") != text_id:
            errors["text field does not match file"].append(vid)
        if not (isinstance(ref, list) and len(ref) == depth and all(isinstance(x, int) for x in ref)):
            errors[f"ref is not a list of {depth} integers"].append(vid)
            continue
        if r.get("id") != meta["id_prefix"] + "." + ".".join(map(str, ref)):
            errors["id does not match ref"].append(vid)
        by_parent[".".join(map(str, ref[:-1]))].append(ref[-1])

    expected = meta["expected_units"]
    for parent, n in expected.items():
        got = sorted(by_parent.get(parent, []))
        if got != list(range(1, n + 1)):
            errors["units per division"].append(
                f"{parent or '(top)'}: {len(got)} units, expected {n}"
                + ("" if got == list(range(1, len(got) + 1)) else " (numbering has gaps or repeats)"))
    stray = sorted(set(by_parent) - set(expected))
    if stray:
        errors["unexpected division"].append(str(stray))
    return errors, warnings


def check_cross_refs(libraries, errors_by_text):
    all_ids = {r["id"] for recs in libraries.values() for r in recs if isinstance(r, dict) and "id" in r}
    for name, recs in libraries.items():
        for r in recs:
            refs = r.get("cross_refs", []) if isinstance(r, dict) else []
            if not isinstance(refs, list):
                errors_by_text[name]["cross_refs is not a list"].append(r.get("id"))
                continue
            for target in refs:
                if target not in all_ids:
                    errors_by_text[name]["cross_ref to unknown id"].append(f"{r.get('id')} -> {target}")
                if target == r.get("id"):
                    errors_by_text[name]["cross_ref to itself"].append(target)


PRINCIPLE_FIELDS = ["id", "name", "meaning", "supporting", "applies_when", "misleads_when",
                    "related", "conflicts_with", "modern_application", "situations",
                    "life_stages", "aims", "restricted_for", "review_status"]
RESTRICTION_VALUES = {"under18", "distress"}


def load_principles():
    out = []
    for path in sorted((ROOT / "data" / "principles").glob("*.json")):
        for p in load(path):
            p["_file"] = path.name
            out.append(p)
    return out


def validate_principles(principles, unit_ids):
    """Principles: unique IDs, real supporting units, valid links and vocabulary,
    and reciprocal conflicts (if A conflicts with B, B lists A)."""
    errors, warnings = defaultdict(list), defaultdict(list)
    ids = Counter(p.get("id") for p in principles)
    for pid, n in ids.items():
        if n > 1:
            errors["duplicate principle id"].append(f"{pid} x{n}")
    known = set(ids)
    by_id = {p["id"]: p for p in principles if "id" in p}
    for p in principles:
        pid = p.get("id", "?")
        missing = [f for f in PRINCIPLE_FIELDS if f not in p]
        extra = [f for f in p if f not in PRINCIPLE_FIELDS and f != "_file"]
        if missing:
            errors["principle missing field"].append(f"{pid}: {', '.join(missing)}")
        if extra:
            errors["principle unknown field"].append(f"{pid}: {', '.join(extra)}")
        for f in ("name", "meaning", "applies_when", "misleads_when", "modern_application"):
            if is_empty(p.get(f)):
                errors[f"principle empty {f}"].append(pid)
        if not p.get("supporting"):
            errors["principle without supporting units"].append(pid)
        for uid in p.get("supporting", []):
            if uid not in unit_ids:
                errors["principle cites unknown unit"].append(f"{pid} -> {uid}")
        for f in ("related", "conflicts_with"):
            for other in p.get(f, []):
                if other not in known:
                    errors[f"principle {f} unknown id"].append(f"{pid} -> {other}")
                if other == pid:
                    errors[f"principle {f} itself"].append(pid)
        for other in p.get("conflicts_with", []):
            if other in by_id and pid not in by_id[other].get("conflicts_with", []):
                errors["conflict not reciprocal"].append(f"{pid} -> {other}")
        for f, allowed in (("situations", VOCAB["situations"]), ("life_stages", VOCAB["life_stages"]),
                           ("aims", VOCAB["aims"])):
            bad = [v for v in p.get(f, []) if v not in allowed]
            if bad:
                errors[f"principle unknown {f}"].append(f"{pid}: {bad}")
            if not p.get(f):
                errors[f"principle empty {f}"].append(pid)
        bad = [v for v in p.get("restricted_for", []) if v not in RESTRICTION_VALUES]
        if bad:
            errors["principle unknown restriction"].append(f"{pid}: {bad}")
        if p.get("review_status") not in VOCAB["review_status"]:
            errors["principle unknown review_status"].append(pid)
    return errors, warnings


def report(title, problems, limit=8):
    total = sum(len(v) for v in problems.values())
    print(f"  {title}: {total}")
    for check, examples in sorted(problems.items()):
        shown = ", ".join(map(str, examples[:limit])) + (f", ... (+{len(examples) - limit} more)" if len(examples) > limit else "")
        print(f"    [{len(examples)}] {check}: {shown}")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    allow_incomplete = "--allow-incomplete" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None

    libraries, results = {}, {}
    gita = load(ROOT / "data" / "gita.json")
    gita_comm = load(ROOT / "data" / "gita_commentaries.json")["verses"]
    libraries["gita"] = gita
    results["gita"] = validate_gita(gita, gita_comm, allow_incomplete)
    for text_id, meta in REGISTRY.items():
        path = ROOT / "data" / f"{text_id}.json"
        if not path.exists():
            results[text_id] = ({"library not built": [str(path.relative_to(ROOT))]}, {})
            libraries[text_id] = []
            continue
        recs = load(path)
        comm_path = ROOT / "data" / "commentaries" / f"{text_id}.json"
        comm = load(comm_path)["units"] if comm_path.exists() else {}
        libraries[text_id] = recs
        results[text_id] = validate_text(text_id, meta, recs, comm, allow_incomplete)
    check_cross_refs(libraries, {k: v[0] for k, v in results.items()})
    unit_ids = {r["id"] for recs in libraries.values() for r in recs if isinstance(r, dict) and "id" in r}
    principles = load_principles()
    libraries["principles"] = principles
    results["principles"] = validate_principles(principles, unit_ids)

    failed = False
    for name, (errors, warnings) in results.items():
        if only and name != only:
            continue
        status = "INVALID" if errors else "VALID"
        failed |= bool(errors)
        print(f"{name}: {len(libraries[name])} records: {status}")
        if warnings:
            report("Warnings", warnings)
        if errors:
            report("Errors", errors)
    print("INVALID" if failed else "VALID")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
