# Agent frameworks, runtimes, protocols and reference repositories (state as of 30 September 2026)

Method notes for the report writer:

- "Verified" below means seen directly on 2026-09-30 in the vendor's docs, the GitHub REST API (`gh api repos/...`), or the PyPI JSON API. Star counts, latest release tags and dates all come from those APIs on that day and are cited to the repo or PyPI page.
- "Third-party" means a claim from a search-result snippet or a non-vendor article that I did not confirm against a primary source. Treat these as leads, not facts.
- Several doc pages were summarised by a fetch tool that mis-stated years as 2024 for LangGraph and DSPy releases. The GitHub and PyPI APIs show 2026 for the same tags; the API dates are used here.
- Pages I could not fetch (network or tool failures) are listed under Gaps rather than filled from memory.

## 1. Current state of each framework (versions, features, direction)

### Takeaway
By September 2026 every major framework has converged on the same feature set (agent loop plus an explicit workflow/graph layer, checkpointed state, human approval, MCP, and an opinionated "harness" with planning, filesystem, subagents and compaction), so the differentiators are maturity, ecosystem and hosting rather than capability. For a Python project on Claude, the Claude Agent SDK is current and actively shipped (near-daily releases) but still pre-1.0, while LangGraph, Microsoft Agent Framework, Google ADK, CrewAI, Pydantic AI and DSPy are all past 1.0.

### Cited Findings

Snapshot table (all verified via GitHub API and PyPI on 2026-09-30):

| Framework | Stars | Latest version (date) | Licence | URL |
|---|---|---|---|---|
| Claude Agent SDK (Python) | 8,195 | 0.2.162 (2026-09-29) | MIT | https://github.com/anthropics/claude-agent-sdk-python |
| Claude Agent SDK (TypeScript) | 1,780 | 0.3.285 (2026-09-29) | not stated by API | https://github.com/anthropics/claude-agent-sdk-typescript |
| OpenAI Agents SDK (Python) | 29,784 | 0.22.3 (2026-09-17) | MIT | https://github.com/openai/openai-agents-python |
| LangGraph | 42,512 | 1.2.12 (2026-09-21) | MIT | https://github.com/langchain-ai/langgraph |
| LangChain Deep Agents | 29,871 | 0.7.20 (2026-09-29) | MIT | https://github.com/langchain-ai/deepagents |
| Google ADK (Python) | 21,686 | 2.10.0 (2026-09-25) | Apache-2.0 | https://github.com/google/adk-python |
| Microsoft Agent Framework | 13,878 | python-1.19.0 (2026-09-18) | MIT | https://github.com/microsoft/agent-framework |
| AutoGen (maintenance mode) | 61,239 | python-v0.7.5 (2025-09-30) | CC-BY-4.0 | https://github.com/microsoft/autogen |
| Semantic Kernel | 28,614 | dotnet-1.80.1 (2026-09-03) | MIT | https://github.com/microsoft/semantic-kernel |
| Pydantic AI | 20,286 | 2.52.0 (2026-09-30); a 1.x line is still released (v1.107.7, same day) | MIT | https://github.com/pydantic/pydantic-ai |
| CrewAI | 59,222 | 1.15.23 (2026-09-28) | MIT | https://github.com/crewAIInc/crewAI |
| LlamaIndex (core) | 52,371 | v0.14.25 (2026-09-21) | MIT | https://github.com/run-llama/llama_index |
| LlamaIndex Workflows (repo now `llama-agents`) | 453 | llama-index-workflows 2.25.0 (2026-09-25) | MIT | https://github.com/run-llama/llama-agents |
| DSPy | 38,434 | 3.4.0 (2026-09-25) | MIT | https://github.com/stanfordnlp/dspy |
| smolagents | 29,604 | v1.26.0 (2026-05-29) | Apache-2.0 | https://github.com/huggingface/smolagents |
| Mastra (TypeScript) | 28,451 | @mastra/core 1.72.0 (2026-09-30) | custom (not SPDX) | https://github.com/mastra-ai/mastra |
| Agno | 42,400 | v3.0.11 (2026-09-23) | Apache-2.0 | https://github.com/agno-agi/agno |
| Strands Agents (repo now `harness-sdk`) | 8,581 | strands-agents 1.57.1 on PyPI (2026-09-25) | Apache-2.0 | https://github.com/strands-agents/harness-sdk |

Claude Agent SDK and Claude Managed Agents

