"""Viveka answer engine: understand -> clarify -> retrieve -> compare ->
recommend -> challenge -> act.

Rules this module enforces:
  - Quotes come only from the library files in data/ (never generated).
  - Every part of an answer is labelled: source text, commentator's view,
    historical example, or Viveka's application.
  - Public mode shows only reviewed/approved material; internal mode allows
    drafts but marks the whole answer DRAFT.
  - Safety overrides fit: crisis and danger are handled first; renunciation,
    abandoning responsibilities and fatalism are never offered to anyone in
    distress or not known to be an adult; leaving abuse or danger is always
    supported, with help lines.
  - Nothing is written to disk or sent anywhere.
"""

import json
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

from .frames import FRAME_EXCLUDE, detect_frames, frame_boosts
from .understand import understand

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PUBLIC_STATUSES = {"reviewed", "approved"}
SCHOOL_LABEL = {"advaita": "Śaṅkara (Advaita)", "vishishtadvaita": "Rāmānuja (Viśiṣṭādvaita)",
                "dvaita": "Madhva (Dvaita)"}
SITUATION_LABEL = {
    "grief_loss": "grief and loss", "fear_anxiety": "fear and anxiety", "anger_resentment": "anger",
    "failure_setback": "a setback", "lack_of_motivation": "low motivation",
    "conflict_of_duties": "conflicting duties", "relationships_forgiveness": "a relationship",
    "ego_pride_envy": "pride or comparison", "temptation_self_control": "self-control",
    "success_wealth": "money or success", "purpose_meaning": "meaning and direction",
    "ageing_death_impermanence": "ageing and mortality",
}

# Never quote verses with these flags as guidance: they belong to the war
# setting or rank people by birth or gender.
NEVER_QUOTE_FLAGS = {"war", "caste_gender"}
# Withheld unless the person is known to be an adult and not in distress.
HOLD_FLAGS_MINOR = {"under18_hold", "renunciation"}
HOLD_FLAGS_DISTRESS = {"under18_hold", "renunciation", "death", "distress_gentle"}

# Principles that could be misread as 'stay and endure' when someone is in danger.
DANGER_EXCLUDE = {"dont-quit-because-its-hard", "bear-what-comes-and-goes", "patience", "seek-a-parents-peace",
                  "forgiveness-as-strength", "keep-your-word", "loving-without-clinging", "same-regard-for-all",
                  "no-hatred", "meet-people-where-they-are", "hard-at-first-sweet-later", "trust-alongside-effort",
                  "nature-and-the-inner-controller", "your-nature-shapes-you", "fortitude-that-holds",
                  "neither-troubling-nor-troubled", "action-over-inaction"}
DANGER_PREFER = ["duty-of-protection", "fearlessness", "ask-for-help-when-lost", "self-as-friend",
                 "no-self-torture", "reflect-then-choose"]

STOP = set("""a an the and or but if then so to of in on at for with from by as is are was were be been being i me my
mine we our you your he she it they them their this that these those do does did have has had not no yes can could
should would will just very really about into over under than too also there here what which who whom when where why
how all any some more most other such only own same up down out off again further once am im ive id dont cant wont
get got go going make made feel feeling felt want wanted think know like him her his hers she he they them
us myself yourself himself herself one thing things lot keep still even every always never""".split())


def tokens(text):
    out = []
    for w in re.findall(r"[a-z]+", text.lower()):
        if w in STOP or len(w) < 3:
            continue
        for suf in ("ing", "ness", "ment", "ed", "ly", "es", "s"):
            if w.endswith(suf) and len(w) - len(suf) >= 4:
                w = w[: -len(suf)]
                break
        out.append(w)
    return out


