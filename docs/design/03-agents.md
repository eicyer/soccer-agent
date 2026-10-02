# 03 · Agents

**Status:** Roles Decided; models and limits Proposed · **Last updated:** 2026-10-02

Four agents plus a Chat responder. Each has one job, a typed output, and no more tools than that job needs. None of them writes a Plan or touches the FPL account ([decision 0001](../decisions/0001-solver-writes-every-plan.md)).

| Agent | Job | Model (Proposed) | Tools | Writes |
|---|---|---|---|---|
| Scout | News → Start Probability and Player Status | DeepSeek V4 Flash; free Qwen 3.8 27B as backup | Fetch news sources | Scout report |
| Planner | Choose a Candidate Plan, or add Constraints and re-solve; keep the Chip Schedule | DeepSeek V4 Pro | `candidate_plans`, `score_plan`, `player_xp` | Chosen Plan, Chip Schedule, Owner Questions |
| Checker | Review the chosen Plan against a checklist; Veto or pass | GLM 5.3 Flash (a different family from the Planner) | `player_xp`, `rule_check` | Verdict |
| Retrospective | Compare expected with actual; propose Lessons | DeepSeek V4 Pro | Read run history | Lessons |
| Chat responder | Answer the Owner; turn requests into Instructions | DeepSeek V4 Pro | Read-only state and traces | Draft Instructions |

Models are settings, not code. Every model's open-weight licence is checked before use, since OpenRouter also lists closed models. Model choice per role is revisited by eval ([06](06-evaluation.md)).

## Scout

**Input:** the players that matter this Gameweek (the squad plus everyone in any Candidate Plan, about 60), with FPL's `news` text and the news sources.

**Output, one record per player:**

```json
{
  "player": "Bukayo Saka",
  "start_probability": 0.85,
  "status": "doubtful",
  "evidence": "Arteta: 'Bukayo trained today, we'll assess him tomorrow.'",
  "source_url": "https://…",
  "published_at": "2026-10-09T13:05:00Z"
}
```

`status` is one of fit, doubtful, injured, suspended, rotation risk. The output is validated against this schema; anything that fails is dropped and the player falls back to FPL's chance-of-playing flag.

**Rules:**

- Quote the evidence; never paraphrase a source into a number without it.
- No source newer than FPL's own flag means: use FPL's flag.
- The Scout's text never reaches another agent. Only the validated fields do ([05](05-execution-and-safety.md), prompt injection).

**News sources (Open):** FPL's own `news` field is always used. Which other sources to read (official club and Premier League injury pages, reputable outlets' RSS) depends on what can be fetched reliably and within their terms. Decided before the Scout ships in Gameweek 8.

## Planner

**Input:** Candidate Plans with xP per Gameweek; the Scout report; active Instructions; relevant Lessons; the Chip Schedule.

**Loop:** look at the Candidate Plans; either choose one, or add a Constraint (lock, ban, cap on hits, chip in Gameweek t) and ask for new Candidate Plans. Capped at three re-solves.

**Output:**

```json
{
  "chosen_plan_id": "plan-2",
  "reasoning": "Plan 2 keeps a free transfer for Gameweek 9, when Liverpool play twice…",
  "evidence": ["player_xp:Salah:gw9", "scout:Salah"],
  "confidence": 0.7,
  "chip_schedule": {"wildcard": 12, "bench_boost": 9, "triple_captain": 9, "free_hit": 16},
  "owner_questions": []
}
```

Every factual claim in `reasoning` cites a tool output in `evidence`; the Checker enforces this.

**Chip Schedule:** revised every Main Run. To move a Chip, the Planner compares options with `score_plan` (for example Bench Boost in Gameweek 9 against 14) and records why. Fixed chip rules in code are the baseline it is evaluated against.

## Checker

Sees the chosen Plan, the Candidate Plans, the Scout report and tool outputs. Does **not** see the Planner's reasoning, so it judges the Plan rather than the argument for it.

**Checklist, each item pass or fail:**

1. Every player transferred in or captained has a Start Probability of at least 0.75, or the Planner's evidence explains why not.
2. Any Points Hit is covered by at least the hit's cost in extra xP within the horizon.
3. The Plan doesn't sell a player whose only problem is one bad fixture, when the next ones are good.
4. Chip timing matches the Chip Schedule or the change is justified.
5. Nothing contradicts a hard Instruction or an active Lesson.

**Verdict:** pass, Veto (listing failed items), or insufficient evidence (treated as a Veto). One revision, then a second Veto becomes an Owner Question defaulting to the Fallback Plan.

## Retrospective

Runs after the Gameweek. Gets the Plan, the Candidate Plans, xP, Scout output, actual points and existing Lessons.

**Output:** at most three new Lessons, plus confirm or retire decisions on existing ones.

```json
{
  "lesson": "Treat a manager saying 'we'll assess him' as start probability ≤ 0.6, not 0.85.",
  "kind": "process",
  "gameweek": 8,
  "evidence": "Scout gave Saka 0.85; he was benched. Same phrase preceded 3 of 4 benchings this season.",
  "expires_after_gameweek": 14
}
```

Rules: process Lessons only, never "player X is bad"; each cites evidence; each expires after six Gameweeks unless confirmed by new evidence (Proposed); the Owner can delete any Lesson by Chat. The Planner receives only Lessons relevant to the current decision (Proposed: matched by tag, at most five).

## Chat responder

Answers the Owner's questions using read-only access to the run state, Plans, Lessons and traces. A request to change something becomes a draft Instruction, restated to the Owner as hard or soft; it takes effect only once the Owner confirms. Chat can't change a Plan any other way.

## Prompts

Prompts live in version-controlled files, one per agent, with a version number recorded on every trace. A prompt change ships only with an eval result ([06](06-evaluation.md)). Static parts come first so provider-side caching can work.
