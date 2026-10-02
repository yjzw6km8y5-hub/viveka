"""Owner-approval gate for outside input, and the 8 PM health check (PROCESS.md v2).

Nothing from the AI Review Desk reaches STATUS.md, CONTEXT.md, PROCESS.md, PROJECT_BRIEF.md
or reviews/ until the owner approves it. Unapproved items stay local (proposals/pending/ and
proposals/sources/ are not committed). Every decision is logged in proposals/APPROVALS.md.

  python scripts/proposals.py import            new or changed desk files -> local pending items
  python scripts/proposals.py summary           Health section, then pending items in plain language
  python scripts/proposals.py approve [--only 2] [--except 3 5] [--push]
                                                merge items shown in the last summary; --except
                                                declines those numbers; --only leaves the rest pending
  python scripts/proposals.py decline 1 --reason "superseded"
  python scripts/proposals.py restore 2         move a declined item back to pending
  python scripts/proposals.py health            the Health section only

The desk folder defaults to '../AI Review Desk/Viveka' next to the repo; set
VIVEKA_REVIEW_DESK to override. Times are local (America/Toronto on the owner's PC).
"""
import argparse, csv, datetime, difflib, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESK = Path(os.environ.get("VIVEKA_REVIEW_DESK", ROOT.parent / "AI Review Desk" / "Viveka"))
PROP = ROOT / "proposals"
PENDING, APPROVED, DECLINED, SOURCES = (PROP / d for d in ("pending", "approved", "declined", "sources"))
STATE = PROP / "state.json"          # local
APPROVALS = PROP / "APPROVALS.md"    # committed log of every decision
CYCLES = ROOT / "logs" / "cycles.csv"

TARGETS = {  # kind -> (file, section heading)
    "must-fix": ("STATUS.md", "## Must-fix (from approved reviews; do these first)"),
    "should-fix": ("STATUS.md", "## Should-fix (from approved reviews)"),
    "idea": ("CONTEXT.md", "## Approved ideas from reviews"),
    "context": ("CONTEXT.md", "## Approved context updates"),
    "doc": ("repo root", None),
    "file": ("reviews/", None),
}
KIND_WORDS = {"must-fix": "must fix", "should-fix": "should fix", "idea": "idea", "context": "context update",
              "doc": "shared document", "file": "file to archive in reviews/"}
ROOT_DOCS = ("PROCESS.md", "PROJECT_BRIEF.md")
KINDS = {"must-fix": "must-fix", "must fix": "must-fix", "should-fix": "should-fix", "should fix": "should-fix",
         "idea": "idea", "ideas": "idea"}

# Health thresholds (PROCESS.md v2, gap 4)
RUNNER_MAX_H, CODEX_MAX_H, OBSERVER_MAX_H, SUMMARY_MAX_H = 3, 3, 6, 26
FAILED_IN_A_ROW = 3


# ---------------------------------------------------------------- helpers
def now():
    return datetime.datetime.now().astimezone()


def load_state():
    st = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    st.setdefault("imported", {}); st.setdefault("last_listed", []); st.setdefault("last_summary", None)
    used = [int(p.name[:3]) for d in (PENDING, APPROVED, DECLINED) if d.exists() for p in d.glob("[0-9][0-9][0-9]-*.md")]
    st["next_id"] = max([st.get("next_id", 1)] + [u + 1 for u in used])
    return st


def save_state(st):
    PROP.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical(name):
    """'PROCESS (1).md' (a Drive re-upload) -> 'PROCESS.md'."""
    return re.sub(r" \(\d+\)(?=\.\w+$)", "", name)


def first_sentence(text, limit=160):
    text = re.sub(r"\s+", " ", text).strip()
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    s = m.group(1) if m else text
    s = s[:1].upper() + s[1:]
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def write_proposal(st, kind, title, summary, body, source, extra=None):
    pid = st["next_id"]
    st["next_id"] += 1
    meta = {"id": pid, "kind": kind, "target": TARGETS[kind][0], "title": title, "summary": summary,
            "source": source, "imported": now().strftime("%Y-%m-%d %H:%M"), **(extra or {}),
            "body_sha256": sha(body.strip())}
    PENDING.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "proposal"
    path = PENDING / f"{pid:03d}-{slug}.md"
    path.write_text("```json\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n```\n\n" + body.strip() + "\n",
                    encoding="utf-8", newline="\n")
    return path