@lru_cache(maxsize=1)
def load_library():
    units = {}
    for r in json.loads((DATA / "gita.json").read_text(encoding="utf-8")):
        units[r["id"]] = dict(r, text="gita")
    registry = {k: v for k, v in json.loads((DATA / "texts.json").read_text(encoding="utf-8")).items()
                if not k.startswith("_")}
    text_schools = {"gita": ["advaita", "vishishtadvaita", "dvaita"]}
    text_titles = {"gita": "Bhagavad Gita"}
    for tid, meta in registry.items():
        path = DATA / f"{tid}.json"
        if path.exists():
            for r in json.loads(path.read_text(encoding="utf-8")):
                units[r["id"]] = r
        text_schools[tid] = list(meta.get("commentaries", {}))
        text_titles[tid] = meta["title"]
    gita_comm = json.loads((DATA / "gita_commentaries.json").read_text(encoding="utf-8"))["verses"]
    comm_present = {vid: set(d) for vid, d in gita_comm.items()}
    for tid in registry:
        cp = DATA / "commentaries" / f"{tid}.json"
        if cp.exists():
            for uid, d in json.loads(cp.read_text(encoding="utf-8"))["units"].items():
                comm_present[uid] = set(d)
    principles = []
    for path in sorted((DATA / "principles").glob("*.json")):
        principles += json.loads(path.read_text(encoding="utf-8"))
    examples = []
    for path in sorted((DATA / "examples").glob("*.json")):
        examples += json.loads(path.read_text(encoding="utf-8"))
    help_res = json.loads((DATA / "help_resources.json").read_text(encoding="utf-8"))

    # Retrieval index over principle text.
    docs = {p["id"]: tokens(" ".join([p["name"], p["meaning"], p["applies_when"], p["modern_application"]]))
            for p in principles}
    df = Counter(t for d in docs.values() for t in set(d))
    idf = {t: math.log(1 + len(docs) / n) for t, n in df.items()}
    return {"units": units, "principles": {p["id"]: p for p in principles}, "examples": examples,
            "help": help_res, "docs": {k: set(v) for k, v in docs.items()}, "idf": idf,
            "text_schools": text_schools, "text_titles": text_titles, "comm_present": comm_present}


# ------------------------------------------------------------------ safety

def quotable(unit, sit, mode):
    if mode == "public" and unit.get("review_status") not in PUBLIC_STATUSES:
        return False
    if not unit.get("situations"):
        return False  # narrative units are never offered as guidance
    flags = set(unit.get("safety_flags", []))
    if flags & NEVER_QUOTE_FLAGS:
        return False
    if sit.treat_as_minor and flags & HOLD_FLAGS_MINOR:
        return False
    if sit.distress and flags & HOLD_FLAGS_DISTRESS:
        return False
    return True


def principle_allowed(p, sit, mode):
    if mode == "public" and p.get("review_status") not in PUBLIC_STATUSES:
        return False
    restricted = set(p.get("restricted_for", []))
    if "under18" in restricted and sit.treat_as_minor:
        return False
    if "distress" in restricted and sit.distress:
        return False
    if sit.danger and p["id"] in DANGER_EXCLUDE:
        return False
    return True


def help_lines(lib, kinds, region=None):
    regions = lib["help"]["regions"]
    order = [region] if region in regions else []
    order += [r for r in ("IN", "US", "UK") if r not in order]
    out = []
    for r in order:
        for h in regions[r]:
            if set(h["for"]) & set(kinds):
                out.append({"region": r, "name": h["name"], "number": h["number"]})
    return out


# ------------------------------------------------------------------ retrieve

def score_principle(p, sit, qtoks, lib, boosts):
    s, why = 0.0, []
    b = boosts.get(p["id"], 0.0)
    if b:
        s += b
        why.append("addresses the kind of problem you describe")
    shared = [x for x in sit.situations if x in p["situations"]]
    if shared:
        s += 2.0 * len(shared)
        why.append("speaks to " + ", ".join(SITUATION_LABEL[x] for x in shared))
    overlap = qtoks & lib["docs"][p["id"]]
    if overlap:
        s += 0.6 * sum(lib["idf"].get(t, 0) for t in overlap)
        why.append("echoes your words: " + ", ".join(sorted(overlap)[:4]))
    if sit.life_stage and sit.life_stage in p["life_stages"]:
        s += 1.0
        why.append(f"fits the {sit.life_stage} stage you described")
    elif sit.life_stage and sit.life_stage not in p["life_stages"]:
        s -= 2.0
    return s, why


