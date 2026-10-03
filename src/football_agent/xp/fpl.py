"""xP from FPL's own published numbers: the baseline our xP Model must beat.

Next Gameweek: FPL's `ep_next`, which already allows for injuries and doubts.
Later Gameweeks in the Planning Horizon: points per elapsed Gameweek, scaled by
fixture difficulty and the number of fixtures (0 in a Blank, 2 in a Double),
with injured players assumed to recover gradually. Crude on purpose; it only has
to let the Solver run until the xP Model replaces it.
"""

from football_agent.data.model import Fixture, Game, Player

# FPL difficulty rating (1 easy to 5 hard) to a points multiplier.
DIFFICULTY_MULTIPLIER = {1: 1.2, 2: 1.1, 3: 1.0, 4: 0.9, 5: 0.8}

# How much an unavailable player's chance of playing recovers per Gameweek.
RECOVERY_PER_GAMEWEEK = 0.25

XP = dict[int, dict[int, float]]  # player id -> Gameweek id -> xP


def _difficulty(fixture: Fixture, team_id: int) -> int:
    return fixture.home_difficulty if fixture.home_team_id == team_id else fixture.away_difficulty


def _availability(player: Player, weeks_ahead: int) -> float:
    """Chance a player is available, `weeks_ahead` Gameweeks after the next one."""
    if player.status == "a":
        return 1.0
    now = (player.chance_of_playing_next_round or 0) / 100
    return min(1.0, now + RECOVERY_PER_GAMEWEEK * weeks_ahead)


def fpl_xp(game: Game, gameweek_ids: list[int]) -> XP:
    """xP for every player over the given Gameweeks, the first being the next one."""
    if not gameweek_ids or gameweek_ids[0] != game.next_gameweek.id:
        raise ValueError("the horizon must start at the next Gameweek")
    elapsed = sum(gw.finished for gw in game.gameweeks.values())

    xp: XP = {}
    for player in game.players.values():
        per_gameweek = player.total_points / elapsed if elapsed else player.points_per_game
        by_gameweek = {gameweek_ids[0]: player.ep_next}
        for weeks_ahead, gw_id in enumerate(gameweek_ids[1:], start=1):
            fixtures = game.fixtures_for(player.team_id, gw_id)
            fixture_factor = sum(
                DIFFICULTY_MULTIPLIER[_difficulty(f, player.team_id)] for f in fixtures
            )
            by_gameweek[gw_id] = per_gameweek * fixture_factor * _availability(player, weeks_ahead)
        xp[player.id] = by_gameweek
    return xp
