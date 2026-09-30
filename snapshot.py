"""Save a raw snapshot of the public FPL API.

bootstrap-static only ever shows the current state, so prices, ownership and
injury flags are lost unless we record them. Snapshots are stored untouched
(gzipped JSON) under data/raw/<UTC timestamp>/ so they can be re-parsed later.

Usage: python3 snapshot.py
"""

import gzip
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://fantasy.premierleague.com/api/"
RAW_DIR = Path(__file__).parent / "data" / "raw"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch(path: str, retries: int = 3) -> bytes:
    request = urllib.request.Request(BASE + path, headers=HEADERS)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def save(out_dir: Path, name: str, body: bytes) -> None:
    json.loads(body)  # refuse to store an error page as data
    with gzip.open(out_dir / f"{name}.json.gz", "wb") as f:
        f.write(body)


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    out_dir = RAW_DIR / stamp
    out_dir.mkdir(parents=True)

    bootstrap = fetch("bootstrap-static/")
    save(out_dir, "bootstrap-static", bootstrap)

    endpoints = {
        "fixtures": "fixtures/",
        "event-status": "event-status/",
        "set-piece-notes": "team/set-piece-notes/",
    }
    # Live points for the gameweek in progress (or just finished).
    current = [e["id"] for e in json.loads(bootstrap)["events"] if e["is_current"]]
    if current:
        endpoints[f"event-{current[0]}-live"] = f"event/{current[0]}/live/"

    failed = []
    for name, path in endpoints.items():
        try:
            save(out_dir, name, fetch(path))
        except Exception as error:
            failed.append(name)
            print(f"FAILED {name}: {error}", file=sys.stderr)

    saved = sorted(p.name for p in out_dir.iterdir())
    print(f"{out_dir}: saved {len(saved)} files{f', {len(failed)} failed' if failed else ''}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
