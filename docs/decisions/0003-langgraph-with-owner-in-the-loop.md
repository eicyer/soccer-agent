# LangGraph runs the pipeline, with the Owner in the loop

Each run is a LangGraph graph whose state is checkpointed after every step. We chose it over a plain Python pipeline (with Pydantic AI agents) because the Owner wants to be consulted by chat at the moments that matter, and LangGraph's interrupts let a run pause for the Owner and resume hours later from its checkpoint. Its graph view in LangGraph Studio and its recognition among employers were secondary reasons.

## Consequences

Every pause needs a default for when the Owner doesn't reply before the Final Run, so a missing reply never stops the team being set. Decisions influenced by the Owner must be recorded as such, so evals can separate the agent's contribution from the Owner's.
