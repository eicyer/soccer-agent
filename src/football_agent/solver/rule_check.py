"""The Rule Check: is a Gameweek's moves legal? Plain code that trusts nobody, the Solver included.

Returns every rule broken, in words, so a failure explains itself in logs and Memos.
"""

from collections import Counter

from football_agent.data.model import Game
from football_agent.solver.plan import GameweekMoves, TeamState, selling_price

FREE_TRANSFER_CHIPS = {"wildcard", "freehit"}


def rule_check(game: Game, state: TeamState, moves: GameweekMoves) -> list[str]:
    rules = game.rules
    violations: list[str] = []

    if moves.gameweek_id != game.next_gameweek.id:
        violations.append(f"moves are for Gameweek {moves.gameweek_id}, not the next one")

    unknown = [
        p for p in (*moves.starting, *moves.bench, *moves.transfers_in) if p not in game.players
    ]
    if unknown:
        return [*violations, f"unknown players: {unknown}"]

    # Transfers must turn the current squad into the Plan's squad.
    if set(moves.transfers_out) - set(state.squad):
        violations.append("selling players who aren't in the squad")
    if set(moves.transfers_in) & set(state.squad):
        violations.append("buying players already in the squad")
    expected = (set(state.squad) - set(moves.transfers_out)) | set(moves.transfers_in)
    if expected != moves.squad:
        violations.append("the transfers don't produce the Plan's squad")
    if len(moves.starting) + len(moves.bench) != len(moves.squad):
        violations.append("a player appears twice in the lineup")

    # Squad shape.
    if len(moves.squad) != rules.squad_size:
        violations.append(
            f"the squad has {len(moves.squad)} players, not {rules.squad_size} players"
        )
    in_squad = Counter(game.players[p].position_id for p in moves.squad)
    for position in rules.positions.values():
        if in_squad[position.id] != position.squad_count:
            violations.append(
                f"the squad has {in_squad[position.id]} {position.code}, not {position.squad_count}"
            )
    per_team = Counter(game.players[p].team_id for p in moves.squad)
    for team_id, count in per_team.items():
        if count > rules.team_limit:
            violations.append(
                f"{count} players from {game.teams[team_id].name}; "
                f"at most {rules.team_limit} allowed"
            )

    # Budget: bank plus selling prices must cover what is bought.
    proceeds = sum(
        selling_price(game.players[p], state.squad[p], rules.sell_on_fee)
        for p in moves.transfers_out
        if p in state.squad
    )
    cost = sum(game.players[p].price for p in moves.transfers_in)
    if state.bank + proceeds - cost < 0:
        violations.append(f"over budget by £{(cost - proceeds - state.bank) / 10:.1f}m")

    # Starting eleven and bench.
    if len(moves.starting) != rules.starting_size:
        violations.append(f"{len(moves.starting)} starters, not {rules.starting_size}")
    starting = Counter(game.players[p].position_id for p in moves.starting)
    for position in rules.positions.values():
        if not position.min_start <= starting[position.id] <= position.max_start:
            violations.append(
                f"{starting[position.id]} {position.code} starting; "
                f"must be {position.min_start} to {position.max_start}"
            )
    goalkeeper = next(p.id for p in rules.positions.values() if p.code == "GKP")
    if moves.bench and game.players[moves.bench[0]].position_id != goalkeeper:
        violations.append("the bench must list the goalkeeper first")

    if moves.captain not in moves.starting:
        violations.append("the captain isn't in the starting eleven")
    if moves.vice_captain not in moves.starting or moves.vice_captain == moves.captain:
        violations.append("the vice-captain must be a different starter")

    # Chips and Points Hits.
    if moves.chip is not None and moves.chip not in state.chips_available:
        violations.append(f"chip {moves.chip} isn't available")
    if state.is_new or moves.chip in FREE_TRANSFER_CHIPS:
        due_hits = 0
    else:
        if len(moves.transfers_in) != len(moves.transfers_out):
            violations.append("buying and selling different numbers of players")
        due_hits = max(0, len(moves.transfers_in) - state.free_transfers)
    if moves.points_hits != due_hits:
        violations.append(f"the Plan records {moves.points_hits} Points Hits; {due_hits} are due")

    return violations
