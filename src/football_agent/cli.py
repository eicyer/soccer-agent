"""Command-line entry point."""

import argparse
import sys
from pathlib import Path

from football_agent.data.model import load_game
from football_agent.data.snapshot import latest_snapshot, take_snapshot
from football_agent.decision_log import write_decision
from football_agent.report import squad_entry_report
from football_agent.solver.plan import TeamState
from football_agent.solver.rule_check import check_plan
from football_agent.solver.solver import candidate_plans
from football_agent.xp.fpl import fpl_xp

HORIZON_LENGTH = 5


def _snapshot(args: argparse.Namespace) -> int:
    out = take_snapshot(args.out)
    print(out)
    return 0


def _pick_squad(args: argparse.Namespace) -> int:
    snapshot_dir = take_snapshot(args.snapshots) if args.fresh else latest_snapshot(args.snapshots)
    game = load_game(snapshot_dir)
    first = game.next_gameweek.id
    horizon = [gw for gw in range(first, first + HORIZON_LENGTH) if gw in game.gameweeks]
    xp = fpl_xp(game, horizon)
    state = TeamState.new(game)

    candidates = candidate_plans(game, state, xp, horizon, k=args.k)
    best = candidates.plans[0].first
    violations = check_plan(game, state, candidates.plans[0])
    if violations:
        # The Solver and the Rule Check disagree: a bug. Never print a squad to enter.
        print("Rule Check failed:", *violations, sep="\n  ", file=sys.stderr)
        return 1

    print(f"Snapshot {snapshot_dir.name} · xP from FPL · Gameweeks {horizon[0]}–{horizon[-1]}\n")
    print(squad_entry_report(game, best, {pid: xp[pid][first] for pid in best.squad}))
    if candidates.is_close_call:
        gap = candidates.plans[0].objective - candidates.plans[1].objective
        print(f"\nClose Call: the next-best Plan scores {gap:.2f} less over the horizon.")

    record = write_decision(
        args.decisions,
        kind="new-squad",
        gameweek_id=first,
        snapshot=snapshot_dir.name,
        xp_source="fpl",
        candidates=candidates,
        chosen=0,
        decided_by="solver",
    )
    print(f"\nDecision log entry: {record}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="football-agent")
    commands = parser.add_subparsers(dest="command", required=True)

    snapshot = commands.add_parser("snapshot", help="save a Snapshot of the public FPL API")
    snapshot.add_argument("--out", type=Path, default=Path("data/raw"))
    snapshot.set_defaults(handler=_snapshot)

    pick = commands.add_parser("pick-squad", help="pick a new team's first squad")
    pick.add_argument("--snapshots", type=Path, default=Path("data/raw"))
    pick.add_argument("--decisions", type=Path, default=Path("data/decisions"))
    pick.add_argument("--fresh", action="store_true", help="take a new Snapshot first")
    pick.add_argument("-k", type=int, default=3, help="how many Candidate Plans to compare")
    pick.set_defaults(handler=_pick_squad)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
