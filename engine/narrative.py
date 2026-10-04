"""Long stories: listen, reflect back, ask what would change the advice, then advise on the central dilemma
(owner decision 2026-10-03, DECISIONS.md).

Everything here is deterministic and fast, so a listening turn is answered in well under a second:
  - analyse(story): the people named, the feelings named, the competing pulls (Dharma / Artha / Kama / Moksha)
    with the person's own words as evidence, and which decision facts are still missing.
  - reflection(): "Here's what I'm hearing", built only from words the person wrote (quoted exactly).
  - followups(): 1-3 questions for missing facts that would change the advice; never the same one twice.
  - advise(): runs the engine on the central dilemma (not on side details), with safety read from the whole story.
  - check_*(): the narrative gate. Reflection quotes must be exact; the advice must address the core pulls and
    refer to the person's specifics; questions must be new and about something not yet known.
"""
import re

from .core import _build, answer, load_library
from .gate import check as gate_check

AIMS = {
    "artha": (r"\b(?:career|job|jobs|work|working|salary|promotion|transfer|offer|business|money|earn\w*|loan|emi|debts?|"
              r"savings|visa|company|investor|startup|app|fees|finances?|income|pay|paid|lakhs?|bank|shop|clients?|"
              r"customers|appraisals?|interviews?|employ\w*|engineering|coaching|scholarship|academy|competition)\b"),
    "dharma": (r"\b(?:duty|duties|depend\w*|responsib\w*|parents|father|mother|dad|mum|mom|papa|amma|care of|look after|"
               r"looks? after|son|daughters?|children|kids|family|family's|honou?r|expected|promise\w*|executor|fair|"
               r"community|caste|right thing|honest\w*|safe|safety|wife|husband|brother|sister|in-laws|grandmother|"
               r"elders?|obligation|support\w*|protect\w*|report\w*|pregnant|baby|sacrific\w*)\b"),
    "kama": (r"\b(?:love|loved|loves|marry|marriage|married|seeing someone|boyfriend|girlfriend|partner|music|sitar|dance|"
             r"dancing|bharatanatyam|passion|dream\w*|happy|happiness|enjoy\w*|friends?|friendship|"
             r"desire|joy|belong\w*|left out|remarry\w*|blessing|together|lonely|self-respect|feel like myself)\b"),
    "moksha": (r"\b(?:peace|spiritual\w*|ashram|god|meaning|purpose|freedom|liberation|calling|swami|sannyas\w*|soul|"
               r"inner|gita|upanishads|ghats|temple|faith|last part of life)\b"),
}
AIM_LABEL = {"artha": "Artha: work, money and security", "dharma": "Dharma: duty to the people and values you stand by",
             "kama": "Kama: love and what you want for your own life", "moksha": "Moksha: inner freedom and meaning"}
AIM_SHORT = {"artha": "Artha", "dharma": "Dharma", "kama": "Kama", "moksha": "Moksha"}

PEOPLE = ["parents", "father", "mother", "dad", "mum", "mom", "papa", "amma", "brother", "sister", "brothers", "sisters",
          "wife", "husband", "partner", "boyfriend", "girlfriend", "son", "sons", "daughter", "daughters", "children", "kids",
          "baby", "in-laws", "mother-in-law", "father-in-law", "brother-in-law", "grandmother", "grandfather", "uncle",
          "aunt", "cousin", "friend", "friends", "best friend", "colleague", "colleagues", "manager", "boss", "team lead",
          "teacher", "guru", "swami", "family", "siblings"]
FEELINGS = ["guilty", "guilt", "resentful", "angry", "furious", "scared", "afraid", "frightened", "ashamed", "shame",
            "tired", "exhausted", "hopeless", "sad", "lonely", "alone", "hurt", "stuck", "confused", "anxious", "worried",
            "dread", "dreading", "overwhelmed", "invisible", "used", "drowning", "sick", "embarrassed", "stupid", "left out",
            "torn", "frustrated", "bitter", "humiliated", "disappointed", "helpless", "trapped", "jealous", "proud", "regret",
            "terrible", "miserable", "cold", "dizzy"]

