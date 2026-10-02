# Observability, evaluation and cost control of multi-agent LLM systems (state as of 30 September 2026)

All pages were fetched on 2026-09-30 unless a publication date is given. "Listicle" marks a figure that comes from a vendor comparison article rather than the vendor's own page.

## Observability: standards (OpenTelemetry GenAI, OpenInference), tools, and what good agent tracing captures

### Takeaway
The OpenTelemetry GenAI conventions (including agent, workflow and tool spans) are still in "Development" status in September 2026 and have moved to their own repository with no tagged release, so attribute names can still change; OpenInference (Apache-2.0) is the practical instrumentation layer used by both Langfuse and Phoenix for the Claude Agent SDK. The Agent SDK itself emits OTLP natively (traces are beta) with subagent spans nested under the parent tool span, so Langfuse can be fed either by the native export or by the OpenInference instrumentor.

### Cited Findings

**OpenTelemetry GenAI semantic conventions**
- The GenAI conventions no longer live on opentelemetry.io's main semconv page: "GenAI semantic conventions have moved to the OpenTelemetry GenAI semantic conventions repository" and the old page "is no longer maintained in this repository" — [opentelemetry.io agent spans page](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)
- The new repository `open-telemetry/semantic-conventions-genai` has no published releases ("There aren't any releases here") — [GitHub releases](https://github.com/open-telemetry/semantic-conventions-genai/releases)
- Agent and framework spans are all in **Development** status. Defined operations: `create_agent` (CLIENT), `invoke_agent` (CLIENT for remote, INTERNAL for in-process), `invoke_workflow` (INTERNAL, coordinated multi-agent processes), `plan` (INTERNAL). Span name format `invoke_agent {gen_ai.agent.name}` — [gen-ai-agent-spans.md](https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/gen-ai-agent-spans.md)
- Key agent attributes: `gen_ai.operation.name` (required), `gen_ai.agent.id`, `gen_ai.agent.name`, `gen_ai.agent.description`, `gen_ai.agent.version`, `gen_ai.conversation.id`, and usage attributes `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.cache_write.input_tokens`. Content attributes (`gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`, `gen_ai.tool.definitions`) are opt-in because they are "likely to contain sensitive information" — [gen-ai-agent-spans.md](https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/gen-ai-agent-spans.md)
- Model-level spans are also **Development**: inference, embeddings, retrievals, fetch response, memory, and execute tool. Tool span name is `{gen_ai.operation.name} {gen_ai.tool.name}`; attributes `gen_ai.tool.name` (required), `gen_ai.tool.call.id`, `gen_ai.tool.type` — [gen-ai-spans.md](https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/gen-ai-spans.md)

**OpenInference**
- OpenInference is "a set of conventions and plugins that is complementary to OpenTelemetry to enable tracing of AI applications"; Apache-2.0; span kinds include LLM, AGENT, TOOL, CHAIN, RETRIEVER, EVALUATOR, GUARDRAIL; Python packages include `openinference-instrumentation-claude-agent-sdk`, `openinference-instrumentation-anthropic`, `openinference-instrumentation-mcp` — [Arize-ai/openinference](https://github.com/Arize-ai/openinference)

**Claude Agent SDK native telemetry (primary documentation)**
- The SDK "does not produce telemetry of its own"; it runs the Claude Code CLI as a child process, which exports three OTLP signals: metrics (tokens, cost, sessions, tool decisions), log events (each prompt, API request, API error, tool result) and traces. Traces are beta and need `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` in addition to `CLAUDE_CODE_ENABLE_TELEMETRY=1` and `OTEL_TRACES_EXPORTER=otlp`; "Span names and attributes may change between releases" — [Agent SDK observability](https://code.claude.com/docs/en/agent-sdk/observability)
- Span names: `claude_code.interaction` (one turn of the loop), `claude_code.llm_request` (model, latency, token counts), `claude_code.tool` with children `claude_code.tool.blocked_on_user` and `claude_code.tool.execution`, and `claude_code.hook`. These are Claude-specific names, not the `gen_ai.*` convention names — [Agent SDK observability](https://code.claude.com/docs/en/agent-sdk/observability)
- Subagent attribution: "the subagent's `llm_request` and `tool` spans nest under the parent agent's `claude_code.tool` span, so the full delegation chain appears as one trace" — [Agent SDK observability](https://code.claude.com/docs/en/agent-sdk/observability)
- Spans carry `session.id`; the SDK injects W3C `TRACEPARENT`/`TRACESTATE` so the agent run becomes a child of an application span that is active when `query()` is called — [Agent SDK observability](https://code.claude.com/docs/en/agent-sdk/observability)
- Content is not exported by default. Opt-in flags: `OTEL_LOG_USER_PROMPTS=1`, `OTEL_LOG_TOOL_DETAILS=1` (tool arguments, and real agent/skill/MCP server names on cost and token metrics), `OTEL_LOG_TOOL_CONTENT=1` (tool output, truncated at 60 KB by default; MCP tool results need Claude Code v2.1.283+), `OTEL_LOG_RAW_API_BODIES` — [Agent SDK observability](https://code.claude.com/docs/en/agent-sdk/observability)
- Pitfalls for short weekly jobs: export errors fail silently unless `CLAUDE_CODE_OTEL_DIAG_STDERR=1` is set; traces and logs export every 5 s and metrics every 60 s by default, and spans can be dropped on exit, so lower `OTEL_TRACES_EXPORT_INTERVAL`, `OTEL_LOGS_EXPORT_INTERVAL`, `OTEL_METRIC_EXPORT_INTERVAL`; do not use the `console` exporter because stdout is the SDK message channel; use `OTEL_SERVICE_NAME` and `OTEL_RESOURCE_ATTRIBUTES` (e.g. `service.version`) to tag runs — [Agent SDK observability](https://code.claude.com/docs/en/agent-sdk/observability)

**Tool-specific Claude Agent SDK support**
- Langfuse's documented Python route uses three packages (`langfuse`, `claude-agent-sdk`, `openinference-instrumentation-claude-agent-sdk`) and `ClaudeAgentSDKInstrumentor().instrument()`; "Every tool call and model completion is captured as an OpenTelemetry span and forwarded to Langfuse". Noted issues: instrument before application code, call `langfuse.flush()` in short-lived processes. The page does not document token, cost or subagent capture — [Langfuse Claude Agent SDK integration](https://langfuse.com/integrations/frameworks/claude-agent-sdk)
- Phoenix uses the same OpenInference package; documented capture is AGENT spans wrapping the full `query()` call and TOOL spans per tool invocation, with `hide_inputs`/`hide_outputs` masking. Token counts, cost and subagents are not mentioned — [Phoenix Claude Agent SDK integration](https://arize.com/docs/phoenix/integrations/python/claude-agent-sdk)
- LangSmith has a native integration (`langsmith[claude-agent-sdk]`, `configure_claude_agent_sdk()`) that traces agent queries, tool invocations, model interactions and MCP server operations — [LangSmith docs](https://docs.langchain.com/langsmith/trace-claude-agent-sdk)
- Search-result snippet only (not verified on a fetched page): Langfuse accepts OTLP over HTTP/protobuf but not gRPC — [search result pointing to Langfuse docs/discussions](https://langfuse.com/integrations/frameworks/claude-agent-sdk)

**Pricing and self-hosting (vendor pages)**
- Langfuse Cloud: Hobby free, 50k units/month, 30-day retention; Core $29/month, 100k units, 90 days; Pro $199/month, 100k units, 3 years; Enterprise $2,499/month; overage $8 per 100k units falling to $6 at 50M+ — [Langfuse pricing](https://langfuse.com/pricing)
- Langfuse self-hosting: open source and free, some "(EE)" features need a licence key; docs are at version v4; requires PostgreSQL, ClickHouse, Redis/Valkey and S3/blob storage; Docker Compose for a single VM, Helm/cloud templates for production — [Langfuse self-hosting](https://langfuse.com/self-hosting)
- LangSmith: Developer free (1 seat, 5k base traces/month); Plus $39/seat/month (10k base traces); base traces 14-day retention, extended 180-day; self-hosted and hybrid only on Enterprise — [LangChain pricing](https://www.langchain.com/pricing)
- Braintrust: Starter free (1 GB processed data, 10k scores, 14-day retention, unlimited users); Pro $249/month (5 GB, 50k scores, 30 days); on-premises only on Enterprise — [Braintrust pricing](https://www.braintrust.dev/pricing)
- Pydantic Logfire: Personal free (10M records/month, 3 projects, 30-day retention, hard cap at $0); Team $49/month (10M included, $2 per additional million); Growth $249/month (up to 90-day retention); self-hosted only on Enterprise — [Pydantic pricing](https://pydantic.dev/pricing)
- Listicle figures, unverified on vendor pages: Arize Phoenix is free to self-host with managed cloud from $50/month; W&B Weave is free for individuals — [search results summarising Arize/Latitude/Braintrust comparison articles](https://arize.com/blog/best-ai-observability-tools-for-autonomous-agents-in-2026/)

**What practitioners say tracing should enable**
- Anthropic's multi-agent research system monitors "agent decision patterns and interaction structures" without reading conversation contents — [Anthropic, "How we built our multi-agent research system", 13 June 2025](https://www.anthropic.com/engineering/multi-agent-research-system)
- Anthropic defines the transcript as "The complete record of a trial, including outputs, tool calls, reasoning, intermediate results", and says "You won't know if your graders are working well unless you read the transcripts and grades from many trials" — [Anthropic, "Demystifying evals for AI agents", 9 January 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

### Inferences
- For this project there are two distinct Langfuse feeds. The native CLI export gives subagent nesting, token counts on `llm_request` spans and cost metrics, but under beta `claude_code.*` names; the OpenInference instrumentor gives AGENT/TOOL spans that Langfuse renders natively but whose token/cost/subagent coverage is undocumented. Testing both on one run and checking which yields per-subagent cost is the safest way to choose.
- Because GenAI semconv is still Development with no release, pin instrumentation package versions and treat attribute names as unstable; a resume claim of "OTel GenAI-compliant tracing" should say "Development-status conventions".
- A good trace design for the FPL agent follows from the documented primitives: one session per gameweek (`session.id`), one trace per run with an application root span (via `TRACEPARENT`), subagent spans nested under the Manager's tool span, prompt/agent version in `OTEL_RESOURCE_ATTRIBUTES` (`service.version`), cost per model from `model_usage`.
- At one run per week every hosted free tier listed above is far more than sufficient; self-hosting Langfuse (four services) is a resume talking point rather than a cost necessity.
- Langfuse and Phoenix are the two options with free open-source self-hosting; LangSmith, Braintrust and Logfire restrict self-hosting to enterprise plans.

### Gaps
- Helicone: no primary page fetched; no verified pricing, self-hosting or Claude Agent SDK information.
- W&B Weave and Phoenix pricing/licence are from comparison articles only, not vendor pages.
- No source states when GenAI semconv will be stabilised, nor was `OTEL_SEMCONV_STABILITY_OPT_IN` guidance found in the pages fetched.
- Whether Langfuse maps native `claude_code.*` spans to its generation/cost model automatically was not verified; nor was the Langfuse OTLP endpoint path.
- Prompt-version linkage to traces (Langfuse prompt management) was not researched from primary docs.
- I found no independent, first-hand head-to-head comparison of these tools for multi-agent tracing; comparison articles located were all vendor-authored.

## Evaluation: what Anthropic, OpenAI, Hamel Husain and Shreya Shankar, Eugene Yan and Inspect recommend

### Takeaway
The consistent advice is: start from error analysis on real traces, write a small set (20-50) of unambiguous tasks, grade outcomes rather than the path, prefer binary judgements, validate every LLM judge against human labels (TPR/TNR or kappa), and run multiple trials with proper standard errors. Capability evals should start hard; those that reach high pass rates graduate into a near-100% regression suite.

### Cited Findings

**Anthropic, "Demystifying evals for AI agents" (9 January 2026)**
- Vocabulary: task, trial, grader, transcript, outcome (the final environment state), evaluation harness, agent harness — [Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- Three grader types: code-based (fast, cheap, reproducible, but brittle to valid variation), model-based (flexible, but non-deterministic and needing calibration against humans), human (gold standard, slow and expensive) — [Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- Capability evals "should start at a low pass rate, targeting tasks the agent struggles with"; regression evals "should have a nearly 100% pass rate"; high-pass capability evals can "graduate" into the regression suite — [Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- Non-determinism: pass@k is the likelihood of at least one success in k attempts; pass^k is the probability all k trials succeed. A 75% per-trial rate over 3 trials gives pass^k of about 42% — [Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- "20-50 simple tasks drawn from real failures is a great start"; two domain experts should independently reach the same verdict on each task; test both cases where a behaviour should and should not occur — [Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- "grade what the agent produced, not the path it took", since "agents regularly find valid approaches that eval designers didn't anticipate"; allow partial credit — [Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- LLM judges "should be closely calibrated with human experts"; give the judge a way out such as returning "Unknown" — [Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- Offline evals sit alongside production monitoring, A/B tests, user feedback, manual transcript review and human studies: "automated evals for fast iteration, production monitoring for ground truth, and periodic human review for calibration" — [Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

**Anthropic, multi-agent research system (13 June 2025, older)**
- "Start with a set of about 20 queries representing real usage patterns"; LLM judge rubric covered factual accuracy, citation accuracy, completeness, source quality and tool efficiency; judge whether the agent "achieved the correct final state"; "People testing agents find edge cases that evals miss" — [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)

**Anthropic, "A statistical approach to model evaluations" (19 November 2024, older)**
- Report the standard error of the mean; 95% CI is mean ± 1.96 × SEM — [Anthropic](https://www.anthropic.com/research/statistical-approach-to-model-evals)
- Cluster standard errors on the unit of randomisation: "clustered standard errors on popular evals can be over three times as large as naive standard errors" — [Anthropic](https://www.anthropic.com/research/statistical-approach-to-model-evals)
- Reduce variance by resampling answers and using question-level averages; use paired-difference analysis (models' per-question scores correlate 0.3 to 0.7); do a power analysis before running — [Anthropic](https://www.anthropic.com/research/statistical-approach-to-model-evals)

**Hamel Husain and Shreya Shankar, evals FAQ (page last updated 21 September 2026)**
- Error analysis is "the most important activity in evals": open coding (free-text notes on traces), axial coding into a failure taxonomy, continue until "new reviews stop revealing failure modes or changing existing ones"; target 100+ diverse traces and review "at least 30 traces yourself before asking the agent" — [hamel.dev evals FAQ](https://hamel.dev/blog/posts/evals-faq/)
- Use binary pass/fail rather than 1-5 scales; Likert scales give inconsistent adjacent-point labels, need larger samples and invite middle-value defaults — [hamel.dev evals FAQ](https://hamel.dev/blog/posts/evals-faq/)
- LLM judge validation: split labelled data into a few-shot training set, a dev set (about 40-45%) and a held-out test set (about 40-45%); measure true positive rate and true negative rate; plan for "100 to 200 examples for each failure mode"; one judge per failure mode — [hamel.dev evals FAQ](https://hamel.dev/blog/posts/evals-faq/)
- "Generic evaluation metrics ... are not useful for evaluating LLM outputs in most AI applications" (helpfulness, coherence, ROUGE, BERTScore); use them only to find traces worth reading — [hamel.dev evals FAQ](https://hamel.dev/blog/posts/evals-faq/)
- For multi-step and agentic traces, focus on "the first upstream failure" because errors compound — [hamel.dev evals FAQ](https://hamel.dev/blog/posts/evals-faq/)
- CI evals run on fixed test sets and gate releases; online monitoring samples live traces, with "100+ fresh traces each review cycle" every 2-4 weeks and 10-20 traces weekly in between — [hamel.dev evals FAQ](https://hamel.dev/blog/posts/evals-faq/)
- "If you're passing 100% of your evals, you're likely not challenging your system enough"; teams studied spent "60-80% of development time on error analysis and evaluation" — [hamel.dev evals FAQ](https://hamel.dev/blog/posts/evals-faq/)
- Code assertions for objective checks always; LLM judges only for subjective failures that persist; write evaluators for discovered failures, not imagined ones. "Synthetic data cannot tell you how common a failure is in production." Give a judge only the part of the trace it needs — [hamel.dev evals FAQ](https://hamel.dev/blog/posts/evals-faq/)

**Eugene Yan, LLM-evaluators survey (August 2024, older)**
- Direct scoring for objective criteria such as factuality; pairwise comparison for subjective ones because "pairwise comparisons lead to more stable results"; simplify to binary outputs — [eugeneyan.com](https://eugeneyan.com/writing/llm-evaluators/)
- Prefer Cohen's kappa (0.41-0.60 is moderate agreement) and precision/recall over raw agreement or correlation — [eugeneyan.com](https://eugeneyan.com/writing/llm-evaluators/)
- Documented biases in older models: position bias (claude-v1 about 70%), verbosity bias (longer responses favoured "more than 90% of the time"), self-enhancement bias (claude-v1 25% higher win rate for its own outputs). A panel of three smaller models outperformed a single gpt-4 judge at 1/7 the cost — [eugeneyan.com](https://eugeneyan.com/writing/llm-evaluators/)

**OpenAI evaluation best practices (current docs page)**
- "Evaluate early and often. Write scoped tests at every stage"; five steps: objective, dataset, metrics, run and compare, continuously evaluate — [OpenAI docs](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- Single-agent evals cover instruction following, functional correctness, tool selection and tool-argument precision; multi-agent systems add agent handoff accuracy — [OpenAI docs](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- For judges: "Use pairwise comparison or pass/fail for more reliability", reason before scoring, control for length bias, calibrate against human labels. Anti-patterns include generic metrics, datasets unlike production traffic and "vibe-based evals" — [OpenAI docs](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

**Inspect (UK AI Security Institute)**
- Inspect is "developed by the UK AI Security Institute and Meridian Labs" (released May 2024); built from datasets, solvers, scorers and agents; supports custom and MCP tools, sandboxing (Docker, Kubernetes and others), more than 20 model providers, and can "run arbitrary external agents like Claude Code, Codex CLI, and Gemini CLI"; includes the Inspect View log viewer and over 200 pre-built evals — [inspect.aisi.org.uk](https://inspect.aisi.org.uk/)
- Built-in scorers mostly report `accuracy` and `stderr`; model-graded scorers `model_graded_qa()` and `model_graded_fact()` have customisable templates and can use multiple grader models — [Inspect scorers](https://inspect.aisi.org.uk/scorers.html)

### Inferences
- Anthropic ("grade the outcome, not the path") and Hamel/OpenAI (inspect the whole trace, tool selection, handoffs) are compatible: outcome graders decide pass/fail, trajectory inspection is for diagnosis and for targeted checks such as "did the scout extract the injury correctly". The project's decision-level evals fit the second category and can mostly be code-graded against ground truth.
- The planned ablation (solver-only vs solver-plus-agents vs average manager) is a paired design: compare points per gameweek on the same gameweeks and report paired differences with standard errors, clustering by gameweek. With about 38 gameweeks a season, power is low and should be stated openly.
- Injury-news extraction is an objective task suited to a hand-labelled set and precision/recall; if an LLM judge is used for the sceptic's critique quality, it needs a labelled validation split and reported TPR/TNR.
- A weekly cadence makes "online" evaluation cheap: every live run can be read in full, which exceeds Hamel's 10-20 traces weekly guidance.
- The Hamel figure of 100-200 labelled examples per failure mode is sized for production products; for a personal project it is a target to disclose shortfall against rather than meet.

### Gaps
- Inspect's epochs/reducers and standard-error options were not retrieved (the page fetched did not cover them); no verified detail on how Inspect aggregates multiple trials.
- No Shreya Shankar paper (e.g. on judge alignment) was fetched directly; her views are represented only through the joint FAQ.
- No primary source found on CI regression-suite design specific to the Claude Agent SDK.
- Eugene Yan's bias figures concern 2023-era models; no 2026 replication was found.

## Evaluating forecasting and decision agents when training data may contain the answers (temporal leakage)

### Takeaway
2025-2026 research agrees that any backtest overlapping the model's training window is contaminated, that vendor-stated cutoffs are unreliable, and that entity masking only partly helps. The only fully clean design is prospective: record timestamped decisions before outcomes resolve, which is how ForecastBench and LLM-SoccerArena work.

### Cited Findings
- ForecastBench (Karger, Bastani, Chen, Jacobs, Halawi, Zhang, Tetlock; submitted 30 Sept 2024, v5 28 Feb 2025) avoids leakage by being "comprised solely of questions about future events that have no known answer at the time of submission"; 1,000 auto-generated questions; in the paper "expert forecasters outperform the top-performing LLM (p-value < 0.001)" — [arXiv 2409.19839](https://arxiv.org/abs/2409.19839)
- ForecastBench describes itself as "a dynamic, contamination-free benchmark" with a Tournament leaderboard (tools allowed) and a Baseline leaderboard (raw model) — [forecastbench.org](https://www.forecastbench.org/)
- LLM-SoccerArena (Schröder, Schweisthal, Müller, Weinmann, Feuerriegel; 27 July 2026) is a prospective live benchmark on the 2026 FIFA World Cup: timestamped forecasts for all 104 matches and 15 tournament questions from seven LLMs, varying model, information access, prompting and horizon, scored by Brier score. "LLMs with web access outperform those without, but only by a small margin (i.e., a 0.023 improvement in Brier score)" — [arXiv 2607.24573](https://arxiv.org/abs/2607.24573)
- "Detecting Lookahead Bias in LLM Forecasts" (Gao, Jiang, Yan; Dec 2025, revised June 2026): a date-only recall query estimates "Lookahead Propensity"; it is positive in-sample and "collapse[s] essentially to zero right after the training-data cutoff"; forecast accuracy is amplified on high-LAP cases — [arXiv 2512.23847](https://arxiv.org/abs/2512.23847)
- "Temporal Leakage in LLM Backtesting" (Zhang, Stadie; 4 Aug 2026): the standard pre/post-cutoff comparison is uninformative, and "four flagship models fail it on questions they cannot have memorized"; leakage concentrates on surprising, heavily covered outcomes; proposes a known-cutoff boundary test plus a matched clean control model to produce a leakage-adjusted score — [arXiv 2608.02985](https://arxiv.org/abs/2608.02985)
- HindsightBench (Jia; July 2026, revised Aug 2026): models leak "parametric knowledge of what followed a historical date" as period knowledge, not only outcome lookup; present in every 2026-generation model tested; effective cutoffs "precede vendor-reported dates by up to 8 months" and span 22 months across vendors — [arXiv 2607.18867](https://arxiv.org/abs/2607.18867)
- BlindTrade (Jeon, Lee; 18 March 2026) anonymises all company identifiers to remove memorisation and survivorship bias; reports Sharpe 1.40 ± 0.22 over 20 seeds on 2025 YTD and notes regime dependence — [arXiv 2603.17692](https://arxiv.org/abs/2603.17692)
- FinCAD (Li, Wang, Ma; May 2026, revised Aug 2026) names "parametric look-ahead bias" and corrects it at decoding time; largest in-sample return correction -67.1%; in-sample/out-of-sample leaderboard Spearman correlation rose from +0.779 to +0.846 — [arXiv 2605.24564](https://arxiv.org/abs/2605.24564)
- Search-result abstracts only (papers not opened): anonymised headlines can outperform in-sample, anonymisation "inadvertently weakens the extracted signal", and "look-ahead advantages survive entity anonymization ... and decay LLM trading-agent Sharpe ratios past the training cutoff by half"; DatedGPT trains twelve 1.3B-parameter models with annual cutoffs 2013-2024 — [Anonymization and Information Loss, arXiv 2511.15364](https://arxiv.org/html/2511.15364v2); [DatedGPT, arXiv 2603.11838](https://arxiv.org/html/2603.11838v2)

### Inferences
- For the FPL agent the credible headline result is live forward testing in the 2026-27 season with decisions logged (timestamped, immutable) before each deadline; that mirrors ForecastBench and LLM-SoccerArena exactly.
- Past-season backtests are still useful for the deterministic solver and for plumbing, but agent results from seasons inside the model's training window should be labelled contaminated. The model in use states a June 2026 cutoff, and HindsightBench suggests effective cutoffs differ from stated ones, so the safe boundary is "gameweeks played after deployment".
- Player-name masking is weaker in football than in equities: a stat line often identifies a player, and the literature reports masking leaves residual leakage and costs signal. It is at best a secondary robustness check.
- A cheap leakage diagnostic in the LAP spirit: ask the model, with no tools, for a past gameweek's scores and see whether recall accuracy predicts the agent's backtest edge.
- The SoccerArena web-access result (0.023 Brier) is a useful prior that a news scout may add only a small margin, which justifies the ablation design.

### Gaps
- No published study of LLM agents on Fantasy Premier League specifically was found.
- Current ForecastBench leaderboard numbers and its projected LLM-superforecaster parity date were not retrievable from the site; older figures in a search snippet (superforecasters 0.096 Brier) were not verified on a primary page.
- Prophet Arena details come only from a search summary.
- Several leakage papers are 2026 preprints without confirmed peer review.

## Calibration and proper scoring rules for LLM confidence

### Takeaway
The Brier score is the standard proper scoring rule in recent LLM forecasting and calibration work, and verbalised confidence is a distinct, often poor, dimension that does not track accuracy. Results are sensitive to how confidence is elicited and measured, so the protocol must be fixed and reported.

### Cited Findings
- ConfidenceBench (ffrench-Constant, Yang, Huang, Kapoor; 10 July 2026) scores verbalised confidence with the Brier score on 200 multiple-choice questions across 15 frontier models; best Brier 0.103 (Claude Opus 4.6 and Gemini 3.1 Pro Preview), worst 0.367 (Gemini 3.1 Flash-Lite); "Accuracy and calibration diverge substantially across model families"; several models scored worse than a random baseline — [arXiv 2607.20526](https://arxiv.org/abs/2607.20526)
- "Same Answer, Different Confidence" (Kim, Kang; May 2026, revised Aug 2026): whether verbalised confidence beats token likelihood "depends on how the token likelihood is measured"; ECE rankings flipped in 4 of 12 settings and AUROC rankings in 9 of 12 depending on protocol; swapping an answer alias for the canonical form shifted confidence by 0.072. Tested on three 7-8B models only — [arXiv 2605.27752](https://arxiv.org/abs/2605.27752)
- LLM-SoccerArena and ForecastBench both use Brier score as the primary forecasting metric — [arXiv 2607.24573](https://arxiv.org/abs/2607.24573); [arXiv 2409.19839](https://arxiv.org/abs/2409.19839)
- Search-result abstracts only: verbalised confidence is "often saturated at high confidence levels, despite much lower accuracy"; a COLM 2026 paper attributes verbalised overconfidence to identifiable internal circuits; one method normalises confidence over self-generated distractor answers — [arXiv 2604.01457](https://arxiv.org/pdf/2604.01457); [arXiv 2509.25532](https://arxiv.org/pdf/2509.25532)
- Vendor blog claim, unverified: "Platt scaling on 200+ examples commonly cuts ECE by 30 to 60 percent on verbalized confidence" — [Future AGI blog](https://futureagi.com/blog/evaluating-llm-confidence-uncertainty-2026/)

### Inferences
- Report Brier score as the headline (it is proper and needs no binning) with a reliability diagram; treat ECE as secondary because it is binning- and protocol-sensitive.
- Make agents emit numeric probabilities for resolvable binary events (player starts, player is ruled out, captain outscores alternative) in a fixed structured format, log them before the deadline, and score after resolution. Compare against a base-rate baseline and, where available, a market or bookmaker-implied probability.
- With roughly a few dozen resolved predictions per week, a season yields enough samples for a reliability curve with coarse bins; early-season numbers need wide intervals.
- Post-hoc recalibration needs a held-out set and should be fitted only on earlier gameweeks to avoid a second form of leakage.

### Gaps
- No authoritative guideline document (from a lab or standards body) on scoring LLM confidence was found; the recommendation rests on convergent practice in the papers above.
- Log score versus Brier trade-offs and Brier decomposition (reliability/resolution) were not sourced.
- The Platt-scaling figure lacks a primary source.

## Cost: prompt caching, model tiering, batch, context management, programmatic tool calling, budgets

### Takeaway
On current Anthropic pricing the main levers are model tier (Haiku 4.5 at $1/$5 versus Opus 5.5 at $4/$20 per MTok), cache reads at 5-10% of input price, a 50% batch discount that stacks with caching, and keeping tool output out of context. Published savings include 37% fewer tokens from programmatic tool calling, 85% from tool search and 98.7% in one code-execution-with-MCP example, while multi-agent designs cost about 15x a chat in tokens.

### Cited Findings

**Current pricing (platform.claude.com, fetched 2026-09-30; USD per MTok, input / output)**
- Claude Fable 5.1: $10 / $50, cache read $0.25. Claude Opus 5.5: $4 / $20, cache read $0.20. Claude Opus 5: $5 / $25. Claude Sonnet 5.5 and Sonnet 5: $2 / $10, cache read $0.20. Claude Sonnet 4.6: $3 / $15. Claude Haiku 4.5: $1 / $5, cache read $0.10 — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Sonnet 5's $2/$10 introductory price became standard; the planned rise to $3/$15 on 1 September 2026 "will not occur" — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Claude 4.7 and later use a tokenizer that "produces approximately 30% more tokens for the same text", so per-token prices are not directly comparable with Sonnet 4.6 and earlier — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Claude 4.6 and later include the 1M-token context window at standard pricing — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Web search costs $10 per 1,000 searches plus tokens; web fetch has no extra charge; code execution is free when used with web search/web fetch tools, otherwise 1,550 free hours per month then $0.05 per hour per container — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Tool use adds a system prompt of 286 tokens on Opus 5.5 and Sonnet 5.5 (auto/none) and 496 on Haiku 4.5, plus every tool definition and tool result as input tokens — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)

**Prompt caching**
- Multipliers: 5-minute write 1.25x, 1-hour write 2x, read 0.1x base input (0.05x on Opus 5.5, 0.025x on Fable 5.1). Caching "pays off after one cache read for the 5-minute duration ... or after two cache reads for the 1-hour duration" — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Up to 4 explicit breakpoints; automatic caching via a single top-level `cache_control`; prefix order is tools, then system, then messages, and a change at one level invalidates it and everything after; 20-block lookback; a breakpoint on content that changes every request (e.g. a timestamp) yields no hits — [Prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- Minimum cacheable prompt: 512 tokens for Opus 5.5, Opus 5, Sonnet 5.5 and Fable; 1,024 for Sonnet 5 and Sonnet 4.6; 4,096 for Haiku 4.5 — [Prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- Invalidation: changing tool definitions invalidates the whole cache; toggling web search/citations or speed invalidates system and messages; changing tool choice or adding/removing images invalidates messages; thinking and effort changes are model-specific — [Prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- Caches are isolated per workspace on the Claude API; usage reports `cache_read_input_tokens`, `cache_creation_input_tokens` and `input_tokens`, which sum to total input — [Prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- The Agent SDK caches automatically. Default TTL is 5 minutes with an API key; `ENABLE_PROMPT_CACHING_1H`, `CLAUDE_CODE_PROMPT_CACHE_TTL` and `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` select 1-hour TTL for the main conversation and subagents separately — [Agent SDK cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking)

**Batch processing**
- 50% discount on input and output; up to 100,000 requests or 256 MB per batch; "most batches finishing in less than 1 hour", expiry at 24 hours; results kept 29 days; `stream`, `speed` and `max_tokens: 0` unsupported — [Batch processing docs](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- Batch and caching discounts stack, but cache hits in batches are best-effort; the docs advise the 1-hour cache for batches with shared context — [Batch processing docs](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- The batch discount does not apply to Claude Managed Agents sessions — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)

**Context management**
- Context editing (beta header `context-management-2025-06-27`): `clear_tool_uses_20250919` clears oldest tool results past a trigger (default 100,000 input tokens), keeping the last 3 tool uses by default, with `clear_at_least` and `exclude_tools`; `clear_thinking_20251015` manages thinking blocks. Clearing tool results invalidates the cached prefix, which is what `clear_at_least` is for. Responses report `cleared_input_tokens` — [Context editing docs](https://platform.claude.com/docs/en/build-with-claude/context-editing)
- Server-side compaction replaces older turns with a summary; on-demand compaction uses beta header `compact-2026-09-04`; threshold compaction is a separate beta; client-side SDK compaction is deprecated — [Compaction docs](https://platform.claude.com/docs/en/build-with-claude/compaction); [Context editing docs](https://platform.claude.com/docs/en/build-with-claude/context-editing)

**Tool-call efficiency (published savings; both posts are from late 2025, older)**
- Programmatic tool calling: "Average usage dropped from 43,588 to 27,297 tokens, a 37% reduction on complex research tasks"; tool search tool: "85% reduction in token usage", with accuracy rising from 49% to 74% on Opus 4 and 79.5% to 88.1% on Opus 4.5; tool use examples raised complex-parameter accuracy from 72% to 90% — [Anthropic, "Advanced tool use", 24 Nov 2025](https://www.anthropic.com/engineering/advanced-tool-use)
- Code execution with MCP: "from 150,000 tokens to 2,000 tokens—a time and cost saving of 98.7%" in one worked example, by loading tool definitions on demand and filtering results in code; caveat that it "requires a secure execution environment with appropriate sandboxing, resource limits, and monitoring" — [Anthropic, "Code execution with MCP", 4 Nov 2025](https://www.anthropic.com/engineering/code-execution-with-mcp)

**Multi-agent token cost and tiering**
- "agents typically use about 4× more tokens than chat interactions" and "multi-agent systems use about 15× more tokens than chats"; token usage alone explained 80% of performance variance on BrowseComp; an Opus 4 lead with Sonnet 4 subagents beat single-agent Opus 4 by 90.2% on an internal research eval — [Anthropic, 13 June 2025](https://www.anthropic.com/engineering/multi-agent-research-system)
- Anthropic's own guidance: "Choose Haiku for simple tasks, Sonnet for most production workloads, and Opus for the most complex reasoning" — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)

**Budgets and cost accounting in the Agent SDK**
- `total_cost_usd` is a "client-side estimate, not authoritative billing data", computed from a bundled price table; use the Usage and Cost API for billing truth — [Agent SDK cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking)
- Result `usage` excludes subagents, while `total_cost_usd` and `model_usage` (per model) include them; "the `usage` field undercounts as soon as nesting occurs" — [Agent SDK cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking)
- Parallel tool calls produce several assistant messages sharing one message ID, so deduplicate by ID; per-step `output_tokens` is a placeholder and must be read from the result message — [Agent SDK cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking)
- `max_budget_usd` (Python) caps a call's own spend and ends with result subtype `error_max_budget_usd`; failed runs still carry cost; there are separate subagent depth, concurrency and spend limits — [Agent SDK cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking)

### Inferences
- A once-weekly run gets no cross-run cache benefit (5-minute or 1-hour TTL); caching only pays within a run, across the Manager's turns and across subagents sharing an identical tools+system prefix. Design accordingly: stable tool list and system prompt first, volatile gameweek data last, no timestamps in the prefix.
- Haiku 4.5's 4,096-token minimum means short subagent prompts on Haiku will silently not cache; check `cache_read_input_tokens` per subagent.
- Batch suits the offline parts (eval grading, labelling backtest news items, judge runs) at 50% off, not the interactive agent loop; the Agent SDK loop itself is not a batch workload.
- Because the MCP tools are deterministic and can return large tables (player stats, fixtures), trimming results at the tool (top-N, selected columns) or filtering in code is likely the largest single saving, consistent with the 37% and 98.7% figures, which are task-specific and not guaranteed.
- "Cost per point" should use `total_cost_usd`/`model_usage` (which include subagents), reconciled periodically against the Usage and Cost API, and broken down per subagent via trace spans to find which specialist earns its cost. The 15x token figure sets the expectation that agents must add measurable points over solver-only to justify themselves.
- When comparing models by price, account for the roughly 30% tokenizer inflation on newer models.

### Gaps
- No independent (non-Anthropic) measurements of caching or routing savings were collected; all quantified savings here are Anthropic's own and mostly from late 2025.
- Subagent spend-limit option names and defaults were referenced but not retrieved.
- Threshold-compaction defaults and billing were not retrieved.
- No source was found quantifying model-routing savings for agent pipelines specifically.
- Task budgets / effort settings and their cost effects were not researched.
