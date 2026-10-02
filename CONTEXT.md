# Football Agent

An autonomous manager for one Fantasy Premier League team. It turns football data and news into weekly team decisions and is judged on the points those decisions score.

## Language

**Owner**:
The person whose FPL team the agent manages, and the only person who answers Owner Questions and gives Instructions.
_Avoid_: User, manager

**Instruction**:
A standing request from the Owner, restated by the agent as either hard (turned into a Constraint the Solver must obey) or soft (guidance the Planner weighs). It lasts until removed or until its end date.
_Avoid_: Preference, override, command

**Gameweek**:
One round of Premier League fixtures, with a single deadline after which the team is locked.
_Avoid_: Round, matchweek, week

**Snapshot**:
An untouched copy of the public FPL API at one moment. Snapshots are never edited, and everything else is derived from them.
_Avoid_: Dump, scrape, backup

**Expected Points (xP)**:
A model's estimate of the points a player will score in a given Gameweek. Comes from the project's own xP Model once it beats FPL's published estimate, and from FPL's estimate until then. Never produced by an LLM.
_Avoid_: Projection, prediction, forecast, ep_next (that is FPL's estimate specifically)

**xP Model**:
The project's own model that produces xP for every player and Gameweek in the Planning Horizon, using the Scout's Start Probability for minutes.
_Avoid_: Points model, predictor

**Season Total**:
The team's total FPL points over the season, and the single quantity the agent tries to maximise. Overall rank is reported but not optimised.
_Avoid_: Score, performance, rank (when meaning the objective)

## Measuring

**Shadow Team**:
An imaginary team that makes its own decisions all season without ever being executed, such as Solver only or Solver plus Scout. Compared with the real team on Season Total.
_Avoid_: Ghost team, simulation, baseline team

**Paired Comparison**:
Each Gameweek, what each baseline would have chosen from the real team's actual squad, scored on that Gameweek's real points. The main statistical evidence of what the agents add.
_Avoid_: Counterfactual, A/B test

## Running

**Main Run**:
The full decision run about 24 hours before a Gameweek deadline. It builds the Plan and sends the memo, but executes nothing.
_Avoid_: Weekly run, job

**Final Run**:
The short run about 2 hours before the deadline. It re-checks news, re-solves only if something material changed, and executes.
_Avoid_: Check run, execution run

**Retrospective**:
The step after a Gameweek finishes that compares what was expected with what happened and proposes Lessons.
_Avoid_: Review, post-mortem

**Lesson**:
One short, itemised point about the agent's own process, citing the Gameweek and evidence behind it. Lessons are used automatically, expire unless new evidence confirms them, and can be deleted by the owner. A claim about a player's outcome is never a Lesson.
_Avoid_: Memory, insight, learning, note

## News

**Scout**:
The agent that reads team news and press-conference reports and turns them into a Start Probability and Player Status for each relevant player.
_Avoid_: News agent, researcher

**Start Probability**:
The chance a player is in his team's starting eleven for a given Gameweek. The Scout's only numeric output; the xP model turns it into expected minutes.
_Avoid_: Availability, chance of playing (that is FPL's own coarser flag)

**Player Status**:
One of fit, doubtful, injured, suspended or rotation risk, always with the source it came from.
_Avoid_: Injury status, flag

**Material Change**:
A move in Start Probability, beyond a set threshold, for a player in the squad or in any Candidate Plan. The only thing that makes the Final Run re-solve.

**Memo**:
The Main Run's report to the Owner: the chosen Plan, why, any Veto, any open Owner Questions, and the run's cost.
_Avoid_: Report, digest, summary

**Owner Question**:
A pause in which the agent asks the Owner to decide, each with a default that applies if there is no answer by the Final Run. Asked only for: a Wildcard or Free Hit (default: skip it, keeping it in the Chip Schedule), a Close Call (default: the Planner's choice), a Points Hit (default: proceed), and a second Veto (default: the Fallback Plan).
_Avoid_: Approval request, interrupt, prompt

**Close Call**:
When the top two Candidate Plans are within about 1 xP of each other over the Planning Horizon.

**Points Hit**:
A points deduction (−4 per transfer) for making more transfers than the free ones available.
_Avoid_: Hit, penalty, cost

**Owner Influence**:
The record that a decision was shaped by the Owner, through an Owner Question answer, an Instruction or a chat. Evals use it to separate the agent's contribution from the Owner's.

**Chat**:
A conversation the Owner can open at any time to ask about the agent's reasoning. It changes a Plan only by creating an Instruction.
_Avoid_: Conversation, assistant

**Spend Cap**:
The hard limit on model spending for scheduled runs: $1 per Gameweek and $5 per month. Hitting the Gameweek limit stops spending and plays the Fallback Plan.
_Avoid_: Budget (that means the FPL squad budget)

## Deciding

**Plan**:
A complete set of team moves (transfers, starting eleven, bench order, captain, vice-captain and chip) for each Gameweek in the Planning Horizon. Only the first Gameweek's moves are ever executed. Every Plan is produced by the Solver; no agent writes one.
_Avoid_: Proposal, recommendation, decision (when meaning the moves themselves)

**Planning Horizon**:
The run of upcoming Gameweeks a Plan covers, about five. It rolls forward and is planned afresh every Gameweek.
_Avoid_: Lookahead, window

**Solver**:
The optimiser that turns xP and Constraints into legal, ranked Plans.
_Avoid_: Optimiser, engine

**Candidate Plans**:
The Solver's top few Plans for a Gameweek, from which the Planner chooses.

**Planner**:
The agent that weighs the Candidate Plans and either chooses one or adds a Constraint and asks the Solver again.
_Avoid_: Manager, analyst

**Chip**:
A once-per-half-season power: Wildcard, Free Hit, Bench Boost or Triple Captain. Each half (Gameweeks 1–19 and 20–38) has its own set, and unused chips expire at the end of the half.
_Avoid_: Power-up, boost

**Chip Schedule**:
The Planner's pencilled-in target Gameweek for each remaining Chip, revised every Gameweek and passed to the Solver as Constraints.
_Avoid_: Chip plan, chip strategy

**Double Gameweek**:
A Gameweek in which some teams play twice. A **Blank Gameweek** is one in which some teams don't play at all.
_Avoid_: DGW, BGW (in prose)

**Constraint**:
A rule the Solver must obey, such as locking a player in or banning one out. Constraints come from the Planner, the Chip Schedule or a hard Instruction.
_Avoid_: Override, rule

## Checking

**Checker**:
The agent that reviews the Planner's chosen Plan against a fixed checklist, on a different model and without seeing the Planner's reasoning. It can Veto once.
_Avoid_: Sceptic, critic, reviewer, judge

**Veto**:
The Checker's objection to a chosen Plan. The first sends the Plan back to the Planner for one revision; a second becomes an Owner Question, defaulting to the Fallback Plan.
_Avoid_: Rejection, block

**Fallback Plan**:
The Solver's top Candidate Plan, played after a second Veto if the Owner doesn't choose, or when the Spend Cap is hit. It is what the solver-only baseline would play.
_Avoid_: Default plan, safe plan

**Rule Check**:
The check in code, run before any execution, that the Plan is legal: squad rules, budget, deadline, and that what is sent matches what was approved. It is not an agent and cannot be argued with.
_Avoid_: Validation, guardrail, policy check