SLOTS = [  # (slot, cue that shows we already know it, question)
    ("want", r"\bi (?:really |truly |also )?(?:want|wish|hope|dream|would like|'d like|'d love|would love|long)\b|\bi love\b",
     "If nothing stood in the way, what would you choose?"),
    ("dependents", r"depend(?:s)? on (?:me|us)|rely on (?:me|us)|main earner|i'?m paying|i support|only (?:son|child|daughter)"
                   r"|look after (?:him|her|them)|sends? money",
     "Who depends on you here, and in what way?"),
    ("tried", r"\bi (?:have |'ve |already )?(?:tried|asked|told|talked|spoke|raised|mentioned|confronted|complained|blocked)\b",
     "What have you already tried, and how did it go?"),
    ("timeline", r"\b(?:\d+|one|two|three|four|five|six|eight|ten|twelve) (?:weeks?|months?|days?)\b|deadline|needs an answer"
                 r"|until (?:saturday|sunday|monday|friday)|by (?:january|february|march|april|may|june|july|august|september|"
                 r"october|november|december|next month)|next month",
     "Is there a deadline, and how much time do you really have?"),
    ("money", r"lakhs?|salary|loan|emi|savings|income|fees|debts?|rupees|\$\d|provident fund|pension",
     "If things go wrong, how much room do you have financially?"),
    ("fixed", r"\bcan'?t (?:just )?(?:quit|leave|change|afford)|no choice|there'?s no one else|only (?:son|child)",
     "What can't change here, whatever you decide?"),
    ("reversible", r"revers|undo|go back|come back|can always|for good|forever|permanent",
     "If you chose one way and it went badly, could you change course later?"),
]
SLOT_PRIORITY = {"artha": ["want", "money", "timeline", "dependents"], "dharma": ["dependents", "tried", "fixed"],
                 "kama": ["want", "tried", "reversible"], "moksha": ["want", "dependents", "reversible"]}


def sentences(story):
    """Split into sentences; long unpunctuated speech is cut into windows of about 30 words."""
    out = []
    for part in re.split(r"(?<=[.!?])\s+|\n+", story):
        part = part.strip()
        words = part.split()
        if len(words) <= 45:
            if part:
                out.append(part)
            continue
        i = 0
        while i < len(words):  # rebuild exact substrings of the original text
            chunk = words[i:i + 30]
            m = re.search(r"\s+".join(map(re.escape, chunk)), part)
            out.append(m.group(0) if m else " ".join(chunk))
            i += 30
    return out


