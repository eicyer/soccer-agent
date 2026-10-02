# 06 · Evaluation

**Status:** Decided; statistics and thresholds Proposed · **Last updated:** 2026-10-02

The question every eval serves: **which parts of the system earn their tokens?** "The agents add nothing over the Solver" is a valid answer.

## The leakage rule

Every model already knows how past seasons went, so an agent backtested on a past season is partly remembering, not deciding. Research puts effective knowledge cutoffs up to 8 months later than vendors state ([research](../research/multi-agent-architecture.md)). So:

- **Agent results come only from live, timestamped decisions.** Every decision is stored with its inputs and a timestamp before the deadline, and graded after.
- **Backtests are for code without LLMs:** the Solver, the xP Model and the plumbing. These can be trained and tested on data from before each Gameweek, so they can't have seen the answers.
- Any agent number from a past season is labelled contaminated wherever it appears.

## Layers and what each eval isolates

Because the Solver writes every Plan ([decision 0001](../decisions/0001-solver-writes-every-plan.md)), each layer's effect can be measured on its own:

| Variant | Inputs | Choice | Isolates |
|---|---|---|---|
| Solver only | FPL's chance of playing | Top Candidate Plan | The baseline |
| + Scout | Scout's Start Probability | Top Candidate Plan | Value of reading news |
| + Planner | Scout | Planner's choice and Constraints | Value of judgement |
| Full agent | Scout | Planner, then Checker | Value of the Checker |
| Full agent + Owner | Same | Including Owner Influence | Value of the Owner's input |

## Paired Comparison (main evidence)

Every Gameweek, from the real team's actual squad, compute what each variant would have chosen, then score every choice on that Gameweek's actual points.

- **Statistic:** the per-Gameweek points difference between each variant and the one below it, averaged over the season with standard errors. Paired, because all variants face the same squad and the same football.
- **Honest power:** about 30 live Gameweeks is a small sample and FPL points are noisy. Report the confidence interval, never only the mean; expect wide intervals.
- **Cost:** variants without an LLM cost nothing to compute; LLM variants reuse the real run's outputs, so the Paired Comparison adds no model spend.

## Shadow Teams (headline number)

Imaginary teams that make their own decisions all season from their own squads, never executed:

- **Solver only** and **Solver + Scout**, both free to run.
- **Full agent:** the real team itself, rather than a second LLM pipeline, to save cost.
- **Fixed chip rules** variant, as the baseline for the Chip Schedule.

The season-end comparison of Season Totals is one data point per team, so it's the story, not the proof. Shadow Teams start in Gameweek 6, the first live Gameweek.

## Component evals

| Component | Metric | Ground truth |
|---|---|---|
| Scout | Brier score on Start Probability, and against FPL's own flag | Whether the player started (`element-summary` history) |
| Planner | Stated confidence against outcome (Brier); how often re-solving helped | Actual points of chosen versus top Candidate Plan |
| Checker | Veto rate; points gained or lost by Vetoes | Actual points of vetoed versus final Plan |
| Chip Schedule | Points from each chip against the fixed-rules baseline | Actual points |
| Lessons | Paired Comparison with and without Lessons, on Gameweeks where they applied | Actual points |
| xP Model | Mean absolute error and calibration against FPL's `ep_next`, by position | Actual points, backtested |

Confidence is always asked for in the same fixed way, because results are sensitive to how it's elicited.

## Regression suite

A set of 20–50 hand-picked cases from real failures, run before any prompt or model change ships:

- Each case is a frozen input (Snapshot, news, Candidate Plans) with a binary expected outcome, such as "the Scout marks this player doubtful" or "the Checker vetoes this Plan".
- Grading is code where possible; where a judge model is needed, it grades one failure type, pass or fail, and is checked against hand labels first.
- Cases grow from the Retrospective: every notable failure becomes a case.

This runs locally on free models during development ([08](08-infrastructure.md)).

## Owner Influence

Every decision records whether the Owner shaped it: an Owner Question answer, an Instruction or a Chat request. Reports show the agent with and without the Owner's changes, so the Owner's input is credited to the Owner.
