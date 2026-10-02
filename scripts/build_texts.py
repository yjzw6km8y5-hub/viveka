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

def clean_lines(wikitext, join_dandas=True):
    """Wikitext -> plain text lines (markup, templates and categories removed).
    Commentary passes join_dandas=False: its parsers key on the source's own '।।N।।'."""
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", wikitext, flags=re.S)  # footnotes
    text = re.sub(r"\{\{[^{}]*\}\}", "", text, flags=re.S)
    text = re.sub(r"\[\[(?:वर्गः|Category|en):[^\]]*\]\]", "", text)
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("'''", "").replace("''", "").replace("&nbsp;", " ").replace("\xa0", " ")
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        line = line.strip("=").strip()
        line = re.sub(r"\s\|(?=\s|$)", " ।", line)  # ASCII pipe used as a danda
        if join_dandas:
            line = line.replace("।।", "॥")  # two single dandas typed for a double danda
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


LOOSE_END = re.compile(r"॥\s*([०-९0-9]+)?\s*(?:॥)?\s*$")


def split_units_loose(lines, start=None, stop=None):
    """Like split_units, but tolerant of a missing closing ॥ ('॥ ३') or a missing
    number ('… आस ॥'): an unnumbered unit takes the previous number + 1. Any
    explicit number that breaks the sequence stops the build for inspection."""
    if start:
        idx = next(i for i, ln in enumerate(lines) if re.search(start, ln))
        lines = lines[idx + 1:]
    if stop:
        idx = next((i for i, ln in enumerate(lines) if re.search(stop, ln)), len(lines))
        lines = lines[:idx]
    units, current, prev = [], [], 0
    for ln in lines:
        current.append(ln)
        m = LOOSE_END.search(ln)
        if m and "॥" in ln:
            n = int(m.group(1).translate(DIGITS)) if m.group(1) else prev + 1
            if n != prev + 1:
                raise ValueError(f"numbering jumps from {prev} to {n} at: {ln}")
            units.append(([n], current))
            current, prev = [], n
    if current:
        raise ValueError(f"unterminated unit: {current}")
    return units


def bhashya_labelled(text, label_re, comment_re=r"ए\.?\d[\d.\-]*", section_break=None):
    """Commentary pages that label each mantra ('1.2.3') and its comment ('ए.1.2.3').

    Returns {(a, b, c): comment}. Labels repeated by a typo take previous + 1.
    Mantras without their own comment share the next comment (joint comment).
    """
    segs, _ = labelled_segments(text, label_re)
    out, prev, pending = {}, None, []
    for label, body in segs:
        ref = tuple(number(label))
        if prev and ref == prev:
            ref = ref[:-1] + (ref[-1] + 1,)
        prev = ref
        pending.append(ref)
        parts = re.split(rf"^{comment_re}\s*$", body, maxsplit=1, flags=re.M)
        if len(parts) < 2:
            # No comment label: a comment may still follow the mantra's closing
            # '।।N।।' (e.g. Katha 1.2.18). Only an empty remainder means a joint comment.
            m = re.search(r"।।\s*\d+\s*।।", body)
            rest = body[m.end():].strip() if m else ""
            if len(rest) < 80:
                continue
            parts = [body[:m.end()], rest]
        comment = parts[1]
        if section_break:
            comment = re.split(section_break, comment, flags=re.M)[0]
        for r in pending:
            out[r] = comment.strip()
        pending = []
    return out


# ---------------------------------------------------------------- parsers
# Each parser returns a list of (ref, lines, page_snapshot).

def parse_isha(raw):
    page = raw["text"][0]
    units = split_units(clean_lines(page["wikitext"]), start=r"अथ ईशोपनिषत्", stop=r"इति ईशोपनिषत्")
    return [(n, lines, page) for n, lines in units]


def bhashya_isha(raw, records):
    """Śaṅkara's comment on mantra N follows the marker 'शा.भा.N'."""
    text = "\n".join(clean_lines(raw["bhashya"][0]["wikitext"], join_dandas=False))
    parts = re.split(r"^शा\.भा\.\s*([०-९]+)\s*$", text, flags=re.M)
    out = {}
    for num, body in zip(parts[1::2], parts[2::2]):
        n = int(num.translate(DIGITS))
        # The comment ends where the next mantra's heading number begins.
        body = re.split(r"^[०-९]+\s*$", body, maxsplit=1, flags=re.M)[0].strip()
        out[(n,)] = {"advaita": body}
    return out


