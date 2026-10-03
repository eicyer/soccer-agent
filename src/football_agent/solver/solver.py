"""The Solver: a mixed-integer program over the Planning Horizon, returning Candidate Plans.

See docs/design/02-solver-and-xp.md. Not yet modelled: Chips (the Chip Schedule arrives
with the Planner) and Constraints from agents or Instructions.
"""

from dataclasses import dataclass, field

import pulp

from football_agent.data.model import Game
from football_agent.solver.plan import GameweekMoves, Plan, TeamState, selling_price
from football_agent.xp.fpl import XP

DISCOUNT = 0.85  # later Gameweeks' xP counts for less: it's less certain
BENCH_WEIGHT = 0.1  # bench xP counts a little, to value cover
CLOSE_CALL_XP = 1.0  # Candidate Plans this close are a Close Call
TIME_LIMIT_SECONDS = 60


@dataclass(frozen=True)
class SolverSettings:
    discount: float = DISCOUNT
    bench_weight: float = BENCH_WEIGHT
    time_limit: int = TIME_LIMIT_SECONDS


@dataclass(frozen=True)
class CandidatePlans:
    plans: list[Plan]
    excluded: list[str] = field(default_factory=list)

    @property
    def is_close_call(self) -> bool:
        return len(self.plans) > 1 and self.plans[0].xp - self.plans[1].xp <= CLOSE_CALL_XP


class Infeasible(Exception):
    pass


class NotProvenOptimal(Exception):
    """The time limit ended the solve before optimality was proven."""


def candidate_plans(
    game: Game,
    state: TeamState,
    xp: XP,
    horizon: list[int],
    k: int = 5,
    settings: SolverSettings | None = None,
) -> CandidatePlans:
    """The top k Plans, each differing from the others in its first Gameweek's squad or captain."""
    model = _Model(game, state, xp, horizon, settings or SolverSettings())
    plans: list[Plan] = []
    for _ in range(k):
        plan = model.solve()
        if plan is None:
            break
        plans.append(plan)
        model.exclude_first_gameweek(plan.first)
    if not plans:
        raise Infeasible("no legal Plan exists for this team state")
    return CandidatePlans(plans)


