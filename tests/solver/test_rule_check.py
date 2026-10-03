from dataclasses import replace

import pytest

from football_agent.data.model import Game
from football_agent.solver.plan import TeamState, selling_price
from football_agent.solver.rule_check import rule_check

from .helpers import cheapest_legal_squad, moves_for


@pytest.fixture
def squad(real_game: Game) -> list[int]:
    return cheapest_legal_squad(real_game)


def existing_team(game: Game, squad: list[int], **overrides: object) -> TeamState:
    state = dict(
        squad={p: game.players[p].price for p in squad},
        bank=0,
        free_transfers=1,
        chips_available=frozenset({"wildcard", "freehit", "bboost", "3xc"}),
    )
    state.update(overrides)
    return TeamState(**state)  # type: ignore[arg-type]


def swap(game: Game, squad: list[int], out_id: int) -> int:
    """A same-position, same-price-or-cheaper player not in the squad and from a new team."""
    out = game.players[out_id]
    teams = {game.players[p].team_id for p in squad}
    return next(
        p.id
        for p in sorted(game.players.values(), key=lambda p: p.price)
        if p.position_id == out.position_id
        and p.id not in squad
        and p.team_id not in teams
        and p.price <= out.price
    )


def test_legal_new_squad_passes(real_game: Game, squad: list[int]) -> None:
    assert rule_check(real_game, TeamState.new(real_game), moves_for(real_game, squad)) == []


def test_squad_must_have_fifteen_players(real_game: Game, squad: list[int]) -> None:
    moves = moves_for(real_game, squad)
    short = replace(moves, transfers_in=moves.transfers_in[:-1], bench=moves.bench[:-1])
    assert any("15 players" in v for v in rule_check(real_game, TeamState.new(real_game), short))


def test_position_counts(real_game: Game, squad: list[int]) -> None:
    moves = moves_for(real_game, squad)
    extra_forward = next(
        p.id for p in real_game.players.values() if p.position_id == 4 and p.id not in squad
    )
    # Swap the benched midfielder for a fourth forward.
    bench = (moves.bench[0], moves.bench[1], extra_forward, moves.bench[3])
    broken = replace(
        moves,
        transfers_in=(*moves.starting, *bench),
        bench=bench,
    )
    violations = rule_check(real_game, TeamState.new(real_game), broken)
    assert any("FWD" in v for v in violations)


def test_team_limit(real_game: Game, squad: list[int]) -> None:
    moves = moves_for(real_game, squad)
    team_id = real_game.players[moves.starting[1]].team_id
    same_team = [
        p.id
        for p in real_game.players.values()
        if p.team_id == team_id and p.position_id == 2 and p.id not in squad
    ][:3]
    defenders = [moves.starting[1], *same_team]
    starting = (moves.starting[0], *defenders, *moves.starting[5:])
    broken = replace(moves, starting=starting, transfers_in=(*starting, *moves.bench))
    violations = rule_check(real_game, TeamState.new(real_game), broken)
    assert any("at most 3" in v for v in violations)


def test_budget(real_game: Game, squad: list[int]) -> None:
    poor = replace(TeamState.new(real_game), bank=100)
    violations = rule_check(real_game, poor, moves_for(real_game, squad))
    assert any("budget" in v for v in violations)


def test_formation(real_game: Game, squad: list[int]) -> None:
    moves = moves_for(real_game, squad)
    # Start the backup goalkeeper instead of a forward: two goalkeepers, one forward.
    starting = (*moves.starting[:-1], moves.bench[0])
    bench = (moves.starting[-1], *moves.bench[1:])
    broken = replace(moves, starting=starting, bench=bench, captain=starting[-2])
    violations = rule_check(real_game, TeamState.new(real_game), broken)
    assert any("GKP" in v for v in violations)
    assert any("goalkeeper first" in v for v in violations)


def test_captain_and_vice_must_start_and_differ(real_game: Game, squad: list[int]) -> None:
    moves = moves_for(real_game, squad)
    benched = replace(moves, captain=moves.bench[1])
    same = replace(moves, vice_captain=moves.captain)
    assert any("captain" in v for v in rule_check(real_game, TeamState.new(real_game), benched))
    assert any("vice" in v for v in rule_check(real_game, TeamState.new(real_game), same))


def test_transfers_must_match_the_squad(real_game: Game, squad: list[int]) -> None:
    state = existing_team(real_game, squad)
    out_id = squad[5]
    in_id = swap(real_game, squad, out_id)
    new_squad = [in_id if p == out_id else p for p in squad]
    moves = moves_for(real_game, new_squad, transfers_in=(in_id,), transfers_out=(out_id,))
    assert rule_check(real_game, state, moves) == []

    wrong = replace(moves, transfers_out=(squad[6],))
    assert any("don't produce" in v for v in rule_check(real_game, state, wrong))


def test_points_hits_must_match_transfers(real_game: Game, squad: list[int]) -> None:
    state = existing_team(real_game, squad, free_transfers=1)
    outs = squad[5:7]
    ins = []
    current = list(squad)
    for out_id in outs:
        in_id = swap(real_game, [*current, *squad], out_id)  # never buy back a sold player
        current = [in_id if p == out_id else p for p in current]
        ins.append(in_id)
    moves = moves_for(real_game, current, transfers_in=tuple(ins), transfers_out=tuple(outs))
    assert any("Points Hit" in v for v in rule_check(real_game, state, moves))
    assert rule_check(real_game, state, replace(moves, points_hits=1)) == []
    wildcard = replace(moves, chip="wildcard")
    assert rule_check(real_game, state, wildcard) == []


def test_chip_must_be_available(real_game: Game, squad: list[int]) -> None:
    state = existing_team(real_game, squad, chips_available=frozenset())
    moves = moves_for(real_game, squad, transfers_in=(), chip="bboost")
    assert any("chip" in v for v in rule_check(real_game, state, moves))


def test_selling_price_keeps_half_of_a_rise_rounded_down(real_game: Game) -> None:
    player = replace(real_game.players[1], price=63)
    assert selling_price(player, 60, 0.5) == 61
    assert selling_price(replace(player, price=58), 60, 0.5) == 58