ORDINALS = {"प्रथम": 1, "द्वितीय": 2, "तृतीय": 3, "चतुर्थ": 4, "पञ्चम": 5, "षष्ठ": 6,
            "सप्तम": 7, "अष्टम": 8, "नवम": 9, "दशम": 10, "एकादश": 11, "द्वादश": 12}
ORDINAL_RE = "|".join(sorted(ORDINALS, key=len, reverse=True))


def split_sections(lines, heading_re):
    """Yield (section number, lines) using headings such as 'द्वितीयः खण्डः'."""
    current, buf = None, []
    for ln in lines:
        m = re.fullmatch(heading_re, ln)
        if m:
            if current is not None:
                yield current, buf
            current, buf = ORDINALS[m.group(1)], []
        elif current is not None:
            buf.append(ln)
    if current is not None:
        yield current, buf


def parse_kena(raw):
    page = raw["text"][0]
    lines = clean_lines(page["wikitext"])
    out = []
    for khanda, sec in split_sections(lines, rf"({ORDINAL_RE})ः खण्डः"):
        sec = [ln for ln in sec if not re.match(r"॥?\s*इति केनोपनिषद", ln)]
        if khanda == 4:  # closing peace chant follows the last mantra
            sec = sec[: next(i for i, ln in enumerate(sec) if ln.startswith("ॐ आप्यायन्तु"))]
        for n, ulines in split_units(sec):
            out.append(([khanda] + n, ulines, page))
    return out


def labelled_segments(text, label_re):
    """Split commentary text at lines matching label_re; return [(label, body)]."""
    parts = re.split(rf"^({label_re})\s*$", text, flags=re.M)
    return list(zip(parts[1::2], parts[2::2])), parts[0]


def bhashya_kena(raw, records):
    """Śaṅkara's Kena bhāṣya labels mantra text '1.k.m' and commentary 'ए.1.k.m'.

    Its first khaṇḍa has 8 mantras where our text has 9: its 1.1.3 covers our
    1.3 and 1.4. Its 1.3.7-10 are explained together in one comment. Its 1.2.1
    has no label: the comment sits between the khaṇḍa heading and 1.2.2.
    """
    text = "\n".join(clean_lines(raw["bhashya"][0]["wikitext"], join_dandas=False))
    segs, _ = labelled_segments(text, r"1\.\d\.\d+")
    out, prev = {}, None
    pending = []  # mantra labels whose comment comes later (joint comment)
    for label, body in segs:
        k, m = number(label)[1:]
        if prev and (k, m) == prev:
            m += 1  # a repeated label (1.1.8 printed as 1.1.7, 1.3.9 as 1.3.8)
        prev = (k, m)
        pending.append((k, m))
        parts = re.split(r"^ए\.[\d.\-]+\s*$", body, maxsplit=1, flags=re.M)
        if len(parts) < 2:
            continue
        # A comment ends at the khaṇḍa colophon or the next khaṇḍa's heading.
        section_break = r"^(?:इति \S+ खण्डः.*|\S+ (?:खण्ड|खणड)\s*)$"
        comment = re.split(section_break, parts[1], flags=re.M)[0].strip()
        if k == 1 and m == 8:  # khaṇḍa 2 opens without labels; its first comment follows 'यदि मन्यसे ... ।।1।।'
            m2 = re.search(r"मीमँस्यमेव ते मन्ये विदितम्।।1।।", parts[1])
            if m2:
                out[(2, 1)] = {"advaita": parts[1][m2.end():].strip()}
        for kk, mm in pending:
            targets = [(kk, mm)]
            if kk == 1 and mm == 3:
                targets = [(1, 3), (1, 4)]
            elif kk == 1 and mm >= 4:
                targets = [(1, mm + 1)]
            for t in targets:
                out[t] = {"advaita": comment}
        pending = []
    return out


def parse_katha(raw):
    """Six pages, one per vallī, in reading order (adhyāya 1: vallīs 1-3, adhyāya 2: 1-3)."""
    out = []
    for i, page in enumerate(raw["text"]):
        adhyaya, valli = divmod(i, 3)
        lines = clean_lines(page["wikitext"])
        start = r"शान्तिः शान्तिः शान्तिः" if i == 0 else None
        # The last page closes with the peace chant, numbered 2.3.19 by the source and
        # by Śaṅkara, who comments on it; it is kept. The repeat after the colophon is not.
        stop = r"^ॐ शान्तिः" if i == 5 else r"^(?:ॐ )?सह नाववतु|इति काठकोपनिषदि"
        units = split_units_loose(lines, start=start, stop=stop)
        out += [([adhyaya + 1, valli + 1] + n, ulines, page) for n, ulines in units]
    return out


