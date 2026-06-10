#!/usr/bin/env python3
"""Scrape ETHGlobal event dates + per-sponsor prize pools (for the §9 forecast).

Pulls the /events listing, keeps real hackathon slugs (drops Pragma talks,
happy-hours, coworks), and fetches each event page — rate-limited like
pull_projects.py. Past pages (HTTP 200) yield dates, total pool, and per-sponsor
$ amounts; upcoming pages (HTTP 500, sponsors unpublished) are recorded from a
known date table.

Outputs:
  event_meta.csv     event, slug, start_date, end_date, total_pool_usd, n_sponsors, status
  event_sponsors.csv event, slug, start_date, sponsor, prize_usd
"""

import csv
import random
import re
import ssl
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

try:
    import certifi
    SSL = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL = ssl.create_default_context()

BASE = "https://ethglobal.com"
MIN_DELAY, MAX_DELAY = 1.5, 4.0
MAX_RETRIES = 4
JUNK = ("pragma-", "happy-hour", "cowork", "anniversary", "-with-", "10y")

# Upcoming events 500 (sponsors unpublished); dates from the /events listing.
UPCOMING_DATES = {
    "newyork2026": ("2026-06-12", "2026-06-14"),
    "lisbon2026": ("2026-07-24", "2026-07-26"),
    "ethonline2026": ("2026-09-04", "2026-09-16"),
    "tokyo2026": ("2026-09-25", "2026-09-27"),
    "mumbai": ("2026-11-06", "2026-11-08"),
}
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}


def log(m):
    print(m, file=sys.stderr, flush=True)


def fetch(url):
    """Return (status, html). Retries transient errors; returns HTTPError code."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (event-scrape)"})
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(req, timeout=30, context=SSL) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except HTTPError as e:
            if e.code in (404, 500):       # definitive: don't retry
                return e.code, ""
            last = e
        except URLError as e:
            last = e
        time.sleep(2.5 * attempt + random.uniform(0, 1.5))
    log(f"    ! gave up on {url}: {last}")
    return None, ""


def parse_date(html):
    m = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|"
        r"November|December)\s+(\d{1,2})\s*(?:[–-]\s*(\d{1,2}))?,?\s*(\d{4})", html)
    if not m:
        return "", ""
    mon, d1, d2, yr = m.group(1), int(m.group(2)), m.group(3), m.group(4)
    start = f"{yr}-{MONTHS[mon]:02d}-{d1:02d}"
    end = f"{yr}-{MONTHS[mon]:02d}-{int(d2):02d}" if d2 else start
    return start, end


def parse_sponsors(html):
    pairs = re.findall(r">([^<>]{2,45})</h4><p[^>]*>\$([0-9,]+)</p>", html)
    out, seen = [], set()
    for name, amt in pairs:
        name = name.strip()
        key = (name, amt)
        if key in seen:
            continue
        seen.add(key)
        out.append((name, int(amt.replace(",", ""))))
    return out


def parse_name(html, slug):
    m = re.search(r'property="og:title"\s+content="([^"]+)"', html) or \
        re.search(r"<title>([^<]+)</title>", html)
    if m:
        return re.sub(r"\s*[|–-]\s*ETHGlobal.*$", "", m.group(1)).strip()
    return slug


def main():
    log("Fetching /events listing...")
    _, listing = fetch(f"{BASE}/events")
    slugs = list(dict.fromkeys(re.findall(r'href="/events/([a-z0-9\-]+)"', listing)))
    real = [s for s in slugs if not any(j in s for j in JUNK)]
    log(f"  {len(slugs)} slugs -> {len(real)} real-hackathon slugs")

    meta_rows, spon_rows = [], []
    for i, slug in enumerate(real, 1):
        log(f"[{i}/{len(real)}] {slug}")
        status, html = fetch(f"{BASE}/events/{slug}")
        if status == 200 and html:
            start, end = parse_date(html)
            sponsors = parse_sponsors(html)
            name = parse_name(html, slug)
            total = sum(a for _, a in sponsors)
            meta_rows.append([name, slug, start, end, total, len(sponsors), "past"])
            for sp, amt in sponsors:
                spon_rows.append([name, slug, start, sp, amt])
            log(f"    past | {start} | {len(sponsors)} sponsors | ${total:,}")
        elif status in (500, 404):
            start, end = UPCOMING_DATES.get(slug, ("", ""))
            st = "upcoming" if slug in UPCOMING_DATES else "unpublished"
            meta_rows.append([parse_name(listing, slug) or slug, slug, start, end, 0, 0, st])
            log(f"    {st} (HTTP {status})")
        else:
            log(f"    skipped (status {status})")
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    with open("event_meta.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["event", "slug", "start_date", "end_date",
                    "total_pool_usd", "n_sponsors", "status"])
        w.writerows(meta_rows)
    with open("event_sponsors.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["event", "slug", "start_date", "sponsor", "prize_usd"])
        w.writerows(spon_rows)

    past = sum(1 for r in meta_rows if r[6] == "past")
    log(f"\nDone. {len(meta_rows)} events ({past} past w/ data), "
        f"{len(spon_rows)} sponsor rows.")


if __name__ == "__main__":
    main()
