# soccer-agent

An autonomous Fantasy Premier League manager. A mathematical Solver builds every Plan; open-weight LLM agents read the news, choose between Plans and check each other; the Owner is asked only where it matters. Every layer is measured against a Solver-only baseline.

- Design: [`docs/design/`](docs/design/README.md)
- Glossary: [`CONTEXT.md`](CONTEXT.md)
- Decisions: [`docs/decisions/`](docs/decisions/)

## Development

```sh
uv sync
uv run pytest
uv run ruff check
```