def recover_unlabelled(found, records, section_break=None):
    """Where the commentary page forgot a mantra's label, that mantra's text and
    comment sit inside the previous mantra's comment. Split them out by finding
    a pair of the mantra's opening words (the page sometimes misspells a word,
    e.g. ब्राहृ for ब्रह्म, so several pairs are tried); the comment follows the
    mantra's closing '।।N।।'."""
    for prev, rec in zip(records, records[1:]):
        ref, pref = tuple(rec["ref"]), tuple(prev["ref"])
        if ref in found or pref not in found:
            continue
        words = [w.strip("।॥") for w in rec["devanagari"].split()]
        body = found[pref]
        for k in range(min(4, len(words) - 1)):
            i = body.find(f"{words[k]} {words[k + 1]}")
            if i >= 0:
                break
        else:
            continue
        i = body.rfind("\n", 0, i) + 1  # start of the line holding the mantra
        own = body[i:]
        m = re.search(r"।।\s*\d+\s*।।", own)
        if not m:
            continue
        comment = re.sub(r"^\s*ए\.?[\d.\-]+\s*\n", "", own[m.end():].lstrip())
        if section_break:
            comment = re.split(section_break, comment, flags=re.M)[0]
        found[pref] = re.sub(r"\n\s*ए\.?[\d.\-]+\s*$", "", body[:i].rstrip())
        found[ref] = comment.strip()
    return found


def bhashya_katha(raw, records):
    text = "\n".join(clean_lines(raw["bhashya"][0]["wikitext"], join_dandas=False))
    brk = r"^\S+ (?:अध्याय|वल्ली)(?:\s.*)?$"  # no \b: vowel signs are not \w
    found = bhashya_labelled(text, r"\d\.\d\.\d+", section_break=brk)
    found = recover_unlabelled(found, records, section_break=brk)
    return {r: {"advaita": c} for r, c in found.items()}


def split_numbered(lines, drop=None):
    """Units end at a numbered double danda. Text closed by an unnumbered ॥
    (invocations, prefatory verses) is dropped, as are lines matching `drop`."""
    units, current = [], []
    for ln in lines:
        if drop and re.fullmatch(drop, ln):
            continue
        current.append(ln)
        m = END_MARK.search(ln)
        if m:
            units.append((number(m.group(1)), current))
            current = []
        elif ln.rstrip().endswith("॥"):
            current = []  # unnumbered verse: not a unit
    return units


def parse_nitishataka(raw):
    page = raw["text"][0]
    lines = clean_lines(page["wikitext"])
    stop = next((i for i, ln in enumerate(lines) if ln.startswith("सम्बद्धसम्पर्कतन्तु")), len(lines))
    units = split_numbered(lines[:stop], drop=r"अपि च\s*[-–:]?")
    return [(n, ulines, page) for n, ulines in units]


SPEAKER_NAMES = {"वैशंपायन": "Vaishampayana", "वैशम्पायन": "Vaishampayana", "द्वाःस्थ": "doorkeeper",
                 "धृतराष्ट्र": "Dhritarashtra", "विदुर": "Vidura", "विरोचन": "Virochana", "प्रह्लाद": "Prahlada",
                 "हंस": "the swan", "साध्य": "the Sadhyas", "सनत्सुजात": "Sanatsujata", "सुधन्वा": "Sudhanva",
                 "सुधन्वन्": "Sudhanva", "केशिनी": "Keshini", "केशि": "Keshini", "आत्रेय": "Atreya", "कश्यप": "Kashyapa"}


