"""The decision log: what was decided, from what, and when, written before the deadline.

Live, timestamped decisions are the only honest evidence for evals (docs/design/06-evaluation.md).
Until Postgres arrives (M2) each entry is a JSON file, to be imported into the Postgres log.
"""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from football_agent.solver.solver import CandidatePlans


def write_decision(
    out_dir: Path,
    *,
    kind: str,
    gameweek_id: int,
    snapshot: str,
    xp_source: str,
    candidates: CandidatePlans,
    chosen: int,
    decided_by: str,
    now: datetime | None = None,
) -> Path:
    decided_at = now or datetime.now(UTC)
    record = {
        "kind": kind,
        "gameweek": gameweek_id,
        "decided_at": decided_at.isoformat(),
        "snapshot": snapshot,
        "xp_source": xp_source,
        "decided_by": decided_by,
        "close_call": candidates.is_close_call,
        "chosen": chosen,
        "candidate_plans": [asdict(plan) for plan in candidates.plans],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"gw{gameweek_id:02d}-{kind}-{decided_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(record, indent=2))
    return path
