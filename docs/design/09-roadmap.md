# 09 · Roadmap

**Status:** Decided · **Last updated:** 2026-10-02

Goal: the full agent pipeline built by **27 October** and live from Gameweek 9. The Owner has little time on 2–6 October and 9–13 October, so those windows hold only light tasks.

| Gameweek | Deadline (UTC) |
|---|---|
| 6 | Sat 10 Oct, 10:00 |
| 7 | Sat 17 Oct, 10:00 |
| 8 | Fri 23 Oct, 17:30 |
| 9 | Sat 31 Oct, 11:00 |

## Milestones

### M0 · Data flowing (2–6 Oct, light)

- Tick workflow running the daily Snapshot into the public Snapshot repo
- Code repo made public after a history check
- **Owner:** create an FPL account (no team yet)

**Exit:** a Snapshot lands every day without anyone touching it.

### M1 · First squad (7–8 Oct, full) → Gameweek 6

- Solver on FPL's xP: squad rules, budget, a 5-Gameweek horizon, Candidate Plans
- Initial squad picked; Shadow Teams and decision log start
- **Owner:** register the team and enter the squad by hand by **8 Oct**

**Exit:** team registered with the Solver's squad; Solver tests cover every squad rule.

### M2 · Setup (9–13 Oct, light)

- **Owner, about 30 minutes in total:** create the Postgres project, the Telegram bot, an OpenRouter key with $5 prepaid and top-up off, a Langfuse project
- Nothing runs for Gameweek 6; FPL keeps the entered team

**Exit:** all secrets in GitHub Actions.

### M3 · Auto-execution (14–17 Oct, full) → Gameweek 7

- Login capture script; encrypted token storage and rotation
- Rule Check, dry run, idempotent executor with post-write verification
- Reversible first write: bench swap and back
- Main Run and Final Run on the Solver alone; Telegram Memo; Paired Comparison scoring
- **Owner:** run the login script once (about 5 minutes)

**Exit:** Gameweek 7 executed by the Final Run with no human action, verified against the account.

### M4 · Scout (18–23 Oct, full) → Gameweek 8

- Scout with validated output, Material Change detection in the Final Run
- Langfuse tracing and the Spend Cap
- Scout Brier scoring in the Retrospective step

**Exit:** Gameweek 8 Plans use Start Probabilities; every model call traced with its cost.

### M5 · Full pipeline (18–27 Oct, full) → Gameweek 9

- LangGraph graphs with Postgres checkpoints
- Planner with re-solves and the Chip Schedule
- Owner Questions with defaults, Chat via the tick, Instructions
- Checker with Veto and the Fallback Plan
- Retrospective and Lessons
- Regression suite seeded with the first cases

**Exit:** a dry-run Main Run and Final Run for Gameweek 9 complete end to end, including one answered Owner Question, by 27 Oct.

### After 27 October

- xP Model, adopted only when it beats FPL's xP in backtests
- MCP server
- Dashboard
- Experiments: Planner model ablation (DeepSeek against Kimi), prompt optimisation, price-change runs

## Risks

| Risk | Likelihood | Effect | Mitigation |
|---|---|---|---|
| FPL writes don't work headlessly | Medium | No autonomy | Found early in M3; fall back to confirm mode by Telegram |
| 18–27 Oct is too dense | Medium | Checker and Lessons slip | They move to early November; nothing else depends on them |
| FPL deletes the team | Low | Season data stops | Accepted by the Owner; Shadow Teams continue from Snapshots |
| Open models are too weak as Planner | Medium | Planner adds nothing | The Paired Comparison shows it; the Fallback Plan is the floor |
| Free-tier limits change | Low | A service stops | Postgres and Langfuse can be swapped; Snapshots are in git |
| News sources can't be fetched reliably | Medium | Scout falls back to FPL's flag | Decide sources before M4 |
