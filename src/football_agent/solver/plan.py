"""Plans and the team state they start from (see CONTEXT.md: Plan, Planning Horizon)."""

from dataclasses import dataclass

from football_agent.data.model import Game, Player

CHIPS = ("wildcard", "freehit", "bboost", "3xc")
FREE_TRANSFER_CHIPS = frozenset({"wildcard", "freehit"})  # their transfers are free


@dataclass(frozen=True)
class TeamState:
    """The real team just before a Gameweek's deadline."""

    squad: dict[int, int]  # player id -> purchase price, tenths of a million
    bank: int  # tenths of a million
    free_transfers: int
    chips_available: frozenset[str]

    @property
    def is_new(self) -> bool:
        """A team not yet registered: its first squad costs no transfers."""
        return not self.squad

    @classmethod
    def new(cls, game: Game, chips_available: frozenset[str] = frozenset(CHIPS)) -> "TeamState":
        return cls({}, game.rules.initial_budget, 0, chips_available)


@dataclass(frozen=True)
class GameweekMoves:
    """A Plan's moves for one Gameweek."""

    gameweek_id: int
    transfers_in: tuple[int, ...]
    transfers_out: tuple[int, ...]
    starting: tuple[int, ...]  # 11 player ids
    bench: tuple[int, ...]  # 4 player ids in bench order; the goalkeeper first
    captain: int
    vice_captain: int
    chip: str | None
    points_hits: int  # number of paid transfers
    xp: float

    @property
    def squad(self) -> frozenset[int]:
        return frozenset(self.starting) | frozenset(self.bench)


@dataclass(frozen=True)
class Plan:
    """Moves for every Gameweek in the Planning Horizon. Only the first is executed."""

    gameweeks: tuple[GameweekMoves, ...]
    xp: float  # the Solver's objective: discounted xP over the horizon, net of Points Hits

    @property
    def first(self) -> GameweekMoves:
        return self.gameweeks[0]


def advance(game: Game, state: TeamState, moves: GameweekMoves) -> TeamState:
    """The team state after a Gameweek's moves, ready for the next Gameweek.

    Prices are held at today's values across the horizon; Free Hit's squad reversion
    isn't modelled yet (chips arrive with the Chip Schedule).
    """
    rules = game.rules
    proceeds = sum(
        selling_price(game.players[p], state.squad[p], rules.sell_on_fee)
        for p in moves.transfers_out
    )
    cost = sum(game.players[p].price for p in moves.transfers_in)
    squad = {p: price for p, price in state.squad.items() if p not in moves.transfers_out}
    squad.update({p: game.players[p].price for p in moves.transfers_in})

    used = 0 if moves.chip in FREE_TRANSFER_CHIPS else len(moves.transfers_in)
    if state.is_new:
        free = 1
    else:
        # Unused free transfers roll over, one more each Gameweek, up to the cap.
        free = min(rules.max_free_transfers, max(0, state.free_transfers - used) + 1)
    chips = state.chips_available - {moves.chip} if moves.chip else state.chips_available
    return TeamState(squad, state.bank + proceeds - cost, free, chips)


def selling_price(player: Player, purchase_price: int, sell_on_fee: float) -> int:
    """FPL keeps a share of any rise (rounded down) and passes on every fall."""
    if player.price <= purchase_price:
        return player.price
    return purchase_price + int((player.price - purchase_price) * sell_on_fee)
