import pytest

from football_agent.data.model import Game
from football_agent.solver.plan import TeamState, advance
from football_agent.solver.rule_check import check_plan
from football_agent.solver.solver import SolverSettings, candidate_plans
from football_agent.xp.fpl import XP, fpl_xp

HORIZON = [6, 7, 8, 9, 10]


@pytest.fixture(scope="module")
def xp(real_game: Game) -> XP:
    return fpl_xp(real_game, HORIZON)


@pytest.fixture(scope="module")
def new_team_plans(real_game: Game, xp: XP):
    return candidate_plans(real_game, TeamState.new(real_game), xp, HORIZON, k=3)


@pytest.fixture(scope="module")
def existing_team(real_game: Game, new_team_plans) -> TeamState:
    """The best new squad, registered, with some players' prices since risen."""
    state = advance(real_game, TeamState.new(real_game), new_team_plans.plans[0].first)
    risen = {p: price - 3 for p, price in list(state.squad.items())[:5]}
    return TeamState(
        squad={**state.squad, **risen},
        bank=state.bank,
        free_transfers=2,
        chips_available=frozenset(),
    )


def test_new_team_plans_are_legal_across_the_horizon(real_game: Game, new_team_plans) -> None:
    for plan in new_team_plans.plans:
        assert check_plan(real_game, TeamState.new(real_game), plan) == []


def test_plans_are_ranked_and_distinct(new_team_plans) -> None:
    plans = new_team_plans.plans
    assert len(plans) == 3
    assert plans[0].xp >= plans[1].xp >= plans[2].xp
    assert len({(p.first.squad, p.first.captain) for p in plans}) == 3


def test_existing_team_plans_are_legal_across_the_horizon(
    real_game: Game, existing_team: TeamState, xp: XP
) -> None:
    plans = candidate_plans(real_game, existing_team, xp, HORIZON, k=2)
    for plan in plans.plans:
        assert check_plan(real_game, existing_team, plan) == []


@pytest.mark.parametrize("discount", [1.0, 1.2])
def test_points_hits_never_bank_free_transfers(
    real_game: Game, existing_team: TeamState, xp: XP, discount: float
) -> None:
    # Valuing later Gameweeks as much as (or more than) this one is when a hit
    # bought only to bank a free transfer would pay, if the model allowed it.
    settings = SolverSettings(discount=discount)
    plan = candidate_plans(real_game, existing_team, xp, HORIZON, k=1, settings=settings).plans[0]
    assert check_plan(real_game, existing_team, plan) == []


def test_takes_a_points_hit_when_it_pays(real_game: Game, existing_team: TeamState, xp: XP) -> None:
    owned_ids = set(existing_team.squad)
    boosted = dict(xp)
    stars = sorted(
        (p for p in real_game.players.values() if p.id not in owned_ids and p.price <= 45),
        key=lambda p: p.id,
    )
    # Three cheap outsiders who will score 30 next Gameweek: worth two free transfers and a hit.
    for star in [s for s in stars if s.position_id == 3][:3]:
        boosted[star.id] = {**xp[star.id], 6: 30.0}
    state = TeamState(existing_team.squad, existing_team.bank, 2, frozenset())
    plan = candidate_plans(real_game, state, boosted, HORIZON, k=1).plans[0]
    assert len(plan.first.transfers_in) == 3
    assert plan.first.points_hits == 1
    assert check_plan(real_game, state, plan) == []


def test_injured_player_is_not_started(real_game: Game, xp: XP) -> None:
    star = max(real_game.players.values(), key=lambda p: xp[p.id][6])
    without_star = {**xp, star.id: {gw: 0.0 for gw in HORIZON}}
    plan = candidate_plans(real_game, TeamState.new(real_game), without_star, HORIZON, k=1)
    assert star.id not in plan.plans[0].first.starting


def test_formulation_hit_cannot_bank_a_free_transfer(
    real_game: Game, existing_team: TeamState, xp: XP
) -> None:
    import pulp

    from football_agent.solver.solver import _Model

    state = TeamState(existing_team.squad, existing_team.bank, 1, frozenset())
    model = _Model(real_game, state, xp, HORIZON, SolverSettings())
    first, second = HORIZON[:2]
    # Force a pointless Points Hit with no transfers in the first Gameweek.
    model.problem += model.hits[first] == 1
    model.problem += pulp.lpSum(model.buy[p.id][first] for p in model.players) == 0
    model.problem += model.free[second] >= 3
    assert model.solve() is None  # one unused free transfer rolls into two, never three


def test_formulation_cannot_buy_and_sell_in_one_gameweek(
    real_game: Game, existing_team: TeamState, xp: XP
) -> None:
    from football_agent.solver.solver import _Model

    outsider = next(p for p in real_game.players.values() if p.id not in existing_team.squad)
    model = _Model(real_game, existing_team, xp, HORIZON, SolverSettings())
    week = HORIZON[1]
    model.problem += model.buy[outsider.id][week] == 1
    model.problem += model.sell[outsider.id][week] == 1
    assert model.solve() is None
