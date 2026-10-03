"""Typed view of a Snapshot: players, teams, Gameweeks, fixtures and the game's rules.

Money is kept in tenths of a million (FPL's own unit, so 75 is £7.5m) as integers,
never floats. Rules are read from the Snapshot, never hard-coded, except the
Points Hit cost, which the API doesn't publish.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from football_agent.data.snapshot import read_json

POINTS_HIT_COST = 4  # points per transfer beyond the free ones; not published by the API


@dataclass(frozen=True)
class Position:
    id: int
    code: str  # GKP, DEF, MID, FWD
    squad_count: int  # exactly this many in a 15-player squad
    min_start: int
    max_start: int


@dataclass(frozen=True)
class Team:
    id: int
    name: str
    short_name: str


@dataclass(frozen=True)
class Player:
    id: int
    name: str  # FPL's display name, e.g. "Saka"
    team_id: int
    position_id: int
    price: int  # tenths of a million
    # FPL's own code, not the Scout's Player Status: a available, d doubtful, i injured,
    # s suspended, u unavailable (usually left the club), n not in the league
    fpl_status: str
    chance_of_playing_next_round: int | None  # FPL's own flag, 0-100, None when no concern
    ep_next: float  # FPL's published xP for the next Gameweek
    points_per_game: float
    total_points: int
    minutes: int


@dataclass(frozen=True)
class Gameweek:
    id: int
    deadline: datetime
    is_current: bool
    is_next: bool
    finished: bool


@dataclass(frozen=True)
class Fixture:
    id: int
    gameweek_id: int | None  # None while unscheduled
    home_team_id: int
    away_team_id: int
    home_difficulty: int  # FPL's difficulty rating for the home team, 1 easy to 5 hard
    away_difficulty: int
    finished: bool


@dataclass(frozen=True)
class Rules:
    squad_size: int
    starting_size: int
    team_limit: int  # most players allowed from one Premier League team
    initial_budget: int  # tenths of a million
    max_free_transfers: int  # most free transfers that can be banked
    sell_on_fee: float  # share of a price rise kept when selling
    points_hit_cost: int
    positions: dict[int, Position]


@dataclass(frozen=True)
class Game:
    """Everything one Snapshot says about the state of the game."""

    rules: Rules
    teams: dict[int, Team]
    players: dict[int, Player]
    gameweeks: dict[int, Gameweek]
    fixtures: list[Fixture]

    @property
    def next_gameweek(self) -> Gameweek:
        upcoming = [gw for gw in self.gameweeks.values() if gw.is_next]
        if not upcoming:
            raise ValueError("no upcoming Gameweek: the season is over")
        return upcoming[0]

    def fixtures_for(self, team_id: int, gameweek_id: int) -> list[Fixture]:
        """A team's fixtures in a Gameweek: none in a Blank, two in a Double."""
        return [
            f
            for f in self.fixtures
            if f.gameweek_id == gameweek_id and team_id in (f.home_team_id, f.away_team_id)
        ]


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_game(snapshot_dir: Path) -> Game:
    bootstrap = read_json(snapshot_dir, "bootstrap-static")
    fixtures = read_json(snapshot_dir, "fixtures")
    if not isinstance(bootstrap, dict) or not isinstance(fixtures, list):
        raise ValueError(f"{snapshot_dir} doesn't look like an FPL Snapshot")
    settings = bootstrap["game_settings"]

    positions = {
        t["id"]: Position(
            id=t["id"],
            code=t["singular_name_short"],
            squad_count=t["squad_select"],
            min_start=t["squad_min_play"],
            max_start=t["squad_max_play"],
        )
        for t in bootstrap["element_types"]
    }
    rules = Rules(
        squad_size=settings["squad_squadsize"],
        starting_size=settings["squad_squadplay"],
        team_limit=settings["squad_team_limit"],
        initial_budget=settings["squad_total_spend"],
        max_free_transfers=1 + settings["max_extra_free_transfers"],
        sell_on_fee=settings["transfers_sell_on_fee"],
        points_hit_cost=POINTS_HIT_COST,
        positions=positions,
    )
    if sum(p.squad_count for p in positions.values()) != rules.squad_size:
        raise ValueError("position counts don't add up to the squad size")

    teams = {t["id"]: Team(t["id"], t["name"], t["short_name"]) for t in bootstrap["teams"]}
    players = {
        e["id"]: Player(
            id=e["id"],
            name=e["web_name"],
            team_id=e["team"],
            position_id=e["element_type"],
            price=e["now_cost"],
            fpl_status=e["status"],
            chance_of_playing_next_round=e["chance_of_playing_next_round"],
            ep_next=float(e["ep_next"] or 0),
            points_per_game=float(e["points_per_game"] or 0),
            total_points=e["total_points"],
            minutes=e["minutes"],
        )
        for e in bootstrap["elements"]
        if not e.get("removed")
    }
    gameweeks = {
        e["id"]: Gameweek(
            id=e["id"],
            deadline=_parse_time(e["deadline_time"]),
            is_current=e["is_current"],
            is_next=e["is_next"],
            finished=e["finished"],
        )
        for e in bootstrap["events"]
    }
    fixture_list = [
        Fixture(
            id=f["id"],
            gameweek_id=f["event"],
            home_team_id=f["team_h"],
            away_team_id=f["team_a"],
            home_difficulty=f["team_h_difficulty"],
            away_difficulty=f["team_a_difficulty"],
            finished=f["finished"],
        )
        for f in fixtures
    ]
    return Game(rules, teams, players, gameweeks, fixture_list)
