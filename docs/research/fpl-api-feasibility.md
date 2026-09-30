# FPL API feasibility: can the agent read data and make moves?

Researched 2026-09-30 (Gameweek 5 of 2026/27 in progress, GW6 deadline 2026-10-10 10:00 UTC).

## Verdict

| Question | Answer | Confidence |
|---|---|---|
| Can we read all the data we need? | **Yes** | Verified first-hand |
| Do write endpoints exist for transfers, lineup/captain and chips? | **Yes** | Verified first-hand in the site's own JavaScript |
| Can a script call them once it holds a token? | **Probably yes** | Reported by others; not tested by us |
| Can the agent log in fully unattended, forever? | **No.** A human browser login is needed about twice a season | Inferred from the login design plus third-party reports |
| Is it allowed? | **No.** The terms prohibit automated access; account suspension is possible | Verified first-hand in the 2026/27 terms |

Nothing in this document was tested with a logged-in account. No login and no write request was attempted.

## 1. Reading data — verified

All requests below were plain `curl` with a browser User-Agent and no credentials, base `https://fantasy.premierleague.com/api/`.

| Endpoint | Status | What it gives |
|---|---|---|
| `bootstrap-static/` | 200, 1.8 MB | 667 players, 20 teams, 38 gameweeks with deadlines, chips, game settings |
| `fixtures/` | 200 | Every fixture with difficulty ratings and results |
| `element-summary/{player}/` | 200 | A player's match-by-match history and upcoming fixtures |
| `event/{gw}/live/` | 200 | Live points for every player in a gameweek |
| `entry/{team}/` | 200 | Any manager's team summary |
| `entry/{team}/history/` | 200 | Any manager's season history and chips used |
| `entry/{team}/event/{gw}/picks/` | 200 | Any manager's squad for a past gameweek |
| `entry/{team}/transfers/` | 200 | Any manager's transfer history |
| `leagues-classic/{id}/standings/` | 200 | League tables (314 is the overall league) |
| `team/set-piece-notes/` | 200 | Penalty and free-kick takers |
| `event-status/`, `dream-team/{gw}/`, `stats/most-valuable-teams/`, `regions/` | 200 | Misc |
| `my-team/{team}/` | **403** | Needs login: current squad, selling prices, bank, free transfers, chips available |
| `transfers/` | **403** | Needs login |

Per-player fields in `bootstrap-static` include expected goals/assists, injury `news` and `chance_of_playing_next_round`, ownership, transfers in/out, price, and price-change fields, which is enough to build a projection model without any other source.

Infrastructure: responses are served through Varnish with `cache-control: max-age=300`, so polling more often than every five minutes returns the same data. No bot challenge was seen on the API host during these probes. Rate limits were not tested.

## 2. Logging in — partly verified

**Verified first-hand**

- The old email-and-password POST to `users.premierleague.com/accounts/login/` is no longer the mechanism. The site now uses OpenID Connect against `https://account.premierleague.com/as`. Source: the site's main bundle (`/assets/index-JfaMSGvw.js`, fetched 2026-09-30), which configures an OIDC client with `client_id: bfcbaf69-aade-4c1b-8f00-c1cb8a193030`, `scope: openid profile email offline_access`, redirect to the site origin, and automatic silent renewal.
- Authenticated API calls carry the header `X-API-Authorization: Bearer <access token>`. Same source.
- The discovery document at `https://account.premierleague.com/as/.well-known/openid-configuration` returns 200 and lists grant types `authorization_code`, `refresh_token`, `device_code` and others. There is no password grant, so a script cannot swap email and password for a token directly.
- The `offline_access` scope means refresh tokens are issued.

**Reported by others, not verified**

- Access tokens last about 8 hours; refresh tokens last about 180 days and rotate on every use; logging in again in the same session kills all earlier tokens. Refreshing works from a plain script with no bot challenge. Source: README of https://github.com/kru3ish/fpl-auto-manager (15 commits, 0 stars, date not shown).
- The provider is PingOne (Ping Identity). Source: README of https://github.com/ulrikmjelde/FPL_AI_MANAGER, which also deliberately does not automate the first login.
- The best-known Python client, `amosbastian/fpl`, is unmaintained and its login is broken; a fix is sitting in an unmerged PR from 2025-08-10. Source: https://github.com/amosbastian/fpl/pull/135

**Unknown**

- Whether the interactive login page has a captcha or bot detection that blocks Playwright.
- Whether the `client_id` a third-party repo quotes (`1f243d70-…`) still works; it differs from the one in today's bundle, which suggests it has changed at least once.
- Exact token lifetimes.

