# Tasks / Backlog

Working backlog for follow-up improvements. Tracked in-repo (public) as part of
the engineering record — it documents process, not the shipped behavior spec.

## Verify weekly-review computed stats (deterministic, not a priority)

**Problem.** The weekly review's stats block (trade count, L/S/NT split, grade
distribution, average GPA, win rate, tag tallies) is computed by the LLM in-head
across all in-range journals. Unlike the per-trade *write* path, these numbers
are verified by **nothing** — `test_weekly_review.py` checks filename/title,
section presence, and the verdict token, but never recomputes the figures. A
miscount or a wrong GPA average ships silently and looks plausible.

**Fix (cheap, on-thesis).** Extend the weekly test to recompute the stats from
the in-range fixture trades and assert the numbers in the weekly file match.
Keeps generation non-deterministic, verifies the arithmetic deterministically —
same philosophy as the rest of the suite. Pairs naturally with a committed
cross-skill golden-week fixture (known-correct trades to recompute against).

**Later, only at journal scale.** A runtime aggregator (`aggregate_week.py` the
skill calls to emit counts/distribution/GPA/tag-tallies/prior-order/ledger-join
as a structured digest, then the LLM *interprets* it) becomes worth it for
monthly/quarterly rollups (20–60 trades) where hand-aggregation degrades. For
3–5-trade weeks it's over-engineering — skip until longer-horizon reviews exist.

**Trigger to revisit:** adding monthly/quarterly review horizons, or a recurring
hand-fix of a wrong stat in a shipped weekly.

## Rotation map is inert during pre-market (blocking — do not merge the branch)

**Status.** `feat/premarket-rotation-map` is **unmerged and must stay unmerged**
until this is fixed. The suite is green (173 passed) and both sample briefings
validate 14/14 including `rotation_map` — the tests pass against a payload shape
CNBC never emits.

**Problem.** `reg_chg_pct` goes `None` for every US equity row partway through the
pre-market window. CNBC rolls its top-level quote over at some point before the
open: after the roll `last` equals `previous_day_closing` and `change_pct` is the
literal string `UNCH`, so `_to_float("UNCH")` returns `None` and
`fetch_market_data.py` writes `reg_chg_pct: None` for every symbol.
`references/rotation-map-read.md` then collapses to the quiet-tape line whenever
`SPY.reg_chg_pct` is unavailable — so past the roll the map silently prints
"no material rotation" no matter what the tape did.

**The failure is time-dependent, which is worse than always-broken** — it works in
early tests and dies in real use, with no signal that anything went wrong.
Measured against the live endpoint:

| Sample | `reg_chg_pct` | Meaning |
|---|---|---|
| 2026-08-12 06:59 ET | populated, correct | completed prior session (SPY −0.32 = Aug 11's 770.56 vs Aug 10's 773.03) |
| 2026-08-12 09:26 ET | `None` | rolled to `UNCH` |
| 2026-08-11 09:27 ET | `None` | same, 12/12 rotation ETFs |
| 2026-08-12 09:36 ET | populated, **wrong** | today's live move (SPY 0.33) |
| 2026-08-12 09:46 ET | populated, **wrong** | today's live move (SPY 0.28 — drifting while `chg_pct` stays frozen at 0.54) |

So the field passes through three phases: correct early in pre-market, `None`
after CNBC's roll, then repopulated **with today's in-progress session** once the
cash open passes.

**The post-open phase is the dangerous one.** `reg_chg_pct` is non-`None`, so the
map builds and prints a confident `**Rotation map (prior close):**` line computed
from the first minutes of *today* — mislabelled at the source and plausible
enough not to look wrong. That state is reachable through a documented workflow:
SKILL.md Step 5 explicitly sanctions re-running the briefing near the open for a
fresher snapshot. Sourcing the basis from IBKR daily bars removes the phase
dependence entirely.

The exact roll boundary is still unbounded between 07:00 and 09:26 ET — a probe
meant to bracket it started too late. Bracketing it is optional; the field is
unusable in two of three phases regardless.

**Why the tests missed it.** The `_cnbc_json` fixture in
`tests/test_fetch_market_data.py` builds `previous_day_closing=100.0, last=98.0,
change_pct="-2.0"` — top-level `last` differing from prior close, with a
parseable number. That shape does not occur pre-market. Any fix must re-shape
this fixture to match a real pre-market payload, or the same class of bug ships
again.

