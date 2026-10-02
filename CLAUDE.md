# football-agent

An autonomous Fantasy Premier League agent. Priorities, in order: agent performance, cost, observability, evals.

Core rule of the design: the LLM never predicts points. Numbers come from models and solvers exposed as tools; agents handle news, planning and judgement.

## Commits

- Small and meaningful: one logical change per commit. If the message needs "and", split it.
- Concise subject in the imperative, under 60 characters, no trailing full stop ("Add FPL snapshotter"). Add a body only to explain why.
- The author is always Emir's GitHub account: `Emir Icyer <124095333+eicyer@users.noreply.github.com>`. It is set in this repo's git config; never override it with `--author` or another identity. No `Co-Authored-By` trailers, including for Claude.
- Every commit leaves the repo working: code runs, tests pass.
- Commit or push only when asked. Never force-push `main` or rewrite pushed history.

## Code

- Python. Type-hint function signatures. Prefer the standard library until a dependency clearly earns its place.
- New logic comes with tests. Anything touching scoring rules, squad constraints or money gets tested first.
- Keep modules deep: a small interface over real behaviour. No speculative abstractions or config for cases that don't exist yet.
- Fail loudly. No silent fallbacks or swallowed exceptions, especially around FPL writes.
- Comments explain why, not what.

## Secrets and data

- Secrets (FPL tokens, API keys) live in `.env`, never in code, logs, traces or commits.
- `data/` is git-ignored. Raw API snapshots are stored untouched and never edited; derive, don't mutate.

## FPL writes

- Every write path supports a dry run and logs the exact payload before sending.
- Wildcard and Free Hit are irreversible: always require Emir's explicit approval.
- Confirm mode must keep working as the fallback whenever auto mode breaks.

## Agents and evals

- Every LLM call is traced with model, tokens and cost. Untraced calls are bugs.
- A change to a prompt, model or agent step is justified by an eval result, not by a good-looking example.
- Backtests on past seasons leak, because the model already knows the results. Say so wherever such numbers are reported.

## Docs

- Research goes in `docs/research/`, with sources, and separates what was verified from what was reported.
- Significant architecture decisions get a short record in `docs/decisions/`: context, decision, consequences.
