"""Builders for legal and deliberately broken Plans on the real Snapshot."""

from collections import Counter

from football_agent.data.model import Game
from football_agent.solver.plan import GameweekMoves


def cheapest_legal_squad(game: Game) -> list[int]:
    """15 available players: the cheapest per position, at most one per team."""
    squad: list[int] = []
    teams: Counter[int] = Counter()
    for position in game.rules.positions.values():
        candidates = sorted(
            (
                p
                for p in game.players.values()
                if p.position_id == position.id and p.fpl_status == "a"
            ),
            key=lambda p: (p.price, p.id),
        )
        picked = 0
        for player in candidates:
            if teams[player.team_id] == 0 and picked < position.squad_count:
                squad.append(player.id)
                teams[player.team_id] += 1
                picked += 1
    return squad


def moves_for(game: Game, squad: list[int], **overrides: object) -> GameweekMoves:
    """New-team moves for the next Gameweek, in a 4-4-2 with the backup goalkeeper benched."""
    by_position: dict[str, list[int]] = {}
    for player_id in squad:
        code = game.rules.positions[game.players[player_id].position_id].code
        by_position.setdefault(code, []).append(player_id)
    gk, df, md, fw = (by_position[c] for c in ("GKP", "DEF", "MID", "FWD"))
    starting = (gk[0], *df[:4], *md[:4], *fw[:2])
    bench = (gk[1], df[4], md[4], fw[2])
    moves = dict(
        gameweek_id=game.next_gameweek.id,
        transfers_in=tuple(squad),
        transfers_out=(),
        starting=starting,
        bench=bench,
        captain=starting[-1],
        vice_captain=starting[-2],
        chip=None,
        points_hits=0,
        xp=0.0,
    )
    moves.update(overrides)
    return GameweekMoves(**moves)  # type: ignore[arg-type]
