"""Download the Bhagavad Gita chapter pages from Sanskrit Wikisource.

Saves one JSON snapshot per chapter in data/raw/ (wikitext plus page and
revision IDs), so the library can be rebuilt from a pinned revision without
touching the network again.

Usage: python scripts/fetch_wikisource.py
"""

import datetime
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://sa.wikisource.org/w/api.php"
INDEX_TITLE = "भगवद्गीता"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
USER_AGENT = "Viveka-verse-library/0.1 (non-commercial scripture study app)"
REQUEST_GAP_SECONDS = 2

DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def api_get(params, attempts=5):
    params = {**params, "format": "json", "formatversion": "2", "maxlag": "5"}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(attempts):
        time.sleep(REQUEST_GAP_SECONDS)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code != 429 or attempt == attempts - 1:
                raise
            wait = int(err.headers.get("Retry-After") or 10 * (attempt + 1))
            print(f"  rate limited, waiting {wait}s")
            time.sleep(wait)


def chapter_titles():
    data = api_get({"action": "query", "titles": INDEX_TITLE, "prop": "links", "pllimit": "max"})
    links = data["query"]["pages"][0]["links"]
    return [link["title"] for link in links if link["title"].startswith(INDEX_TITLE + "/")]


def chapter_number(wikitext):
    """Read the chapter number from the verse markers, e.g. ॥२- १॥ -> 2.

    Only <poem> blocks are searched: the commentary sections also contain
    markers such as ॥ २४ - २५ ॥ (a joint note on verses 24-25).
    """
    poems = "\n".join(re.findall(r"<poem>(.*?)</poem>", wikitext, flags=re.S))
    nums = {int(m.translate(DEVANAGARI_DIGITS)) for m in re.findall(r"॥\s*([०-९]+)\s*-", poems)}
    if len(nums) != 1:
        raise ValueError(f"expected one chapter number in verse markers, found {sorted(nums)}")
    return nums.pop()


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    titles = chapter_titles()
    if len(titles) != 18:
        raise SystemExit(f"expected 18 chapter pages, found {len(titles)}: {titles}")

    for title in titles:
        data = api_get({
            "action": "query",
            "titles": title,
            "prop": "revisions",
            "rvprop": "ids|timestamp|content",
            "rvslots": "main",
            "redirects": "1",
        })
        page = data["query"]["pages"][0]
        title = page["title"]  # the redirect target, if the index linked a redirect
        rev = page["revisions"][0]
        wikitext = rev["slots"]["main"]["content"]
        chapter = chapter_number(wikitext)
        snapshot = {
            "chapter": chapter,
            "title": title,
            "pageid": page["pageid"],
            "revid": rev["revid"],
            "timestamp": rev["timestamp"],
            "retrieved": datetime.date.today().isoformat(),
            "url": "https://sa.wikisource.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
            "permalink": f"https://sa.wikisource.org/w/index.php?oldid={rev['revid']}",
            "licence": "CC BY-SA 4.0 (Wikisource text); underlying Sanskrit work is public domain",
            "wikitext": wikitext,
        }
        out = RAW_DIR / f"ch{chapter:02d}.json"
        out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"ch{chapter:02d}  rev {rev['revid']}  {title}")


if __name__ == "__main__":
    main()
