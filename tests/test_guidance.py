"""Tests for the gate follow-up and the guidance fixes (STATUS.md must-fix 1-3).
Run: python tests/test_guidance.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import engine.gate as gate_mod  # noqa: E402
from engine.core import answer, load_library, render  # noqa: E402

lib = load_library()
real_check = gate_mod.check
Q = "Should I forgive my brother who cheated me in business?"


def with_check(fake, fn):
    gate_mod.check = fake
    try:
        return fn()
    finally:
        gate_mod.check = real_check


def test_failing_answer_is_replaced_by_a_checked_alternative():
    first = answer(Q, gate=False)["recommendation"]["principle"]
    fake = lambda a, l, e=None: ["test failure"] if (a["recommendation"] or {}).get("principle") == first else real_check(a, l, e)
    a = with_check(fake, lambda: answer(Q))
    assert a.get("regenerated") and a["recommendation"]["principle"] != first
    assert a["gate_log"][0] == {"principle": first, "failures": ["test failure"]}
    assert all(e["failures"] for e in a["gate_log"][:-1]) and a["gate_log"][-1]["failures"] == []


def test_nothing_passes_asks_a_clarifying_question_if_one_exists():
    text = "Should I take the job?"
    fake = lambda a, l, e=None: [] if a.get("clarify") else ["test failure"]
    a = with_check(fake, lambda: answer(text))
    if answer(text, gate=False)["clarifying_questions"]:
        assert a.get("clarify") and not a["sources"] and "question" in a["recommendation"]["text"]
    else:
        assert a.get("withheld")


def reject_all_but_withheld(a, l, e=None):
    """Every candidate fails; the withheld fallback is judged by the real gate."""
    return real_check(a, l, e) if a.get("withheld") else ["test failure"]


def test_nothing_passes_withholds_but_keeps_safety():
    text = "I'm 15 and I skip meals every day so I can get skinny."
    a = with_check(reject_all_but_withheld, lambda: answer(text))
    assert a.get("withheld") and not a["sources"]
    assert a["safety"] and a["protective"], "safety and protective guidance must survive withholding"


def test_teen_restricting_food_gets_trusted_adult_and_doctor():
    for text in ["I'm 16 and I've stopped eating properly because I want to be thinner. My friends say I look great.",
                 "i've been making myself throw up after dinner. i'm 14. please don't tell me to tell my mum",
                 "I'm 15 and I skip meals every day so I can get skinny. Nobody has noticed."]:
        a = answer(text)
        t = render(a).lower()
        assert a["protective"] and "trusted adult" in t and "doctor" in t, text
        assert a["recommendation"]["principle"] in gate_mod.PROTECTIVE_PRINCIPLES["eating"], text
        assert a["recommendation"]["principle"] != "honour-the-grief-first", text


def test_adult_restricting_food_gets_a_doctor_not_a_trusted_adult():
    t = render(answer("I'm 32 and I barely eat because I hate my body.")).lower()
    assert "doctor" in t and "trusted adult" not in t


def test_abuse_overrides_and_supports_getting_away():
    a = answer("I'm 15. My stepdad controls what I eat and hits me if I eat too much.")
    assert a["safety"]["level"] == "danger" and "1098" in render(a)


def test_no_inferred_fact_is_put_in_the_persons_mouth():
    a = answer("My husband died two years ago and I've met someone kind. My in-laws say remarrying would dishonour his memory.")
    t = render(a)
    assert "you describe yourself" not in t and "inferred" in t
    assert a["recommendation"]["principle"] != "honour-the-grief-first"


def test_gate_catches_words_the_person_did_not_write():
    a = answer(Q, gate=False)
    a["recommendation"]["why_it_fits_you"] = "For your situation (you said 'I am a monk')."
    assert any("did not write" in f for f in real_check(a, lib))


def test_changed_circumstances_change_the_recommendation():
    base = answer("My husband died two years ago and I've met someone kind. My in-laws say remarrying would dishonour his memory.")
    recent = answer("My wife died three months ago. A woman from my office wants to marry me and my family says I should decide quickly.")
    threat = answer("My husband died last year and my brother-in-law says he will hurt me if I remarry.")
    assert "recent" in recent["recommendation"]["application"].lower()
    assert threat["safety"]["level"] == "danger" and not base["safety"]


def test_suffering_is_never_called_deserved():
    for text in ["Why do bad things happen to good people?", "My aunt says I was born deaf because of karma from a past life. Is that true?"]:
        a = answer(text)
        assert "deserve" not in render(a).lower()
        assert a["recommendation"]["principle"] not in ("fate-decides", "nature-and-the-inner-controller")


def test_audit_cue_matches_audits_not_auditorium():
    from engine.frames import detect_frames
    assert "witness_wrong" not in detect_frames("I am anxious about giving a speech in the auditorium tomorrow.")
    for t in ["My manager asked me to change the numbers before the audit.", "The auditors are coming and I know of fraud."]:
        assert "witness_wrong" in detect_frames(t)


def test_cycle10_frames_fire_on_their_cues_and_not_on_nearby_text():
    from engine.frames import detect_frames
    assert "credit_taken" in detect_frames("My colleague took credit for my project.")
    assert "credit_taken" not in detect_frames("I gave my colleague credit for the project.")
    assert "identity_loss" in detect_frames("I don't know who I am without my job.")
    assert "prepare_for_death" in detect_frames("I'm 70 and want to prepare for death peacefully.")
    assert "prepare_for_death" not in detect_frames("I want to prepare for my exam.")
    assert "identity_loss" not in detect_frames("My identity was stolen and the bank wants documents.")
    assert "prepare_for_death" not in detect_frames("I loved my last years at school.")


def test_withheld_answer_passes_the_real_gate():
    for text in [Q, "I'm 15 and I skip meals every day so I can get skinny.", "I'm 15. My stepdad hits me when he drinks."]:
        a = with_check(reject_all_but_withheld, lambda: answer(text))
        assert a.get("withheld") and a["final_gate_failures"] == [] and a["displayable"], text  # rechecked, passed
        assert real_check(a, lib) == [], (text, real_check(a, lib))   # and passes the real gate


def test_final_fallback_fails_closed_when_the_active_gate_still_rejects():
    for text in [Q, "I'm 15 and I skip meals every day so I can get skinny.", "I'm 15. My stepdad hits me when he drinks."]:
        def run():
            a = answer(text)
            return a, gate_mod.check(a, lib)   # the active check, as answer() used it
        a, active = with_check(lambda a, l, e=None: ["test failure"], run)
        assert a["blocked"] and a["displayable"] is False and a["final_gate_failures"] == ["test failure"], text
        assert not a["recommendation"] and not a["sources"] and not a["challenge"] and not a["example"], text
        assert not a["protective"] and not a["next_step"], text
        t = render(a)
        assert "not showing one" in t and "Recommendation" not in t and "Source text" not in t, text
        if a["safety"]:  # the library's own help lines survive
            assert a["safety"]["help"] and a["safety"]["help"][0]["number"] in t, text
        assert active, "this test must exercise an answer the active gate rejects"
    # Invariant: an answer marked displayable passes the active check.
    for fake in (lambda a, l, e=None: ["x"], reject_all_but_withheld, real_check):
        for text in [Q, "I'm 15 and I skip meals every day so I can get skinny."]:
            a = with_check(fake, lambda: answer(text))
            if a["displayable"]:
                assert with_check(fake, lambda: gate_mod.check(a, lib)) == [], text


def test_every_replacement_is_checked_before_one_is_accepted():
    raw_ = answer(Q, gate=False)
    first = raw_["recommendation"]["principle"]
    rejected = [first] + [c["id"] for c in sorted((c for c in raw_["shortlist"] if c["id"] != first),
                                                  key=lambda c: (not c["frame_supported"], -c["score"]))[:2]]
    fake = lambda a, l, e=None: ["test failure"] if (a["recommendation"] or {}).get("principle") in rejected else real_check(a, l, e)
    a = with_check(fake, lambda: answer(Q))
    assert [g["principle"] for g in a["gate_log"][:3]] == rejected
    assert all(g["failures"] for g in a["gate_log"][:3]) and a["recommendation"]["principle"] not in rejected


def test_unknown_age_is_protected_by_the_gate():
    a = answer("Should I forgive my brother who cheated me in business?", gate=False)
    assert a["understanding"]["minor"] == "unknown"
    a["recommendation"]["principle"] = "full-renunciation-path"
    assert any("restricted principle" in f for f in real_check(a, lib))


def test_eating_risk_is_found_by_meaning_not_exact_phrases():
    from engine.understand import understand
    for t in ["I force myself to vomit after meals.", "I have barely eaten for several days to lose weight.",
              "i only have 600 calories a day and count every calorie so i stay thin", "I think I have an eating disorder."]:
        assert understand(t).protective == ["eating"], t
    for t in ["I stopped eating lunch at my desk because I eat with my colleagues now.",
              "I skip breakfast because I'm never hungry in the morning.", "I'm fasting for Navratri this week.",
              "I've been throwing up because I have the flu."]:
        assert understand(t).protective == [], t
    for t in ["I stopped eating lunch at my desk because I eat with my colleagues now.",
              "I skip breakfast because I'm never hungry in the morning.", "I'm fasting for Navratri this week."]:
        a = answer(t)
        u = a["understanding"]
        assert not u["distress"] and not u["protective"], t
        assert a["safety"] is None and a["protective"] is None and a["displayable"], t
        assert "help" not in render(a).split("Recommendation")[0].lower(), t
    for t in ["Since my mother died I have stopped eating and I cry every day.", "I've stopped eating. I don't know why."]:
        u = understand(t)
        assert u.distress, t
    a = answer("i'm 14 and i make myself throw up after dinner")
    t = render(a).lower()
    assert "as soon as you can" in t and "today or tomorrow" in t


def test_paired_circumstances_change_the_recommendation():
    top = lambda t: answer(t)["recommendation"]["principle"]
    base = top("My husband died two years ago and I've met someone kind. My in-laws say remarrying would dishonour his memory.")
    recent = top("My wife died three months ago. A woman from my office wants to marry me and my family says I should decide quickly.")
    other = top("My mother was widowed five years ago and now wants to remarry. It feels like a betrayal of my father. Should I object?")
    assert recent != "dharmic-desire-is-legitimate" and other != "dharmic-desire-is-legitimate"
    assert len({base, recent, other}) >= 2
    dep = answer("My husband died four years ago. I live with my in-laws and depend on them for money, and they say they will throw me out if I remarry.")
    assert "afford" in dep["recommendation"]["application"]
    abstract = top("Why do bad things happen to good people?")
    personal = top("Why did my mother have to die of cancer? She was the kindest person I knew.")
    assert abstract != personal and personal == "honour-the-grief-first"


def test_karma_question_is_answered_directly():
    a = answer("My aunt says I was born deaf because of karma from a past life. Is that true?")
    app = a["recommendation"]["application"].lower()
    assert "no one can know" in app and "punishment you earned" in app
    assert "karma_blame" in a["recommendation"]["basis_frames"]


def test_no_invented_motives_or_power():
    for text in ["My husband died two years ago and I've met someone kind. My in-laws say remarrying would dishonour his memory.",
                 "My mother was widowed five years ago and now wants to remarry. It feels like a betrayal of my father. Should I object?",
                 "Why did my mother have to die of cancer? She was the kindest person I knew."]:
        t = render(answer(text)).lower()
        assert "has power over" not in t and "have power over" not in t, text
        assert "comes from their own grief" not in t and "your sense of betrayal is" not in t, text
    t = render(answer("Why did my mother have to die of cancer? She was the kindest person I knew.")).lower()
    assert "your mother, think about what they need" not in t


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
            print("ok", n)