def file_version(f):
    """Exact version of a desk file: name, modified time, size and SHA-256 of its bytes (PROCESS.md v3).
    Google Drive for desktop does not expose Drive file IDs locally, so the hash identifies the version."""
    raw = f.read_bytes()
    return {"file": f.name, "modified": datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def version_text(v):
    return f"{v['file']}, modified {v['modified']}, {v['bytes']} bytes, sha256 {v['sha256'][:12]}" if v else "version not recorded"


def read_proposal(path):
    m = re.match(r"```json\n(.*?)\n```\n\n(.*)", path.read_text(encoding="utf-8"), re.S)
    return json.loads(m.group(1)), m.group(2)


def pending():
    if not PENDING.exists():
        return []
    return sorted((read_proposal(p) + (p,) for p in PENDING.glob("*.md")), key=lambda t: t[0]["id"])


def split_review(text):
    """Review -> [(kind, title, body)]. Understands '## must-fix' sections with '### Title' items,
    and bullet items like '- **Must-fix — Title.** body'."""
    items, kind, title, buf = [], None, None, []

    def flush():
        if kind and (title or "".join(buf).strip()):
            body = "\n".join(buf).strip()
            items.append((kind, title or first_sentence(body, 80), body))

    for line in text.splitlines():
        h2 = re.match(r"##\s+(.+?)\s*$", line)
        h3 = re.match(r"###\s+(.+?)\s*$", line)
        bullet = re.match(r"-\s+\*\*(must[- ]fix|should[- ]fix|ideas?)\s*[—–:-]\s*(.+?)\*\*\s*(.*)$", line, re.I)
        if bullet:
            flush()
            kind, title, buf = KINDS[bullet.group(1).lower()], bullet.group(2).strip().rstrip("."), [bullet.group(3)]
        elif h2 and not line.startswith("###"):
            flush()
            kind, title, buf = KINDS.get(h2.group(1).strip().lower()), None, []
        elif h3 and kind:
            flush()
            title, buf = h3.group(1).strip(), []
        elif kind:
            if title and buf and re.match(r"-\s+\*\*", line):  # next bullet of another type ends the item
                flush()
                kind, title, buf = None, None, []
            else:
                buf.append(line)
    flush()
    return items


def item_summary(body):
    m = re.search(r"(?:Next action|Proposed action):\s*(.+)", body)
    return first_sentence(m.group(1) if m else body)


def log_decision(rows):
    """rows: [(date, source, version, id, title, decision)] -> proposals/APPROVALS.md"""
    if not APPROVALS.exists():
        APPROVALS.write_text("# Approvals\n\nEvery owner decision on outside input (PROCESS.md v2, gap 2).\n\n"
                             "| Date | Source file | Version | # | Finding | Decision |\n|---|---|---|---:|---|---|\n",
                             encoding="utf-8", newline="\n")
    with APPROVALS.open("a", encoding="utf-8", newline="\n") as f:
        for d, src, ver, pid, title, dec in rows:
            f.write(f"| {d} | {src} | {ver} | {pid} | {title.replace('|', '/')} | {dec} |\n")


# ---------------------------------------------------------------- import
def cmd_import(args):
    if not DESK.is_dir():
        sys.exit("Review Desk folder not found; set VIVEKA_REVIEW_DESK.")
    st = load_state()
    made = []
    for f in sorted(DESK.iterdir(), key=lambda p: p.stat().st_mtime):
        if not f.is_file() or f.suffix.lower() not in (".md", ".txt"):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        digest = sha(text)
        if st["imported"].get(f.name) == digest:
            continue
        name, source = canonical(f.name), f"AI Review Desk/Viveka/{f.name}"
        ver = {"version": file_version(f)}
        SOURCES.mkdir(parents=True, exist_ok=True)
        snap = SOURCES / name
        old = snap.read_text(encoding="utf-8") if snap.exists() else None
        if f.name in (args.baseline or []):  # already handled by the owner: only later changes are proposed
            snap.write_text(text, encoding="utf-8", newline="\n")
        elif name in ROOT_DOCS:
            snap.write_text(text, encoding="utf-8", newline="\n")
            heading = first_sentence(text.lstrip("# "), 100)
            diff = "\n".join(difflib.unified_diff((old or "").splitlines(), text.splitlines(),
                                                  f"previous {name}", f"new {name}", lineterm=""))
            made.append(write_proposal(st, "doc", f"{'Update' if old else 'Add'} {name}",
                                       f"{'Replace' if old else 'Add'} {name} at the repo root: \"{heading}\"",
                                       text + "\n\nChange:\n\n```diff\n" + diff + "\n```", source, {"doc_file": name, **ver}))
        elif name.upper().startswith("CONTEXT"):
            new = text.splitlines()
            added = [l[1:] for l in difflib.unified_diff((old or "").splitlines(), new, lineterm="", n=0)
                     if l.startswith("+") and not l.startswith("+++") and l[1:].strip()]
            snap.write_text(text, encoding="utf-8", newline="\n")
            if added:
                diff = "\n".join(difflib.unified_diff((old or "").splitlines(), new, f"previous {name}", f"new {name}", lineterm=""))
                body = "Lines to add to CONTEXT.md:\n\n" + "\n".join(added) + "\n\nFull change:\n\n```diff\n" + diff + "\n```"
                made.append(write_proposal(st, "context", f"Context update from {name}",
                                           f"{len(added)} new or changed lines, e.g. \"{first_sentence(added[0].lstrip('-# '), 100)}\"",
                                           body, source, ver))
        else:
            snap.write_text(text, encoding="utf-8", newline="\n")
            items = split_review(text)
            for kind, title, body in items:
                made.append(write_proposal(st, kind, title, item_summary(body), body, source, {"review_file": name, **ver}))
            if not items:
                made.append(write_proposal(st, "file", f"Archive {name}", "No must-fix, should-fix or idea items "
                                           "found; approving archives it in reviews/.", text, source, {"review_file": name, **ver}))
        st["imported"][f.name] = digest
    save_state(st)
    print(f"{len(made)} new item(s) imported." + "".join(f"\n  {p.name}" for p in made))


# ---------------------------------------------------------------- health
def when(t):
    if t is None:
        return "never"
    d = (now().date() - t.date()).days
    day = "today" if d == 0 else "yesterday" if d == 1 else t.strftime("%Y-%m-%d")
    return f"{day} {t.strftime('%H:%M')}"


def mtime(p):
    return datetime.datetime.fromtimestamp(p.stat().st_mtime).astimezone()


def hours_since(t):
    return (now() - t).total_seconds() / 3600 if t else None


def read_cycles():
    if not CYCLES.exists():
        return []
    with CYCLES.open(encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f) if r.get("time")]


