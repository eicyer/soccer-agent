# 05 · Execution and safety

**Status:** Decided in principle; auth details Proposed until tested · **Last updated:** 2026-10-02

The only part of the system that changes the real world. Evidence for every API claim here is in the [feasibility research](../research/fpl-api-feasibility.md); nothing has yet been tested with a logged-in account.

## Accepted risk

Automating the account breaches clause 28(d) of the FPL terms ("use automated systems to access the Game"); the stated penalty is suspension or deletion of the team. The Owner has accepted this risk for their own team. Two limits stay regardless:

- **Registration is manual.** Clause 5 forbids registrations "made by agents or third parties", so the Owner creates the account and enters the first squad by hand (Gameweek 6).
- **One account only.** Clause 6 forbids multiple accounts, so there is no test account; the first real write is a deliberately harmless one (below).

## Authentication

FPL uses OpenID Connect at `account.premierleague.com/as`, with no password grant, so a script can't log in from an email and password.

**Proposed flow:**

1. **Once, on the Owner's Mac:** a small Playwright script opens a real browser; the Owner logs in; the script captures the refresh token (scope includes `offline_access`).
2. **Store it** encrypted in Postgres. Refresh tokens reportedly rotate on every use, so GitHub secrets (which a workflow can't update) won't work; the encryption key lives in GitHub secrets instead.
3. **Each run** exchanges the refresh token for a short-lived access token and saves the new refresh token in the same transaction.
4. **When refresh fails** (expiry, or the Owner logging in elsewhere), alert the Owner to repeat step 1. Expected about twice a season.

Reported lifetimes (about 8 hours for access, 180 days for refresh) are unverified; the alert path doesn't depend on them.

## Writes

| Action | Call | Notes |
|---|---|---|
| Transfers, Wildcard, Free Hit | `POST /api/transfers/` | Wildcard and Free Hit can't be cancelled once confirmed |
| Lineup, captain, vice, bench, Bench Boost, Triple Captain | `POST /api/my-team/{entry}/` | Can be changed freely until the deadline |

Every write:

1. **Passes the Rule Check** in code: legal squad, budget with real selling prices, free transfers, deadline not passed, and the payload matches the Plan that was approved or defaulted, field by field.
2. **Is logged in full** before sending: payload, Plan id, run id.
3. **Has an idempotency key** of entry + Gameweek + Plan id. Before sending transfers, the executor re-reads the account; if the transfers are already there, it skips them.
4. **Is verified after sending** by re-reading `my-team/` and comparing it with the Plan. A mismatch alerts the Owner.
5. **Supports dry run,** which does everything except the POST. Dry run is the default everywhere except the scheduled Final Run.

**First write (Gameweek 7):** swap two bench players, verify, swap back, verify. Only then does the Final Run execute for real. If writes don't work, the fallback is confirm mode: the Final Run sends the exact moves by Telegram for the Owner to make in the app.

## Prompt injection

The agent combines all three risky properties: it reads untrusted text (news), holds account access, and changes state. The defence is structural, not prompt wording:

- **The Scout has no account access and no write tools.** Its only output is the validated schema in [03](03-agents.md); free text from sources never reaches the Planner, Checker or executor.
- **Agents have no account access at all.** Only the executor, which is plain code, holds the token.
- **The Rule Check doesn't trust agents.** It checks the payload against the Solver's Plan, which an agent can choose but not write.
- **Scraped text never becomes a Lesson** without the Retrospective restating it as a process point with evidence.
- **Telegram input** only becomes an Instruction after the Owner's confirmation ([04](04-owner-interface.md)).

## Secrets

| Secret | Lives in |
|---|---|
| FPL refresh token | Postgres, encrypted |
| Encryption key, OpenRouter key, Telegram bot token, Postgres URL, Langfuse keys | GitHub Actions secrets |
| Local development | `.env`, git-ignored |

No secret appears in logs, traces, Memos or commits. Traces record payloads after redaction (Proposed: token-shaped strings and the entry id masked).

## Kill switch

`/pause` in Chat stops all execution until `/resume`; the Final Run sends the Plan as a Telegram message instead. The same flag can be set directly in Postgres if Telegram is down.