def excluded_by_frames(frames):
    return set().union(*(FRAME_EXCLUDE.get(f, set()) for f in frames)) if frames else set()


def retrieve(sit, lib, mode, k=8):
    qtoks = set(tokens(sit.text))
    frames = detect_frames(sit.text, danger=sit.danger)
    # In danger, only the safety-and-agency set is considered, whatever else is mentioned.
    boosts = frame_boosts(["danger"] if sit.danger else frames)
    if "renounce_wish" in frames and sit.life_stage in ("elder", "renunciant") and not sit.distress:
        boosts["full-renunciation-path"] = boosts.get("full-renunciation-path", 0) + 6.0
    excluded = excluded_by_frames(frames)
    scored = []
    for p in lib["principles"].values():
        if not principle_allowed(p, sit, mode) or p["id"] in excluded:
            continue
        if sit.danger and p["id"] not in boosts:
            continue  # in danger, only principles chosen for safety and agency
        verses = [lib["units"][u] for u in p["supporting"] if u in lib["units"]
                  and quotable(lib["units"][u], sit, mode)]
        if not verses:
            continue  # nothing we may quote for this person: skip the principle
        s, why = score_principle(p, sit, qtoks, lib, boosts)
        if s > 0:
            scored.append({"principle": p, "score": round(s, 2), "why": why, "verses": verses})
    scored.sort(key=lambda x: -x["score"])
    return scored[:k], frames


# ------------------------------------------------------------------ compose

def commentary_for(units, lib):
    """Commentator's views on the quoted units. Missing schools are stated once per text."""
    out, missing_text, missing_unit = [], {}, []
    for unit in units:
        tid = unit.get("text", "gita")
        schools_for_text = lib["text_schools"].get(tid, [])
        noted = {n["school"] for n in unit.get("school_notes", [])}
        for n in unit.get("school_notes", []):
            out.append({"label": "Commentator's view", "unit": unit["id"], "school": n["school"],
                        "commentator": SCHOOL_LABEL.get(n["school"], n["commentator"]), "note": n["note"]})
        for school in ("advaita", "vishishtadvaita", "dvaita"):
            if school in noted:
                continue
            if school not in schools_for_text:
                missing_text.setdefault(tid, []).append(SCHOOL_LABEL[school])
            else:
                missing_unit.append(f"{SCHOOL_LABEL[school]} on {unit['id']}")
    for tid, names in missing_text.items():
        names = sorted(set(names))
        out.append({"label": "Commentator's view", "missing":
                    f"No commentary by {' or '.join(names)} on the {lib['text_titles'].get(tid, tid)} is in the library yet."})
    if missing_unit:
        out.append({"label": "Commentator's view", "missing":
                    "Our source has no comment from " + "; ".join(missing_unit) + "."})
    return out


def describe_person(sit):
    bits = []
    if sit.life_stage:
        bits.append(f"you describe yourself as a {sit.life_stage}")
    if sit.age is not None:
        bits.append(f"you are {sit.age}")
    if sit.people:
        bits.append("this involves your " + ", ".join(sit.people[:3]))
    return "; ".join(bits)


SAFETY_PLAN = ("Your safety comes first. Quietly prepare: keep your ID, important papers, some money and a charged "
               "phone where you can reach them; tell one trusted person what is happening; and save a help-line number. "
               "Leaving can be planned step by step, and the help lines can advise on shelter and money, so dependence "
               "does not have to trap you.")


