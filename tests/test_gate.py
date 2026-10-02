"""Unit tests for engine/gate.py. Run: python tests/test_gate.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.core import answer, load_library  # noqa: E402
from engine.gate import check  # noqa: E402

lib = load_library()
Q = "Should I forgive my brother who cheated me in business?"


def raw(text, profile=None):
    return answer(text, profile, gate=False)


def test_altered_quote_fails():
    a = raw(Q)
    assert a["sources"], "need a quoted source"
    a["sources"][0]["english"] += " (altered)"
    assert any("quote not in library" in f for f in check(a, lib))


def test_missing_recommendation_and_step_fail():
    a = raw(Q)
    a["recommendation"], a["next_step"] = None, None
    fails = check(a, lib)
    assert "no recommendation" in fails and "no next step" in fails


def test_crisis_needs_help_resources():
    a = raw("I want to end my life")
    assert a["safety"]["level"] == "crisis" and not check(a, lib)
    a["safety"]["help"] = []
    assert any("no help resources" in f for f in check(a, lib))


def test_restricted_principle_for_distress_fails():
    a = raw(Q)
    a["understanding"]["distress"] = True
    a["safety"] = a["safety"] or {"level": "support", "help": [1]}
    a["recommendation"]["principle"] = "full-renunciation-path"
    assert any("restricted principle" in f for f in check(a, lib))


def test_production_call_without_expect_is_gated():
    a = answer(Q)
    assert "gate_failures" in a
    if a["gate_failures"]:
        assert a["withheld"] and not a["sources"]


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
            print("ok", n)
