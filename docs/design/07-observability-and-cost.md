# 07 · Observability and cost

**Status:** Decided; tool details Proposed until tested · **Last updated:** 2026-10-02

## What must be answerable

For any decision, in under a minute: what the agent saw, which tools it called with what results, what each model said, which Lessons and Instructions were active, what it cost, and which prompt and model versions produced it.

## Two records, two jobs

| Record | Holds | Kept | Used for |
|---|---|---|---|
| **Langfuse traces** | Every node, model call and tool call, with inputs, outputs, tokens and cost | 30 days on the free tier | Debugging and inspecting individual runs |
| **Postgres decision log** | Each run's inputs, Candidate Plans, choices, Verdicts, Owner Influence, costs, versions | Forever | Evals, the Memo, the dashboard |

The decision log is the source of truth for evals, so losing old traces when the free tier expires them costs nothing that matters.

## Tracing

- **One trace per run**, with the Gameweek and run type (Main, Final, Retrospective) as the session, so a Gameweek's runs group together.
- **Spans** for each graph node, model call and tool call, through Langfuse's LangChain and LangGraph integration over OpenTelemetry.
- **Attributes on every model span:** agent, model, prompt version, input and output tokens, cost.
- **Short jobs flush explicitly** before exiting, so spans aren't lost when the GitHub Actions job ends.
- **Redaction** before export: tokens and the entry id are masked ([05](05-execution-and-safety.md)).

Pin library versions: OpenTelemetry's conventions for agent spans are still in Development status and may change.

## Cost model

Prices from OpenRouter's public model list on 2 October 2026, per million tokens (input / output). Token volumes are estimates until measured.

| Role | Model | Price | Tokens per Gameweek (est.) | Cost per Gameweek |
|---|---|---|---|---|
| Scout | DeepSeek V4 Flash | $0.028 / $0.056 | 550k in, 40k out | ~$0.02 |
| Planner | DeepSeek V4 Pro | $0.21 / $0.42 | 600k in, 60k out | ~$0.15 |
| Checker | GLM 5.3 Flash | $0.15 / $0.50 | 100k in, 20k out | ~$0.03 |
| Retrospective | DeepSeek V4 Pro | $0.21 / $0.42 | 100k in, 10k out | ~$0.03 |
| Chat | DeepSeek V4 Pro | $0.21 / $0.42 | depends on use | ~$0.01 a message |
| **Total** | | | | **~$0.25, about $1 a month** |

Everything else is free: GitHub Actions (public repo), Langfuse free tier, Postgres free tier, and local models for development and evals.

## Spend Cap

Three layers, so no single bug can overspend:

1. **Prepaid credit:** $5 a month loaded on OpenRouter with automatic top-up off. The account can't spend more than its balance.
2. **Per Gameweek in code:** $1. Every model call records its cost; before each call, the run checks the Gameweek total. At the cap it stops calling models and plays the Fallback Plan.
3. **Per call:** a maximum output length per agent, and the Planner's three-re-solve limit.

A warning goes to the Owner at 80% of either cap.

## Keeping cost down

- **Model tiering:** the cheapest model that passes the regression suite for each role.
- **Compact tool outputs:** names not ids, top results only, no raw API dumps in context.
- **Stable prompt prefixes** (instructions and tool definitions first, nothing time-dependent there) so providers that cache repeated prefixes can.
- **Only relevant Lessons** reach the Planner, at most five.
- **The Final Run is cheap by design:** without a Material Change it only runs the Scout on the squad.
- **Development on local models,** so iteration costs nothing.

## Cost metrics

Reported in the Memo and on the dashboard: cost per run, per Gameweek and per month, and **points added per dollar** for each layer, from the Paired Comparison ([06](06-evaluation.md)).