def tailor(p, sit):
    """Viveka's application: the principle's modern application, fitted to what the person said."""
    if sit.danger:
        return SAFETY_PLAN + " " + p["modern_application"]
    parts = []
    if len(sit.options) == 2:
        parts.append(f"You are weighing '{sit.options[0]}' against '{sit.options[1]}'.")
    c = sit.constraints
    if c["irreversible"]:
        parts.append(f"Part of this ('{c['irreversible'][0]}') is hard to undo, so take the reversible steps first.")
    if c["urgency"]:
        parts.append(f"You mention a time limit ('{c['urgency'][0]}'); decide what must be settled by then and what can wait.")
    if c["power_imbalance"]:
        parts.append(f"Your {c['power_imbalance'][0]} has power over your situation, so plan for how they may react and who could support you.")
    elif sit.people:
        parts.append(f"Since this involves your {sit.people[0]}, think about what they need as well as what you need.")
    if c["dependency"] or c["money"]:
        parts.append("Because money or dependency is involved, check what you can afford and secure that before any big move.")
    parts.append(p["modern_application"])
    return " ".join(parts)


def pick_example(principle_ids, sit, lib, mode):
    for e in lib["examples"]:
        if mode == "public" and e.get("review_status") not in PUBLIC_STATUSES:
            continue
        if "under18" in e["restricted_for"] and sit.treat_as_minor:
            continue
        if "distress" in e["restricted_for"] and sit.distress:
            continue
        if set(e["principles"]) & set(principle_ids):
            label = "Historical example" + (" (story from the texts)" if e["kind"] == "scripture_story" else "")
            return {"label": label, "id": e["id"], "title": e["title"], "event": e["event"],
                    "source": e["source"], "lesson": e["lesson"], "limits": e["limits_of_analogy"],
                    "verified": e["verified"]}
    return None


def clarifying_questions(sit, shortlist, lib, mode):
    """At most two, and only when the answer would change the recommendation."""
    qs = []
    if any(w in sit.text.lower() for w in ("scared of him", "scared of her", "afraid of him", "afraid of her",
                                           "he shouts at me", "she shouts at me")) and not sit.danger:
        qs.append("Are you safe right now?")
    if sit.minor == "unknown" and shortlist:
        import copy
        adult = copy.copy(sit)
        adult.minor = "no"
        alt, _ = retrieve(adult, lib, mode)
        if alt and alt[0]["principle"]["id"] != shortlist[0]["principle"]["id"]:
            qs.append("Are you 18 or older? The answer changes which passages fit.")
    if "conflict_of_duties" in sit.situations and len(sit.options) < 2 and "?" in sit.text:
        qs.append("What are the main options you are choosing between?")
    if not detect_frames(sit.text) and (not sit.situations or len(sit.text.split()) < 6) and not sit.danger:
        qs.append("Could you tell me a little more about what is happening? A few details would let me answer for your situation.")
    return qs[:2]