class _Model:
    def __init__(
        self, game: Game, state: TeamState, xp: XP, horizon: list[int], settings: SolverSettings
    ) -> None:
        self.game, self.xp, self.horizon, self.settings = game, xp, horizon, settings
        rules = game.rules
        # Players who can't score in the horizon only slow the solve, unless already owned.
        players = [
            pl
            for pl in game.players.values()
            if pl.id in state.squad or sum(xp[pl.id].get(week, 0.0) for week in horizon) > 0
        ]
        self.players = players
        ids = [p.id for p in players]
        weeks = horizon
        first = weeks[0]

        self.problem = pulp.LpProblem("fpl", pulp.LpMaximize)
        binary = {"cat": "Binary"}
        self.squad = pulp.LpVariable.dicts("squad", (ids, weeks), **binary)
        self.start = pulp.LpVariable.dicts("start", (ids, weeks), **binary)
        self.captain = pulp.LpVariable.dicts("captain", (ids, weeks), **binary)
        self.buy = pulp.LpVariable.dicts("buy", (ids, weeks), **binary)
        self.sell = pulp.LpVariable.dicts("sell", (ids, weeks), **binary)
        self.hits = pulp.LpVariable.dicts("hits", weeks, lowBound=0, cat="Integer")
        self.free = pulp.LpVariable.dicts(
            "free", weeks, lowBound=0, upBound=rules.max_free_transfers, cat="Integer"
        )
        self.bank = pulp.LpVariable.dicts("bank", weeks, lowBound=0)
        # 1 when a Gameweek uses more transfers than it has free (whether or not a hit is due).
        self.over = pulp.LpVariable.dicts("over", weeks, cat="Binary")
        big = rules.squad_size + rules.max_free_transfers
        p = self.problem

        def buy_price(pid: int) -> int:
            return game.players[pid].price

        def sell_price(pid: int) -> int:
            if pid in state.squad:
                return selling_price(game.players[pid], state.squad[pid], rules.sell_on_fee)
            return game.players[pid].price

        for i, week in enumerate(weeks):
            previous = weeks[i - 1] if i else None
            for pid in ids:
                was_in = self.squad[pid][previous] if previous else (1 if pid in state.squad else 0)
                p += self.squad[pid][week] == was_in + self.buy[pid][week] - self.sell[pid][week]
                p += self.buy[pid][week] + self.sell[pid][week] <= 1
                p += self.start[pid][week] <= self.squad[pid][week]
                p += self.captain[pid][week] <= self.start[pid][week]

            # Squad shape and lineup.
            p += pulp.lpSum(self.squad[pid][week] for pid in ids) == rules.squad_size
            p += pulp.lpSum(self.start[pid][week] for pid in ids) == rules.starting_size
            p += pulp.lpSum(self.captain[pid][week] for pid in ids) == 1
            for position in rules.positions.values():
                at = [pl.id for pl in players if pl.position_id == position.id]
                p += pulp.lpSum(self.squad[pid][week] for pid in at) == position.squad_count
                p += pulp.lpSum(self.start[pid][week] for pid in at) >= position.min_start
                p += pulp.lpSum(self.start[pid][week] for pid in at) <= position.max_start
            for team_id in game.teams:
                at = [pl.id for pl in players if pl.team_id == team_id]
                p += pulp.lpSum(self.squad[pid][week] for pid in at) <= rules.team_limit

            # Money: the bank carries over, selling at selling prices and buying at current ones.
            bank_before = self.bank[previous] if previous else state.bank
            p += self.bank[week] == bank_before + pulp.lpSum(
                sell_price(pid) * self.sell[pid][week] - buy_price(pid) * self.buy[pid][week]
                for pid in ids
            )

            # A new team's first squad is free; otherwise free transfers, then Points Hits.
            transfers = pulp.lpSum(self.buy[pid][week] for pid in ids)
            if week == first and state.is_new:
                p += self.hits[week] == 0
                p += self.free[week] == 0
            else:
                free_now = self.free[week]
                if week == first:
                    p += free_now == state.free_transfers
                p += self.hits[week] >= transfers - free_now
                p += self.hits[week] <= big * self.over[week]
                p += transfers - free_now <= big * self.over[week]
            if i + 1 < len(weeks):
                after = self.free[weeks[i + 1]]
                if week == first and state.is_new:
                    p += after == 1
                else:
                    # Unused free transfers roll over, one more each Gameweek, up to the cap.
                    # Going over (paying hits) leaves exactly one for next time; a hit never
                    # buys extra free transfers.
                    p += after <= self.free[week] - transfers + 1 + big * self.over[week]
                    p += after <= 1 + big * (1 - self.over[week])
                    p += after >= 1

        # Can't sell what you don't own. Players owned now are never bought within the
        # horizon either: buying one back after selling would reset its selling price.
        for pid in ids:
            if pid not in state.squad:
                p += self.sell[pid][first] == 0
            else:
                for week in weeks:
                    p += self.buy[pid][week] == 0

        objective = []
        for i, week in enumerate(weeks):
            weight = settings.discount**i
            for pid in ids:
                points = xp[pid].get(week, 0.0)
                objective.append(
                    weight
                    * points
                    * (
                        self.start[pid][week]
                        + self.captain[pid][week]
                        + settings.bench_weight * (self.squad[pid][week] - self.start[pid][week])
                    )
                )
            objective.append(-weight * rules.points_hit_cost * self.hits[week])
        p += pulp.lpSum(objective)

    def exclude_first_gameweek(self, moves: GameweekMoves) -> None:
        week = self.horizon[0]
        chosen = [self.squad[pid][week] for pid in moves.squad]
        p = self.problem
        p += pulp.lpSum([*chosen, self.captain[moves.captain][week]]) <= len(chosen)

    def solve(self) -> Plan | None:
        self.problem.solve(pulp.HiGHS(msg=False, timeLimit=self.settings.time_limit))
        # PuLP reports a time-limited solve as "Optimal"; the solution status tells the truth.
        if self.problem.sol_status == pulp.LpSolutionOptimal:
            return self._read_plan()
        if pulp.LpStatus[self.problem.status] == "Infeasible":
            return None
        raise NotProvenOptimal(
            f"solver stopped after {self.settings.time_limit}s without proving optimality "
            f"(status {pulp.LpStatus[self.problem.status]}, solution {self.problem.sol_status})"
        )

    def _read_plan(self) -> Plan:
        rules = self.game.rules
        gameweeks = []
        for week in self.horizon:

            def on(var: dict, week: int = week) -> bool:
                return var[week].value() > 0.5

            squad = [pl for pl in self.players if on(self.squad[pl.id])]
            starting = [pl for pl in squad if on(self.start[pl.id])]
            captain = next(pl for pl in starting if on(self.captain[pl.id]))
            points = {pl.id: self.xp[pl.id].get(week, 0.0) for pl in squad}
            vice = max((pl for pl in starting if pl.id != captain.id), key=lambda pl: points[pl.id])
            goalkeeper = next(pos.id for pos in rules.positions.values() if pos.code == "GKP")
            benched = [pl for pl in squad if pl not in starting]
            bench = sorted(benched, key=lambda pl: (pl.position_id != goalkeeper, -points[pl.id]))
            gameweeks.append(
                GameweekMoves(
                    gameweek_id=week,
                    transfers_in=tuple(pl.id for pl in self.players if on(self.buy[pl.id])),
                    transfers_out=tuple(pl.id for pl in self.players if on(self.sell[pl.id])),
                    starting=tuple(
                        pl.id
                        for pl in sorted(starting, key=lambda pl: (pl.position_id, -points[pl.id]))
                    ),
                    bench=tuple(pl.id for pl in bench),
                    captain=captain.id,
                    vice_captain=vice.id,
                    chip=None,
                    points_hits=round(self.hits[week].value()),
                    xp=sum(points[pl.id] for pl in starting) + points[captain.id],
                )
            )
        return Plan(tuple(gameweeks), pulp.value(self.problem.objective))
