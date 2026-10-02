"""Problem frames: what kind of situation this is, and which principles are
candidates for it. A frame is detected from explicit cues in the person's
words; its principles get a strong, ordered boost before word matching.

Frames are editorial judgements (draft), kept here so reviewers can read and
change them in one place.
"""

import re

# frame id: (regex cues, principles in order of usual fit)
FRAMES = {
    "decision": (
        [r"\bshould i\b", r"\bwhether (?:to|i)\b", r"\bcan't decide\b", r"\bcannot decide\b", r"\bchoose between\b",
         r"\bor should\b", r"\btorn between\b", r"\bdilemma\b", r"\bwhat (?:do|should) i do\b", r"\bneeds me but\b",
         r"\bmy own life\b", r"\bwant me to choose\b"],
        ["name-the-confusion", "reflect-then-choose", "weigh-consequences-and-capacity", "clear-understanding",
         "understand-before-acting", "own-path-over-imitation", "choose-again-after-delusion"]),
    "family_care": (
        [r"\b(?:father|mother|dad|mom|mum|parents?|grandmother|grandfather)\b[^.?!]{0,40}\b(?:ill|sick|hospital|old|ageing|aging|dementia|care)\b",
         r"\blook after\b", r"\bcare(?:giver| for)\b", r"\bsick (?:father|mother|parent)\b"],
        ["name-the-confusion", "work-for-the-good-of-all", "reciprocity", "reflect-then-choose", "keep-contributing"]),
    "study_focus": (
        [r"\bexams?\b", r"\bstudy(?:ing)?\b", r"\bhomework\b", r"\bdistract", r"\bscrolling\b", r"\bfocus\b",
         r"\bphone\b", r"\bsocial media\b", r"\bgaming\b"],
        ["chariot-of-the-mind", "guard-the-senses", "pleasant-versus-good", "single-pointed-resolve",
         "steady-practice", "hard-at-first-sweet-later"]),
    "outcome_anxiety": (
        [r"\bresults?\b", r"\binterview\b", r"\bwaiting to hear\b", r"\bwhat if i fail\b", r"\bperformance\b",
         r"\bexam anxiety\b", r"\bnervous about\b", r"\bpressure to (?:get|score|perform)\b", r"\bmarks\b", r"\bgrades?\b"],
        ["work-not-results", "evenness-in-success-and-failure", "steadiness-under-pressure", "giving-up-fruit-brings-peace"]),
    "grief": (
        [r"\bdied\b", r"\bpassed away\b", r"\bdeath of\b", r"\bfuneral\b", r"\bgrie(?:f|ving)\b", r"\bmiscarriage\b",
         r"\blost my (?:mother|father|mom|dad|wife|husband|son|daughter|friend|brother|sister|baby|grandmother|grandfather)\b"],
        ["honour-the-grief-first", "ask-for-help-when-lost", "sorrow-ends-in-stillness", "self-is-not-destroyed",
         "the-witness", "every-reason-to-seek-is-valid", "grief-for-the-inevitable"]),
    "anger": (
        [r"\bangry\b", r"\banger\b", r"\bfurious\b", r"\brage\b", r"\blost my temper\b", r"\byell(?:ed|ing)?\b",
         r"\bshout(?:ed|ing)?\b", r"\brevenge\b"],
        ["desire-anger-chain", "withstand-the-surge", "three-gates", "speech-without-harm", "calm-before-clarity"]),
    "hurt_by_someone": (
        [r"\bbetray", r"\bforgive\b", r"\bhurt me\b", r"\blied to me\b", r"\bcheated on\b", r"\bresent", r"\bgrudge\b"],
        ["forgiveness-as-strength", "no-hatred", "feel-others-pain-as-your-own", "same-regard-for-all"]),
    "i_hurt_someone": (
        [r"\bi (?:hurt|lied|cheated|yelled|shouted|betrayed|stole|took money)\b", r"\bmy fault\b", r"\bapolog",
         r"\bi regret\b", r"\bguilty (?:about|for) (?:what i|lying|cheating|stealing|hurting)\b"],
        ["apologise-sincerely", "even-the-wrongdoer-can-cross", "knowledge-purifies", "honesty"]),
    "envy": (
        [r"\bjealous\b", r"\benv(?:y|ious)\b", r"\bcompar(?:e|ing|ison)\b", r"\beveryone else\b", r"\bbetter than me\b",
         r"\binfluencers?\b"],
        ["envy-and-comparison", "more-than-body-and-roles", "delight-in-the-welfare-of-all", "do-not-covet",
         "content-with-what-comes"]),
    "pride_credit": (
        [r"\bproud\b", r"\barrogan", r"\brecognition\b", r"\bi earned it\b", r"\bpromoted\b", r"\bsuccess went\b"],
        ["credit-is-not-yours-alone", "humility", "praise-and-blame-alike", "no-recognition-seeking"]),
    "failure": (
        [r"\bfailed\b", r"\bfailure\b", r"\brejected\b", r"\bfired\b", r"\blaid off\b", r"\bdidn't get\b",
         r"\bdid not get\b", r"\bmess(?:ed|ing)? (?:everything |it all |things )?up\b", r"\brelapse"],
        ["effort-never-wasted", "voice-your-fear-of-failing", "evenness-in-success-and-failure", "graded-practice",
         "self-as-friend"]),
    "motivation": (
        [r"\bprocrastinat", r"\bunmotivated\b", r"\bno motivation\b", r"\blazy\b", r"\bcan't start\b",
         r"\bcannot start\b", r"\bstuck\b", r"\bkeep putting off\b", r"\bgive up\b"],
        ["procrastination-as-a-state", "graded-practice", "hard-at-first-sweet-later", "the-wish-carries-you",
         "steady-practice", "small-practice-protects"]),
    "money": (
        [r"\bmoney\b", r"\bsalary\b", r"\brich\b", r"\bwealth\b", r"\bdebt\b", r"\binheritance\b", r"\bbonus\b",
         r"\bgreed", r"\bpay\b", r"\bprofit\b"],
        ["wealth-never-satisfies", "lasting-versus-passing-treasure", "gold-and-stone-alike", "trust-alongside-effort",
         "give-without-expecting-return"]),
    "temptation": (
        [r"\baddict", r"\bcraving\b", r"\bcan't stop\b", r"\bcannot stop\b", r"\bporn\b", r"\balcohol\b",
         r"\bdrinking\b", r"\bgambl", r"\btempt", r"\bbinge\b", r"\bsmok"],
        ["withstand-the-surge", "chariot-of-the-mind", "suppression-backfires", "engage-without-attraction-or-aversion",
         "guard-your-gains", "guard-the-senses"]),
    "purpose": (
        [r"\bpurpose\b", r"\bmeaning(?:less)?\b", r"\bempty\b", r"\bpoint of\b", r"\bpointless\b", r"\bwhat am i doing\b",
         r"\bwhat to do with my life\b", r"\bunfulfilled\b", r"\bcalling\b"],
        ["purpose-beyond-pleasure", "act-as-offering", "know-it-in-this-life", "turn-inward", "skill-in-action",
         "keep-contributing"]),
    "ageing": (
        [r"\bretire", r"\bgetting old", r"\bold age\b", r"\bageing\b", r"\baging\b", r"\bempty nest\b",
         r"\bchildren (?:have )?(?:left|moved out)\b"],
        ["keep-contributing", "more-than-body-and-roles", "knowledge-handed-down", "see-the-pain-of-ageing-clearly",
         "impermanence"]),
    "career": (
        [r"\bquit\b", r"\bresign", r"\bleave my job\b", r"\bjob offer\b", r"\bchange (?:jobs?|careers?)\b",
         r"\bdrop out\b", r"\bswitch (?:my )?(?:major|course|field)\b"],
        ["own-path-over-imitation", "dont-quit-because-its-hard", "your-nature-shapes-you", "weigh-consequences-and-capacity",
         "skill-in-action"]),
    "renounce_wish": (
        [r"\brenounc", r"\bmonk\b", r"\bashram\b", r"\bsannyas", r"\bleave (?:everything|it all|the world)\b",
         r"\bspiritual life\b", r"\bgive up everything\b"],
        ["renounce-selfishness-not-the-world", "two-paths-both-lead", "hold-both-together", "full-renunciation-path"]),
    "witness_wrong": (
        [r"\bcorrupt", r"\bfraud\b", r"\bbribe", r"\bunethical\b", r"\bcover(?:ing)? up\b", r"\bwhistle", r"\breport (?:it|him|her|them)\b",
         r"\bbully(?:ing)?\b"],
        ["duty-of-protection", "honesty", "clear-understanding", "fearlessness"]),
    "peer_pressure": (
        [r"\bpeer pressure\b", r"\beveryone (?:else )?is doing\b", r"\bfit in\b", r"\bmy friends (?:want|say|think)\b",
         r"\bpopular\b"],
        ["independent-of-the-crowd", "own-path-over-imitation", "pleasant-versus-good"]),
    "fear_courage": (
        [r"\bscared\b", r"\bafraid\b", r"\bterrified\b", r"\bfear\b", r"\bpublic speaking\b", r"\bpanic\b", r"\bnervous\b"],
        ["fearlessness", "knowledge-dissolves-fear", "steadiness-under-pressure", "calm-before-clarity",
         "small-practice-protects"]),
    "honesty": (
        [r"\blie\b", r"\blying\b", r"\btell (?:him|her|them) the truth\b", r"\bhonest", r"\bsecret\b", r"\bconfess"],
        ["honesty", "speech-without-harm", "apologise-sincerely"]),
    "parent_child": (
        [r"\bmy parents (?:want|don't|won't|expect|disapprove)\b", r"\bmy (?:son|daughter) (?:wants|won't|doesn't)\b",
         r"\bour (?:son|daughter)\b", r"\bdisapprove", r"\barranged marriage\b", r"\binter-?caste\b", r"\binterfaith\b"],
        ["meet-people-where-they-are", "seek-a-parents-peace", "respect-different-paths", "loving-without-clinging",
         "reflect-then-choose"]),
    "loneliness": (
        [r"\blonely\b", r"\bloneliness\b", r"\bisolated\b", r"\bno friends\b", r"\bdon't know anyone\b",
         r"\bdo not know anyone\b", r"\ball alone\b"],
        ["nourish-one-another", "friend-of-all-beings", "ask-for-help-when-lost", "act-as-offering", "keep-contributing"]),
    "impostor": (
        [r"\bimpostor\b", r"\bimposter\b", r"\bnot (?:that |really )?good enough\b", r"\bfind out i'?m\b",
         r"\bdon't deserve\b", r"\bdo not deserve\b", r"\bi'?m a fraud\b"],
        ["not-the-sole-doer", "credit-is-not-yours-alone", "praise-and-blame-alike", "knowledge-dissolves-fear",
         "every-reason-to-seek-is-valid"]),
    "burnout": (
        [r"\bburn(?:t|ed) out\b", r"\bburnout\b", r"\bexhausted\b", r"\boverwork", r"\b\d{2,3} hours a week\b",
         r"\bno rest\b", r"\btaking leave\b", r"\bsleep (?:only )?(?:\d|four|three|two) hours\b"],
        ["moderation-in-living", "no-self-torture", "name-the-confusion", "ask-for-help-when-lost"]),
    "insulted": (
        [r"\binsult", r"\bhumiliat", r"\bmock", r"\blaugh(?:s|ed)? at me\b", r"\bbelittl", r"\bput(?:s)? me down\b"],
        ["honour-and-dishonour-alike", "praise-and-blame-alike", "speech-without-harm", "calm-before-clarity"]),
    "fatalism": (
        [r"\bfate\b", r"\bdestiny\b", r"\bwhy (?:even )?(?:try|bother)\b", r"\bno point (?:in )?trying\b",
         r"\bit's all written\b", r"\bkarma (?:is|will)\b"],
        ["effort-never-wasted", "graded-practice", "small-practice-protects", "the-wish-carries-you",
         "every-reason-to-seek-is-valid"]),
    "death_question": (
        [r"\bafter (?:we|i|you|people) die\b", r"\bwhen we die\b", r"\bafterlife\b", r"\blife after death\b",
         r"\bscared of (?:death|dying)\b", r"\bafraid of (?:death|dying)\b", r"\bprepare for death\b"],
        ["self-is-not-destroyed", "persist-in-the-real-question", "the-real-does-not-perish", "knowledge-dissolves-fear",
         "humility-before-the-unknown", "mortality-is-certain"]),
    "spiritual_doubt": (
        [r"\bsatsang\b", r"\bmore devoted\b", r"\bspiritual enough\b", r"\bnot religious enough\b", r"\bbad at (?:prayer|praying|meditation|meditating)\b",
         r"\bfeel like a fake\b", r"\bmy (?:prayers?|puja|sadhana)\b"],
        ["every-reason-to-seek-is-valid", "small-offerings-with-love", "graded-practice", "the-wish-carries-you", "steady-practice"]),
    "coercive_authority": (
        [r"\b(?:guru|teacher|leader|pastor|swami)\b[^.?!]{0,60}\b(?:demands?|obey|cut off|without question|controls?)\b",
         r"\bdoubt is a sin\b", r"\bobey (?:him|her|them) without\b"],
        ["reflect-then-choose", "clear-understanding", "weigh-consequences-and-capacity", "renounce-selfishness-not-the-world",
         "hold-both-together"]),
    "friendship_hurt": (
        [r"\bignor(?:es|ing|ed) me\b", r"\bleft me out\b", r"\bexclud", r"\bghost(?:ed|ing)\b", r"\bsitting with other people\b",
         r"\bdoesn't talk to me\b", r"\bstopped talking to me\b"],
        ["speech-without-harm", "feel-others-pain-as-your-own", "honour-the-grief-first", "nourish-one-another", "ask-for-help-when-lost"]),
    "controlling": (
        [r"\btoo controlling\b", r"\bi'?m controlling\b", r"\bpossessive\b", r"\bcheck (?:his|her|their) phone\b"],
        ["let-go-of-mine", "feel-others-pain-as-your-own", "loving-without-clinging", "humility"]),
    "lending": (
        [r"\bborrow", r"\blend(?:ing)?\b", r"\bpay(?:s)? (?:it |me )?back\b", r"\bowes me\b"],
        ["reciprocity", "give-without-expecting-return", "speech-without-harm", "honesty"]),
    "revenge": (
        [r"\brevenge\b", r"\bget back at\b", r"\bmake (?:him|her|them) pay\b", r"\bpay for what\b"],
        ["three-gates", "desire-anger-chain", "non-violence", "withstand-the-surge", "no-hatred"]),
    "risky_choice": (
        [r"\ball my savings\b", r"\binvest", r"\bcrypto\b", r"\bdrop out\b", r"\bstart a (?:business|bakery|company|startup)\b",
         r"\btake a (?:big )?loan\b", r"\bquit my (?:stable )?\w* ?job\b"],
        ["weigh-consequences-and-capacity", "quick-success-passes", "independent-of-the-crowd", "own-path-over-imitation",
         "pleasant-versus-good"]),
    "difficult_conversation": (
        [r"\bhow (?:do|can|should) i (?:talk|tell|say|bring (?:it|this) up)\b", r"\bhow to tell\b", r"\bshould i say something\b",
         r"\btalk to (?:him|her|them) about\b"],
        ["speech-without-harm", "honesty", "meet-people-where-they-are", "feel-others-pain-as-your-own"]),
    "practice": (
        [r"\bmeditat", r"\bmy mind wanders\b", r"\bmind keeps wandering\b", r"\bcan't concentrate\b", r"\bjapa\b",
         r"\bmorning practice\b"],
        ["steady-practice", "restless-mind-can-be-trained", "graded-practice", "inward-meditation", "small-practice-protects"]),
    "family_shame": (
        [r"\bin jail\b", r"\bin prison\b", r"\barrested\b", r"\bconvicted\b", r"\bfamily (?:is )?ashamed\b",
         r"\bdisgrace(?:d)? (?:the|our) family\b"],
        ["even-the-wrongdoer-can-cross", "same-regard-for-all", "no-hatred", "reflect-then-choose", "name-the-confusion"]),
    "danger": (
        [],  # set by understand(): danger cues
        # Lead with the person's own choice and courage; avoid verses of self-reproach.
        ["reflect-then-choose", "fearlessness", "ask-for-help-when-lost", "duty-of-protection"]),
}


