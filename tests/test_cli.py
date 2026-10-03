import json
import shutil
from pathlib import Path

import pytest

from football_agent.cli import main

from .conftest import FIXTURE_SNAPSHOT


def test_cli_requires_a_command() -> None:
    with pytest.raises(SystemExit):
        main([])


def test_pick_squad_prints_squad_and_writes_decision(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    snapshots = tmp_path / "raw"
    shutil.copytree(FIXTURE_SNAPSHOT, snapshots / "2026-09-30T135901Z")
    decisions = tmp_path / "decisions"

    code = main(
        ["pick-squad", "--snapshots", str(snapshots), "--decisions", str(decisions), "-k", "1"]
    )

    out = capsys.readouterr().out
    assert code == 0
    for heading in ("GKP", "DEF", "MID", "FWD", "Starting eleven", "Bench, in order", "(C)"):
        assert heading in out
    [record_path] = decisions.iterdir()
    record = json.loads(record_path.read_text())
    assert record["gameweek"] == 6
    assert record["kind"] == "new-squad"
    assert record["snapshot"] == "2026-09-30T135901Z"
    assert len(record["candidate_plans"]) == 1
