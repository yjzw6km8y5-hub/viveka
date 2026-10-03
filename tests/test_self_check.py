"""Tests that scripts/self_check.py fails closed (Codex review 202610022233, finding 1).
Run: python tests/test_self_check.py"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import self_check  # noqa: E402

GOOD = [{"id": "X1", "notes": [], "gate": []}]


def in_temp_dir(fn):
    real = self_check.SELFCHECK
    with tempfile.TemporaryDirectory() as d:
        self_check.SELFCHECK = Path(d)
        try:
            fn(Path(d))
        finally:
            self_check.SELFCHECK = real


def stale(d):
    (d / "paired.json").write_text(json.dumps(GOOD), encoding="utf-8")
    (d / "paired_summary.md").write_text("stale", encoding="utf-8")


def test_failed_command_with_stale_passing_json_is_a_problem():
    def check(d):
        stale(d)
        results, problems = self_check.run_set("paired", lambda args: (1, "Traceback\nboom"))
        assert results is None and problems and "failed to run" in problems[0]
        assert not (d / "paired.json").exists() and not (d / "paired_summary.md").exists()
    in_temp_dir(check)


def test_successful_command_that_wrote_nothing_is_a_problem():
    def check(d):
        stale(d)
        results, problems = self_check.run_set("paired", lambda args: (0, ""))
        assert results is None and problems and "wrote no results" in problems[0]
    in_temp_dir(check)


def test_unreadable_or_empty_output_is_a_problem():
    for body in ["not json", "[]", '[{"id": "X1"}]']:
        def check(d, body=body):
            def runner(args):
                (d / "paired.json").write_text(body, encoding="utf-8")
                return 0, ""
            results, problems = self_check.run_set("paired", runner)
            assert results is None and problems and "unreadable" in problems[0]
        in_temp_dir(check)


def test_fresh_good_output_passes():
    def check(d):
        def runner(args):
            (d / "paired.json").write_text(json.dumps(GOOD), encoding="utf-8")
            return 0, ""
        assert self_check.run_set("paired", runner) == (GOOD, [])
    in_temp_dir(check)


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
            print("ok", n)