- The Agent SDK is described as "Build production AI agents with Claude Code as a library": it "gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript", and the library "runs the Claude Code binary" — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- Listed capabilities: built-in tools, hooks, subagents, MCP, permissions, sessions (resume or fork), skills/commands/memory loaded from `.claude/`, and plugins — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- Anthropic positions four options: Agent SDK (you operate the process), Claude Code CLI, Client SDK (write your own tool loop or use the beta tool runner), and Managed Agents (Anthropic hosts the loop) — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- Auth restriction: third-party developers may not offer claude.ai login or rate limits for products built on the Agent SDK; API-key auth is required — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- Python package `claude-agent-sdk` is at 0.2.162, uploaded 2026-09-29, requires Python 3.10+ — [PyPI](https://pypi.org/project/claude-agent-sdk/). A search-result summary quoted 0.2.95 on 25 September; PyPI and the GitHub release tag both show 0.2.162, so the summary was stale — [GitHub releases](https://github.com/anthropics/claude-agent-sdk-python/releases)
- Subagent limits are configurable from Python SDK v0.2.127: nesting depth default 3 (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`), concurrency default 20 (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`), and a spend cap `max_budget_usd` that ends the query with `error_max_budget_usd` — [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents)
- A `Workflow` tool for "dozens to hundreds of agents" moves orchestration into a script run outside the conversation context; it is documented for the TypeScript SDK v0.3.149+ only — [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents)
- Claude Managed Agents is "a pre-built, configurable agent harness that runs in managed infrastructure", status beta, requires header `managed-agents-2026-04-01`; core concepts are Agent, Environment, Session, Events — [Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)
- Managed Agents supports cron-scheduled runs ("scheduled deployments"), self-hosted sandboxes, persistent filesystems and server-side event history; it is not eligible for Zero Data Retention or HIPAA BAA — [Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)
- Managed Agents timeline: public beta 2026-04-08; agent memory beta 2026-04-23; multi-agent orchestration and Outcomes beta 2026-05-06; self-hosted sandboxes 2026-05-19; scheduled deployments 2026-06-09; session budgets and an "advisor" model option 2026-07-07; permission policies with `auto` mode 2026-08-07 — [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)
- Skills API and Files API left beta on 2026-08-19 — [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)
- Models released in the period include Claude Opus 5 (2026-07-24), Opus 5.5 (2026-09-22) and Sonnet 5.5 (2026-09-28) — [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)
- Third-party claim: Managed Agents costs standard token rates plus $0.08 per session-hour of active runtime. Not confirmed on the docs page I fetched — [search summary citing claude.com blog](https://claude.com/blog/claude-managed-agents)

OpenAI Agents SDK

- 0.14.0 added beta Sandbox Agents (`SandboxAgent`, `Manifest`, `SandboxRunConfig`), local/Docker/hosted sandbox backends, sandbox memory, and resume via `RunState` and `SandboxSessionState` — [release notes](https://openai.github.io/openai-agents-python/release/)
- 0.19.0 added `ProgrammaticToolCallingTool`; 0.20.0 added MCP Python SDK v2 support and `RunState.add_input()`; 0.21.0 requires `openai>=3.0.0,<4`; 0.22.0 gives each `RunState` checkpoint its own usage snapshot — [release notes](https://openai.github.io/openai-agents-python/release/)
- Still 0.x with a breaking change in most minor versions (default model changed twice, refusal handling, sandbox path rules) — [release notes](https://openai.github.io/openai-agents-python/release/)
- Third-party: the sandbox and "model-native harness" update was announced 2026-04-15. The OpenAI announcement page returned HTTP 403 to me — [search summary](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)

LangGraph and Deep Agents

- LangGraph is "a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents"; LangChain's agents sit above it and Deep Agents is a harness layer on top — [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- Core langgraph is 1.2.12 (2026-09-21) — [PyPI](https://pypi.org/project/langgraph/). 1.2.12 added response-schema support to interrupts — [GitHub releases](https://github.com/langchain-ai/langgraph/releases)
- Third-party: 1.1.0 shipped 2026-03-10 and 1.2.0 on 2026-05-11; 1.1.7 and 1.2.3 were yanked for regressions — [search summary of PyPI history](https://pypi.org/project/langgraph/)
- Deep Agents is "an opinionated agent that runs out of the box", "inspired by Claude Code", with planning, pluggable filesystem backends, subagents with isolated context, summarisation, tool-call approval, memory, skills and sandboxes — [deepagents README](https://github.com/langchain-ai/deepagents)

Google ADK

- ADK offers LlmAgent plus workflow agents, graph workflows, session/state/memory, action confirmations, MCP and OpenAPI tools, A2A, and deployment to Google's agent runtime, Cloud Run or GKE; languages are Python, TypeScript, Go, Java and Kotlin — [adk.dev](https://adk.dev/)
- google-adk is 2.10.0 (2026-09-25) — [PyPI](https://pypi.org/project/google-adk/)
- Third-party: Python 2.0 reached GA in June 2026 and added a graph execution engine (routing, fan-out/fan-in, loops, retry) and a Task API for structured delegation — [search summary of PyPI/DEV posts](https://pypi.org/project/google-adk/)

Microsoft Agent Framework (successor to AutoGen and Semantic Kernel)

- 1.0 shipped 2026-04-03 with stable single agents, provider connectors (Foundry, Azure OpenAI, OpenAI, Anthropic, Bedrock, Gemini, Ollama), middleware, pluggable memory, a graph workflow engine with checkpointing, and the sequential, concurrent, handoff, group-chat and Magentic-One patterns. DevUI, Azure Durable Functions support and the Agent Harness were preview at that point — [Microsoft devblog](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)
- Current docs list four areas: Agents, a "Harness Agent" (planning, todo tracking, compaction, file access, memory, tool approval), Workflows (functional and graph), and Integrations; languages are .NET, Python and Go (Go in public preview) — [Microsoft Learn overview](https://learn.microsoft.com/en-us/agent-framework/overview/)
- Microsoft's own guidance: "If you can write a function to handle the task, do that instead of using an AI agent" — [Microsoft Learn overview](https://learn.microsoft.com/en-us/agent-framework/overview/)
- AutoGen README: "AutoGen is now in maintenance mode. It will not receive new features or enhancements and is community managed going forward. New users should start with Microsoft Agent Framework" — [AutoGen README](https://github.com/microsoft/autogen)
- Third-party: Semantic Kernel 1.x is supported for at least one year after the 2026-04-03 GA — [search summary](https://atlan.com/know/ai-agent/microsoft/semantic-kernel/)

Pydantic AI

- Described as typed end to end, model-agnostic, with Logfire (OpenTelemetry) observability, Pydantic Evals, MCP, deferred tools with human approval, Pydantic Graph, streaming, and a "capability" primitive that bundles tools, instructions, hooks and settings; a Harness library ships ready-made capabilities — [Pydantic AI overview](https://pydantic.dev/docs/ai/overview/)
- Durable execution integrations: Temporal, DBOS, Prefect, Restate and AWS Lambda (co-maintained with vendors), plus Kitaru and Airflow — [Pydantic AI durable execution](https://pydantic.dev/docs/ai/integrations/durable_execution/overview/)
- Two release lines are live: v2.52.0 and v1.107.7 were both published 2026-09-30 — [GitHub releases](https://github.com/pydantic/pydantic-ai/releases)

CrewAI

- Two layers: Flows are "the backbone" (state, events, control flow) and Crews are autonomous agent teams used inside a Flow step; docs say "use both" — [CrewAI introduction](https://docs.crewai.com/en/introduction)
- Flows use `@start`, `@listen`, `@router`; Pydantic-typed state; `@persist` snapshots state to SQLite with resume and fork; `@human_feedback` pauses for approval; memory via LanceDB — [CrewAI Flows](https://docs.crewai.com/en/concepts/flows)

LlamaIndex Workflows

- "An event-driven, async-first, step-based way to control the execution flow of AI applications"; steps emit and consume events, with context state, pluggable persistence, human review points, a server (`llama-agents-server`) and a `llamactl` deploy CLI. The repo was renamed from `workflows-py` to `llama-agents` (the old name redirects) — [llama-agents README](https://github.com/run-llama/llama-agents)

DSPy

- 3.4.0 (2026-09-25) is labelled an "LM transition release" with native LM engines, a `LocalInterpreter`, and async ReActV2; 3.3.0 added ReActV2 with native tool calling; 3.3.1 added MCP v2 compatibility and GEPA multi-proposal support — [DSPy releases](https://github.com/stanfordnlp/dspy/releases). Feature names here come from an automated page summary and should be checked before quoting.

smolagents

- `CodeAgent` writes actions as Python code (claimed "30% fewer steps"); `ToolCallingAgent` uses JSON tool calls; sandboxes via E2B, Blaxel, Modal or Docker; the local executor is explicitly not a security boundary; MCP tools supported; core is about 1,000 lines — [smolagents README](https://github.com/huggingface/smolagents)
- Last release was v1.26.0 on 2026-05-29, four months old, the slowest cadence in this list — [GitHub](https://github.com/huggingface/smolagents)

Mastra

- TypeScript framework; agents, tools via `createTool()` with Zod schemas, model router in `provider/model` form — [Mastra docs](https://mastra.ai/docs)
- Not Python, so relevant only as a comparison point for this project — [Mastra repo](https://github.com/mastra-ai/mastra)

Newcomers and fast movers in 2026

- General-purpose agent harness repos now dwarf the frameworks in stars: OpenClaw 390,855; Hermes Agent (Nous Research) 250,248; opencode 211,073 (now under `anomalyco/opencode`); Claude Code 148,664; Codex CLI 127,371; Pi 110,654 (now `earendil-works/pi`); Gemini CLI 107,194; OpenHands 89,606; DeerFlow 83,263; goose 54,806 (now `aaif-goose/goose`) — [OpenClaw](https://github.com/openclaw/openclaw), [Hermes Agent](https://github.com/NousResearch/hermes-agent), [opencode](https://github.com/anomalyco/opencode), [Claude Code](https://github.com/anthropics/claude-code), [Codex](https://github.com/openai/codex), [Pi](https://github.com/earendil-works/pi), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [OpenHands](https://github.com/OpenHands/OpenHands), [DeerFlow](https://github.com/bytedance/deer-flow), [goose](https://github.com/aaif-goose/goose)
- Agno is at v3.0.11 with 42,400 stars — [Agno](https://github.com/agno-agi/agno)
- Third-party, unverified: a DeepSeek agent harness in developer preview from 2026-08-13 that reportedly gained about 95,000 stars in two days; "Mecatl" by Stacklok as a Kubernetes-native harness; OpenClaw 2.0 announced 2026-08-30 — [search summary](https://stacklok.com/blog/what-are-the-leading-open-source-ai-agent-harnesses-2026/), [OpenClaw on Wikipedia](https://en.wikipedia.org/wiki/OpenClaw)

### Inferences
- The word "harness" has become the standard term in 2026: Anthropic, OpenAI, Microsoft, LangChain, Pydantic and Strands all ship something named that way. Describing the project as "a Manager harness on the Claude Agent SDK with subagents, hooks and an MCP tool server" uses current vocabulary.
- Claude Agent SDK is a credible, current choice, but it is pre-1.0, single-vendor, and wraps the Claude Code binary. A recruiter-facing write-up should state why that trade-off was taken (built-in subagents, hooks, permissions, sessions) rather than present it as the neutral default.
- Managed Agents now covers the project's exact shape (cron schedule, persistent sessions, memory stores, multi-agent, budgets). It is a plausible "production path" to mention, with the caveat that it is still beta.
- AutoGen should not be cited as a current choice; Microsoft Agent Framework is the successor.
- Star counts favour older projects (AutoGen, CrewAI, LlamaIndex) and do not track current momentum; release cadence is a better signal here.

### Gaps
- Could not fetch the OpenAI "next evolution of the Agents SDK" post (HTTP 403), so harness and memory details for OpenAI are from the changelog and third-party summaries only.
- Could not fetch ADK's workflow docs or Mastra's workflow docs (network errors), so ADK 2.0 graph details and Mastra suspend/resume, memory and supervisor-agent details are unverified.
- Pydantic AI 2.0 GA date and what changed between the 1.x and 2.x lines were not found.
- Managed Agents pricing was not confirmed on a primary page.
- The newcomer claims (DeepSeek harness, Mecatl) were not verified against any repo.

## 2. Architectural differences: graph versus agent loop versus handoffs; state, checkpointing, human-in-the-loop, subagents, streaming

### Takeaway
There are three base models: an LLM-driven agent loop with subagents as tools (Claude Agent SDK, smolagents, Deep Agents), explicit graphs or event-driven workflows with checkpointed state (LangGraph, ADK 2.x workflows, Microsoft Agent Framework workflows, LlamaIndex Workflows, CrewAI Flows), and handoffs where control transfers between peers (OpenAI Agents SDK, also a pattern in Microsoft Agent Framework). Most frameworks now offer two of the three, and vendor guidance consistently says to use deterministic code for fixed steps and reserve the LLM loop for open-ended ones.

### Cited Findings

Comparison (each cell cited in the bullets below):

| Framework | Base model | State and checkpointing | Human-in-the-loop | Subagents / multi-agent |
|---|---|---|---|---|
| Claude Agent SDK | Agent loop; subagents via the Agent tool | Sessions persisted, resume or fork; subagent transcripts stored separately | `canUseTool` callback; `AskUserQuestion`; `PreToolUse` hook can `defer` so the process exits and resumes later | Fresh context per subagent, only the final message returns; parallel; depth, concurrency and budget caps |
| OpenAI Agents SDK | Agent loop with handoffs or agents-as-tools | `RunState` serialisable to JSON/string; sessions | `needs_approval` on tools; run returns `interruptions`; approve or reject on the state and rerun | Handoffs (peer takes over) or `Agent.as_tool()` (manager keeps control) |
| LangGraph | Explicit graph / state machine | Checkpointer per thread plus a Store for long-term memory | `interrupt()` and `Command(resume=...)` | Subgraphs; Deep Agents adds subagents |
| Microsoft Agent Framework | Agents plus functional/graph workflows | Workflow checkpointing and hydration | Pause/resume across orchestration patterns; tool approval in the Harness Agent | Sequential, concurrent, handoff, group chat, Magentic-One |
| CrewAI | Flows (event-driven) containing Crews (role-based teams) | `@persist` to SQLite, resume or fork by UUID | `@human_feedback` | Crews |
| LlamaIndex Workflows | Event-driven steps | Context state with pluggable persistence | Human review points in the server | Steps and events |
| Pydantic AI | Typed agent loop; optional Pydantic Graph | Delegated to a durable engine; "durability is not storage" | Deferred tools with approval | Agent delegation; graph |
| smolagents | Code-writing agent loop | In-run memory only | Not documented | Multi-agent hierarchies |

Claude Agent SDK

- Each subagent "runs in its own conversation, which starts fresh"; "intermediate tool calls and results stay inside the subagent; only its final message returns to the parent" — [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents)
- "The only content you pass from parent to subagent is the Agent tool's prompt string, so include any file paths, error messages, or decisions the subagent needs directly in that prompt" — [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents)
- `AgentDefinition` fields include `description`, `prompt`, `tools`, `disallowedTools`, `model`, `skills`, `memory`, `mcpServers`, `maxTurns`, `background`, `effort`, `permissionMode`; subagents run in the background by default — [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents)
- From Claude Code v2.1.210 the harness scans a subagent's final message for instruction-shaped patterns (imitation control tags, turn markers) and neutralises them before the parent reads it — [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents)
- Opus 5 "delegates to subagents more readily than earlier models", so the docs recommend setting the depth, concurrency and spend limits — [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents)
- Approvals: `canUseTool` fires when a tool is not auto-approved or when Claude calls `AskUserQuestion`; it can allow, allow with modified input, deny with a message, or persist a rule. "The callback can stay pending indefinitely" — [Handle approvals and user input](https://code.claude.com/docs/en/agent-sdk/user-input)
- For slow human responses: "register a `PreToolUse` hook that returns the `defer` decision instead of waiting in the callback, so the process can exit and resume later from the persisted session" — [Handle approvals and user input](https://code.claude.com/docs/en/agent-sdk/user-input)
- The callback never fires for auto-approved tools; "for logic that must apply to every tool call, use a `PreToolUse` hook" — [Handle approvals and user input](https://code.claude.com/docs/en/agent-sdk/user-input)
- `AskUserQuestion` is not available inside subagents; each call supports 1 to 4 questions with 2 to 4 options — [Handle approvals and user input](https://code.claude.com/docs/en/agent-sdk/user-input)
- A `PermissionRequest` hook can send Slack, email or push notifications while waiting for approval — [Handle approvals and user input](https://code.claude.com/docs/en/agent-sdk/user-input)

OpenAI Agents SDK

- Two orchestration styles: LLM-driven (the agent plans) and code-driven (structured outputs, chaining, evaluator loops, parallel runs) which is "more predictable regarding speed, cost, and performance" — [Agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/)
- Agents-as-tools: a manager keeps control and calls specialists as bounded subtasks, best "when one agent should own the final answer". Handoffs: a triage agent routes and the specialist becomes the active agent — [Agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/)
- Human-in-the-loop: tools set `needs_approval` (boolean or async callable); a paused run exposes `interruptions`; `result.to_state()` gives a `RunState` that can be serialised, reloaded in another process, approved or rejected, and resumed with `Runner.run(agent, state)`. This works through handoffs and nested `Agent.as_tool()` calls — [Human in the loop](https://openai.github.io/openai-agents-python/human_in_the_loop/)
- Nested handoff history has been opt-in since 0.7.0 — [release notes](https://openai.github.io/openai-agents-python/release/)

LangGraph

- Lets developers "combine hand-coded, deterministic logic with LLM-driven decision-making in a single graph" — [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- Checkpointers "persist a thread's graph state as checkpoints"; Stores "persist application-defined data outside the graph state"; together they give conversation continuity, human-in-the-loop, time travel and fault tolerance — [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- `interrupt()` saves state and waits indefinitely; resuming with `Command(resume=value)` on the same `thread_id` restarts "the entire node from the beginning", so code before the interrupt must be idempotent; interrupt matching is strictly index-based; do not wrap `interrupt()` in a bare try/except — [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

Microsoft Agent Framework

- Use an agent when the task is open-ended and needs autonomous tool use; use a workflow when the process has well-defined steps and multiple agents or functions must coordinate — [Microsoft Learn overview](https://learn.microsoft.com/en-us/agent-framework/overview/)
- Workflows give "explicit control over multi-agent execution paths, plus a robust state management system for long-running and human-in-the-loop scenarios" — [Microsoft Learn overview](https://learn.microsoft.com/en-us/agent-framework/overview/)

Cross-cutting evidence on multi-agent design

- Anthropic's research system uses an orchestrator-worker pattern; Opus 4 lead with Sonnet 4 subagents beat single-agent Opus 4 by 90.2% on its internal research eval; agents use about 4 times the tokens of chat and multi-agent systems about 15 times; token usage alone explained 80% of performance variance — [Anthropic engineering, 2025-06-13](https://www.anthropic.com/engineering/multi-agent-research-system)
- Multi-agent suits heavily parallel, high-value tasks that exceed one context window, and suits poorly tasks needing shared context or tight coordination — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Delegation messages need an objective, an output format, tool and source guidance, and task boundaries; subagents should write outputs to external storage rather than pass everything back through the lead — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Third-party practitioner summaries: LangGraph is "the most common default for complex Python workflows", Pydantic AI for type-safe services, and the provider SDKs when committed to one model ecosystem; LangGraph has the steepest learning curve — [search summary of comparison articles](https://www.alexcloudstar.com/blog/ai-agent-frameworks-comparison-2026/)

### Inferences
- The FPL project's design (Manager plus specialist subagents, deterministic tools for the numbers) matches the "agents as tools / orchestrator-worker" pattern that Anthropic, OpenAI and Microsoft all document. The matching weakness to address is that a pure agent loop has no explicit, inspectable state machine; the weekly pipeline's fixed stages (snapshot, predict, optimise, propose, approve, submit) are better expressed as plain Python around the agent calls.
- For human approval on a scheduled run, the documented Agent SDK route is a `PreToolUse` hook that returns `defer`, a notification, process exit, and a later resume from the persisted session. This is the closest equivalent to LangGraph's `interrupt()` and OpenAI's `RunState` and is worth naming explicitly.
- Setting `max_budget_usd`, spawn depth 1 and a low concurrency cap is a cheap, documentable safety measure, especially on Opus 5-class models.
- Because `AskUserQuestion` does not work in subagents, approval gates must sit in the Manager or in hooks.

### Gaps
- No primary-source streaming comparison was gathered; streaming is supported by all of them per their overviews but details were not compared.
- LangGraph's durability modes and task/idempotency guidance were not on the page fetched.
- ADK's session, resumability and tool-confirmation details were not verified beyond the landing page.

## 3. Durable execution for agents (Temporal, Inngest, Restate, DBOS, LangGraph persistence)

### Takeaway
Durable execution engines are now first-class integrations for the main Python frameworks (Temporal with the OpenAI Agents SDK is GA; Pydantic AI co-maintains five integrations), but the primary sources frame them as crash recovery for a single long run, not as storage or scheduling. For a weekly batch agent that finishes in minutes and can be safely rerun, a scheduler plus idempotent steps and a persisted session is usually enough; an engine earns its place when a run must wait hours or days for a human or must not repeat side effects after a crash.

### Cited Findings

| Engine | Stars | Latest (date) | Python SDK on PyPI | URL |
|---|---|---|---|---|
| Temporal | 23,381 | v1.32.0 (2026-09-11) | temporalio 1.33.0 (2026-09-15) | https://github.com/temporalio/temporal |
| Inngest | 5,900 | v1.45.1 (2026-09-17) | inngest 0.5.19 (2026-06-23) | https://github.com/inngest/inngest |
| Restate | 4,491 | v1.7.12 (2026-09-22) | restate-sdk 1.0.5 (2026-09-02) | https://github.com/restatedev/restate |
| DBOS Transact (Python) | 1,597 | 3.2.0 (2026-09-29) | dbos 3.2.0 | https://github.com/dbos-inc/dbos-transact-py |
| LangGraph SQLite checkpointer | n/a | langgraph-checkpoint-sqlite 3.1.1 (2026-07-30) | same | https://pypi.org/project/langgraph-checkpoint-sqlite/ |

- Temporal maps the agent loop onto a deterministic Workflow that orchestrates, and Activities that do the non-deterministic work ("calling LLMs, invoking tools, making API requests"); "your AI Agent can absolutely make decisions based on non-deterministic LLM outcomes" — [Temporal blog](https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal)
- Temporal cites OpenAI's Codex and Replit's Agent 3 as production users — [Temporal blog](https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal)
- Pydantic AI: durable agents "preserve their progress across transient API failures and application errors or restarts, and handle long-running, asynchronous, and human-in-the-loop workflows" — [Pydantic AI durable execution](https://pydantic.dev/docs/ai/integrations/durable_execution/overview/)
- Pydantic AI: "Durability is not storage"; an engine keeps one run alive across crashes but does not store conversations for later retrieval — [Pydantic AI durable execution](https://pydantic.dev/docs/ai/integrations/durable_execution/overview/)
- LangGraph's built-in persistence (checkpointer plus thread id) gives fault tolerance and indefinite human waits without a separate engine, with the constraint that a resumed node reruns from its start — [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- Microsoft Agent Framework listed Azure Durable Functions support as preview at 1.0 — [Microsoft devblog](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)
- Claude Managed Agents offers the hosted equivalent for Claude: sessions that "resume cleanly after pauses", server-side event history, and cron scheduled deployments — [Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)
- Anthropic's own production lesson: store agent state so runs resume from failures rather than restarting — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Third-party: the Temporal and OpenAI Agents SDK Python integration went GA on 2026-03-23 and `temporalio-openai-agents` 1.0.0 was released 2026-09-16 — [search summary of Temporal changelog](https://temporal.io/blog/announcing-openai-agents-sdk-integration)
- Third-party comparison: Temporal replays workflow code from an event history; Inngest reruns the function per step and injects saved step results; DBOS writes to a Postgres you already run; "Choose Temporal if workflows are complex, long-lived and central enough that someone will own them properly; Restate for the same guarantees with far less infrastructure; Inngest if you're serverless; DBOS if you trust Postgres and would rather add a library than a cluster" — [search summary of comparison articles](https://hackernoon.com/durable-execution-for-ai-agents-langgraph-dbos-inngest-and-temporal-compared)

### Inferences
- I found no first-party Temporal, DBOS, Restate or Inngest integration for the Claude Agent SDK. The SDK runs the Claude Code binary as a subprocess, so an engine would wrap a whole `query()` call as one step rather than checkpoint individual model and tool calls. That limits the benefit compared with the OpenAI Agents SDK or Pydantic AI integrations.
- For this project the honest minimum is: a scheduler (cron, GitHub Actions, or Managed Agents scheduled deployments), idempotent stages keyed by gameweek, immutable data snapshots, the SDK's persisted session for resume, and a deferred approval that survives process exit. That gives most of the durability story without an engine.
- If the owner wants to show durable execution on the CV, DBOS is the lightest credible option (a library over Postgres or SQLite, no cluster) and wraps deterministic stages cleanly. Temporal is the most recognised name but is heavy for one weekly job.
- The one irreversible side effect is submitting transfers to FPL. That single step is where exactly-once semantics and an idempotency check matter most.

### Gaps
- DBOS, Inngest and Restate documentation could not be fetched (domain blocked by the fetch tool), so their agent features, human-wait primitives and cron support are not verified here.
- The independent comparison article and Temporal's integration announcement could not be fetched in full; only search snippets were seen.
- No primary source was found that states when durable execution is unnecessary; the "overkill" judgement above is my inference.

## 4. Model Context Protocol in 2026 and agent-to-agent protocols

### Takeaway
MCP's current spec is 2026-07-28, the largest revision so far: the protocol core is now stateless (no initialise handshake, no session id), server-initiated requests are replaced by multi-round-trip results, and Roots, Sampling, Logging and the old HTTP+SSE transport are deprecated. MCP sits under the Linux Foundation, the official registry is still in preview, and security guidance has shifted to OAuth hardening plus well-documented tool-poisoning and local-server risks. A2A reached 1.0 in March 2026 and is the accepted standard for cross-vendor agent communication, but it is not needed for subagents inside one process.

### Cited Findings

MCP specification and SDKs

- Spec releases: 2025-03-26, 2025-06-18, 2025-11-25, 2026-07-28 (release candidate 2026-05-29) — [spec repo releases](https://github.com/modelcontextprotocol/modelcontextprotocol/releases)
- 2026-07-28 removes the `initialize`/`initialized` handshake and the `Mcp-Session-Id` header; each request carries protocol version, client identity and capabilities in `_meta`; an optional `server/discover` call exists — [MCP blog, 2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- Streamable HTTP now requires an `Mcp-Method` header, and `Mcp-Name` for `tools/call`, `resources/read` and `prompts/get`, so gateways can route without parsing bodies — [MCP changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- Multi Round-Trip Requests: a tool needing input mid-call returns `resultType: "input_required"` and the client retries with `inputResponses` — [MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- List and read results carry `ttlMs` and `cacheScope`; list endpoints no longer vary per connection — [MCP changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- Tasks moved from experimental core to the official extension `io.modelcontextprotocol/tasks`; MCP Apps and Enterprise Managed Authorization are also formal extensions — [MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- Deprecated with a minimum twelve-month window: Roots, Sampling, Logging and the legacy HTTP+SSE transport — [MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- Authorisation changes: RFC 9207 issuer validation, credentials bound to the issuing authorisation server, Dynamic Client Registration deprecated in favour of Client ID Metadata Documents — [MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- Tier 1 SDKs (TypeScript, Python, Go, C#) supported the new spec at release — [MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- Official Python SDK `mcp` is 2.2.0 (2026-09-07), 24,441 stars — [python-sdk](https://github.com/modelcontextprotocol/python-sdk). FastMCP is 4.0.10 (2026-09-25), 27,945 stars, now under `PrefectHQ/fastmcp` — [FastMCP](https://github.com/PrefectHQ/fastmcp)

Governance, roadmap and registry

- The roadmap post (2026-08-22) lists five priorities: agentic messaging primitives, HTTP-native transport for local and remote servers, agent identity and enterprise security (DPoP, workload identity federation), improved primitives including progressive tool discovery, and SDK developer experience. Work runs through Working Groups and Specification Enhancement Proposals; the site footer reads "Model Context Protocol a Series of LF Projects, LLC" — [MCP roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/)
- Third-party: Anthropic donated MCP in December 2025 to the Agentic AI Foundation, a Linux Foundation directed fund co-founded by Anthropic, Block and OpenAI — [search summary; primary post exists](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/)
- "The MCP Registry is currently in preview. Breaking changes or data resets may occur before general availability" — [MCP Registry](https://modelcontextprotocol.io/registry/about)
- The registry stores metadata only (`server.json`: reverse-DNS name such as `io.github.user/server-name`, package location, run instructions); packages stay on npm, PyPI or Docker Hub; namespaces are verified through GitHub, DNS or HTTP challenges; security scanning is delegated to package registries and downstream aggregators; private servers are not supported — [MCP Registry](https://modelcontextprotocol.io/registry/about)
- Registry repo: 7,303 stars, v1.8.1 (2026-08-06) — [registry repo](https://github.com/modelcontextprotocol/registry)

Security

- The spec's security page covers confused deputy (proxy servers must implement per-client consent), token passthrough ("MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server"), SSRF during OAuth discovery, state-handle hijacking, local server compromise, OAuth URL validation, mix-up attacks and scope minimisation — [MCP security best practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)
- With sessions gone, servers needing cross-request state mint explicit handles passed as tool arguments, and "MUST NOT treat possession of a state handle as authentication" — [MCP security best practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)
- Local servers "SHOULD" use stdio to limit access to the MCP client, or require a token or restricted IPC if using HTTP — [MCP security best practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)
- Third-party: a Cloud Security Alliance note says major coding tools auto-execute project-defined MCP servers with developer privileges; reports of a June 2026 "Miasma" campaign planting malicious MCP configs in 73 repositories; tool-poisoning success rates above 60% in benchmarks — [CSA research note](https://labs.cloudsecurityalliance.org/research/csa-research-note-mcp-tool-poisoning-auto-execution-20260701/)

Designing an MCP server (Anthropic guidance, 2025-09-11)

- Consolidate: build task-level tools (for example one `schedule_event`) rather than one tool per API endpoint — [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- Namespace tools with clear prefixes; return high-signal fields and human-readable names rather than opaque ids; add pagination, filtering and truncation with sensible defaults (Claude Code caps tool responses at 25,000 tokens by default); offer a `response_format` of concise or detailed; write error messages that tell the agent how to fix the call; iterate using evaluations on realistic tasks — [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)

A2A

- A2A is "an open source project under the Linux Foundation, contributed by Google", Apache-2.0, with SDKs for Python, Go, JavaScript, Java, .NET and Rust; 25,973 stars — [A2A repo](https://github.com/a2aproject/A2A)
- v1.0.0 was tagged 2026-03-12 and v1.0.1 on 2026-05-28 — [A2A releases](https://github.com/a2aproject/A2A/releases). A third-party article says 1.0 came in April 2026; the tag date is authoritative.
- Spec 1.0 defines Task, Message, Part, Artifact and Agent Card; bindings for JSON-RPC 2.0, gRPC and HTTP+JSON; eight task states including `INPUT_REQUIRED` and `AUTH_REQUIRED`; streaming and webhook push notifications; signed Agent Cards — [A2A specification](https://a2a-protocol.org/latest/specification/)
- Python `a2a-sdk` is 1.2.1 (2026-09-30) — [PyPI](https://pypi.org/project/a2a-sdk/)
- Third-party: more than 150 supporting organisations at the one-year mark (2026-04-09), with integrations across Google, Microsoft and AWS platforms — [Linux Foundation press release](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)
- Microsoft Agent Framework 1.0 shipped MCP support with A2A 1.0 "arriving soon"; ADK lists A2A as a built-in integration — [Microsoft devblog](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/), [adk.dev](https://adk.dev/)

### Inferences
- A local stdio MCP server for the expected-points model and the MILP optimiser is the low-risk, spec-recommended shape. Most of the 2026-07-28 changes affect remote HTTP servers; the practical action for this project is to pin a current SDK (`mcp` 2.x or FastMCP 4.x), avoid the deprecated features (Sampling, Roots, Logging, HTTP+SSE), and keep tools stateless with explicit handles such as a gameweek id or snapshot id.
- The tool-design guidance maps directly: a few task-level tools (`predict_points`, `optimise_squad`, `evaluate_transfer`) with player names in results, compact default output and corrective error messages, rather than one tool per FPL endpoint.
- The Claude Agent SDK also supports in-process SDK MCP servers; whether to run the server in-process or as a separate stdio process is a design choice the project should state. A separate server is reusable from Claude Desktop and other clients, which is a good demo point.
- Publishing the server's metadata to the MCP Registry under an `io.github.<user>/...` namespace is a small, visible credibility step, with the caveat that the registry is in preview.
- A2A is not justified for subagents that live in one process. It would only make sense if the project exposed the FPL agent as a service to other agents; mentioning that boundary shows awareness without over-engineering.
- The security points most relevant here: never pass FPL credentials through the model, keep the write tool (submit transfers) behind an approval hook, and treat scraped news as untrusted input that may carry prompt injection.

### Gaps
- I did not verify the Agentic AI Foundation governance details against the primary post; only the search summary and the LF footer were seen.
- A2A and IBM's ACP merger was not confirmed by any source fetched.
- The third-party security statistics (Miasma, 60% to 72% success rates) were not traced to primary research.
- No primary source was found for a "curated verified registry in Q4 2026" claim seen in one search summary.

## 5. Reference repositories worth studying

### Takeaway
The most transferable patterns come from TradingAgents (specialist analysts, structured debate, a manager that approves, point-in-time data and a decision log fed back as lessons), the deep-research family (scope, supervisor, parallel researchers, compress, write), and the harness repos (planning tool, filesystem as memory, subagents with isolated context, on-demand skills). LangChain's open_deep_research is now archived, so it should be cited as a design reference rather than a live project.

### Cited Findings

| Repo | Stars | Latest (date) | What it is | URL |
|---|---|---|---|---|
| TradingAgents | 109,328 | v0.5.2 (2026-09-29) | Multi-agent trading research firm on LangGraph | https://github.com/TauricResearch/TradingAgents |
| open_deep_research | 12,681 | archived 2026-08-21 | Supervisor plus parallel researchers on LangGraph | https://github.com/langchain-ai/open_deep_research |
| GPT Researcher | 29,830 | v3.7.0 (2026-09-26) | Planner/executor research agent | https://github.com/assafelovic/gpt-researcher |
| dzhng/deep-research | 19,745 | last push 2026-04-11 | Minimal deep research loop (TypeScript) | https://github.com/dzhng/deep-research |
| DeerFlow | 83,263 | v2.1.0 (2026-09-24) | "Super agent harness" on LangGraph | https://github.com/bytedance/deer-flow |
| Deep Agents | 29,871 | 0.7.20 (2026-09-29) | Opinionated harness on LangGraph | https://github.com/langchain-ai/deepagents |
| claude-agent-sdk-demos | 2,764 | last push 2026-08-27 | Official Agent SDK demo apps | https://github.com/anthropics/claude-agent-sdk-demos |
| claude-cookbooks | 53,088 | last push 2026-09-28 | Anthropic notebooks and patterns | https://github.com/anthropics/claude-cookbooks |
| claude-quickstarts | 17,770 | last push 2026-09-29 | Deployable starter apps | https://github.com/anthropics/claude-quickstarts |
| openai-cookbook | 76,279 | last push 2026-09-29 | OpenAI examples | https://github.com/openai/openai-cookbook |
| mini-swe-agent | 8,119 | v2.4.6 (2026-07-23) | Minimal coding agent | https://github.com/SWE-agent/mini-swe-agent |
| OpenHands | 89,606 | v1.24.0 (2026-09-25) | Coding agent platform | https://github.com/OpenHands/OpenHands |

TradingAgents (closest structural analogue to an FPL agent)

- Teams mirror a trading firm: parallel analysts (fundamentals, sentiment, news, technical), bull and bear researchers who debate for a configurable number of rounds (`max_debate_rounds`), a trader, a risk team and a portfolio manager who approves or rejects — [TradingAgents README](https://github.com/TauricResearch/TradingAgents)
- Built on LangGraph; optional SQLite checkpointing resumes an interrupted run from the last successful node — [TradingAgents README](https://github.com/TauricResearch/TradingAgents)
- Two model tiers: a "deep think" model for hard reasoning and a "quick think" model for simpler steps — [TradingAgents README](https://github.com/TauricResearch/TradingAgents)
- Structured outputs for the research manager, trader and portfolio manager — [TradingAgents README](https://github.com/TauricResearch/TradingAgents)
- Memory log: each run appends its decision; later runs on the same ticker fetch realised returns and inject lessons into the portfolio manager prompt — [TradingAgents README](https://github.com/TauricResearch/TradingAgents)
- Point-in-time data: backtests "see only data published by each analysis date"; v0.5.0 added backtesting grids and portfolio awareness — [TradingAgents README](https://github.com/TauricResearch/TradingAgents)
- States it is for research and "not intended as financial, investment, or trading advice", and that results are non-deterministic — [TradingAgents README](https://github.com/TauricResearch/TradingAgents)

Deep research family

- open_deep_research pipeline: scoping and clarification, a supervisor, parallel researcher subagents, compression of findings, final report; separate model roles for summarisation, research, compression and writing; MCP compatible; evaluated on Deep Research Bench (100 PhD-level tasks, LLM judge); archived read-only on 2026-08-21 — [open_deep_research README](https://github.com/langchain-ai/open_deep_research)
- Anthropic's write-up of the same pattern recommends starting evaluation with about 20 cases, LLM-as-judge rubrics, full tracing, and resumable state — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)

Harnesses

- Deep Agents: planning, filesystem backends, subagents with isolated context, automatic summarisation and offloading tool outputs to disk, approve/edit/reject on tool calls, persistent memory, skills — [deepagents README](https://github.com/langchain-ai/deepagents)
- DeerFlow 2.x is a ground-up rewrite from a deep-research tool into a harness on LangGraph: subagents, sandboxes (local, Docker, Kubernetes), progressive skill loading, per-skill `allowed-tools`, long-term memory, short handles to tool results that survive compaction, MCP with tool namespacing, and a trace id on every response — [DeerFlow README](https://github.com/bytedance/deer-flow)
- The official Agent SDK demos include a multi-agent research agent (parallel researcher subagents, synthesis, detailed subagent activity tracking), a file-output resume generator, an `AskUserQuestion` demo with `canUseTool`, and a session-persistence example — [claude-agent-sdk-demos](https://github.com/anthropics/claude-agent-sdk-demos)
- The Agent SDK docs link an Anthropic post on "dynamic workflows" for orchestrating many subagents — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)

### Inferences
Patterns worth copying into the FPL project, in rough order of value:

- Point-in-time data contracts with immutable snapshots, so backtests cannot see the future. The repo already has a raw FPL API snapshotter, which is the right foundation.
- A decision log with post-gameweek grading that is fed back as lessons, as TradingAgents does with realised returns.
- Numbers from deterministic tools, prose from the LLM. Every strong reference keeps the model away from arithmetic.
- Model tiering: a stronger model for the Manager, a cheaper one for specialists.
- Structured outputs at each handoff so the Manager consumes typed results.
- A bounded debate (for example an advocate and a sceptic on a proposed transfer) with a fixed round cap, used sparingly because of the 15x token cost Anthropic reports for multi-agent runs.
- Subagent activity tracking through hooks plus a trace id per run, as in the Agent SDK research demo and DeerFlow.
- A small evaluation set from day one (about 20 cases) and comparison against naive baselines.
- An explicit "not advice, non-deterministic" statement and a reproducibility note.

### Gaps
- I did not read the source code of any of these repos, only READMEs, so claims about implementation quality are not verified.
- The `claude-cookbooks` and `claude-quickstarts` contents were not inspected; specific notebooks to cite were not identified.
- Coding-agent harnesses (OpenHands, mini-swe-agent, opencode, Codex, Pi) were captured by stars and release date only.
- Hugging Face's open deep research example was not located as a standalone repo.

## 6. Existing open-source FPL agents and MCP servers

### Takeaway
There are many FPL MCP servers and a growing number of FPL agents, but almost all are small (the largest MCP server has 80 stars, most agents have 0 to 4) and most are thin wrappers over the public API. No project found combines the Claude Agent SDK, a solver-backed MCP server, approval gates and a scheduled run, so the niche is open; the strongest ideas to borrow are self-grading against baselines, commit-before-deadline proof, and keeping the solver deterministic.

### Cited Findings

MCP servers (stars and dates via GitHub API, 2026-09-30)

- `rishijatia/fantasy-pl-mcp`: 80 stars, Python, v0.1.7 (2026-08-03), on PyPI as `fpl-mcp`; stdio server exposing resources such as `fpl://static/players` plus player search and comparison tools; read-only data access — [repo](https://github.com/rishijatia/fantasy-pl-mcp)
- `fantasypl/mcp`: 0 stars, Go, v0.1.4 (2026-09-21); single static binary with 15 tools including `optimal_squad` ("exact combinatorial optimizer"), `optimal_transfers`, `is_hit_worth_it`, `chip_strategy`; two resources and five prompts; a companion `fplctl` CLI for snapshots, weight tuning, backtests with hold-out seasons and golden-file tests of frozen API payloads — [repo](https://github.com/fantasypl/mcp)
- `lewis-king/fpl-mcp-server`: 3 stars, Python; "out-of-band login" so FPL credentials never reach the LLM (Playwright browser login), executes transfers with validation, fuzzy name resolution so no ids are needed, 4-hour cache with stale fallback — [repo](https://github.com/lewis-king/fpl-mcp-server)
- `nguyenanhducs/fpl-mcp-server`: 1 star, Python 3.13+, v1.0.3 (2026-02-20); 19 tools, 4 resources, 10 strategy prompts, 4-hour bootstrap cache, fuzzy matching, `uvx` and Docker install, and an `mcp-name: io.github.nguyenanhducs/fpl-mcp-server` registry marker — [repo](https://github.com/nguyenanhducs/fpl-mcp-server)
- `dexhamter/fpl-mcp`: 3 stars, Python; 33 read-only tools, async client with per-endpoint TTL cache, bearer-token auth for private squad data — [repo](https://github.com/dexhamter/fpl-mcp)
- `bsovs/fpl-strategy-mcp`: 1 star; "rules-aware" action-policy server returning legal hold, transfer and chip options with reasons and risk; a conservative default that only departs from a validated baseline when a learned action clears a temporal guardrail; optional remote transport with a bearer token — [repo](https://github.com/bsovs/fpl-strategy-mcp)
- Others seen: `dohyung1/x402-fpl-api` (11 stars, 11 tools), `FarazPatankar/fpl-mcp` (remote TypeScript server), `pmc-a/fpl-mcp-server`, `owen-lacey/fpl-mcp`, `minhthong582000/scout-pl-mcp` (Go) — [GitHub search](https://github.com/search?q=fpl+mcp&type=repositories)

Agents

- `EliDehaene01/Fantasy-Premier-League-Manager`: 0 stars, Python, pushed 2026-09-23. Seven agents (six specialists and a manager) as a LangGraph state machine, each a containerised service; a stats pipeline with time-respecting cross-validation and SHAP; a news agent that checks structured availability deterministically before using retrieval; a PuLP solver with fixed, config-driven weights "never an LLM-decided weighting, so the same inputs always produce the same squad"; walk-forward backtest mode on the vaastav archive; human approval of the final recommendation. Explicitly built as a skills-demonstration project — [repo](https://github.com/EliDehaene01/Fantasy-Premier-League-Manager)
- `subhasishgoswami02/fpl-copilot`: 1 star, Python, pushed 2026-09-22. A "predict, commit, grade, calibrate" loop: recommendations are committed to the public repo before each deadline so git timestamps prove they were not retrofitted; quantile predictions (p10/EV/p90); grading with pinball loss and against three naive baselines; the LLM "writes the memo; it never produces the numbers"; rule hypotheses as structured JSON adopted only if they improve backtest calibration; one Python package, SQLite, GitHub Actions cron — [repo](https://github.com/subhasishgoswami02/fpl-copilot)
- `ajaydhungel7/fpl-agent`: 4 stars, Python, built on the Strands framework — [repo](https://github.com/ajaydhungel7/fpl-agent)
- Others seen with 0 to 1 stars: `jgordley/sir-alex-fpl-agent`, `dav1dm0/FPL-agent` (XGBoost), `desantisjg/fantasy_premier_league_helper`, `LionelKavit/Fantasy-Premier-League-Advisor`, `QuisTech/fpl-admin` — [GitHub search](https://github.com/search?q=fantasy+premier+league+agent&type=repositories)

Supporting data and optimisation repos

- `vaastav/Fantasy-Premier-League`: 1,811 stars, gameweek-by-gameweek historical archive used for backtests — [repo](https://github.com/vaastav/Fantasy-Premier-League)
- `solioanalytics/open-fpl-solver`: 191 stars, optimisation tutorials and recipes for FPL — [repo](https://github.com/solioanalytics/open-fpl-solver)
- `sertalpbilal/fpl_optimized`: 69 stars — [repo](https://github.com/sertalpbilal/fpl_optimized)
- `elcaiseri/OpenFPL-Scout-AI`: 27 stars, ML predictions and team optimisation — [repo](https://github.com/elcaiseri/OpenFPL-Scout-AI)

### Inferences
- The space is crowded at the "wrap the FPL API as MCP tools" level, so that alone will not differentiate a CV project. Differentiators with little or no competition: a solver-backed tool surface with typed results, an evaluated decision loop with baselines, deferred human approval on a scheduled run, and a public audit trail.
- The two strongest small projects share the same principle as the large references: deterministic numbers, LLM for reasoning and explanation. The user's design already follows this.
- Ideas worth adopting directly: commit-before-deadline proof and baseline comparison (fpl-copilot); out-of-band authentication so credentials never enter model context (lewis-king); golden-file tests on frozen API payloads and hold-out season backtests (fantasypl/mcp); a conservative default policy that only deviates past a guardrail (fpl-strategy-mcp); name resolution and caching inside the server so the agent never handles raw ids.
- One LangGraph multi-agent FPL manager already exists as a portfolio project. Building on the Claude Agent SDK with an MCP tool server is a distinct stack, which helps the project stand apart.
- FPL deadlines float (Friday nights, Saturday mornings, midweek rounds), so the scheduled run should check the deadline via the API rather than use a fixed weekly cron, as fpl-copilot does.

### Gaps
- None of these repos' code was inspected; descriptions come from READMEs and may overstate what works.
- Star counts are tiny, so there is no adoption signal to separate good from bad; quality was judged from README content only.
- I did not check whether automating transfers through the FPL site complies with FPL's terms of service; this was outside the brief but matters for the approval-gated submit step.
- The `open-fpl-solver` README was not retrieved, so its solver approach is not described here.
