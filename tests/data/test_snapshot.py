import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from football_agent.data.snapshot import (
    latest_snapshot,
    read_json,
    take_snapshot,
)

NOW = datetime(2026, 10, 2, 9, 30, tzinfo=UTC)


def fake_fetch(responses: dict[str, object]):
    def fetch(path: str) -> bytes:
        return json.dumps(responses.get(path, {"path": path})).encode()

    return fetch


def test_takes_every_endpoint_including_live_points(tmp_path: Path) -> None:
    bootstrap = {"events": [{"id": 5, "is_current": True}, {"id": 6, "is_current": False}]}
    out = take_snapshot(tmp_path, fake_fetch({"bootstrap-static/": bootstrap}), NOW)

    assert out.name == "2026-10-02T093000Z"
    assert sorted(p.name for p in out.iterdir()) == [
        "bootstrap-static.json.gz",
        "event-5-live.json.gz",
        "event-status.json.gz",
        "fixtures.json.gz",
        "set-piece-notes.json.gz",
    ]
    assert read_json(out, "bootstrap-static") == bootstrap
    assert read_json(out, "event-5-live") == {"path": "event/5/live/"}


def test_skips_live_points_before_the_season(tmp_path: Path) -> None:
    bootstrap = {"events": [{"id": 1, "is_current": False}]}
    out = take_snapshot(tmp_path, fake_fetch({"bootstrap-static/": bootstrap}), NOW)
    assert not any(p.name.startswith("event-") and "live" in p.name for p in out.iterdir())


def test_failure_leaves_no_complete_snapshot(tmp_path: Path) -> None:
    def fetch(path: str) -> bytes:
        if path == "fixtures/":
            return b"<html>error</html>"
        return json.dumps({"events": []}).encode()

    with pytest.raises(json.JSONDecodeError):
        take_snapshot(tmp_path, fetch, NOW)
    assert not any(p.is_dir() and not p.name.startswith(".") for p in tmp_path.iterdir())


def test_latest_ignores_partial_snapshots(tmp_path: Path) -> None:
    for stamp in ["2026-10-01T090000Z", "2026-10-02T090000Z"]:
        (tmp_path / stamp).mkdir()
    (tmp_path / ".2026-10-03T090000Z.partial").mkdir()

    assert latest_snapshot(tmp_path).name == "2026-10-02T090000Z"
