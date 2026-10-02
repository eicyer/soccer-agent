# 02 · Solver and xP

**Status:** Decided in shape; formulation details Proposed · **Last updated:** 2026-10-02

The deterministic core. The agents only ever see what this layer produces ([decision 0001](../decisions/0001-solver-writes-every-plan.md)).

## xP

**Source, in order of availability:**

1. **Now:** FPL's own `ep_next` for the next Gameweek. For later Gameweeks in the Planning Horizon, a simple proxy (Proposed): the player's points-per-game scaled by fixture difficulty. Crude, but enough for the Solver to run from Gameweek 6.
2. **When it wins:** the project's own xP Model replaces FPL's numbers only after beating them in a backtest.

**The xP Model (Proposed):** predict each scoring component separately, then combine with FPL's scoring rules, so each part is inspectable.

| Component | Predicted from |
|---|---|
| Expected minutes | Scout's Start Probability; recent minutes; position |
| Goals and assists | Expected goals and assists per 90, team attacking strength, opponent defensive strength, home or away |
| Clean sheet | Team defensive strength, opponent attack, home or away |
| Defensive contribution, saves, bonus | Recent per-90 rates |

Library: gradient-boosted trees (LightGBM) for the rate components, with team strengths from a simple rating model fitted on results. Trained only on data available before each Gameweek, so backtests are honest; unlike the LLM agents, a model trained this way can't have seen the outcomes.

## The Solver

A mixed-integer linear program over the Planning Horizon (about 5 Gameweeks), solved with HiGHS through PuLP (Proposed). It returns the top few Candidate Plans, not just the best.

**Decision variables, per player p and Gameweek t:** in squad, in starting eleven, captain, vice-captain, bench order, transferred in, transferred out; plus free transfers banked and Points Hits taken per Gameweek, and chip use per Gameweek.

**Constraints (from `game_settings` in the API, never hard-coded):**

- 15 players: 2 goalkeepers, 5 defenders, 5 midfielders, 3 forwards
- At most 3 players from one Premier League team
- Starting eleven: 1 goalkeeper, 3–5 defenders, 2–5 midfielders, 1–3 forwards (`element_types[].squad_min_play` and `squad_max_play`)
- Budget: squad cost within bank plus selling prices. Selling price is purchase price plus half of any rise, rounded down (`transfers_sell_on_fee`)
- Free transfers: one added per Gameweek, at most 5 banked (`max_extra_free_transfers`); each extra transfer is a −4 Points Hit
- Chips: at most one per Gameweek; each half of the season has its own set; Free Hit reverts the squad the following Gameweek
- Every Constraint from the Planner, the Chip Schedule or a hard Instruction

**Objective:** maximise total xP over the horizon, counting the captain twice, minus Points Hits. Later Gameweeks are discounted (Proposed: ×0.85 per Gameweek) because their xP is less certain; bench xP counts at a small weight to value cover.

**Candidate Plans:** after each solve, add a constraint excluding that Plan's first-Gameweek moves and solve again, until there are k Plans (Proposed: k = 5) or the gap to the best exceeds a threshold. Only the first Gameweek has to differ; later Gameweeks are only intentions.

**Close Call:** the top two Candidate Plans within 1 xP of each other over the horizon (Proposed threshold; tune by eval).

## Interfaces

Tools are plain Python functions called by the agents and wrapped by the MCP server ([08](08-infrastructure.md)):

| Function | Returns |
|---|---|
| `candidate_plans(state, constraints, k)` | Ranked Candidate Plans with xP per Gameweek and the reason each differs from the best |
| `score_plan(state, plan)` | A Plan's xP per Gameweek; used to compare Chip Schedule options |
| `player_xp(player_ids, gameweeks)` | xP broken into components, for the Planner and Checker to cite |
| `rule_check(state, plan)` | Pass, or the list of rules broken |

Outputs are compact (names, not ids; top results only) so they fit cheaply in a model's context.

## Open

- Horizon length, discount and k are set by backtest of the Solver on past seasons, which is honest because the Solver has no LLM in it.
- Whether to model price changes. Not for now.
