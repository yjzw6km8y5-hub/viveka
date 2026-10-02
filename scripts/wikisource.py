"""Shared helpers for fetching pinned snapshots from Sanskrit Wikisource.

Every snapshot stores the page's wikitext together with its page and revision
IDs, so a library can be rebuilt from a fixed revision without the network.
"""

import datetime
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://sa.wikisource.org/w/api.php"
USER_AGENT = "Viveka-verse-library/0.1 (non-commercial scripture study app)"
REQUEST_GAP_SECONDS = 3
LICENCE = "CC BY-SA 4.0 (Wikisource text); underlying Sanskrit work is public domain"


def api_get(params, attempts=6):
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
            wait = int(err.headers.get("Retry-After") or 15 * (attempt + 1))
            print(f"  rate limited, waiting {wait}s", file=sys.stderr)
            time.sleep(wait)


def page_url(title):
    return "https://sa.wikisource.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))


def fetch_page(title):
    """Return a snapshot dict for one page (following redirects), or None if missing."""
    data = api_get({
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "ids|timestamp|content",
        "rvslots": "main",
        "redirects": "1",
    })
    page = data["query"]["pages"][0]
    if "revisions" not in page:
        return None
    rev = page["revisions"][0]
    return {
        "title": page["title"],
        "requested_title": title,
        "pageid": page["pageid"],
        "revid": rev["revid"],
        "timestamp": rev["timestamp"],
        "retrieved": datetime.date.today().isoformat(),
        "url": page_url(page["title"]),
        "permalink": f"https://sa.wikisource.org/w/index.php?oldid={rev['revid']}",
        "licence": LICENCE,
        "wikitext": rev["slots"]["main"]["content"],
    }


def subpages(title):
    """Titles of pages linked from `title` that are its subpages (title/...)."""
    data = api_get({"action": "query", "titles": title, "prop": "links", "pllimit": "max", "redirects": "1"})
    page = data["query"]["pages"][0]
    base = page.get("title", title)
    return [l["title"] for l in page.get("links", []) if l["title"].startswith(base + "/")]
