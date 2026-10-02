# The Solver writes every Plan; agents only adjust inputs and choose

Agent judgement enters a decision in exactly two ways: by adjusting the Solver's inputs (player availability, Constraints) and by choosing among the Solver's Candidate Plans or asking it to re-solve. No agent writes a Plan itself. This guarantees every Plan is legal and keeps all arithmetic in code, and it lets evals measure each route separately: Solver alone, Solver with adjusted inputs, and Solver with adjusted inputs plus the Planner's choice.

## Considered Options

- Agents adjust inputs only, Solver's best Plan is final: simplest, but leaves the agents no say over multi-week trade-offs the xP model can't see.
- Agents choose among Candidate Plans only: can't react to news the xP model hasn't priced in.
- An agent writes Plans directly: rejected because LLMs are unreliable at budget and squad arithmetic, and it would make the agents' contribution impossible to isolate.
