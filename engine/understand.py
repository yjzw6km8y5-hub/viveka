"""Step 1: understand the person's situation from their own words.

Only explicit statements are used. Age and life stage are read separately and
never inferred from each other: 'I'm 70' does not make someone an elder, and
'I'm a student' says nothing about age. Where safety depends on an unknown
(e.g. whether someone is under 18), the engine treats it as unknown and
chooses the conservative option.
"""

import re
from dataclasses import dataclass, field

SITUATION_CUES = {
    "grief_loss": ["died", "death of", "passed away", "lost my", "grief", "grieving", "funeral", "bereave",
                   "miscarriage", "miss him", "miss her", "loss of", "mourning"],
    "fear_anxiety": ["anxious", "anxiety", "afraid", "scared", "fear", "worried", "worry", "panic", "nervous",
                     "terrified", "overthink", "stress", "dread"],
    "anger_resentment": ["angry", "anger", "furious", "resent", "hate", "rage", "betray", "revenge", "bitter",
                         "annoyed", "irritat", "fed up"],
    "failure_setback": ["failed", "failure", "fail ", "rejected", "rejection", "fired", "laid off", "setback",
                        "mistake", "messed up", "didn't get", "did not get", "flunk", "lost my job", "relapse",
                        "thrown everything away", "lost the", "blames me", "my fault"],
    "lack_of_motivation": ["unmotivated", "motivation", "lazy", "procrastinat", "can't start", "cannot start",
                           "no energy", "bored", "stuck", "giving up", "can't focus", "cannot focus"],
    "conflict_of_duties": ["torn", "should i", "duty", "obligation", "responsib", "choose between", "loyal",
                           "promised", "whether to", "dilemma", "expected to"],
    "relationships_forgiveness": ["wife", "husband", "partner", "girlfriend", "boyfriend", "friend", "mother",
                                  "father", "parent", "mom", "mum", "dad", "sibling", "brother", "sister",
                                  "forgive", "apolog", "argument", "fight with", "relationship", "divorce",
                                  "marriage", "in-laws", "son", "daughter", "colleague", "roommate"],
    "ego_pride_envy": ["jealous", "envy", "envious", "compare", "comparison", "pride", "proud", "ego",
                       "arrogan", "credit", "recognition", "status", "humiliat", "embarrass", "insult", "praise",
                       "criticis", "criticiz", "blame", "bitter", "caste", "shamed"],
    "temptation_self_control": ["addict", "craving", "can't stop", "cannot stop", "phone", "scrolling", "porn",
                                "alcohol", "drinking", "gambl", "tempt", "cheat", "binge", "self-control",
                                "habit", "impulse", "sober", "had a drink", "shopping", "credit card", "spend",
                                "drugs", "smok"],
    "success_wealth": ["money", "rich", "salary", "promotion", "wealth", "inherit", "business", "profit",
                       "debt", "loan", "success", "bonus", "property", "pay ", "offer", "job offer"],
    "purpose_meaning": ["purpose", "meaning", "meaningless", "point of", "empty", "direction", "calling",
                        "spiritual", "what to do with my life", "who i am", "worth it", "god", "exist", "selfish",
                        "who am i", "thanks me", "appreciat"],
    "ageing_death_impermanence": ["old age", "ageing", "aging", "retire", "dying", "mortality", "terminal",
                                  "diagnos", "getting older", "end of life", "hospice", "slow down", "my doctor",
                                  "health", "moving abroad", "for good"],
}

PEOPLE = ["mother", "father", "parents", "mom", "mum", "dad", "wife", "husband", "partner", "girlfriend",
          "boyfriend", "friend", "best friend", "boss", "manager", "teacher", "professor", "brother",
          "sister", "son", "daughter", "children", "kids", "colleague", "coworker", "in-laws",
          "mother-in-law", "father-in-law", "grandmother", "grandfather", "landlord", "roommate", "team",
          "employer", "coach", "guru"]

POWER_HOLDERS = {"boss", "manager", "teacher", "professor", "landlord", "employer", "in-laws",
                 "mother-in-law", "father-in-law", "coach", "guru"}
PARENTS = {"mother", "father", "parents", "mom", "mum", "dad"}

# Cues where the person names their own stage or status; every other stage cue is our inference.
STATED_STAGE_CUES = [r"\bi'?m a student\b", r"\bi am a student\b", r"\bi'?m retired\b", r"\bi am retired\b",
                     r"\bi'?m a monk\b", r"\bi have renounced\b", r"\bi'?m married\b", r"\bi am married\b"]

