# 04 · Owner interface

**Status:** Decided; message formats Proposed · **Last updated:** 2026-10-02

The Owner talks to the agent through a private Telegram bot. A web dashboard comes later for browsing results; Langfuse already shows every trace ([07](07-observability-and-cost.md)).

## Principles

- **Ask only where it matters.** Four triggers, nothing else (below).
- **Every question has a default** that applies if there's no answer by the Final Run, so the Owner is never a single point of failure.
- **One tap to answer.** Owner Questions use buttons; typing is only for Chat.
- **Record the Owner's hand.** Every answer, Instruction and Chat-driven change is stored as Owner Influence, so evals can separate the agent's contribution from the Owner's.

## Owner Questions

| Trigger | What the Owner sees | Buttons | Default by the Final Run |
|---|---|---|---|
| Wildcard or Free Hit in the Plan | The Plan with and without the chip, and the xP difference | Play / Skip | Skip; the chip stays in the Chip Schedule |
| Close Call | The top two Candidate Plans side by side, with the Planner's reasoning for its pick | Plan A / Plan B | The Planner's choice |
| Points Hit | The extra transfers, their cost and the xP they gain | Take the hit / No hit | Take the hit |
| Second Veto | The Planner's Plan, the Checker's failed checklist items, and the Fallback Plan | Planner / Fallback | Fallback Plan |

Answers resume the paused LangGraph run from its checkpoint ([decision 0003](../decisions/0003-langgraph-with-owner-in-the-loop.md)). A question nobody answers is resolved by the Final Run with its default, and the Memo after execution says which defaults were used.

## Memo

Sent at the end of the Main Run. Proposed format, kept short enough to read on a phone:

```text
Gameweek 9 · deadline Sat 31 Oct 11:00 UTC

Plan: Watkins → Isak (free transfer). Captain Haaland, vice Salah.
Why: Isak has two home games in the next three; Watkins faces City and Arsenal.
xP this Gameweek 61.2 (Fallback Plan 60.4) · over 5 Gameweeks 297.0
Checker: passed
Chip Schedule: Bench Boost GW9 → GW12 (Liverpool double moved)

❓ 1 question waiting: Close Call (default: Planner's choice)
Cost of this run: $0.19 · month so far $0.61 of $5
Trace: <Langfuse link>
```

## Chat

Message the bot at any time. A scheduled job reads new messages every 15 minutes and replies, so Chat behaves like quick email, not live conversation.

- **Questions** ("why sell Watkins?") are answered from the run's state and trace, citing them.
- **Requests** ("never sell Saka") become a draft Instruction. The bot restates it, for example "Hard rule: Saka is locked in until you remove it", and it takes effect only when the Owner confirms.
- **Commands** (Proposed): `/instructions`, `/lessons`, `/delete_lesson <n>`, `/pause` (no execution until `/resume`; the Final Run alerts instead), `/status`.

## Instructions

Each Instruction is stored with its wording, its restatement, hard or soft, an optional end date and when it was made. Hard Instructions become Solver Constraints; soft ones go into the Planner's input. Both appear in every Memo while active.

## Security

- The bot answers only the Owner's Telegram user id; every other sender is ignored and logged.
- The bot token lives in GitHub secrets.
- Telegram messages are untrusted input: Chat requests only become Instructions after the Owner's explicit confirmation, and Chat has no write access to Plans or the account.

## Later: dashboard

Once a season of data exists: Season Total against the Shadow Teams, Paired Comparison results with error bars, the Scout's Brier score over time, spend per Gameweek, and the Lessons list. Built on the same Postgres data.