def health_rows(st):
    rows = []  # (ok, label, last_worked, why_if_cross)
    cycles = read_cycles()
    parse = lambda s: datetime.datetime.fromisoformat(s).astimezone()
    oks = [parse(r["time"]) for r in cycles if r["result"] == "ok"]
    last_ok = max(oks) if oks else None
    streak = 0
    for r in reversed(cycles):
        if r["result"] == "failed":
            streak += 1
        elif r["result"] in ("ok", "resume"):
            break
    paused = cycles and cycles[-1]["result"] == "paused"
    if not cycles:
        rows.append((False, "Runner cycle", "never", "No cycle has been logged in logs/cycles.csv yet."))
    elif paused or streak >= FAILED_IN_A_ROW:
        last = cycles[-1]
        rows.append((False, "Runner cycle", when(last_ok),
                     f"Paused after {max(streak, FAILED_IN_A_ROW)} failed cycles in a row ({last.get('reason') or 'see STATUS.md'}); reply \"resume\" to restart."))
    elif hours_since(last_ok) is None or hours_since(last_ok) > RUNNER_MAX_H:
        rows.append((False, "Runner cycle", when(last_ok), f"No successful cycle in the last {RUNNER_MAX_H} hours."))
    else:
        rows.append((True, "Runner cycle", when(last_ok), ""))

    reviews = [p for p in (ROOT / "reviews").glob("*cycle*.md")] if (ROOT / "reviews").exists() else []
    last_codex = max((mtime(p) for p in reviews), default=None)
    ok = last_codex is not None and hours_since(last_codex) <= CODEX_MAX_H
    rows.append((ok, "Codex review", when(last_codex), "" if ok else f"No Codex review saved in reviews/ in the last {CODEX_MAX_H} hours."))

    desk_ok = DESK.is_dir()
    obs = [p for p in DESK.glob("*_observer_*.md")] if desk_ok else []
    last_obs = max((mtime(p) for p in obs), default=None)
    ok = last_obs is not None and hours_since(last_obs) <= OBSERVER_MAX_H
    why = "The AI Review Desk folder cannot be read." if not desk_ok else f"No observer review has arrived in the last {OBSERVER_MAX_H} hours."
    rows.append((ok, "ChatGPT observer review received", when(last_obs), "" if ok else why))

    items = pending()
    oldest = min((m["imported"] for m, _, _ in items), default=None)
    rows.append((desk_ok, "Pending proposals", f"{len(items)} pending" + (f", oldest imported {oldest}" if oldest else ""),
                 "" if desk_ok else "The AI Review Desk folder cannot be read, so new items cannot be imported."))

    rows.append((ok, "Scheduled task: ChatGPT observer (every 2 hours)", when(last_obs),
                 "" if ok else f"Judged by its saved reviews: none in the last {OBSERVER_MAX_H} hours."))
    prev = datetime.datetime.fromisoformat(st["last_summary"]) if st.get("last_summary") else None
    ok = prev is None or hours_since(prev) <= SUMMARY_MAX_H
    rows.append((ok, "Scheduled task: 8 PM summary", when(prev) if prev else "first run",
                 "" if ok else f"The previous summary ran more than {SUMMARY_MAX_H} hours ago, so at least one evening was missed."))
    return rows


