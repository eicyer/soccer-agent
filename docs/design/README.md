# Design docs

How the football agent is built and why. Read them in order; each is short.

| # | Doc | Covers |
|---|---|---|
| 00 | [Overview](00-overview.md) | Problem, goals, non-goals, success metrics, the system on one page |
| 01 | [Gameweek pipeline](01-gameweek-pipeline.md) | The Main Run and Final Run graphs, step by step |
| 02 | [Solver and xP](02-solver-and-xp.md) | How Plans and Expected Points are produced |
| 03 | [Agents](03-agents.md) | Scout, Planner, Checker and Retrospective: contracts and models |
| 04 | [Owner interface](04-owner-interface.md) | Owner Questions, Chat, Instructions and the Memo over Telegram |
| 05 | [Execution and safety](05-execution-and-safety.md) | Writing to FPL, the Rule Check, secrets, prompt injection |
| 06 | [Evaluation](06-evaluation.md) | How we prove what the agents add |
| 07 | [Observability and cost](07-observability-and-cost.md) | Tracing, the cost model and the Spend Cap |
| 08 | [Infrastructure](08-infrastructure.md) | Schedules, storage, secrets, local development |
| 09 | [Roadmap](09-roadmap.md) | Milestones to 27 October, exit criteria and risks |

Related:

- [`CONTEXT.md`](../../CONTEXT.md): the glossary. Capitalised terms in these docs (Plan, Scout, Owner Question) are defined there.
- [`docs/decisions/`](../decisions/): decision records for the hard-to-reverse choices.
- [`docs/research/`](../research/): the evidence behind them.

Each doc starts with a status line. **Decided** means agreed and recorded; **Proposed** means the default we will build unless something better turns up; **Open** lists what is still unsettled.