def short_quote(sent, pattern, max_words=28):
    """An exact excerpt of `sent` around the first cue, at most max_words words."""
    words = list(re.finditer(r"\S+", sent))
    if len(words) <= max_words:
        return sent.strip()
    m = re.search(pattern, sent, re.I)
    at = sum(1 for w in words if m and w.start() < m.start()) if m else 0
    lo = max(0, min(at - max_words // 3, len(words) - max_words))
    seg = sent[words[lo].start():words[min(lo + max_words, len(words)) - 1].end()]
    return seg.strip(" ,;")


def analyse(story):
    low = story.lower().replace("’", "'")
    sents = sentences(story)
    scores = {a: 0.0 for a in AIMS}
    best = {}
    for s in sents:
        sl = s.lower()
        for a, pat in AIMS.items():
            n = len(re.findall(pat, sl))
            if not n:
                continue
            w = n * (1.5 if re.search(r"\bi (?:really )?(?:want|love|need|can't|cannot|have to|must|feel)\b", sl) else 1.0)
            scores[a] += w
            if a not in best or w > best[a][0]:
                best[a] = (w, s)
    # Dharma words (family) are everywhere; weigh it a little lower so the other side of the dilemma can surface.
    scores["dharma"] *= 0.8
    ranked = [a for a in sorted(scores, key=lambda a: -scores[a]) if scores[a] > 0]
    core = ranked[:2]
    pulls = [{"aim": a, "label": AIM_LABEL[a], "quote": short_quote(best[a][1], AIMS[a])} for a in core]
    count = {p: len(re.findall(rf"(?<![\w-]){re.escape(p)}(?![\w-])", low)) for p in PEOPLE}
    people = [p for p in sorted(PEOPLE, key=lambda p: -count[p]) if count[p]]  # most-mentioned first
    people = [p for p in people if not any(p != q and re.search(rf"\b{re.escape(p)}\b", q) for q in people)]
    feelings = [f for f in FEELINGS if re.search(rf"\b{re.escape(f)}\b", low)]
    known = {slot for slot, cue, _ in SLOTS if re.search(cue, low)}
    return {"sentences": sents, "scores": scores, "core": core, "pulls": pulls, "people": people[:6],
            "feelings": feelings[:5], "known": known, "words": len(story.split())}


def reflection(an):
    bits = ["Here's what I'm hearing."]
    if an["people"]:
        bits.append("This involves your " + _join(an["people"][:4]) + ".")
    if len(an["pulls"]) == 2:
        a, b = an["pulls"]
        bits.append(f"Two things seem to be pulling against each other. On one side, {a['label'].split(': ')[1]}: "
                    f"you wrote “{a['quote']}”. On the other, {b['label'].split(': ')[1]}: “{b['quote']}”.")
    elif an["pulls"]:
        bits.append(f"What stands out is {an['pulls'][0]['label'].split(': ')[1]}: “{an['pulls'][0]['quote']}”.")
    if an["feelings"]:
        bits.append("You mention feeling " + _join(an["feelings"][:4]) + ".")
    return {"text": " ".join(bits), "people": an["people"], "pulls": an["pulls"], "feelings": an["feelings"]}


def _join(xs):
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def followups(an, asked, rounds):
    """Up to 3 new questions about missing facts that matter for this dilemma. [] means there is enough to go on."""
    if rounds >= 2:
        return []
    order = []
    for a in an["core"]:
        order += [s for s in SLOT_PRIORITY[a] if s not in order]
    order += [s for s, _, _ in SLOTS if s not in order]
    missing = [s for s in order if s not in an["known"] and s not in asked]
    if len([s for s in order[:5] if s not in an["known"]]) <= 1:
        return []  # enough to go on
    text = {s: q for s, _, q in SLOTS}
    return [{"slot": s, "text": text[s]} for s in missing[:3]]


def core_text(an):
    want = next((s for s in an["sentences"] if re.search(SLOTS[0][1], s.lower())), "")
    parts = [p["quote"] for p in an["pulls"]] + ([want] if want else [])
    return " ".join(dict.fromkeys(parts))


def advise(story, profile=None, region=None):
    """-> (answer dict used for the advice, analysis, whole-story answer used for safety)."""
    lib = load_library()
    whole = answer(story, profile, mode="internal", region=region)  # safety is read from everything they wrote
    an = analyse(story)
    level = (whole.get("safety") or {}).get("level")
    if level in ("crisis", "danger") or whole.get("protective"):
        return whole, an, whole
    focus = core_text(an) or story
    a = answer(focus, profile, mode="internal", region=region)
    if not addresses_core(a, an, lib):  # try the shortlist for a principle that speaks to the core pulls
        for c in a.get("shortlist", []):
            if set(lib["principles"][c["id"]].get("aims", [])) & set(an["core"]):
                alt = _build(focus, profile, "internal", region, force=c["id"])
                if not gate_check(alt, lib):
                    alt["regenerated"] = True
                    a = alt
                    break
    a["safety"] = whole.get("safety") or a.get("safety")
    return a, an, whole


def addresses_core(a, an, lib):
    pid = (a.get("recommendation") or {}).get("principle")
    return bool(pid and set(lib["principles"].get(pid, {}).get("aims", [])) & set(an["core"]))


def compose_advice(a, an):
    """The advice in the owner's shape: core dilemma, the pulls in their words, recommendation and why,
    the strongest other view, one next step. Engine wording (the LLM may rewrite it later)."""
    rec = a.get("recommendation") or {}
    meaning = rec.get("text", "")
    if rec.get("name") and meaning.startswith(rec["name"]):
        meaning = meaning[len(rec["name"]):].lstrip(". ")
    level = (a.get("safety") or {}).get("level")
    if level == "danger":
        dilemma = "Before anything else: what you describe sounds unsafe, and your safety comes first."
    elif len(an["pulls"]) == 2:
        x, y = an["pulls"]
        dilemma = (f"At the heart of this, {AIM_SHORT[x['aim']]} ({x['label'].split(': ')[1]}) is pulling against "
                   f"{AIM_SHORT[y['aim']]} ({y['label'].split(': ')[1]}).")
    else:
        dilemma = ""
    comp = a.get("comparison", [])
    # In their words: one short excerpt for each of the people who matter most in the story.
    seen, situation = {p["quote"] for p in an["pulls"]}, []
    def weight(s):
        return sum(len(re.findall(AIMS[x], s.lower())) for x in an["core"])
    for person in an["people"][:4]:
        cands = [s for s in an["sentences"] if re.search(rf"(?<![\w-]){re.escape(person)}(?![\w-])", s.lower())]
        s = max(cands, key=weight) if cands else None
        if s:
            q = short_quote(s, rf"\b{re.escape(person)}\b", 22)
            if q not in seen and all(q not in x and x not in q for x in seen):
                seen.add(q)
                situation.append({"person": person, "quote": q})
    out = {"dilemma": dilemma, "pulls": an["pulls"] if level != "danger" else [], "situation": situation,
           "closest": rec.get("name"), "also": [c["name"] for c in comp[1:3]],
           "recommendation": meaning, "application": rec.get("application", ""), "why": rec.get("why_it_fits_you", ""),
           "other_view": (a.get("challenge") or {}).get("text", ""), "next_step": (a.get("next_step") or {}).get("text", ""),
           "sources": [{"id": s["id"], "english": s["english"], "devanagari": s["devanagari"]} for s in a.get("sources", [])]}
    out["protective"] = (a.get("protective") or {}).get("text", "")
    out["text"] = " ".join([out["protective"], dilemma] + [f"“{p['quote']}”" for p in out["pulls"]] +
                           [f"“{x['quote']}”" for x in situation] +
                           [out["recommendation"], out["application"], out["other_view"], out["next_step"]])
    return out


# ---------------------------------------------------------------- narrative gate
def check_reflection(refl, story):
    fails = []
    low = story.lower().replace("’", "'")
    for q in re.findall(r"“([^”]+)”", refl["text"]):
        if q not in story:
            fails.append(f"reflection quote not in the story: {q[:40]}")
    for p in refl["people"]:
        if not re.search(rf"(?<![\w-]){re.escape(p)}(?![\w-])", low):
            fails.append(f"reflection names someone not in the story: {p}")
    for f in refl["feelings"]:
        if f not in low:
            fails.append(f"reflection names a feeling not in the story: {f}")
    return fails


def check_questions(qs, asked, an):
    fails = []
    slots = [q["slot"] for q in qs]
    if len(qs) > 3:
        fails.append("more than 3 questions")
    if len(set(slots)) != len(slots) or set(slots) & set(asked):
        fails.append("repeats a question")
    if set(slots) & an["known"]:
        fails.append("asks about something the person already said")
    return fails


def check_advice(a, an, text, lib=None):
    """The advice must address the core pulls and refer to the person's specifics."""
    lib = lib or load_library()
    fails = []
    level = (a.get("safety") or {}).get("level")
    if level not in ("crisis", "danger") and not a.get("protective") and an["core"] and not addresses_core(a, an, lib):
        fails.append("advice does not address the central dilemma (" + " vs ".join(an["core"]) + ")")
    low = text.lower()
    if an["people"] and not any(re.search(rf"\b{re.escape(p)}\b", low) for p in an["people"]) and \
            not any(p["quote"].lower() in low for p in an["pulls"]):
        fails.append("advice does not refer to the person's specifics")
    return fails
