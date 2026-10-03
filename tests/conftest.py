from pathlib import Path

import pytest

from football_agent.data.model import Game, load_game

FIXTURE_SNAPSHOT = Path(__file__).parent / "fixtures" / "snapshot"


@pytest.fixture(scope="session")
def real_game() -> Game:
    """The Snapshot of 2026-09-30, committed so tests don't depend on the network."""
    return load_game(FIXTURE_SNAPSHOT)