**Practical consequence.** The realistic design is: you log in once in a real browser, the refresh token is captured and stored, and the agent renews access tokens by itself until the refresh token expires or you log in elsewhere. Expect to repeat the manual login a couple of times a season, and build an alert for when the token dies.

## 3. Writing — endpoints verified, execution not

**Verified first-hand** in the site bundle (the calls the official web app itself makes):

| Action | Call | Body |
|---|---|---|
| Transfers | `POST transfers/` | `{chip, entry, event, transfers: [...]}` |
| Wildcard / Free Hit | `POST transfers/` | `{chip: "<name>", entry, event, transfers: []}` |
| Lineup, captain, vice, bench order | `POST my-team/{entry}/` | `{chip, picks: [...]}` |
| Bench Boost / Triple Captain | `POST my-team/{entry}/` | `{chip: "<name>", picks: [...]}` |
| Create a team | `POST entry-create/` | `{..., picks: [...]}` |

The site's own help text confirms the chip split: Bench Boost and Triple Captain are saved on the Pick Team page and can be cancelled before the deadline; Wildcard and Free Hit are played when confirming transfers and **cannot be cancelled**.

**Reported by others, not verified**

- Each transfer item is `{element_in, element_out, purchase_price, selling_price}` with prices in tenths of a million; each pick is `{element, position, is_captain, is_vice_captain}` with positions 1–11 the starting XI and 12–15 the bench. Source: kru3ish/fpl-auto-manager README.
- Neither third-party repo states plainly that a write succeeded on a real account this season.

**Unknown**

- Whether write calls need extra headers (CSRF, Origin/Referer) beyond the bearer token.
- Whether writes from a non-browser client are flagged.

The first real test should be a harmless, reversible write: swap two bench players and swap them back.

## 4. Terms — verified

From "2026/27 Fantasy Premier League – Terms & Conditions", extracted from the site bundle (`/assets/Terms-Buxxp9b_.js`, shown at https://fantasy.premierleague.com/help/terms), fetched 2026-09-30:

> 28. You also warrant and agree that you shall not: … (d) use automated systems to access the Game and extract information from the Game;

> 27. … you shall not allow any other person access to your account nor share or transfer registration or control of your account with or to another person.

> 6. … only one Registration for the Game per user of the Site or App is permitted. Individuals are not permitted to register multiple accounts on the Site or App.

> 36. In the event of any breach by you of these Terms the Premier League reserves the right in its sole discretion to: (a) permanently or temporarily refuse you entry to the Game; (b) disqualify you from the Game; (c) modify, delete and/or suspend your Registration; …

What this means:

- Clause 28(d) covers **reading** as well as writing. Every community tool that pulls the public API is technically in breach, and that use is widespread and openly tolerated. Writing is a step further.
- The penalty available to the Premier League is losing the team. There is no money at stake in the game itself.
- Clause 6 rules out the obvious mitigation of a second throwaway account.
- Enforcement: one third-party README says managers "have been banned for automating team management". I found no primary source for that. Treat the frequency of enforcement as unknown.

## 5. Ways to execute, ranked

| # | Approach | Autonomy | Reliability | Terms exposure |
|---|---|---|---|---|
| 1 | Agent decides, you click confirm in the FPL app | None on the last step | Cannot break | Lowest (read only) |
| 2 | One manual browser login, agent stores the refresh token and calls the write endpoints | Full between logins | Good if reports hold; breaks when FPL changes auth | Clear breach of 28(d) |
| 3 | Playwright drives the real site in a persistent browser profile | Full | Brittle to UI changes; heavier to run | Same breach, harder to distinguish from a human |

Recommendation: build the executor behind one interface with option 1 as the default and option 2 as a switch. Everything upstream of the last step is identical, so the architecture does not depend on which one is on.

## 6. Historical data for backtesting

- https://github.com/vaastav/Fantasy-Premier-League — the standard dataset. Its README says weekly updates stopped at the end of 2024-25; only three updates a season are planned now (start, after January, end). Good for past seasons, not for live use. Licence file present; terms not checked.
- For the live 2026/27 season we should snapshot the official API ourselves every gameweek from day one. `bootstrap-static` only ever shows the current state, so prices, ownership and injury flags are lost if not recorded.
- Understat, FBref and olbauday/FPL-Elo-Insights were not checked.

## Not established

- A successful authenticated call of any kind (no account was used).
- Bot protection on the interactive login page.
- Rate limits.
- Any confirmed case of a ban for automation.
