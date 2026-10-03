"""Human-readable views of Plans, in the order the FPL app asks for things."""

from football_agent.data.model import Game
from football_agent.solver.plan import GameweekMoves


def _line(game: Game, player_id: int, xp: float | None = None) -> str:
    player = game.players[player_id]
    team = game.teams[player.team_id].short_name
    text = f"{player.name:<16} {team:<4} £{player.price / 10:.1f}m"
    return f"{text}  xP {xp:.1f}" if xp is not None else text


def squad_entry_report(game: Game, moves: GameweekMoves, xp: dict[int, float]) -> str:
    """What to enter when registering a new team: the squad by position, then the lineup."""
    lines = [f"Squad for Gameweek {moves.gameweek_id}, by position (as the FPL app asks):"]
    for position in game.rules.positions.values():
        players = sorted(
            (p for p in moves.squad if game.players[p].position_id == position.id),
            key=lambda p: -xp[p],
        )
        lines.append(f"  {position.code}")
        lines += [f"    {_line(game, p)}" for p in players]
    cost = sum(game.players[p].price for p in moves.squad)
    budget = game.rules.initial_budget
    lines.append(f"  Cost £{cost / 10:.1f}m, leaving £{(budget - cost) / 10:.1f}m in the bank")

    lines.append("")
    lines.append("Pick Team:")
    lines.append("  Starting eleven")
    for p in moves.starting:
        tag = " (C)" if p == moves.captain else " (V)" if p == moves.vice_captain else ""
        lines.append(f"    {_line(game, p, xp[p])}{tag}")
    lines.append("  Bench, in order")
    for i, p in enumerate(moves.bench, start=1):
        lines.append(f"    {i}. {_line(game, p, xp[p])}")
    lines.append(f"  xP this Gameweek {moves.xp:.1f}")
    return "\n".join(lines)
