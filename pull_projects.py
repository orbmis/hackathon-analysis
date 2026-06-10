#!/usr/bin/env python3
"""Pull all projects from the ETHGlobal Explorer API and write a consolidated CSV.

Iterates page by page until a page returns no rows, sleeping a random amount of
time between requests to stay friendly with rate limits.

The run is resumable: rows are appended to the CSV as each page is fetched (so a
cancel never loses progress), already-saved project IDs are skipped on restart,
and you can jump straight to a page with --start-page:

    python3 pull_projects.py                 # start/continue from page 1
    python3 pull_projects.py --start-page 73 # resume from page 73
"""

import argparse
import csv
import os
import random
import ssl
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def make_ssl_context():
    """Build an SSL context with a working CA bundle.

    Python on macOS often ships without wired-up system certificates, so prefer
    certifi's bundle when present and fall back to the default context.
    """
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CONTEXT = make_ssl_context()

BASE_URL = "https://www.ethglobalexplorer.com/api/projects"
OUTPUT_CSV = "ethglobal_projects.csv"

# Random pause (seconds) inserted between page requests to avoid rate limiting.
MIN_DELAY = 1.5
MAX_DELAY = 4.0

# Retry settings for transient failures (e.g. HTTP 429 / network blips).
MAX_RETRIES = 5
RETRY_BACKOFF = 5.0  # base seconds, grows with each retry

# An empty `data` page is treated as the end ONLY if it stays empty across this
# many retries — the API occasionally returns a spurious empty page mid-stream.
EMPTY_PAGE_RETRIES = 4

CSV_FIELDS = ["id", "title", "description", "url", "event", "prizes", "prize_count"]


def fetch_page(page):
    """Fetch a single page, returning the parsed JSON dict."""
    import json

    query = urlencode({"page": page, "q": "", "event": "", "prize": "", "tag": ""})
    url = f"{BASE_URL}?{query}"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (data-pull script)"})

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (HTTPError, URLError) as err:
            last_err = err
            wait = RETRY_BACKOFF * attempt + random.uniform(0, 2)
            status = getattr(err, "code", "n/a")
            print(
                f"  ! page {page} attempt {attempt}/{MAX_RETRIES} failed "
                f"(status={status}): {err}. Retrying in {wait:.1f}s",
                file=sys.stderr,
            )
            time.sleep(wait)
    raise RuntimeError(f"Failed to fetch page {page} after {MAX_RETRIES} attempts") from last_err


def flatten(project):
    """Turn one project record into a flat CSV row."""
    prizes = project.get("project_prizes") or []
    prize_names = [p.get("name", "") for p in prizes]
    return {
        "id": project.get("id"),
        "title": project.get("title", ""),
        "description": project.get("description", ""),
        "url": project.get("url", ""),
        "event": project.get("event", ""),
        "prizes": "; ".join(prize_names),
        "prize_count": len(prize_names),
    }


def load_existing_ids(path):
    """Read IDs already present in the CSV so a resumed run can skip them."""
    ids = set()
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return ids
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw = (row.get("id") or "").strip()
            if raw:
                ids.add(int(raw) if raw.isdigit() else raw)
    return ids


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Page number to begin from (default: 1). Use to resume an interrupted run.",
    )
    args = parser.parse_args()

    # Load any IDs already saved so a resumed run doesn't duplicate them.
    seen_ids = load_existing_ids(OUTPUT_CSV)
    file_exists = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
    if seen_ids:
        print(
            f"Resuming: {len(seen_ids)} projects already in {OUTPUT_CSV} will be skipped.",
            file=sys.stderr,
        )

    page = args.start_page
    total_count = None
    no_progress_streak = 0
    added = 0  # new rows written this run

    # Append mode: writes survive a cancel; header only for a brand-new file.
    out = open(OUTPUT_CSV, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(out, fieldnames=CSV_FIELDS)
    if not file_exists:
        writer.writeheader()
        out.flush()

    while True:
        print(f"Fetching page {page}...", file=sys.stderr)
        payload = fetch_page(page)
        data = payload.get("data") or []

        if total_count is None:
            total_count = payload.get("totalCount")
            if total_count is not None:
                print(f"  totalCount reported: {total_count}", file=sys.stderr)

        # The API sometimes returns a spurious empty page mid-stream, so don't
        # trust a single empty response — re-request the same page a few times
        # before concluding we've genuinely reached the end.
        if not data:
            for attempt in range(1, EMPTY_PAGE_RETRIES + 1):
                wait = random.uniform(MIN_DELAY, MAX_DELAY) + attempt
                print(
                    f"  page {page} came back empty (verify {attempt}/{EMPTY_PAGE_RETRIES}); "
                    f"re-checking in {wait:.1f}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)
                data = fetch_page(page).get("data") or []
                if data:
                    print(f"  page {page} recovered with {len(data)} rows.", file=sys.stderr)
                    break
            if not data:
                print(
                    f"  page {page} still empty after {EMPTY_PAGE_RETRIES} retries — "
                    "treating as end of data.",
                    file=sys.stderr,
                )
                break

        new_on_page = 0
        for project in data:
            pid = project.get("id")
            if pid in seen_ids:
                continue
            seen_ids.add(pid)
            writer.writerow(flatten(project))
            new_on_page += 1
            added += 1

        out.flush()  # persist this page before sleeping, so a cancel is safe

        print(
            f"  page {page}: {len(data)} rows ({new_on_page} new), "
            f"total saved {len(seen_ids)} (+{added} this run)",
            file=sys.stderr,
        )

        # Stop once we've collected everything the API says exists.
        if total_count is not None and len(seen_ids) >= total_count:
            print("  collected all reported rows — stopping.", file=sys.stderr)
            break

        # Safety net: if several consecutive pages add nothing new, the API is
        # looping or out of fresh data — stop rather than spin forever.
        no_progress_streak = no_progress_streak + 1 if new_on_page == 0 else 0
        if no_progress_streak >= 5:
            print(
                "  5 consecutive pages with no new rows — stopping.",
                file=sys.stderr,
            )
            break

        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        print(f"  sleeping {delay:.2f}s before next page...", file=sys.stderr)
        time.sleep(delay)
        page += 1

    out.close()
    print(
        f"\nDone. Added {added} new projects this run; "
        f"{len(seen_ids)} total in {OUTPUT_CSV}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