def answer(question, profile=None, mode="internal", region=None):
    lib = load_library()
    if mode not in ("internal", "public"):
        raise ValueError("mode must be 'internal' or 'public'")
    sit = understand(question, profile)
    out = {
        "mode": mode,
        "notice": ("DRAFT: internal test answer using unreviewed material. Not for users."
                   if mode == "internal" else "Shows only reviewed material."),
        "understanding": {
            "dilemma": sit.dilemma, "situations": sit.situations, "people": sit.people,
            "options": sit.options, "obligations": sit.obligations, "constraints": sit.constraints,
            "age": sit.age, "minor": sit.minor, "life_stage": sit.life_stage,
            "distress": sit.distress, "danger": sit.danger, "self_harm": sit.self_harm,
        },
        "clarifying_questions": [], "safety": None, "shortlist": [], "comparison": [],
        "recommendation": None, "sources": [], "commentary": [], "example": None,
        "challenge": None, "next_step": None,
    }

    # Safety first. Self-harm (the person or someone they know): no philosophy, only care and help.
    if sit.other_at_risk:
        out["safety"] = {
            "label": "Viveka's application", "level": "crisis",
            "message": ("Your friend's safety comes first, and this is not a secret to keep. If they may act soon, call emergency "
                        "services now and stay with them if you can. Otherwise, tell a trusted adult or a professional today, "
                        "and share a help line with your friend. You do not have to handle this alone."),
            "help": help_lines(lib, ["self_harm"], region),
        }
        out["next_step"] = {"label": "Viveka's application",
                            "text": "Right now, contact a trusted adult or a help line about your friend, and check that someone is with them."}
        return out
    if sit.self_harm:
        out["safety"] = {
            "label": "Viveka's application", "level": "crisis",
            "message": ("I'm really glad you said this. You deserve support right now from a person, not a book. "
                        "Please contact one of these lines, or someone you trust, today. If you are in immediate danger, call emergency services."),
            "help": help_lines(lib, ["self_harm"], region),
        }
        out["next_step"] = {"label": "Viveka's application",
                            "text": "Call or message one of the lines above, or tell one person you trust how you are feeling, today."}
        return out
    if sit.danger:
        out["safety"] = {
            "label": "Viveka's application", "level": "danger",
            "message": ("What you describe sounds unsafe. Leaving or getting away from abuse or danger is never a failure of duty, "
                        "and you do not have to handle it alone."),
            "help": help_lines(lib, ["danger", "abuse"] + (["under18"] if sit.treat_as_minor else []), region),
        }

    if sit.distress and not out["safety"]:
        out["safety"] = {
            "label": "Viveka's application", "level": "support",
            "message": ("It sounds like you are carrying a lot. If this heaviness has lasted a while, talking to someone "
                        "trained to help can make a real difference; it is a sign of strength, not weakness."),
            "help": help_lines(lib, ["distress", "self_harm"], region)[:2],
        }

    shortlist, frames = retrieve(sit, lib, mode)
    out["understanding"]["frames"] = frames
    out["clarifying_questions"] = clarifying_questions(sit, shortlist, lib, mode)
    if not frames and (not sit.situations or len(sit.text.split()) < 6) and not sit.danger and not sit.distress:
        # Too little to go on: ask instead of guessing.
        out["recommendation"] = {"label": "Viveka's application",
                                 "text": "I'd like to understand a little more before suggesting anything."}
        out["next_step"] = {"label": "Viveka's application",
                            "text": "Tell me what happened, who is involved, and what you are weighing up."}
        return out
    out["shortlist"] = [{"id": c["principle"]["id"], "score": c["score"]} for c in shortlist]
    if not shortlist:
        out["recommendation"] = {
            "label": "Viveka's application",
            "text": ("Viveka does not yet have reviewed passages that fit this situation." if mode == "public"
                     else "No principle in the library fits this situation well enough. This is a gap to fill."),
        }
        return out

    top3 = shortlist[:3]
    ids3 = {c["principle"]["id"] for c in top3}
    for c in top3:
        p = c["principle"]
        out["comparison"].append({
            "principle": p["id"], "name": p["name"], "fit": c["why"],
            "disagrees_with": [x for x in p["conflicts_with"] if x in ids3] or p["conflicts_with"][:2],
            "consequence_if_followed": p["applies_when"], "limits": p["misleads_when"],
        })

    best = top3[0]
    bp = best["principle"]
    person = describe_person(sit)
    why = "; ".join(best["why"])
    out["recommendation"] = {
        "label": "Viveka's application", "principle": bp["id"], "name": bp["name"],
        "text": f"{bp['name']}. {bp['meaning']}",
        "why_it_fits_you": (f"For your situation ({person}): " if person else "For your situation: ") + why + ".",
        "application": tailor(bp, sit),
    }

    quoted = best["verses"][:2]
    for u in quoted:
        out["sources"].append({"label": "Source text", "id": u["id"], "english": u["english"],
                               "devanagari": u["devanagari"], "review_status": u["review_status"]})
    out["commentary"] = commentary_for(quoted, lib)

    # Challenge: the strongest alternative, preferring a principle that genuinely conflicts.
    alt = None
    excluded = excluded_by_frames(frames)
    for c in shortlist[1:]:
        if c["principle"]["id"] in excluded:
            continue
        if c["principle"]["id"] in bp["conflicts_with"] and (not sit.life_stage or sit.life_stage in c["principle"]["life_stages"]):
            alt = c
            break
    if alt is None:
        for cid in bp["conflicts_with"]:
            cp = lib["principles"].get(cid)
            if cp and cid not in excluded and principle_allowed(cp, sit, mode) and \
                    (not sit.life_stage or sit.life_stage in cp["life_stages"]):
                verses = [lib["units"][u] for u in cp["supporting"] if quotable(lib["units"][u], sit, mode)]
                if verses:
                    alt = {"principle": cp, "verses": verses}
                    break
    if alt is None:
        alt = next((c for c in shortlist[1:] if c["principle"]["id"] not in excluded), None)
    if alt:
        ap = alt["principle"]
        out["challenge"] = {
            "label": "Viveka's application", "principle": ap["id"], "name": ap["name"],
            "text": f"If your conscience leans the other way, here is the other view: {ap['name']}. {ap['meaning']}",
            "source": {"label": "Source text", "id": alt["verses"][0]["id"], "english": alt["verses"][0]["english"]},
            "when_the_recommendation_misleads": bp["misleads_when"],
        }
    out["example"] = pick_example([bp["id"]] + ([alt["principle"]["id"]] if alt else []), sit, lib, mode)
    out["next_step"] = {"label": "Viveka's application", "text": bp["modern_application"]}
    if sit.danger:
        out["next_step"]["text"] = ("Today, save one help-line number where it is safe to keep it, and tell one person "
                                    "you trust what is happening.")
    return out


