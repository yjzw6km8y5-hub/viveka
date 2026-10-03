"""Overwrite, in place, the four screenshots the Claude chat reads in AI Review Desk/Viveka (CLAUDE.md section 15).

  python scripts/desk_screens.py HOME.jpg ANSWER_TOP.jpg ANSWER_DETAILS.jpg PHONE.jpg

screen1 = home; screen2 = top of an answer ("I had a fight with my best friend"); screen3 = the details of that
answer; screen4 = phone width, any answer. Take them in the browser pane at http://127.0.0.1:8765 after every UI change.
The files are created by the Claude chat and must keep their identity: they are overwritten in place, never deleted,
renamed or recreated. A missing file is reported, not created.
"""
import sys
from pathlib import Path

DESK = Path(__file__).resolve().parent.parent.parent / "AI Review Desk" / "Viveka"


def main():
    srcs = sys.argv[1:]
    if len(srcs) != 4:
        sys.exit(__doc__)
    for i, src in enumerate(srcs, 1):
        dest = DESK / f"screen{i}.jpg"
        if not dest.exists():
            print(f"{dest.name}: not found; not created (the Claude chat must create it)")
            continue
        data = Path(src).read_bytes()
        with open(dest, "r+b") as f:  # same file, same Drive ID
            f.seek(0)
            f.write(data)
            f.truncate()
        print(f"{dest.name}: overwritten in place ({len(data)} bytes)")


if __name__ == "__main__":
    main()