STAGE_CUES = {
    "student": [r"\bi'?m a student\b", r"\bi am a student\b", r"\bmy (?:exams?|college|university|school|degree|course|classes)\b",
                r"\bstudying\b", r"\bin (?:college|university|high school|school)\b"],
    "householder": [r"\bmy (?:wife|husband|kids|children|son|daughter|job|boss|manager|mortgage|business)\b",
                    r"\bi'?m married\b", r"\bi am married\b", r"\bwe have (?:a baby|kids|children)\b",
                    r"\bwith (?:a baby|\w+ (?:small |young |little )?(?:kids|children))\b", r"\bmy (?:wife and|husband and) kids\b"],
    "elder": [r"\bi'?m retired\b", r"\bi am retired\b", r"\bafter (?:my )?retirement\b", r"\bmy grandchild"],
    "renunciant": [r"\bi'?m a monk\b", r"\bsannyas", r"\bliving in an ashram\b", r"\bi have renounced\b"],
}

SELF_HARM = ["kill myself", "suicide", "suicidal", "end my life", "end it all", "don't want to live",
             "do not want to live", "want to die", "hurt myself", "self harm", "self-harm", "self harms",
             "self-harms", "cutting myself", "no reason to live", "better off without me", "if i disappeared",
             "if i was gone", "if i were gone", "wish i was dead", "wish i were dead", "don't want to be here anymore",
             "do not want to be here anymore", "never wake up", "not want to be alive", "don't want to be alive",
             "nobody would care if i", "no one would care if i", "nobody would miss me", "no one would miss me",
             "no will to live", "tired of living", "don't want to exist", "do not want to exist",
             "life isn't worth living", "life is not worth living", "nothing to live for", "give up on life",
             "overdose", "jump off", "want to disappear forever", "end things", "not be around anymore",
             "if i wasn't here", "if i weren't here", "if i was not here", "if i were not here", "if i was gone",
             "better off without me", "better off if i", "not here anymore", "the insurance money"]
OTHER_AT_RISK = ["hurt himself", "hurt herself", "hurt themselves", "kill himself", "kill herself",
                 "kill themselves", "end his life", "end her life", "end their life", "she self-harms",
                 "he self-harms", "she self harms", "he self harms", "my friend self", "friend told me she self",
                 "friend told me he self", "friend is suicidal", "planning to hurt"]
DANGER = ["hits me", "hit me", "beats me", "beat me", "beating", "abuse", "abusive", "violent", "violence",
          "threatens", "threatened", "unsafe", "not safe", "scared to go home", "afraid to go home",
          "forced to marry", "forced marriage", "locks me", "locked me", "controls my money", "stalk",
          "harass", "hurts me", "touches me", "assault", "scared to be at home", "afraid to be at home",
          "scared at home", "afraid at home", "forcing me to marry", "force me to marry", "making me marry",
          "forced to get married", "verbally abusive", "slaps me", "kicked me out", "threw me out",
          "met online", "meet him alone", "meet her alone", "keep it secret", "send him photos", "send her photos",
          "nudes", "blackmail", "sextortion", "embarrassing photo", "private photo", "intimate photo", "leaked my",
          "takes my pension", "takes my money", "takes all my money", "dowry", "sexually harass", "send me back",
          "threatening to post", "won't let me leave", "took my passport", "locked in", "grooming", "followed me home",
          "will hurt me", "hurt me if", "going to hurt me", "threatens to hurt", "threatened to hurt", "controls what i eat"]
DISTRESS = ["hopeless", "worthless", "can't go on", "nothing matters", "no point in anything",
            "everything feels pointless", "everything is pointless", "pointless lately", "don't feel anything",
            "do not feel anything", "feel nothing", "empty inside", "i deserve it", "i deserve this", "deserve to suffer",
            "can't do this anymore", "cannot do this anymore", "no energy for anything", "don't see the point",
            "do not see the point", "drinking every night", "stopped eating", "not eating properly", "make myself sick",
            "make myself throw up", "skip meals", "want to be thinner", "starving myself", "cannot go on", "falling apart", "depressed", "depression",
            "breakdown", "can't cope", "cannot cope", "unbearable", "crying every", "numb", "exhausted all the time",
            "no way out", "trapped"]

# Protective needs (STATUS.md must-fix 2): restricting or purging food needs a doctor and, for anyone
# not known to be an adult, a trusted adult who is safe for them. Detected separately from distress so the
# answer can carry concrete guidance; it also counts as distress, so gentle handling applies.
# Eating risk = purging, or a named eating disorder, or restricting food for weight or body reasons.
# Restriction alone ("I stopped eating lunch at my desk", fasting for a festival) is not a protective need.
EATING_PURGING = [r"\b(?:make|makes|making|made|force|forces|forcing|forced) (?:myself|me) (?:to )?(?:be sick|sick|throw up|vomit|puke)\b",
                  r"\bthrow(?:ing)? up (?:after|on purpose)\b", r"\bvomit(?:ing)? (?:after|on purpose)\b",
                  r"\bpurg(?:e|es|ing)\b", r"\blaxatives?\b[^.?!]{0,40}\b(?:lose|weight|thin|fat)\b"]
