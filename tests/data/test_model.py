from datetime import UTC, datetime

from football_agent.data.model import Game


def test_rules_come_from_the_snapshot(real_game: Game) -> None:
    rules = real_game.rules
    assert (rules.squad_size, rules.starting_size, rules.team_limit) == (15, 11, 3)
    assert rules.initial_budget == 1000
    assert rules.max_free_transfers == 5
    counts = {p.code: (p.squad_count, p.min_start, p.max_start) for p in rules.positions.values()}
    assert counts == {"GKP": (2, 1, 1), "DEF": (5, 3, 5), "MID": (5, 2, 5), "FWD": (3, 1, 3)}


def test_players_teams_and_gameweeks(real_game: Game) -> None:
    assert len(real_game.teams) == 20
    assert len(real_game.players) == 667
    raya = real_game.players[1]
    assert (raya.name, raya.position_id, raya.price) == ("Raya", 1, 61)
    assert len(real_game.gameweeks) == 38
    assert real_game.next_gameweek.id == 6
    assert real_game.next_gameweek.deadline == datetime(2026, 10, 10, 10, 0, tzinfo=UTC)


def test_every_team_plays_once_in_a_normal_gameweek(real_game: Game) -> None:
    for team_id in real_game.teams:
        assert len(real_game.fixtures_for(team_id, 7)) == 1
