"""Owner-approval gate for outside input (AI Review Desk -> proposals/ -> instruction files).

Nothing from the AI Review Desk is written to STATUS.md, CONTEXT.md or reviews/ until
the owner approves it. Commands:

  python scripts/proposals.py import            new desk files -> proposals/pending/
  python scripts/proposals.py summary           plain-language list of pending proposals
  python scripts/proposals.py approve [--except 2 5] [--push]
                                                merge the proposals shown in the last summary
                                                (except those numbers, which are declined)
  python scripts/proposals.py restore 2         move a declined proposal back to pending

The desk folder defaults to '../AI Review Desk/Viveka' next to the repo; set
VIVEKA_REVIEW_DESK to override.
"""
import argparse, datetime, difflib, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESK = Path(os.environ.get("VIVEKA_REVIEW_DESK", ROOT.parent / "AI Review Desk" / "Viveka"))
PROP = ROOT / "proposals"
PENDING, APPROVED, DECLINED, SOURCES = (PROP / d for d in ("pending", "approved", "declined", "sources"))
STATE = PROP / "state.json"

TARGETS = {  # proposal kind -> (file, section heading)
    "must-fix": ("STATUS.md", "## Must-fix (from approved reviews; do these first)"),
    "should-fix": ("STATUS.md", "## Should-fix (from approved reviews)"),
    "idea": ("CONTEXT.md", "## Approved ideas from reviews"),
    "context": ("CONTEXT.md", "## Approved context updates"),
    "file": ("reviews/", None),
    "doc": ("repo root", None),
}
ROOT_DOCS = ("PROCESS.md", "PROJECT_BRIEF.md")  # shared documents that live at the repo root
KIND_WORDS = {"must-fix": "must fix", "should-fix": "should fix", "idea": "idea",
              "context": "context update", "file": "file to archive in reviews/",
              "doc": "shared document"}


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"next_id": 1, "imported": {}, "last_listed": []}


def save_state(st):
    PROP.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_proposal(st, kind, title, summary, body, source, extra=None):
    pid = st["next_id"]
    st["next_id"] += 1
    meta = {"id": pid, "kind": kind, "target": TARGETS[kind][0], "title": title, "summary": summary,
            "source": source, "imported": datetime.date.today().isoformat(), **(extra or {})}
    PENDING.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "proposal"
    path = PENDING / f"{pid:03d}-{slug}.md"
    path.write_text("```json\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n```\n\n" + body.strip() + "\n",
                    encoding="utf-8", newline="\n")
    return path


def read_proposal(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"```json\n(.*?)\n```\n\n(.*)", text, re.S)
    return json.loads(m.group(1)), m.group(2)


def first_sentence(text, limit=160):
    text = re.sub(r"\s+", " ", text).strip()
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    s = m.group(1) if m else text
    s = s[:1].upper() + s[1:]
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def split_review(text):
    """Observer review -> [(kind, title, body)] from its must-fix / should-fix / idea sections."""
    items, kind, title, buf = [], None, None, []

    def flush():
        if kind and (title or "".join(buf).strip()):
            body = "\n".join(buf).strip()
            items.append((kind, title or first_sentence(body, 80), body))

    for line in text.splitlines():
        h2 = re.match(r"##\s+(.+?)\s*$", line)
        h3 = re.match(r"###\s+(.+?)\s*$", line)
        if h2 and not line.startswith("###"):
            flush()
            name = h2.group(1).strip().lower()
            kind = {"must-fix": "must-fix", "must fix": "must-fix", "should-fix": "should-fix",
                    "should fix": "should-fix", "idea": "idea", "ideas": "idea"}.get(name)
            title, buf = None, []
        elif h3 and kind:
            flush()
            title, buf = h3.group(1).strip(), []
        elif kind:
            buf.append(line)
    flush()
    return items


def item_summary(body):
    m = re.search(r"Next action:\s*(.+)", body)
    return first_sentence(m.group(1) if m else body)


