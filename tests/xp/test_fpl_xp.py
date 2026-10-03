from dataclasses import replace

import pytest

from football_agent.data.model import Fixture, Game
from football_agent.xp.fpl import fpl_xp

HORIZON = [6, 7, 8, 9, 10]


def test_next_gameweek_uses_fpl_ep_next(real_game: Game) -> None:
    xp = fpl_xp(real_game, HORIZON)
    assert all(xp[p.id][6] == p.ep_next for p in real_game.players.values())


def test_injured_player_recovers_over_the_horizon(real_game: Game) -> None:
    injured = next(
        p
        for p in real_game.players.values()
        if p.fpl_status == "i" and p.chance_of_playing_next_round == 0 and p.total_points > 10
    )
    xp = fpl_xp(real_game, HORIZON)[injured.id]
    assert xp[6] == 0
    assert 0 < xp[7] < xp[10] or xp[10] == 0  # 0 only if the team blanks


def test_blank_scores_zero_and_double_scores_more(real_game: Game) -> None:
    team_id = 1
    fixtures = [
        f
        for f in real_game.fixtures
        if not (f.gameweek_id == 8 and team_id in (f.home_team_id, f.away_team_id))
    ]
    blank = replace(real_game, fixtures=fixtures)
    double_fixture = Fixture(9999, 9, team_id, 2, 3, 3, False)
    double = replace(real_game, fixtures=[*real_game.fixtures, double_fixture])

    player = next(
        p for p in real_game.players.values() if p.team_id == team_id and p.total_points > 10
    )
    assert fpl_xp(blank, HORIZON)[player.id][8] == 0
    assert fpl_xp(double, HORIZON)[player.id][9] > fpl_xp(real_game, HORIZON)[player.id][9]


def test_horizon_must_start_at_next_gameweek(real_game: Game) -> None:
    with pytest.raises(ValueError):
        fpl_xp(real_game, [7, 8])


@pytest.mark.parametrize("fpl_status", ["u", "n"])
def test_players_who_left_never_come_back(real_game: Game, fpl_status: str) -> None:
    scorer = max(real_game.players.values(), key=lambda p: p.total_points)
    gone = replace(scorer, fpl_status=fpl_status, chance_of_playing_next_round=None, ep_next=0.0)
    game = replace(real_game, players={**real_game.players, scorer.id: gone})
    assert all(points == 0 for points in fpl_xp(game, HORIZON)[scorer.id].values())
