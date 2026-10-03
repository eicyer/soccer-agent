from dataclasses import replace

import pytest

from football_agent.data.model import Game
from football_agent.solver.plan import TeamState
from football_agent.solver.rule_check import rule_check
from football_agent.solver.solver import candidate_plans
from football_agent.xp.fpl import fpl_xp

HORIZON = [6, 7, 8, 9, 10]


@pytest.fixture(scope="module")
def new_team_plans(real_game: Game):
    return candidate_plans(
        real_game, TeamState.new(real_game), fpl_xp(real_game, HORIZON), HORIZON, k=3
    )


def test_new_team_plans_are_legal(real_game: Game, new_team_plans) -> None:
    state = TeamState.new(real_game)
    for plan in new_team_plans.plans:
        assert rule_check(real_game, state, plan.first) == []


def test_plans_are_ranked_and_distinct(new_team_plans) -> None:
    plans = new_team_plans.plans
    assert len(plans) == 3
    assert plans[0].xp >= plans[1].xp >= plans[2].xp
    firsts = {(p.first.squad, p.first.captain) for p in plans}
    assert len(firsts) == 3


def test_later_gameweeks_follow_free_transfer_rules(real_game: Game, new_team_plans) -> None:
    plan = new_team_plans.plans[0]
    # Replay the horizon: each later Gameweek must be a legal step from the one before.
    squad = {pid: real_game.players[pid].price for pid in plan.first.squad}
    bank = real_game.rules.initial_budget - sum(squad.values())
    free = 1
    for moves in plan.gameweeks[1:]:
        assert set(moves.transfers_out) <= set(squad)
        assert moves.points_hits == max(0, len(moves.transfers_in) - free)
        bank += sum(real_game.players[p].price for p in moves.transfers_out)
        bank -= sum(real_game.players[p].price for p in moves.transfers_in)
        assert bank >= 0
        for pid in moves.transfers_out:
            del squad[pid]
        for pid in moves.transfers_in:
            squad[pid] = real_game.players[pid].price
        assert set(squad) == moves.squad
        free = min(
            real_game.rules.max_free_transfers,
            free - len(moves.transfers_in) + moves.points_hits + 1,
        )


def test_existing_team_plan_is_legal_and_uses_free_transfers(
    real_game: Game, new_team_plans
) -> None:
    squad = new_team_plans.plans[0].first.squad
    spent = sum(real_game.players[p].price for p in squad)
    state = TeamState(
        squad={p: real_game.players[p].price for p in squad},
        bank=real_game.rules.initial_budget - spent,
        free_transfers=2,
        chips_available=frozenset(),
    )
    plans = candidate_plans(real_game, state, fpl_xp(real_game, HORIZON), HORIZON, k=2)
    for plan in plans.plans:
        assert rule_check(real_game, state, plan.first) == []


def test_injured_player_is_not_started(real_game: Game) -> None:
    xp = fpl_xp(real_game, HORIZON)
    star = max(real_game.players.values(), key=lambda p: xp[p.id][6])
    injured = replace(real_game, players={**real_game.players})
    xp[star.id] = {gw: 0.0 for gw in HORIZON}
    plan = candidate_plans(injured, TeamState.new(injured), xp, HORIZON, k=1).plans[0]
    assert star.id not in plan.first.starting