def cmd_import(args):
    if not DESK.is_dir():
        sys.exit(f"Review Desk folder not found ({DESK.name}); set VIVEKA_REVIEW_DESK.")
    st = load_state()
    made = []
    for f in sorted(DESK.iterdir()):
        if not f.is_file() or f.suffix.lower() not in (".md", ".txt"):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        digest = sha(text)
        if st["imported"].get(f.name) == digest:
            continue
        source = f"AI Review Desk/Viveka/{f.name}"
        if f.name in (args.baseline or []):  # already handled by the owner: only later changes are proposed
            SOURCES.mkdir(parents=True, exist_ok=True)
            (SOURCES / f.name).write_text(text, encoding="utf-8", newline="\n")
        elif "_observer_" in f.name or "review" in f.name.lower():
            snap = SOURCES / f.name
            SOURCES.mkdir(parents=True, exist_ok=True)
            snap.write_text(text, encoding="utf-8", newline="\n")
            items = split_review(text)
            for kind, title, body in items:
                made.append(write_proposal(st, kind, title, item_summary(body), body, source,
                                           {"review_file": f.name}))
            if not items:
                made.append(write_proposal(st, "file", f"Archive {f.name}", "No must-fix, should-fix or idea "
                                           "sections found; approving archives it in reviews/.", text, source,
                                           {"review_file": f.name}))
        elif f.name.upper().startswith("CONTEXT"):
            snap = SOURCES / f.name
            old = snap.read_text(encoding="utf-8").splitlines() if snap.exists() else []
            new = text.splitlines()
            added = [l[1:] for l in difflib.unified_diff(old, new, lineterm="", n=0)
                     if l.startswith("+") and not l.startswith("+++") and l[1:].strip()]
            SOURCES.mkdir(parents=True, exist_ok=True)
            snap.write_text(text, encoding="utf-8", newline="\n")
            if added:
                diff = "\n".join(difflib.unified_diff(old, new, f"previous {f.name}", f"new {f.name}", lineterm=""))
                body = "Lines to add to CONTEXT.md:\n\n" + "\n".join(added) + "\n\nFull change:\n\n```diff\n" + diff + "\n```"
                made.append(write_proposal(st, "context", f"Context update from {f.name}",
                                           f"{len(added)} new or changed lines from {f.name}, e.g. "
                                           f"\"{first_sentence(added[0].lstrip('-# '), 100)}\"", body, source))
        elif f.name in ROOT_DOCS:
            snap = SOURCES / f.name
            old = snap.read_text(encoding="utf-8").splitlines() if snap.exists() else []
            SOURCES.mkdir(parents=True, exist_ok=True)
            snap.write_text(text, encoding="utf-8", newline="\n")
            diff = "\n".join(difflib.unified_diff(old, text.splitlines(), f"previous {f.name}", f"new {f.name}", lineterm=""))
            made.append(write_proposal(st, "doc", f"{'Update' if old else 'Add'} {f.name}",
                                       f"{'Replace' if old else 'Add'} {f.name} at the repo root: \"{first_sentence(text.lstrip('# '), 100)}\"",
                                       text + "\n\nChange:\n\n```diff\n" + diff + "\n```", source, {"doc_file": f.name}))
        else:
            made.append(write_proposal(st, "file", f"Archive {f.name}", f"Unrecognised desk file; approving "
                                       "archives it in reviews/.", text, source, {"review_file": f.name}))
        st["imported"][f.name] = digest
    save_state(st)
    print(f"{len(made)} new proposal(s) imported." + "".join(f"\n  {p.name}" for p in made))


def pending():
    return sorted((read_proposal(p) + (p,) for p in PENDING.glob("*.md")), key=lambda t: t[0]["id"])


def cmd_summary(_):
    st = load_state()
    items = pending()
    st["last_listed"] = [m["id"] for m, _, _ in items]
    save_state(st)
    if not items:
        print("No pending proposals.")
        return
    print(f"{len(items)} pending proposal(s) from the AI Review Desk. Nothing has been merged yet.\n")
    for m, _, _ in items:
        print(f"{m['id']}. {m['title']} ({KIND_WORDS[m['kind']]}, would go into {m['target']}; from {m['source'].split('/')[-1]})")
        print(f"   {m['summary']}")
    print('\nReply "approve" to merge all of these, or "approve except 2" to decline some.')


def insert_under(path, heading, block):
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if heading in text:
        i = text.index(heading) + len(heading)
        nxt = re.search(r"\n## ", text[i:])
        j = i + nxt.start() if nxt else len(text)
        text = text[:j].rstrip("\n") + "\n" + block.rstrip() + "\n" + text[j:]
    else:
        # STATUS.md: must-fix sections lead, should-fix follow, then the rest. CONTEXT.md: append.
        lead = r"Must-fix" if "Must-fix" in heading else r"(?:Must-fix|Should-fix)"
        m = re.search(rf"\n## (?!{lead})", text) if path.name == "STATUS.md" else None
        sec = f"{heading}\n{block.rstrip()}\n"
        text = text[: m.start() + 1] + sec + "\n" + text[m.start() + 1:] if m else text.rstrip("\n") + "\n\n" + sec
    path.write_text(text, encoding="utf-8", newline="\n")