def print_health(st):
    print("Health")
    for ok, label, last, why in health_rows(st):
        print(f"{'✔' if ok else '✘'} {label}: last worked {last}" if "pending" not in last else f"{'✔' if ok else '✘'} {label}: {last}")
        if not ok:
            print(f"   Why: {why}")


def cmd_health(_):
    print_health(load_state())


# ---------------------------------------------------------------- summary and approval
def cmd_summary(_):
    st = load_state()
    print_health(st)
    print()
    items = pending()
    st["last_listed"] = [m["id"] for m, _, _ in items]
    st["last_summary"] = now().isoformat(timespec="minutes")
    save_state(st)
    if not items:
        print("No pending proposals tonight.")
        return
    print(f"{len(items)} pending proposal(s) from the AI Review Desk. Nothing has been merged yet.\n")
    for m, _, _ in items:
        print(f"{m['id']}. {m['title']} ({KIND_WORDS[m['kind']]}, would go into {m['target']}; from {m['source'].split('/')[-1]})")
        print(f"   {m['summary']}")
        v = m.get("version")
        newer = v and any(o.get("version") and o["version"]["file"] == v["file"] and o["version"]["sha256"] != v["sha256"]
                          and o["version"]["modified"] > v["modified"] for o, _, _ in items)
        print(f"   Version: {version_text(v)}" + (" (older version: a newer copy of this file is also listed)" if newer else ""))
    print("\nAn approval covers only these exact versions. A file changed after this summary is listed again next time.")
    print('\nReply "approve" to merge all of these, or "approve except 2" to leave some out.')


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


def git(*a):
    exe = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"
    subprocess.run([exe, *a], cwd=ROOT, check=True)


def check_integrity(m, body):
    if m.get("body_sha256") and sha(body.strip()) != m["body_sha256"]:
        return "the pending item was edited after it was imported"
    v = m.get("version")
    if m["kind"] == "doc" and v:
        content = body.rsplit("\n\nChange:\n\n```diff", 1)[0].rstrip() + "\n"
        if hashlib.sha256(content.encode("utf-8")).hexdigest() != v["sha256"]:
            return "the document does not match the hash of the version that was listed"
    return None


