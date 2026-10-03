"""Save Snapshots of the public FPL API.

bootstrap-static only ever shows the current state, so prices, ownership and
injury flags are lost unless we record them. Each Snapshot is a directory of
untouched, gzipped JSON responses named by its UTC timestamp.
"""

import gzip
import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

API_BASE = "https://fantasy.premierleague.com/api/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
STAMP_FORMAT = "%Y-%m-%dT%H%M%SZ"

Fetch = Callable[[str], bytes]


def fetch_api(path: str, retries: int = 3) -> bytes:
    request = urllib.request.Request(API_BASE + path, headers=HEADERS)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def _save(out_dir: Path, name: str, body: bytes) -> None:
    json.loads(body)  # refuse to store an error page as data
    with gzip.open(out_dir / f"{name}.json.gz", "wb") as f:
        f.write(body)


def take_snapshot(root: Path, fetch: Fetch = fetch_api, now: datetime | None = None) -> Path:
    """Fetch every endpoint into a new Snapshot directory under root and return it.

    Raises if any endpoint fails, leaving no partial Snapshot behind.
    """
    stamp = (now or datetime.now(UTC)).strftime(STAMP_FORMAT)
    out_dir = root / stamp
    partial = root / f".{stamp}.partial"
    partial.mkdir(parents=True)

    bootstrap = fetch("bootstrap-static/")
    _save(partial, "bootstrap-static", bootstrap)

    endpoints = {
        "fixtures": "fixtures/",
        "event-status": "event-status/",
        "set-piece-notes": "team/set-piece-notes/",
    }
    # Live points for the Gameweek in progress (or just finished).
    current = [e["id"] for e in json.loads(bootstrap)["events"] if e["is_current"]]
    if current:
        endpoints[f"event-{current[0]}-live"] = f"event/{current[0]}/live/"

    for name, path in endpoints.items():
        _save(partial, name, fetch(path))

    partial.rename(out_dir)
    return out_dir


def latest_snapshot(root: Path) -> Path:
    stamps = sorted(
        child for child in root.iterdir() if child.is_dir() and not child.name.startswith(".")
    )
    if not stamps:
        raise FileNotFoundError(f"no Snapshots under {root}")
    return stamps[-1]


def read_json(snapshot_dir: Path, name: str) -> object:
    with gzip.open(snapshot_dir / f"{name}.json.gz") as f:
        return json.load(f)