EATING_NAMED = [r"\beating disorder\b", r"\banorexi", r"\bbulimi", r"\bbinge and purge\b"]
EATING_RESTRICT = [r"\b(?:stopped|stop|stopping|quit) eating\b", r"\bnot eating\b", r"\bstarv(?:e|ing) myself\b",
                   r"\b(?:skip|skips|skipping|skipped) (?:meals?|breakfast|lunch|dinner)\b",
                   r"\b(?:barely|hardly|haven't|have not|not) (?:eat|eaten|eating)\b", r"\bonly eat (?:once|one meal)\b",
                   r"\beat (?:once|one meal) a day\b", r"\bfasting\b", r"\b(?:under|less than|only) \d{3,4} calories\b",
                   r"\bcount(?:ing)? every calorie\b", r"\bdrop weight fast\b", r"\blose weight fast\b"]
EATING_MOTIVE = [r"\bthin(?:ner)?\b", r"\bskinn(?:y|ier)\b", r"\bweight\b", r"\bfat\b", r"\bmy body\b",
                 r"\bcalories\b", r"\bslim(?:mer)?\b", r"\bmy size\b", r"\blook (?:great|good|better)\b"]


def eating_risk(text):
    """-> (risk, purging)"""
    purging = any(re.search(p, text) for p in EATING_PURGING)
    named = any(re.search(p, text) for p in EATING_NAMED)
    restrict = any(re.search(p, text) for p in EATING_RESTRICT) and any(re.search(p, text) for p in EATING_MOTIVE)
    return purging or named or restrict, purging

MINOR_CUES = [r"\bi'?m a (?:teen|teenager|minor)\b", r"\bi am a (?:teen|teenager|minor)\b",
              r"\bin high school\b", r"\bunder 18\b", r"\bunderage\b"]
ADULT_CUES = [r"\bi'?m an adult\b", r"\bover 18\b"]

URGENCY = ["tomorrow", "tonight", "today", "this week", "deadline", "urgent", "immediately", "right now",
           "by friday", "by monday", "in two days", "in a few days", "by the end of"]
IRREVERSIBLE = ["quit", "resign", "divorce", "drop out", "move abroad", "emigrate", "sell the house",
                "break up", "cut off", "disown", "leave home", "leave my", "get married", "elope", "sign"]
MONEY = ["money", "salary", "debt", "loan", "rent", "income", "afford", "fees", "savings", "pay "]
DEPENDENCY = ["depend on", "dependent on", "they pay", "pays for", "my only income", "can't afford to leave",
              "cannot afford to leave", "visa", "live with my parents", "living with my parents"]
OBLIGATION = [r"\bi (?:have to|must|need to|promised|owe)\b", r"\bmy duty\b", r"\bresponsib\w*\b", r"\bexpected to\b"]


@dataclass
class Situation:
    text: str
    situations: list = field(default_factory=list)
    situation_hits: dict = field(default_factory=dict)
    people: list = field(default_factory=list)
    options: list = field(default_factory=list)
    obligations: list = field(default_factory=list)
    constraints: dict = field(default_factory=dict)
    age: int = None
    minor: str = "unknown"          # "yes", "no", "unknown"
    life_stage: str = None          # from the profile, the person's own words, or (marked) inference
    life_stage_source: str = None   # "profile", "stated" or "inferred"
    life_stage_cue: str = ""        # the words the stage was read from
    protective: list = field(default_factory=list)  # e.g. ["eating"]
    purging: bool = False
    months_since_loss: float = None
    self_harm: bool = False
    other_at_risk: bool = False
    danger: bool = False
    distress: bool = False
    dilemma: str = ""

    @property
    def treat_as_minor(self):
        """Conservative: restricted material is withheld unless the person is known to be an adult."""
        return self.minor != "no"


def _has(text, cue):
    return cue in text


def _word(text, cues):
    """Whole-word phrase match (so 'numbers' does not match 'numb')."""
    return any(re.search(r"(?<![a-z])" + re.escape(c.strip()) + r"(?![a-z])", text) for c in cues)


def find_options(raw):
    t = " " + raw.strip() + " "
    pats = [r"\bshould i (.+?) or (.+?)[?.!]", r"\bwhether (?:to|i should) (.+?) or (.+?)[?.!]",
            r"\b(?:do|shall) i (.+?) or (.+?)[?.!]", r"\beither (.+?) or (.+?)[?.!]"]
    for p in pats:
        m = re.search(p, t, flags=re.I | re.S)
        if m:
            return [m.group(1).strip(" ,"), m.group(2).strip(" ,")]
    m = re.search(r"\bshould i (.+?)[?.!]", t, flags=re.I | re.S)
    if m:
        opt = m.group(1).strip(" ,")
        return [opt, "not " + opt]
    return []