def detect_frames(text, danger=False):
    t = text.lower().replace("’", "'")
    found = []
    for fid, (cues, _) in FRAMES.items():
        if any(re.search(c, t) for c in cues):
            found.append(fid)
    if danger:
        found = ["danger"] + [f for f in found if f not in ("danger",)]
    return found


# Frames whose cues signal the person's main question; their candidates outrank
# incidental topics mentioned along the way (e.g. 'exam' inside a scheduling clash).
PRIMARY = {"decision": 1.4, "danger": 2.0, "fatalism": 1.4, "burnout": 1.3, "death_question": 1.3,
           "impostor": 1.2, "loneliness": 1.2, "renounce_wish": 1.3, "witness_wrong": 1.3, "spiritual_doubt": 1.4,
           "coercive_authority": 2.0, "friendship_hurt": 1.3, "controlling": 1.4, "lending": 1.3,
           "i_hurt_someone": 1.3, "revenge": 1.5, "risky_choice": 1.5, "difficult_conversation": 1.3,
           "parent_child": 1.3}
# Principles that must not be offered when a frame is present (they would serve the wrong party).
FRAME_EXCLUDE = {"coercive_authority": {"learn-from-those-who-know", "loving-without-clinging", "full-renunciation-path",
                                        "faith-and-doubt", "ego-that-will-not-listen"}}


def frame_boosts(frames):
    """Principle id -> boost. Earlier principles in a frame get more weight;
    a principle named by several frames accumulates."""
    boost = {}
    for fid in frames:
        w = PRIMARY.get(fid, 1.0)
        for i, pid in enumerate(FRAMES[fid][1]):
            boost[pid] = boost.get(pid, 0) + w * max(6.0 - i, 2.0)
    return boost
