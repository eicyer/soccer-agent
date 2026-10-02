# Innovative architecture patterns for autonomous LLM agents, and analogous decision-making agents (state as of 30 September 2026)

Evidence labels used below: **[fetched]** = I read the primary page; **[snippet]** = seen only in a search-result summary, not opened, treat as unverified; **[vendor]** = self-reported by a party with a commercial interest.

## Memory and self-improvement

### Takeaway
Plain file-based memory that the agent reads and writes with ordinary file tools is a defensible, well-supported default in 2026; the specialised memory layers (Mem0, Zep/graph) rest largely on vendor-run benchmarks whose results conflict. The best-evidenced self-improvement pattern is an incrementally curated "playbook" (ACE), and the best-documented danger is a wrong or stale lesson that persists and self-reinforces.

### Cited Findings
- Letta (12 Aug 2025) **[fetched, vendor]**: a Letta agent on GPT-4o mini that simply stores conversation histories in files scored 74.0% on LoCoMo, above Mem0's reported 68.5% for its graph variant. Their argument: agents are very good at filesystem tools because those are heavily represented in training data, and can reformulate queries iteratively rather than rely on single-hop retrieval. They also say they could not reproduce Mem0's MemGPT baseline and that Mem0 did not answer requests for clarification; they advocate task-based evaluation over retrieval benchmarks. — [Benchmarking AI Agent Memory: Is a Filesystem All You Need?](https://www.letta.com/blog/benchmarking-ai-agent-memory/)
- Disputed numbers **[snippet, vendor]**: Mem0's own "State of AI Agent Memory 2026" reports Mem0 at 92.5 on LoCoMo and 94.4 on LongMemEval versus Zep 80.32 / 71.2 and Letta 74.0. — [Mem0 blog](https://mem0.ai/blog/state-of-ai-agent-memory-2026); contradicted in ordering by a third-party reproducible run dated 2026-09-23 reporting best system 57.6%, Letta 0.11.7 at 52.2%, Mem0 2.1.0 at 50.0%, Zep/Graphiti 0.30.2 at 37.0% recall **[snippet]** — [agent-memory-bench](https://github.com/hamza-dev-tech/agent-memory-bench). Absolute scores and rankings depend heavily on who ran the benchmark.
- Anthropic memory tool (29 Sep 2025) **[fetched, vendor]**: file-based, client-side; Claude can create, read, update and delete files in a memory directory stored in the developer's infrastructure. On an internal agentic-search evaluation set, context editing alone gave a 29% improvement and memory tool plus context editing 39% over baseline; in a 100-turn web-search evaluation context editing cut token consumption by 84%. Internal eval, not independently replicated. — [Managing context on the Claude Developer Platform](https://claude.com/blog/context-management)
- Anthropic launched Memory for Managed Agents in public beta on 23 Apr 2026, with cross-session learning and per-write audit trails; a customer claim of 97% error-rate reduction (Rakuten) is quoted **[snippet, third-party blog, marketing claim]**. — [usewire.io summary](https://usewire.io/blog/anthropic-managed-agents-memory-context-engineering/)
- ACE, "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models", Qizheng Zhang, Changran Hu, Shubhangi Upasani, Boyuan Ma et al. (submitted 6 Oct 2025, revised 29 Mar 2026, ICLR 2026) **[fetched abstract]**: names two failure modes of rewritten contexts, "brevity bias" (domain insight dropped in favour of concise summaries) and "context collapse" (iterative rewriting erodes detail). Remedy: a Generator / Reflector / Curator loop that treats context as an evolving playbook updated from execution feedback without labels. — [arXiv 2510.04618](https://arxiv.org/abs/2510.04618)
- ACE reported results **[snippet of abstract]**: +10.6% on agent benchmarks (AppWorld) and +8.6% on financial reasoning over baselines including ICL, MIPROv2, GEPA and Dynamic Cheatsheet; 86.9% lower adaptation latency; matches the top AppWorld leaderboard agent with a smaller open-source model. Author-reported. — [arXiv 2510.04618](https://arxiv.org/abs/2510.04618)
- Survey, "Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers", Pengfei Du (8 Mar 2026) **[fetched]**: reflective memory's central risk is self-reinforcing error ("if the agent incorrectly concludes 'API X always returns errors with parameter Y,' it will avoid that call path forever, never collecting evidence to overturn the false belief"); also over-generalisation of lessons, and "summarization drift" where repeated compression leaves "a sanitized, generic version of history" and can drop an early safety instruction after a few summary cycles. — [arXiv 2603.07670](https://arxiv.org/html/2603.07670v1)
- Same survey, evaluation gap: on MemoryArena (He et al., 2026) models near-perfect on LoCoMo "plummet to 40–60%", a gap "between passive recall and active, decision-relevant memory use"; only MemoryAgentBench tests selective forgetting; cross-session coherence is "largely unsolved". — [arXiv 2603.07670](https://arxiv.org/html/2603.07670v1)
- Same survey, mitigations: "reflection grounding" (each lesson must cite specific episodic evidence, giving an auditable trail), confidence scores, contradiction checking, periodic expiration, temporal versioning, source attribution, periodic consolidation. These are recommendations, not measured results. — [arXiv 2603.07670](https://arxiv.org/html/2603.07670v1)
- Field evidence that notes are not self-executing: AI Village agents "create exhaustive records but fail to return to them" and write lessons-learned documents then rediscover the same lessons **[snippet]**. — [Asterisk, Field notes from an AI society](https://asteriskmag.substack.com/p/field-notes-from-an-ai-society)
- Pokémon evidence on note quality: Claude "is utterly dependent on the quality of his notes: one incorrect assumption or hallucination embedded into a note can crater progress for days" **[snippet]**. — [LessWrong, Insights into Claude Opus 4.5 from Pokémon](https://www.lesswrong.com/posts/u6Lacc7wx4yYkBQ3r/insights-into-claude-opus-4-5-from-pokemon)
- Memory as an attack surface: 2026 papers on persistent memory poisoning exist (MemPoison, Sleeper Memory Poisoning, MemEvoBench) **[snippet, titles only]**. — [arXiv 2607.14651](https://arxiv.org/pdf/2607.14651), [arXiv 2605.15338](https://arxiv.org/pdf/2605.15338), [arXiv 2604.15774](https://arxiv.org/pdf/2604.15774)

### Inferences
- A file-based season journal is aligned with current practice, not a shortcut: the strongest independent-looking signal (Letta) and Anthropic's own tooling both point to files plus ordinary tools.
- The retrospective loop should follow ACE's shape: append or amend discrete, itemised lessons (delta updates) rather than letting the LLM rewrite the whole journal each week, which is the mechanism for context collapse.
- Each lesson should carry evidence (gameweek, decision, model output, realised outcome), a date, and an expiry or review rule. FPL is high-variance, so a one-week bad outcome is weak evidence; lessons should be about process (e.g. information missed) not outcome, otherwise the self-reinforcing-error failure applies directly.
- Writing memory is not enough; the harness must force reading the relevant lessons at decision time (AI Village observation).
- Scraped news must never be written into durable memory unreviewed, given the poisoning literature.

### Gaps
- No independent, neutral head-to-head of Letta, Mem0 and Zep was read in full; the numbers above conflict and the one third-party benchmark was seen only as a snippet.
- I did not find evidence on memory systems for a weekly-cadence decision agent specifically (about 38 sessions a season); benchmarks are conversational QA.
- Skill libraries (Voyager-style) and Zep's temporal graph paper were not researched in depth.

## Context engineering

### Takeaway
The consensus, set by Anthropic's September 2025 post and not seriously challenged since, is that context is a finite resource that degrades with length ("context rot"), so agents should hold lightweight references, load data just in time, compact, keep structured notes outside the window, and use subagents as context firewalls that return short summaries.

### Cited Findings
- "Effective context engineering for AI agents", Prithvi Rajasekaran, Ethan Dixon, Carly Ryan, Jeremy Hadfield (Anthropic, 29 Sep 2025) **[fetched]**: "As the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases." — [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Just-in-time retrieval: agents "maintain lightweight identifiers (file paths, stored queries, web links, etc.) and use these references to dynamically load data into context at runtime." — [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Compaction: summarise near the limit and restart with the summary; the risk named is that over-aggressive compaction loses subtle context whose importance only shows later. — [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Structured note-taking: persistent notes outside the window; the Pokémon agent kept "precise tallies across thousands of game steps" across context resets. — [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Subagents: each explores extensively but returns a "condensed, distilled summary of its work (often 1,000-2,000 tokens)". — [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Progressive disclosure for tools: present tools as a filesystem of code so the agent reads only the definitions it needs (Adam Jones, Conor Kelly, 4 Nov 2025). — [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- Long-horizon benchmark corroboration: a Vending-Bench 2 run is 3,000–6,000 messages and 60–100M output tokens, far beyond any context window, so the harness must compress; Andon Labs added "proper note-taking and reminder systems". — [Vending-Bench 2](https://andonlabs.com/evals/vending-bench-2)

### Inferences
- For a weekly agent, each gameweek run can start from a fresh context built from the journal plus tool calls, so in-session compaction matters less than a well-structured cross-session state file; summarization drift across weeks is the relevant risk.
- Analyst subagents should return short structured verdicts with pointers to evidence, not raw news dumps, to the Manager.

### Gaps
- I did not fetch Anthropic's Agent Skills posts, so progressive disclosure via skills is supported here only by the code-execution post and general knowledge; no quantitative evidence on skills was found.
- No independent measurement of context rot thresholds for current (2026) models was collected.

## Tools: code execution, tool search, fewer higher-level tools

### Takeaway
Anthropic's measured claims support three moves when tool sets are large or workflows multi-step: on-demand tool discovery, letting the model orchestrate tools from code so intermediate data stays out of context, and adding usage examples. All are presented as paying off only at scale, and code execution brings a sandboxing burden.

### Cited Findings
- "Introducing advanced tool use", Bin Wu et al. (Anthropic, 24 Nov 2025) **[fetched, vendor]**. Tool Search Tool: about 85% fewer tokens (roughly 77K to 8.7K); accuracy on MCP evals Opus 4 49% to 74%, Opus 4.5 79.5% to 88.1%; recommended above roughly 10 tools or 10K tokens of definitions. — [Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)
- Programmatic Tool Calling: 37% token reduction on complex tasks (43,588 to 27,297 average); knowledge retrieval 25.6% to 28.5%; GAIA 46.5% to 51.2%. Best for dependent multi-step calls or large data needing aggregation. — [Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)
- Tool Use Examples: 72% to 90% accuracy on complex parameter handling. — [Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)
- Stated trade-off: each feature adds overhead and is meant for scaling complexity, not simple function calling. — [Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)
- Code execution with MCP: one worked example went from 150,000 to 2,000 tokens (98.7%); intermediate results "stay in the execution environment by default"; agents can persist reusable functions as skills. Cost: "Running agent-generated code requires a secure execution environment with appropriate sandboxing, resource limits, and monitoring." The 98.7% is an illustrative example, not a benchmark. — [Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp)
- Tool design rule: minimal overlap, self-contained, clear purpose; "If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better." — [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- A search summary dated these features to November 2024; the primary page says 24 Nov 2025. — [Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)

### Inferences
- An FPL agent with a handful of MCP tools (xP model, MILP optimiser, squad state, news) is below the threshold where tool search helps; the transferable lesson is few, high-level, non-overlapping tools that return compact results (e.g. top-N transfers with deltas, not the full player table).
- Programmatic calling is relevant for scenario sweeps (many optimiser runs under different constraints) where only a comparison table should reach the model.
- Code-executing agents widen the attack surface if the same context has read untrusted news.

### Gaps
- No independent replication of Anthropic's numbers was found; current GA/beta status of these features in September 2026 was not checked.

## Neuro-symbolic hybrids: LLM orchestrating optimisers, solvers and forecasters

### Takeaway
Published evidence supports the "LLM never does the numbers" rule: when LLMs generate numeric forecasts directly they fail on scale and units, and when they write optimisation models from scratch most failures are modelling errors that occur before the solver runs. Systems that keep a fixed numeric engine and use the LLM to select, rank or parameterise are more reliable.

### Cited Findings
- "LLM as Forecasting Planner: Training-Free Text Conditioning for Time-Series Foundation Models", Nguyen et al. (July 2026) **[fetched]**: the frozen time-series foundation model produces all numbers; the LLM only ranks candidate continuations and judges trajectories against textual context, inside Monte Carlo tree search. Reported 4% error reduction over context-blind baselines on Context-is-Key and up to 60% on Time-MMD with a Chronos backbone. Direct LLM forecasting varied 27–134% by model and failed catastrophically in some domains "from incorrect scale or unit assumptions rather than incorrect trends". Author-reported. — [arXiv 2607.24892](https://arxiv.org/html/2607.24892v1)
- "ORAgentBench: Can LLM Agents Solve Challenging Operations Research Tasks End to End?", Li, Cai, Li, Ding, Hou, Nie, Han, Wang (June 2026) **[fetched]**: 14 model-agent configurations on 107 executable tasks; best pass rate 35.51% (GPT-5.4), 20.59% on hard tasks; modelling errors (missed rules, wrongly encoded constraints) were 54.8% of failures; many feasible answers fell short on solution quality. — [arXiv 2606.19787](https://arxiv.org/html/2606.19787)
- OptiMUS (first version Oct 2023; OptiMUS-0.3 2024) is an LLM agent that formulates MILPs from natural language, writes and debugs solver code and checks solutions **[snippet]**. Older work; the line continues in 2026 (ORPilot, COOPA, Opti-Agent-Bench, titles only). — [arXiv 2310.06116](https://arxiv.org/abs/2310.06116), [ORPilot](https://arxiv.org/pdf/2605.02728), [COOPA](https://arxiv.org/pdf/2606.27611)
- Trading analogue of structural enforcement: an honest-evaluation harness used "registry-validated tools" that exclude look-ahead features structurally, because statistical deflation "has no mechanism against a strategy whose information set is contaminated". — [arXiv 2608.27734](https://arxiv.org/html/2608.27734)
- ForecastBench (Karger, Bastani, Chen, Jacobs, Halawi, Zhang, Tetlock; v5 28 Feb 2025) **[fetched]**: supplying base rates / crowd forecasts ("freeze values") substantially improved LLM forecasts, while retrieved news did not meaningfully help. — [arXiv 2409.19839](https://arxiv.org/html/2409.19839v5)

### Inferences
- Keep the MILP formulation hand-written and fixed; let agents pass only validated parameters (locks, bans, horizon, chip flags, bounded xP adjustments). ORAgentBench suggests LLM-authored constraints are the weak point.
- If news is allowed to change numbers, do it as a bounded, logged, structured adjustment to model inputs (e.g. availability probability), then re-run the optimiser, mirroring the ranker/judge split in LAFP.
- Validate optimiser output deterministically (budget, squad rules, feasibility) before any agent sees or acts on it.
- ForecastBench's null result on news is a caution: news reading should be tested for whether it improves decisions rather than assumed to.

### Gaps
- No paper was found evaluating an LLM that orchestrates a fixed, human-written optimiser for a recurring decision (as opposed to writing the model); the design lesson is inferred from adjacent results.
- OptiMUS and the 2026 OR-agent papers other than ORAgentBench were not read in full.

## Prompt and pipeline optimisation

### Takeaway
GEPA is the leading automatic prompt optimiser and has real production users, mostly for judge and classifier prompts, but a 2026 benchmark shows gains on multi-agent systems are small on average and sometimes negative.

### Cited Findings
- GEPA (Genetic-Pareto) is a reflective optimiser in DSPy that evolves instructions from natural-language reflection on execution traces; ICLR 2026 oral; claims +14% aggregate over MIPROv2 and up to 35x fewer rollouts than GRPO **[snippet, project/vendor pages]**. — [gepa-ai/gepa](https://github.com/gepa-ai/gepa), [Morph summary](https://www.morphllm.com/gepa-prompt-optimization)
- Production use claims **[snippet, from the project's own list]**: "50+ production uses" including Shopify, Databricks, Dropbox; Nubank optimising LLM-as-judge prompts for support agents; Microsoft AI optimising a judge prompt for data filtering. — [gepa-ai/gepa](https://github.com/gepa-ai/gepa); a first-hand production write-up exists from Decagon (not read) — [Decagon](https://decagon.ai/blog/optimizing-gepa-for-production)
- "MAS-PromptBench: When Does Prompt Optimization Improve Multi-Agent LLM Systems?", Juyang Bai, Laixi Shi (Johns Hopkins; arXiv 2606.23664) **[fetched]**: multi-agent extensions of GEPA and MIPRO gave a +4.2 point average single-agent gain but only -0.5 to +2.3 across multi-agent topologies; extremes +24.0 (sequential, BFCL) and -16.0 (independent, MATH). Gains were larger for coding/tool-calling tasks (+3.7 to +4.3) than reasoning (+1.3), for structured communication (+4.3 vs +1.6 freeform), and shrank with team size (+2.4 at n=2 to -2.1 at n=10). The fetch tool reported a date of 24 Aug 2026, which does not match the June 2026 arXiv identifier; treat the exact date as unconfirmed. — [arXiv 2606.23664](https://arxiv.org/html/2606.23664)
- ACE reports beating GEPA and MIPROv2 on its own benchmarks (author-reported). — [arXiv 2510.04618](https://arxiv.org/abs/2510.04618)
- Related 2026 preprints seen by title only: "Coding Agents are Strong Prompt Optimizers" and "A Single Rewrite Suffices: Empirical Lessons from Production Skill Description Optimization". — [arXiv 2609.26261](https://arxiv.org/pdf/2609.26261), [arXiv 2606.30775](https://arxiv.org/pdf/2606.30775)

### Inferences
- Automatic optimisation needs a metric and many labelled or scorable examples. A weekly agent produces about 38 noisy outcomes a season, so optimising the full pipeline against points is not credible; optimising narrow, checkable components (news extraction into structured availability facts, a judge prompt) against a hand-labelled set is.
- Structured inter-agent messages make the system more optimisable, per MAS-PromptBench.

### Gaps
- I did not verify any production claim at its primary source; the list is self-reported by the GEPA project.
- No evidence found of DSPy/GEPA being used with the Claude Agent SDK specifically.

## Analogous systems

### Takeaway
Trading frameworks popularised role-played analyst teams with bull/bear debate, but their headline results are backtests that do not survive rigorous evaluation, and the debate literature finds adversarial debate rarely beats a single strong agent. Long-horizon agent experiments agree that harness, notes and explicit goals matter as much as model strength, and that hallucinated facts spreading between agents is a real failure.

### Cited Findings
**Trading**
- "TradingAgents: Multi-Agents LLM Financial Trading Framework", Yijia Xiao, Edward Sun, Di Luo, Wei Wang (28 Dec 2024; v7 3 Jun 2025) **[fetched abstract]**: fundamental, sentiment and technical analysts; bull and bear researchers who debate; a trader; a risk-management team. Claims improved cumulative return, Sharpe and drawdown; the abstract gives no period or tickers. Older work, still widely used (v0.2.4 referenced in 2026). — [arXiv 2412.20138](https://arxiv.org/abs/2412.20138)
- The project's own repository warns runs are non-deterministic and that backtest results "are not guaranteed to match any published figure" **[snippet]**. — [TauricResearch/TradingAgents](https://github.com/tauricresearch/tradingagents)
- "What Survives Honest Evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery", Eray Gençay (Aug 2026) **[fetched]**: across 453 US stocks and 39 ETFs with realistic costs, every LLM-discovered strategy failed certification against the agent's own recorded trial count; the best went from Sharpe 1.69 in design to 0.18 in evaluation; 0 of 5 independent runs survived; only passive benchmarks certified; a deliberately leaked oracle scored Sharpe 34.7 and passed deflation, showing deflation does not catch leakage. It does not name TradingAgents; it is a critique of the evaluation practice generally. — [arXiv 2608.27734](https://arxiv.org/html/2608.27734)
- Also seen by title: adversarial poisoning of multi-agent trading systems across roles. — [arXiv 2608.24069](https://arxiv.org/pdf/2608.24069)

**Debate structures**
- "If Multi-Agent Debate is the Answer, What is the Question?" (Feb 2025) **[snippet]**: no tested debate method exceeded a 20% win rate against chain-of-thought across 36 scenarios (4 models x 9 benchmarks). — [arXiv 2502.08788](https://www.alphaxiv.org/abs/2502.08788v1)
- "Debate or Vote" (Aug 2025) **[snippet]**: majority voting accounts for most of the gains attributed to debate. — [arXiv 2508.17536](https://arxiv.org/html/2508.17536v1)
- "When and Why Does Multi-Agent Debate Fail and Does It Really Underperform?", Yongqiang Chen, Gang Niu, James Cheng, Bo Han, Masashi Sugiyama (v2 14 Jul 2026) **[fetched]**: competitive debate degenerates into "debate hacking" (persuasion over truth) and can fall up to 15 points below single-agent; consensus-seeking debate suppresses useful disagreement. A collaborative variant with quote-based evidence verification, self-auditing and a calibrated judge beat competitive debate by up to 10 points and single-agent by about 4; benefit is largest with heterogeneous models. — [arXiv 2510.20963](https://arxiv.org/html/2510.20963v2)

**Forecasting**
- ForecastBench v5 (28 Feb 2025): superforecasters Brier 0.096, public 0.121, best LLM (Claude 3.5 Sonnet) 0.122. Older; a later update says the median public forecaster fell from #2 to #22 on the leaderboard by Oct 2025, i.e. many LLMs now beat the public but superforecasters still led **[snippet]**. — [arXiv 2409.19839](https://arxiv.org/html/2409.19839v5), [EA Forum roundup](https://forum.effectivealtruism.org/posts/Spyz3wESZu2eeqhDj/ai-forecasting-in-2026-what-11-analyses-say)
- Metaculus runs a recurring AI Forecasting Benchmark tournament (Spring 2026, $58,000 prizes) **[snippet]**. — [Metaculus AIB](https://www.metaculus.com/aib/)

**Long-horizon game and business agents**
- Vending-Bench 2 (Andon Labs) **[fetched]**: $500 start, one simulated year, adversarial suppliers; leaderboard at fetch time GPT-6 Astra $15,514.70, GPT-6 Sol $14,427.85, Claude Opus 5 $11,181.87, against an estimated ~$63,000 achievable by a good strategy. A search summary of an older snapshot listed Claude Opus 4.7 first at $10,936.76, so the board changes with releases. — [Andon Labs](https://andonlabs.com/evals/vending-bench-2); older snapshot [llm-frontier-wiki](https://github.com/redstone-solution-ou/llm-frontier-wiki/blob/main/wiki/benchmarks/vending-bench-2.md)
- Documented failure modes there: looping, identity drift, hallucinated supplier emails, pricing below cost, paying the same invoice twice; failures of coherence across steps rather than of single-step reasoning **[snippet]**. — [llm-frontier-wiki](https://github.com/redstone-solution-ou/llm-frontier-wiki/blob/main/wiki/benchmarks/vending-bench-2.md)
- Pokémon: Gemini 2.5 Pro finished Pokémon Blue in May 2025 with a richer harness (screen-to-text, puzzle tools, primary/secondary/tertiary goals re-inserted after every context reset, a harness-computed list of reachable unexplored tiles), whereas Claude ran a minimal harness **[snippet]**. — [TIME](https://time.com/7345903/ai-chatgpt-claude-gemini-pokemon/), [The Making of Gemini Plays Pokémon](https://blog.jcz.dev/the-making-of-gemini-plays-pokemon)
- AI Village, "What did we learn from the AI Village in 2025?", Shoshannah Tekofsky (2 Feb 2026) **[fetched]**: late-2025 models were far more persistent than spring ones; in 109,000 chain-of-thought summaries, 64 cases showed explicit intent to fabricate; most false claims had no such intent; Claude models tended to exaggerate accomplishments; one agent's hallucinated belief spread and consumed 8+ hours of team effort. — [AI Village blog](https://aivillageblog.substack.com/p/what-we-learned-2025)

**Fantasy sports and betting**
- An Uppsala University degree project, "Enhancing Fantasy Premier League Strategies through Machine Learning and Large Language Models" (May 2025), exists **[snippet; PDF could not be parsed]**. — [DiVA](https://uu.diva-portal.org/smash/get/diva2:1972615/FULLTEXT02.pdf)
- "FanCric: Multi-Agentic Framework for Crafting Fantasy 11 Cricket Teams" (Oct 2024) **[snippet, title only]**. — [arXiv 2410.01307](https://arxiv.org/pdf/2410.01307)
- Other hits were hobbyist blog posts (LangGraph fantasy research agent, a browser agent told to optimise an FPL team) with no evaluation. — [Medium example](https://medium.com/@jongoodey/how-i-used-an-ai-agent-to-optimise-my-fantasy-premier-league-team-in-minutes-bfc1dc7e8dea)

### Inferences
- A sceptic is better designed as an evidence checker than an opponent: require it to quote tool outputs or journal entries and to flag missing evidence (the collaborative pattern), not to argue the opposite case. A sceptic on a different model family would add the heterogeneity that the literature says helps.
- The trading critique transfers to evaluation of the FPL agent: any backtest must prevent look-ahead structurally (only data available before each deadline), count every configuration tried, and compare against simple baselines (template team, optimiser-only with no LLM). "Optimiser-only" is the honest ablation for whether the agents add value.
- Every subagent claim about an action taken should be verified from system state, not from the agent's report, given observed exaggeration and fabricated actions.
- Standing goals and constraints should be re-injected by the harness each run, as in the Gemini Pokémon harness, rather than trusted to survive in notes.
- There appears to be little rigorous published work on LLM agents for fantasy sports, which makes a well-evaluated FPL agent comparatively novel.

### Gaps
- FinRobot and specific published critiques naming TradingAgents were not found or read; the critique cited is of LLM trading evaluation in general.
- The FPL thesis and FanCric were not read, so their methods and results are unknown.
- No credible published sports-betting LLM agent with out-of-sample results was found.
- ForecastBench's current (2026) leaderboard and whether LLMs have reached superforecaster parity were not verified at a primary source.
- Vending-Bench Arena findings were not detailed on the page fetched.

## Safety and control for agents that take real actions

### Takeaway
Prompt injection remains unsolved at the model level; the accepted approach is architectural: do not let one context combine untrusted input, sensitive access and state-changing actions without a human or deterministic check. Dual-LLM and CaMeL designs are the most principled defences but were reported as not adopted by mainstream harnesses.

### Cited Findings
- Simon Willison, "The lethal trifecta for AI agents" (16 Jun 2025) **[fetched]**: the dangerous combination is access to private data, exposure to untrusted content, and ability to communicate externally. He is sceptical of guardrail products claiming to catch "95% of attacks", since 95% is a failing grade in security. — [simonwillison.net](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- Meta, "Agents Rule of Two" (31 Oct 2025) **[fetched]**: an agent should satisfy no more than two of [A] processing untrustworthy inputs, [B] access to sensitive systems or private data, [C] changing state or communicating externally, within a session. If all three are needed, "the agent should not be permitted to operate autonomously and at a minimum requires supervision — via human-in-the-loop approval or another reliable means of validation." It extends the trifecta to cover state change, not only exfiltration. — [Meta AI](https://ai.meta.com/blog/practical-ai-agent-security/)
- "Design Patterns for Securing LLM Agents against Prompt Injections" (June 2025; authors from Google, Microsoft, IBM, ETH Zurich, EPFL) **[snippet]**: six patterns: action-selector, plan-then-execute, LLM map-reduce, dual LLM, code-then-execute, context-minimisation. — [arXiv 2506.08837](https://arxiv.org/abs/2506.08837), [Willison's write-up](https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/)
- CaMeL, "Defeating Prompt Injections by Design", Edoardo Debenedetti, Ilia Shumailov, Tianqi Fan, Jamie Hayes, Nicholas Carlini et al. (24 Mar 2025, revised 24 Jun 2025) **[fetched abstract]**: a privileged LLM plans from the trusted query, a quarantined LLM handles untrusted data without tools, and an interpreter tracks provenance and enforces capability policies at each tool call; solves 77% of AgentDojo tasks with provable security versus 84% undefended. — [arXiv 2503.18813](https://arxiv.org/abs/2503.18813)
- Adoption status: a 2026 commentary states CaMeL and dual-LLM are "not adopted by any mainstream agent harness" and no production-grade CaMeL exists **[snippet, secondary source, unverified]**; the same result cites a Google April 2026 study finding a 32% rise in malicious injection attempts in Common Crawl between Nov 2025 and Feb 2026 **[snippet, unverified]**. — [The Bright Byte](https://thebrightbyte.com/playbook/expertise/lethal-trifecta-ai-agent-defense-architecture-2026)
- Autonomy levels: "Levels of Autonomy for AI Agents" (Knight First Amendment Institute; arXiv June 2025) defines five levels by the user's role: operator, collaborator, consultant, approver, observer, and argues autonomy is a design decision separate from capability **[snippet]**. — [Knight Institute](https://knightcolumbia.org/content/levels-of-autonomy-for-ai-agents-1), [arXiv 2506.12469](https://arxiv.org/html/2506.12469v2)
- Human-in-the-loop mechanics: LangGraph interrupts pause at designated nodes before sensitive operations, persist state, and resume from the same point after review **[snippet]**. — [LangGraph HITL article](https://sangeethasaravanan.medium.com/human-in-the-loop-tool-calling-with-langgraph-building-interruptible-ai-agents-fd0275ce4523)
- A concrete failure that idempotency would prevent: Vending-Bench agents "paying the same invoice twice" **[snippet]**. — [llm-frontier-wiki](https://github.com/redstone-solution-ou/llm-frontier-wiki/blob/main/wiki/benchmarks/vending-bench-2.md)

### Inferences
- The FPL agent holds all three Rule-of-Two properties: it reads web news (A), holds account credentials (B) and can make transfers (C). The clean fix is structural separation: the news scout runs with no credentials and no action tools and emits only a constrained schema (player id, status enum, probability, source URL); the Manager never sees raw web text; the execute tool sits behind a deterministic policy check and, below full autonomy, an approval gate. This is the dual-LLM and context-minimisation patterns applied.
- Policy-as-code checks before execution should be deterministic and outside the LLM: legal squad, budget, hit cost cap, chip use requires approval, action matches the approved plan, deadline not passed.
- Execution should be dry-run by default, idempotent per gameweek (a recorded intent key checked against account state before acting), and verified by re-reading account state afterwards. FPL transfers are largely irreversible once confirmed and chips cannot be undone, so rollback is mostly unavailable and prevention must carry the weight.
- Mapping the project's autonomy levels onto the Knight Institute's five roles gives a citable framing.

### Gaps
- No primary source was read for policy-as-code tooling, dry-run, idempotency or rollback patterns for agents; those points are inferences from general engineering practice plus the benchmark failure cited.
- The claim that no mainstream harness adopts CaMeL comes from a secondary blog and was not verified; nor was the Google Common Crawl statistic.
- Claude Agent SDK's own permission, hook and approval mechanisms were out of scope here and not researched.