def parse_vidura(raw):
    """Vidura Niti (Mahabharata, Udyoga Parva 33-40). The page writes dandas as
    ASCII full stops and its verse numbers are unreliable (repeats, '-' markers),
    so verses are numbered in order within each chapter; the source's own marker
    is kept in source.marker. Speakers come from the '... उवाच' lines."""
    page = raw["text"][0]
    out, chapter, speaker, n = [], 0, None, 0
    current = []
    for ln in clean_lines(page["wikitext"]):
        m = re.fullmatch(rf"({ORDINAL_RE})ोऽध्यायः", ln)
        if m:
            chapter, n, current = ORDINALS[m.group(1)], 0, []
            continue
        if chapter == 0 or ln.startswith("इति ") or re.search(r"ऽध्यायः\s*\.\.", ln):
            current = []  # colophons ('इति श्रीमहाभारते ... ऽध्यायः .. ४०..') are not verses
            continue
        sm = re.fullmatch(r"(\S+?)\s*(?:उवाच|ऊचुः|न्युवाच|ोवाच)\s*[.।]?", ln) or \
            re.fullmatch(r"(\S+?)(?:न्युवाच|ोवाच)\s*[.।]?", ln)
        if sm:
            word = sm.group(1)
            # sandhi-fused forms: केशिन्युवाच -> केशिनी, सुधन्वोवाच -> सुधन्वा
            name = next((v for k, v in SPEAKER_NAMES.items() if word.startswith(k[:-1] if len(k) > 3 else k)), None)
            speaker = name or word
            current = []
            continue
        em = re.search(r"\.\.\s*([०-९0-9\-]*)\s*\.\.\s*$", ln)
        line = re.sub(r"\s*\.\.\s*[०-९0-9\-]*\s*\.\.\s*$", " ॥", ln)
        line = re.sub(r"\s*\.\s*$", " ।", line).strip()
        current.append(line)
        if em:
            n += 1
            out.append(([chapter, n], current, page, {"speaker": speaker, "marker": em.group(1) or ""}))
            current = []
    return out


CN_ORDINALS = {**ORDINALS, "त्रयोदश": 13, "चतुर्दश": 14, "पञ्चदश": 15, "षोडश": 16, "सप्तदश": 17}
CN_ORDINAL_RE = "|".join(sorted(CN_ORDINALS, key=len, reverse=True))


def parse_chanakya(raw):
    """Chanakya Niti (Cāṇakyanītidarpaṇa, 17 chapters). Verses are numbered in order
    within each chapter; the source's own marker (a few are irregular, e.g. '१.१०')
    is kept in source.marker. The unreliable appendix 'प्रकीर्णश्लोकाः' is left out."""
    page = raw["text"][0]
    out, chapter, n, current = [], 0, 0, []
    for ln in clean_lines(page["wikitext"]):
        if ln.startswith("प्रकीर्णश्लोकाः"):
            break
        m = re.fullmatch(rf"({CN_ORDINAL_RE})ोऽध्यायः(?:\s*\.|\s+\S.*)?", ln)  # ch. 1 carries a Bengali gloss
        if m:
            chapter, n, current = CN_ORDINALS[m.group(1)], 0, []
            continue
        if chapter == 0 or ln.startswith("इति ") or re.fullmatch(r"\(?[०-९]+\)?|॥\s*[०-९]+\s*॥", ln):
            current = []  # title, colophons, chapter-number lines
            continue
        current.append(ln)
        em = re.search(r"॥\s*([०-९0-9.]*)\s*॥?\s*$", ln)
        if em:
            n += 1
            out.append(([chapter, n], current, page, {"marker": em.group(1)}))
            current = []
    if current:
        raise ValueError(f"unterminated unit: {current}")
    return out


PARSERS = {
    "chanakya_niti": (parse_chanakya, None),
    "isha_upanishad": (parse_isha, bhashya_isha),
    "kena_upanishad": (parse_kena, bhashya_kena),
    "katha_upanishad": (parse_katha, bhashya_katha),
    "nitishataka": (parse_nitishataka, None),
    "vidura_niti": (parse_vidura, None),
}


# ---------------------------------------------------------------- build

def build(text_id):
    meta = REGISTRY[text_id]
    raw = json.loads((ROOT / meta["raw"]).read_text(encoding="utf-8"))
    parse, parse_bhashya = PARSERS[text_id]
    units = parse(raw)
    prefix = meta["id_prefix"]

    records, seen, from_source = [], set(), {}
    for unit in units:
        ref, lines, page = unit[:3]
        extra = unit[3] if len(unit) > 3 else {}
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
        if extra.get("marker") is not None:
            records[-1]["source"]["marker"] = extra["marker"]
        if extra.get("speaker"):
            records[-1]["speaker"] = extra["speaker"]
            from_source[uid] = True
        corr = meta.get("speaker_corrections", {}).get(uid)
        if corr:
            records[-1]["speaker"] = corr["speaker"]  # documented fix; evidence in the registry

    commentaries = {}
    if parse_bhashya and raw.get("bhashya"):
        for ref, by_school in parse_bhashya(raw, records).items():
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
            if key == "speaker" and from_source.get(rec["id"]):
                raise SystemExit(f"{rec['id']}: speaker comes from the source; fix it in the parser, not the annotations")
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