**Fix (agreed).** Source the completed-session basis from IBKR
`get_price_history` (`step: ONE_DAY`, `step_count: 2`) instead of `reg_chg_pct`.
Verified working. When IBKR is unavailable the block prints an explicit
`unavailable — no completed-session data` line rather than the quiet-tape line —
honest failure over a fabricated quiet reading, consistent with the `N/A —
reason` discipline elsewhere. No local close cache; no new state file.

**Also unresolved.** Task 8 of the rotation-map plan (standardize the materiality
band in the private framework supplement) was never done, so the band is
undefined and the map runs on model judgment. Non-blocking by design.

## IBKR as the price ledger — open question, probe before designing

**Question.** Should IBKR replace CNBC as the Step 3a price ledger, or supply
only completed-session closes and account positions? Design of the IBKR
integration is **paused** pending one measurement that requires a live
pre-market window.

**Settled on evidence (2026-08-11, do not re-derive):**

- IBKR *does* serve pre-market data — `get_price_history` with
  `outside_rth: true` returns 5-min bars from 08:00Z (04:00 ET), with the RTH
  volume jump visible at 13:30Z.
- Cost is not the blocker. `get_price_snapshot` is ~150–200 tokens/symbol, so a
  full ~65-symbol ledger is ~13k/run against CNBC's ~2k. Intraday-bar history is
  ~4–5k/symbol, but a ledger has no reason to request it.
- `search_contracts` is verbose and ambiguous — `SMH` returns 29 rows
  (`SMHN`/`SMHX`/`SMHI`/`SMHC` plus IT/GB/MX listings), `VIX` returns 45. Contract
  ids must be resolved once and committed, never per-run. Known-good US rows:
  `SPY 756733`, `NVDA 4815747`, `SMH 229725622` (NASDAQ), `VIX 13455763` (CBOE,
  `IND`).
- Futures cannot be statically mapped. `search_futures` returns an expiry ladder
  keyed by `contract_month`/`last_trading_date` and the front month rolls
  quarterly, so ES/NQ/YM/CL/GC/NG would need
  `search_contracts` → `search_futures` → sort → snapshot every run. CNBC resolves
  the front month from one string (`@SP.1`). The tape should stay on CNBC
  regardless of how the per-ticker question resolves.

**Resolved 2026-08-12 (pre-market probe, ~07:00 ET).** IBKR *does* carry a
deterministic session flag: `last.is_close`. Same-minute comparison against the
CNBC ledger:

| Symbol | CNBC `quote_type` | IBKR `last` | `is_close` | `ts` | `change` | `prior-close` |
|---|---|---|---|---|---|---|
| JETS (no pre-mkt print) | `PRIOR-CLOSE` | 31.70 | `true` | absent | `{}` | `31.7` |
| SPY | `PRE-MKT` | 772.25 | `false` | present | `0.22` | `{}` |
| SLV | `PRE-MKT` | 59.89 | `false` | present | `2.29` | `{}` |

`is_close: true` → `PRIOR-CLOSE`; `is_close: false` with a `ts` → `PRE-MKT`;
absent → `N/A`. Agreement with CNBC was exact on all three. Two earlier readings
were wrong and are corrected here: `prior-close: {}` is not silent omission but
complementary population (`change` carries the move when a live print exists,
`prior-close` carries the level when it does not); and IBKR does not promote a
stale price to a live print on trivial volume — JETS showed 53 shares traded and
still flagged `is_close: true`.

**Decision: CNBC stays the ledger.** The correctness objection is gone, so this is
now a cost/maintenance call rather than a safety one, and it still lands the same
way — a 45+ symbol conid map to maintain (with new watchlist tickers silently
dropping), loss of CI coverage on the price path, ~65 MCP round-trips against one
batched HTTP call, and futures that cannot be statically mapped at all. IBKR
supplies completed-session daily closes and account positions; nothing else.

**Trigger to revisit:** CNBC changing or removing the `quote.htm` JSON endpoint,
or a recurring need for venue-accurate fill prices in the briefing.

## Optional: bracket the CNBC pre-market roll time

Not required for the rotation fix (IBKR daily closes are correct at any hour), but
it would tell us whether an early-window briefing can still trust `reg_chg_pct`,
and it is nearly free. `scripts/` has no probe committed; the throwaway version
sampled `cnbc_fetch` every 10 minutes and logged `reg_chg_pct` per symbol. Start
it by 04:30 ET (16:30 MYT) — starting late loses the window, which is how the
2026-08-12 attempt failed.
