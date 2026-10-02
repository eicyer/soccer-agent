# All agents run on open-weight models

The Scout, Planner and Checker all run on open-weight models, not Claude or other closed models. The owner is a student and cost is a hard constraint, which outweighs the expected loss in Planner quality. This rules out the Claude Agent SDK, which only runs Claude, so the agents are built on a provider-agnostic framework and each role's model is a swappable setting.

## Considered Options

- Open models for the Scout and Checker, Claude for the Planner: stronger reasoning where it matters most, rejected on cost.
- Claude throughout, with an open-model Shadow Team for comparison: the most capable option, rejected on cost.

## Consequences

The Checker must still run on a different model from the Planner, now meaning a different open model. Earlier research and cost estimates that assumed Claude models need re-checking.