def first_question(raw):
    sents = re.split(r"(?<=[.?!])\s+", raw.strip())
    for s in sents:
        if "?" in s:
            return s.strip()
    return sents[0].strip() if sents else raw.strip()


NUMBER_WORDS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                "eight": 8, "nine": 9, "ten": 10, "a few": 3, "few": 3, "several": 5}


def months_since_loss(text):
    """'died three months ago' -> 3; 'widowed five years ago' -> 60; 'died last year' -> 12. None if not said."""
    loss = r"(?:died|passed away|was widowed|were widowed|became a widow(?:er)?|lost (?:my|our) \w+)"
    m = re.search(loss + r"[^.?!]{0,30}?\b(\d+|a few|an|a|one|two|three|four|five|six|seven|eight|nine|ten|few|several)"
                  r" (day|week|month|year)s? ago", text)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else NUMBER_WORDS[m.group(1)]
        return n * {"day": 1 / 30, "week": 0.25, "month": 1, "year": 12}[m.group(2)]
    if re.search(loss + r"[^.?!]{0,20}?\b(?:last year)", text):
        return 12
    if re.search(loss + r"[^.?!]{0,20}?\b(?:last|this) (?:week|month)\b", text):
        return 1
    return None


def understand(raw, profile=None):
    profile = profile or {}
    text = " " + raw.lower().replace("’", "'") + " "
    s = Situation(text=raw)

    for sit, cues in SITUATION_CUES.items():
        hits = [c.strip() for c in cues if _has(text, c)]
        if hits:
            s.situation_hits[sit] = hits
    s.situations = sorted(s.situation_hits, key=lambda k: -len(s.situation_hits[k]))

    s.people = [p for p in PEOPLE if re.search(rf"\b{re.escape(p)}\b", text)]
    s.options = find_options(raw)
    s.obligations = [m.group(0) for p in OBLIGATION for m in re.finditer(p, text)]

    # Age: explicit only (or from the profile). Never inferred from life stage.
    age = profile.get("age")
    if age is None:
        # First-person statements only: "my 84-year-old father" is not the user's age.
        for p in [r"\bi'?m (\d{1,2})\b(?!\s*(?:hours|minutes|days|weeks|months|kg|%|-year))",
                  r"\bi am (\d{1,2})\b(?!\s*(?:hours|minutes|days|weeks|months|kg|%|-year))",
                  r"\bmy age is (\d{1,2})\b", r"\bi turned (\d{1,2})\b", r"\bi'?m (?:a|an) (\d{1,2})[- ]year[- ]old\b"]:
            m = re.search(p, text)
            if m:
                age = int(m.group(1))
                break
    s.age = age
    if age is not None:
        s.minor = "yes" if age < 18 else "no"
    elif profile.get("adult") is True or any(re.search(p, text) for p in ADULT_CUES):
        s.minor = "no"
    elif any(re.search(p, text) for p in MINOR_CUES):
        s.minor = "yes"

    # Life stage: explicit cues or the profile only. Never inferred from age.
    s.life_stage = profile.get("life_stage")
    if s.life_stage:
        s.life_stage_source = "profile"
    else:
        for stage, pats in STAGE_CUES.items():
            m = next((m for m in (re.search(p, text) for p in pats) if m), None)
            if m:
                s.life_stage, s.life_stage_cue = stage, m.group(0).strip()
                s.life_stage_source = "stated" if any(re.search(p, text) for p in STATED_STAGE_CUES) else "inferred"
                break

    s.other_at_risk = _word(text, OTHER_AT_RISK)
    s.self_harm = _word(text, SELF_HARM) and not s.other_at_risk
    s.danger = _word(text, DANGER) or any(c in text for c in ("stalk", "harass", "abus"))
    risk, s.purging = eating_risk(text)
    s.protective = ["eating"] if risk else []
    s.distress = s.self_harm or _word(text, DISTRESS) or bool(profile.get("distress")) or bool(s.protective)
    s.months_since_loss = months_since_loss(text)

    # A parent named only as an owner ("my father's property") is not shown as holding power.
    holders = [p for p in s.people if p in POWER_HOLDERS or
               (p in PARENTS and s.treat_as_minor and re.search(rf"\b{p}\b(?!['’]s\b)", text))]
    s.constraints = {
        "power_imbalance": holders,
        "dependency": [c.strip() for c in DEPENDENCY if c in text],
        "money": sorted({c.strip() for c in MONEY if c in text}),
        "urgency": [c for c in URGENCY if c in text],
        "irreversible": sorted({c for c in IRREVERSIBLE if re.search(rf"\b{re.escape(c)}", text)}),
    }
    s.dilemma = first_question(raw)
    return s
