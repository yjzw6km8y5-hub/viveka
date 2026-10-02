"""Build data/gita.json from the Wikisource snapshots plus editorial annotations.

Text fields (devanagari, iast, speaker, source, licence) come only from
data/raw/ch*.json. Editorial fields (context, english, tags, school notes,
safety flags, review status) come only from data/annotations/chNN.json.
Re-running this script never loses editorial work.

Also writes data/gita_commentaries.json: the Sanskrit bhashyas of Shankara,
Ramanuja and Madhva for each verse, so school_notes can be checked against
the commentary text instead of anyone's memory.

Usage: python scripts/build_gita.py
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

from translit import to_iast

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
VOCAB = json.loads((ROOT / "data" / "vocab.json").read_text(encoding="utf-8"))
ANNOTATIONS_DIR = ROOT / "data" / "annotations"  # one file per chapter: ch01.json …
OUT_PATH = ROOT / "data" / "gita.json"
COMMENTARY_PATH = ROOT / "data" / "gita_commentaries.json"
SPEAKER_CORRECTIONS = {
    k: v for k, v in json.loads((ROOT / "data" / "speaker_corrections.json").read_text(encoding="utf-8")).items()
    if not k.startswith("_")
}

EDITORIAL_DEFAULTS = {
    "context": "",
    "english": "",
    "situations": [],
    "life_stages": [],
    "aims": [],
    "school_notes": [],
    "safety_flags": [],
    "review_status": "draft",
}

DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
VERSE_MARKER = re.compile(r"॥\s*([०-९]+)\s*-\s*([०-९]+)\s*॥\s*$")
SPEAKER_BY_MARKER = {re.sub(r"\s+", "", m): name for name, m in VOCAB["speakers"].items()}
HEADER_LINES = {"ॐ", "श्रीपरमात्मने नमः", "अथ श्रीमद्भगवद्गीता"}
BHASHYA_TO_SCHOOL = {s["bhashya"]: key for key, s in VOCAB["schools"].items()}
BHASHYA_TO_SCHOOL["श्री मध्वाचार्यव्याख्या"] = "dvaita"
# Anushtubh = 4 x 8, trishtubh = 4 x 11, jagati = 4 x 12 syllables. A few
# verses are genuinely irregular (e.g. 2.6 has a 12-syllable quarter), so
# other counts are listed for review; counts far outside 30-50 mean a line
# was dropped or merged in parsing and stop the build.
METRE_SYLLABLES = {32: "anushtubh", 44: "trishtubh", 48: "jagati"}
metres, irregular = {}, []


def strip_markup(line):
    line = re.sub(r"<[^>]+>", "", line)
    line = line.replace("'''", "").replace("\xa0", " ")
    return re.sub(r"\s+", " ", line).strip()


def parse_poem(poem, speaker):
    """Return (speaker, verse_lines, (chapter, verse)) for one <poem> block."""
    verse_lines, number = [], None
    for raw in poem.splitlines():
        line = strip_markup(raw)
        if not line:
            continue
        compact = line.replace(" ", "")
        if compact in SPEAKER_BY_MARKER:
            if verse_lines:
                raise ValueError(f"speaker line inside a verse: {poem!r}")
            speaker = SPEAKER_BY_MARKER[compact]
            continue
        is_heading = line in HEADER_LINES or line.endswith("ध्यायः")
        if not verse_lines and is_heading and "।" not in line and "॥" not in line:
            continue
        m = VERSE_MARKER.search(line)
        if m:
            number = (int(m.group(1).translate(DIGITS)), int(m.group(2).translate(DIGITS)))
            line = line[: m.start()].strip()
        verse_lines.append(line)
    return speaker, verse_lines, number


def format_devanagari(lines):
    lines = [re.sub(r"\s*।\s*$", "", ln).strip() for ln in lines]
    lines = [ln + " ।" for ln in lines[:-1]] + [lines[-1] + " ॥"]
    return unicodedata.normalize("NFC", "\n".join(lines))


def parse_commentaries(block):
    """Map school -> Sanskrit commentary text from one {{व्याख्या}} block."""
    parts = re.split(r"'''([^'\n]+?)'''\s*<br>", block)
    found = {}
    for name, text in zip(parts[1::2], parts[2::2]):
        school = BHASHYA_TO_SCHOOL.get(name.strip())
        if not school:
            continue
        text = text.split("}}")[0]
        text = re.sub(r"<br\s*/?>", "\n", text).replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text).strip()
        # Skip editorial placeholders such as "Sri Madhvacharya did not
        # comment on this sloka" (5.15): a real commentary is in Sanskrit.
        if re.search(r"[ऄ-ह]", text):  # Devanagari letters, not just dandas
            found[school] = unicodedata.normalize("NFC", text)
    return found


def syllables(devanagari):
    """Count syllables (vowel nuclei) via the IAST form."""
    return len(re.findall(r"ai|au|[aāiīuūṛṝḷḹeo]", to_iast(devanagari)))


def build_source_records():
    records, commentaries, speaker = [], {}, None
    for path in sorted(RAW_DIR.glob("ch*.json")):
        snap = json.loads(path.read_text(encoding="utf-8"))
        text = snap["wikitext"]
        poems = list(re.finditer(r"<poem>(.*?)</poem>", text, flags=re.S))
        for i, m in enumerate(poems):
            speaker, lines, number = parse_poem(m.group(1), speaker)
            if number is None:
                continue  # chapter colophon (इति ... अध्यायः)
            chapter, verse = number
            if chapter != snap["chapter"]:
                raise ValueError(f"{path.name}: marker says chapter {chapter}")
            vid = f"BG.{chapter}.{verse}"
            if vid in SPEAKER_CORRECTIONS:
                speaker = SPEAKER_CORRECTIONS[vid]["speaker"]
            devanagari = format_devanagari(lines)
            n = syllables(devanagari)
            if not 30 <= n <= 50:
                raise ValueError(f"{vid}: {n} syllables, a line was probably lost or merged: {devanagari!r}")
            metres[METRE_SYLLABLES.get(n, f"irregular ({n})")] = metres.get(METRE_SYLLABLES.get(n, f"irregular ({n})"), 0) + 1
            if n not in METRE_SYLLABLES:
                irregular.append(f"{vid} ({n})")
            records.append({
                "id": vid,
                "chapter": chapter,
                "verse": verse,
                "speaker": speaker,
                "devanagari": devanagari,
                "iast": to_iast(devanagari),
                "source": {
                    "name": "Sanskrit Wikisource",
                    "page": snap["title"],
                    "url": snap["url"],
                    "revision": snap["revid"],
                    "permalink": snap["permalink"],
                    "retrieved": snap.get("retrieved", ""),
                },
                "licence": snap["licence"],
            })
            end = poems[i + 1].start() if i + 1 < len(poems) else len(text)
            comm = parse_commentaries(text[m.end():end])
            if comm:
                commentaries[vid] = comm
    rekey_by_marker(commentaries)
    return records, commentaries


# On the chapter 13 page, each Rāmānuja section sits one verse too early: the
# text under 13.10 is his comment on 13.11 and is marked ।।13.11।।. His markers
# use our 34-verse numbering, so file those sections by their own marker.
# (Śaṅkara and Madhva are placed correctly; their markers use the 35-verse
# numbering, so they must NOT be re-keyed.)
REKEY_BY_OWN_MARKER = {("vishishtadvaita", 13)}


def rekey_by_marker(commentaries):
    moved = {}
    for vid in list(commentaries):
        chapter = int(vid.split(".")[1])
        for school in list(commentaries[vid]):
            if (school, chapter) not in REKEY_BY_OWN_MARKER:
                continue
            text = commentaries[vid].pop(school)
            m = re.match(r"\s*।।\s*(\d+)\.(\d+)", text)
            if m and int(m.group(1)) == chapter:
                moved.setdefault(f"BG.{chapter}.{int(m.group(2))}", {})[school] = text
    for vid, d in moved.items():
        if vid in commentaries:
            commentaries[vid].update(d)
    for vid in [v for v, d in commentaries.items() if not d]:
        del commentaries[vid]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    records, commentaries = build_source_records()
    annotations = {}
    for path in sorted(ANNOTATIONS_DIR.glob("ch*.json")):
        for vid, ann in json.loads(path.read_text(encoding="utf-8")).items():
            if vid in annotations:
                raise SystemExit(f"{vid} is annotated twice (second time in {path.name})")
            annotations[vid] = ann
    ids = {r["id"] for r in records}
    unknown = sorted(set(annotations) - ids)
    if unknown:
        raise SystemExit(f"annotations for unknown verse ids: {unknown}")

    field_order = ["id", "chapter", "verse", "speaker", "context", "devanagari", "iast",
                   "english", "situations", "life_stages", "aims", "school_notes",
                   "safety_flags", "source", "licence", "review_status"]
    out = []
    for rec in records:
        merged = {**EDITORIAL_DEFAULTS, **rec}
        for key, value in annotations.get(rec["id"], {}).items():
            if key not in EDITORIAL_DEFAULTS:
                raise SystemExit(f"{rec['id']}: annotation may not set source-derived field {key!r}")
            merged[key] = value
        out.append({k: merged[k] for k in field_order})

    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    COMMENTARY_PATH.write_text(json.dumps({
        "note": "Sanskrit commentaries extracted from the same Wikisource pages as data/gita.json.",
        "licence": "CC BY-SA 4.0 (Wikisource text); underlying works are public domain",
        "schools": VOCAB["schools"],
        "verses": commentaries,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    speakers = {}
    for r in out:
        speakers[r["speaker"]] = speakers.get(r["speaker"], 0) + 1
    print(f"wrote {len(out)} verses to {OUT_PATH.relative_to(ROOT)}")
    print(f"  speakers: {speakers}")
    print(f"  metres: {metres}")
    if irregular:
        print(f"  irregular syllable counts (check against a printed edition): {', '.join(irregular)}")
    print(f"  annotated: {sum(1 for r in out if r['id'] in annotations)}")
    for school in VOCAB["schools"]:
        n = sum(1 for c in commentaries.values() if school in c)
        print(f"  {school} commentary present for {n} verses")


if __name__ == "__main__":
    main()
