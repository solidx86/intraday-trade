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

**Problem.** `reg_chg_pct` is `None` for every US equity row during pre-market —
the only window the briefing runs in. During pre-market CNBC's top-level quote
has already rolled over: `last` equals `previous_day_closing` (both yesterday's
close) and `change_pct` is the literal string `UNCH`. `_to_float("UNCH")` returns
`None`, so `fetch_market_data.py` writes `reg_chg_pct: None` for every symbol.
`references/rotation-map-read.md` then collapses to the quiet-tape line whenever
`SPY.reg_chg_pct` is unavailable — so the map **always** prints "no material
rotation" in live use. Verified against the live endpoint 2026-08-11 09:27 EDT:
all 12 rotation ETFs returned `reg_chg_pct: None`.

The field never carries the *completed prior* session for US equities. Pre-market
it is `UNCH`; during RTH it is today's in-progress move. It is only correct in the
narrow post-close-before-rollover window, which is not when the skill runs.

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

**The one open measurement.** `get_price_snapshot` carries no session-type field —
nothing equivalent to CNBC's `ExtendedMktQuote.type == PRE_MKT`. Unknown whether,
during pre-market, `last` is a live pre-market print or a silently-returned prior
close. `prior-close` came back `{}` empty in an RTH test, which is documented
behavior ("fields that are unavailable or time out within 10 seconds are
omitted").

**Probe protocol.** Run inside 04:00–09:30 ET (16:00–21:30 MYT):

1. Pick ~6 symbols spanning liquid (e.g. NVDA, SPY), thin-with-no-pre-market
   (PEJ, JETS, XHB all printed `PRIOR-CLOSE` on 2026-08-11), and any symbol held
   in the account but absent from `watchlist.md`.
2. In the same minute, call `get_price_snapshot` with `last`, `change`,
   `prior_close`, `volume` and run `scripts/fetch_market_data.py` over the same
   symbols.
3. Record per symbol: IBKR `last` vs CNBC `last`; IBKR `change_pct` vs CNBC
   `chg_pct`; whether `prior-close` populated; CNBC's `quote_type`.

**Decision rule.** If IBKR returns the prior close as `last` on a thin ETF with
no field distinguishing it from a live print, that reproduces the 2026-06-17
mislabel incident and CNBC stays the ledger permanently. If the session is
recoverable deterministically, re-open the hybrid options.

**Trigger to revisit:** the next pre-market session with IBKR connected.