def render(a):
    """Plain-text rendering with every part labelled."""
    L = [f"[{a['notice']}]", ""]
    if a["safety"]:
        L += [f"{a['safety']['label']}: {a['safety']['message']}"]
        L += [f"  - {h['name']}: {h['number']} ({h['region']})" for h in a["safety"]["help"]]
        L.append("")
    if a["clarifying_questions"]:
        L.append("Questions that could change this answer:")
        L += [f"  - {q}" for q in a["clarifying_questions"]]
        L.append("")
    r = a["recommendation"]
    if r:
        L.append(f"{r['label']} - Recommendation: {r['text']}")
        if r.get("why_it_fits_you"):
            L.append(f"  Why it fits you: {r['why_it_fits_you']}")
        if r.get("application"):
            L.append(f"  In practice: {r['application']}")
        L.append("")
    for s in a["sources"]:
        L.append(f"{s['label']} ({s['id']}): \"{s['english']}\"")
    for c in a["commentary"]:
        L.append(f"  {c['label']} - " + (f"{c['commentator']}: {c['note']}" if "note" in c else c["missing"]))
    if a["example"]:
        e = a["example"]
        L += ["", f"{e['label']}: {e['title']}. {e['event']} Lesson: {e['lesson']} Limits: {e['limits']}"
              + ("" if e["verified"] else " (Not yet verified against its source.)")]
    if a["challenge"]:
        c = a["challenge"]
        L += ["", f"{c['label']} - Strongest alternative: {c['text']}",
              f"  Source text ({c['source']['id']}): \"{c['source']['english']}\"",
              f"  When the recommended principle misleads: {c['when_the_recommendation_misleads']}"]
    if a["next_step"]:
        L += ["", f"{a['next_step']['label']} - One next step: {a['next_step']['text']}"]
    return "\n".join(L)