def cmd_approve(args):
    st = load_state()
    listed = set(st.get("last_listed", []))
    if not listed:
        sys.exit("Nothing to approve: run 'summary' first so the owner sees exactly what is being approved.")
    declined = set(args.except_ or [])
    bad = declined - listed
    if bad:
        sys.exit(f"Not in the last summary: {sorted(bad)}")
    today = datetime.date.today().isoformat()
    touched, merged, refused, reviews = set(), [], [], {}
    APPROVED.mkdir(parents=True, exist_ok=True)
    DECLINED.mkdir(parents=True, exist_ok=True)
    for m, body, path in pending():
        if m["id"] not in listed:
            continue  # arrived after the summary; waits for the next one
        if m["id"] in declined:
            shutil.move(str(path), DECLINED / path.name)
            refused.append(m["id"])
            continue
        target, heading = TARGETS[m["kind"]]
        src = m["source"].split("/")[-1]
        if m["kind"] in ("must-fix", "should-fix", "idea"):
            na = re.search(r"Next action:\s*(.+)", body)
            block = f"- **{m['title']}** ({src}, approved {today}): {first_sentence(na.group(1), 400) if na else m['summary']}"
            insert_under(ROOT / target, heading, block)
            touched.add(target)
        elif m["kind"] == "context":
            lines = body.split("Lines to add to CONTEXT.md:\n\n", 1)[1].split("\n\nFull change:", 1)[0]
            # outside headings must not restructure CONTEXT.md; keep them as bold lines
            lines = re.sub(r"(?m)^#+\s*(.+)$", r"**\1**", lines)
            insert_under(ROOT / target, heading, f"### From {src} (approved {today})\n{lines}")
            touched.add(target)
        elif m["kind"] == "doc":
            content = body.rsplit("\n\nChange:\n\n```diff", 1)[0]  # exactly the version the owner saw
            (ROOT / m["doc_file"]).write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")
            touched.add(m["doc_file"])
        if m.get("review_file"):
            reviews.setdefault(m["review_file"], []).append(m["id"])
        shutil.move(str(path), APPROVED / path.name)
        merged.append(m["id"])
    for name, ids in reviews.items():  # archive the full review once any of its items is approved
        snap = SOURCES / name
        if not snap.exists():
            snap = DESK / name
        dest = ROOT / "reviews" / name
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(f"_Imported from the AI Review Desk; owner approved proposals {ids} on {today}._\n\n"
                        + snap.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        touched.add(f"reviews/{name}")
    st["last_listed"] = []
    save_state(st)
    print(f"Approved and merged: {merged or 'none'}. Declined: {refused or 'none'}. Files changed: {sorted(touched) or 'none'}")
    if args.push and (merged or refused):
        git = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"
        msg = f"Merge owner-approved proposals {merged}" + (f"; declined {refused}" if refused else "")
        subprocess.run([git, "add", "proposals", *sorted(touched)], cwd=ROOT, check=True)
        subprocess.run([git, "commit", "-q", "-m", msg], cwd=ROOT, check=True)
        subprocess.run([git, "push", "-q", "origin", "HEAD"], cwd=ROOT, check=True)
        print("Committed and pushed.")


def cmd_restore(args):
    for p in DECLINED.glob(f"{args.id:03d}-*.md"):
        shutil.move(str(p), PENDING / p.name)
        print(f"Restored {p.name} to pending.")
        return
    sys.exit(f"No declined proposal {args.id}.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("import")
    i.add_argument("--baseline", nargs="+", metavar="FILE", help="desk files the owner has already handled")
    i.set_defaults(fn=cmd_import)
    sub.add_parser("summary").set_defaults(fn=cmd_summary)
    a = sub.add_parser("approve")
    a.add_argument("--except", dest="except_", type=int, nargs="*")
    a.add_argument("--push", action="store_true")
    a.set_defaults(fn=cmd_approve)
    r = sub.add_parser("restore")
    r.add_argument("id", type=int)
    r.set_defaults(fn=cmd_restore)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
