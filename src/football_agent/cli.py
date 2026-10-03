"""Command-line entry point."""

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from football_agent.data.snapshot import snapshot_dates, take_snapshot


def _snapshot(args: argparse.Namespace) -> int:
    today = datetime.now(UTC).date()
    if args.if_missing_today and today in snapshot_dates(args.out):
        print(f"Snapshot for {today} already exists; nothing to do.")
        return 0
    out = take_snapshot(args.out)
    print(out)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="football-agent")
    commands = parser.add_subparsers(dest="command", required=True)

    snapshot = commands.add_parser("snapshot", help="save a Snapshot of the public FPL API")
    snapshot.add_argument("--out", type=Path, default=Path("data/raw"))
    snapshot.add_argument(
        "--if-missing-today",
        action="store_true",
        help="do nothing if a Snapshot for today (UTC) already exists",
    )
    snapshot.set_defaults(handler=_snapshot)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
