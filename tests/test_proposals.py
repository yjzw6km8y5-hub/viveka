"""Regression tests for exact-version proposal approval.

Run: python tests/test_proposals.py
"""
import argparse
import importlib.util
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "proposals.py"
SPEC = importlib.util.spec_from_file_location("viveka_proposals", SCRIPT)
proposals = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proposals)


@contextmanager
def isolated_proposals():
    """Point proposals.py at a disposable project and review desk."""
    names = ("ROOT", "DESK", "PROP", "PENDING", "APPROVED", "DECLINED", "SOURCES",
             "STATE", "APPROVALS", "CYCLES")
    old = {name: getattr(proposals, name) for name in names}
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        root, desk = base / "repo", base / "desk"
        root.mkdir()
        desk.mkdir()
        (root / "STATUS.md").write_text(
            "# Status\n\n## Must-fix (from approved reviews; do these first)\n\n## Next step\n",
            encoding="utf-8",
        )
        (root / "CONTEXT.md").write_text("# Context\n", encoding="utf-8")
        proposals.ROOT, proposals.DESK = root, desk
        proposals.PROP = root / "proposals"
        proposals.PENDING, proposals.APPROVED, proposals.DECLINED, proposals.SOURCES = (
            proposals.PROP / name for name in ("pending", "approved", "declined", "sources")
        )
        proposals.STATE = proposals.PROP / "state.json"
        proposals.APPROVALS = proposals.PROP / "APPROVALS.md"
        proposals.CYCLES = root / "logs" / "cycles.csv"
        try:
            yield root, desk
        finally:
            for name, value in old.items():
                setattr(proposals, name, value)


def import_reviews():
    proposals.cmd_import(argparse.Namespace(baseline=None))


def approve_only(*ids):
    proposals.cmd_approve(argparse.Namespace(only=list(ids), except_=[], push=False))


def test_approval_archives_the_listed_version_not_a_newer_file():
    with isolated_proposals() as (root, desk):
        review = desk / "observer.md"
        v1 = "# Review\n\n## Must-fix\n\n### First finding\nUse version one.\n"
        v2 = "# Review\n\n## Must-fix\n\n### Changed finding\nUse version two.\n"
        review.write_text(v1, encoding="utf-8")
        import_reviews()
        first = proposals.pending()[0][0]

        review.write_text(v2, encoding="utf-8")
        os.utime(review, None)
        import_reviews()
        second = proposals.pending()[1][0]
        assert first["version"]["sha256"] != second["version"]["sha256"]

        state = proposals.load_state()
        state["last_listed"] = [first["id"], second["id"]]
        proposals.save_state(state)
        approve_only(first["id"])

        archived = (root / "reviews" / "observer.md").read_text(encoding="utf-8")
        assert v1 in archived
        assert "Use version two." not in archived
        assert [m["id"] for m, _, _ in proposals.pending()] == [second["id"]]


def test_approval_refuses_a_tampered_pending_item_before_changing_targets():
    with isolated_proposals() as (root, desk):
        review = desk / "observer.md"
        review.write_text(
            "# Review\n\n## Must-fix\n\n### Original finding\nKeep the original body.\n",
            encoding="utf-8",
        )
        import_reviews()
        meta, _, path = proposals.pending()[0]
        before = (root / "STATUS.md").read_text(encoding="utf-8")
        path.write_text(
            path.read_text(encoding="utf-8").replace("Keep the original body.", "Tampered body."),
            encoding="utf-8",
        )
        state = proposals.load_state()
        state["last_listed"] = [meta["id"]]
        proposals.save_state(state)

        try:
            approve_only(meta["id"])
        except SystemExit as exc:
            assert "pending item was edited" in str(exc)
        else:
            raise AssertionError("tampered proposal was approved")
        assert (root / "STATUS.md").read_text(encoding="utf-8") == before
        assert path.exists()


def test_synthetic_urgent_safety_test_is_not_imported_as_a_finding():
    with isolated_proposals() as (_, desk):
        (desk / "observer.md").write_text(
            "# Review\n\n## Must-fix\n\n### URGENT-SAFETY TEST\nSynthetic alert only.\n",
            encoding="utf-8",
        )
        import_reviews()
        assert proposals.pending() == []


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
