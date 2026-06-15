# Sample Journal (synthetic)

This directory is a **fully synthetic** sample of the trade-journal data layer that the three skills coordinate through. Every trade, price, news item, and reflection in here is invented for illustration — none of it is a real trade or real market data.

It exists so that:

1. Reviewers can see the journal schema end-to-end (per-trade entries, premarket briefings, the cross-trade index, the lessons ledger, a weekly review) without any real trading data being published.
2. The deterministic validator test suite in `tests/` has a tracked corpus to check against the schema.

The real journal lives in a separate private repository and is symlinked in at `data/trade-journal/` on working machines (see the main `README.md`).

Layout mirrors the real journal exactly:

```
INDEX.md                 ← one row per trade, written by intraday-trade-mentor
LESSONS.md               ← lessons ledger (schema-versioned state machine)
daily/YYYY-MM-DD/
  premarket.md           ← premarket-briefing output (context)
  TICKER_<L|S|NT>_<W|L|BE|SKIP>.md   ← per-trade journals (execution)
weekly/YYYY-Www_weekly.md  ← weekly-trade-review output
```