def cmd_approve(args):
    st = load_state()
    listed = set(st.get("last_listed", []))
    if not listed:
        sys.exit("Nothing to approve: run 'summary' first so the owner sees exactly what is being approved.")
    declined, only = set(args.except_ or []), set(args.only or [])
    bad = (declined | only) - listed
    if bad:
        sys.exit(f"Not in the last summary: {sorted(bad)}")
    today = now().strftime("%Y-%m-%d")
    touched, merged, refused, reviews, log = set(), [], [], {}, []
    APPROVED.mkdir(parents=True, exist_ok=True)
    DECLINED.mkdir(parents=True, exist_ok=True)
    # Only items shown in the last summary; with --only, the rest stay pending.
    chosen = [(m, body, path) for m, body, path in pending()
              if m["id"] in listed and (not only or m["id"] in only or m["id"] in declined)]
    for m, body, _ in chosen:  # check everything before changing anything
        problem = None if m["id"] in declined else check_integrity(m, body)
        if problem:
            sys.exit(f"Refusing to merge item {m['id']}: {problem}. Nothing was merged.")
    for m, body, path in chosen:
        src = m["source"].split("/")[-1]
        if m["id"] in declined:
            shutil.move(str(path), DECLINED / path.name)
            refused.append(m["id"])
            log.append((today, src, version_text(m.get("version")), m["id"], m["title"], "rejected"))
            continue
        target, heading = TARGETS[m["kind"]]
        if m["kind"] in ("must-fix", "should-fix", "idea"):
            na = re.search(r"(?:Next action|Proposed action):\s*(.+)", body)
            text = first_sentence(na.group(1), 400) if na else m["summary"]
            insert_under(ROOT / target, heading, f"- **{m['title']}** ({src}, approved {today}): {text}")
            touched.add(target)
        elif m["kind"] == "context":
            lines = body.split("Lines to add to CONTEXT.md:\n\n", 1)[1].split("\n\nFull change:", 1)[0]
            lines = re.sub(r"(?m)^#+\s*(.+)$", r"**\1**", lines)  # outside headings must not restructure CONTEXT.md
            insert_under(ROOT / target, heading, f"### From {src} (approved {today})\n{lines}")
            touched.add(target)
        elif m["kind"] == "doc":
            content = body.rsplit("\n\nChange:\n\n```diff", 1)[0]  # exactly the version the owner saw
            (ROOT / m["doc_file"]).write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")
            touched.add(m["doc_file"])
        if m.get("review_file"):
            reviews.setdefault(m["review_file"], []).append(m["id"])
        shutil.move(str(path), APPROVED / path.name)
        touched.add(f"proposals/approved/{path.name}")
        merged.append(m["id"])
        log.append((today, src, version_text(m.get("version")), m["id"], m["title"], "approved"))
    for name, ids in reviews.items():  # archive the full review once any of its items is approved
        dest = ROOT / "reviews" / name
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(f"_Imported from the AI Review Desk; owner approved items {ids} on {today}._\n\n"
                        + (SOURCES / name).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        touched.add(f"reviews/{name}")
    if log:
        log_decision(log)
        touched.add("proposals/APPROVALS.md")
    st["last_listed"] = [i for i in st["last_listed"] if i not in merged and i not in refused] if only else []
    save_state(st)
    print(f"Approved and merged: {merged or 'none'}. Rejected: {refused or 'none'}. Files changed: {sorted(touched) or 'none'}")
    if args.push and log:
        git("add", *sorted(touched))
        git("commit", "-q", "-m", f"Merge owner-approved proposals {merged}" + (f"; rejected {refused}" if refused else ""))
        git("push", "-q", "origin", "HEAD")
        print("Committed and pushed.")


def cmd_decline(args):
    today = now().strftime("%Y-%m-%d")
    DECLINED.mkdir(parents=True, exist_ok=True)
    for pid in args.ids:
        hits = list(PENDING.glob(f"{pid:03d}-*.md"))
        if not hits:
            sys.exit(f"No pending proposal {pid}.")
        m, _ = read_proposal(hits[0])
        shutil.move(str(hits[0]), DECLINED / hits[0].name)
        log_decision([(today, m["source"].split("/")[-1], version_text(m.get("version")), pid, m["title"], f"rejected: {args.reason}")])
        print(f"Declined {pid}: {m['title']}")


def cmd_restore(args):
    for p in DECLINED.glob(f"{args.id:03d}-*.md"):
        shutil.move(str(p), PENDING / p.name)
        print(f"Restored {p.name} to pending.")
        return
    sys.exit(f"No declined proposal {args.id}.")


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # ticks and crosses survive Windows pipes
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("import")
    i.add_argument("--baseline", nargs="+", metavar="FILE", help="desk files the owner has already handled")
    i.set_defaults(fn=cmd_import)
    sub.add_parser("summary").set_defaults(fn=cmd_summary)
    sub.add_parser("health").set_defaults(fn=cmd_health)
    a = sub.add_parser("approve")
    a.add_argument("--except", dest="except_", type=int, nargs="*")
    a.add_argument("--only", type=int, nargs="*")
    a.add_argument("--push", action="store_true")
    a.set_defaults(fn=cmd_approve)
    d = sub.add_parser("decline")
    d.add_argument("ids", type=int, nargs="+")
    d.add_argument("--reason", required=True)
    d.set_defaults(fn=cmd_decline)
    r = sub.add_parser("restore")
    r.add_argument("id", type=int)
    r.set_defaults(fn=cmd_restore)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
