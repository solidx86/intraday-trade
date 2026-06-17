# Evals — premarket-briefing

These are **structural** evals, not content evals. The skill produces a daily news briefing whose content is, by definition, different every day — so we can't write assertions like "must mention the Fed". What we *can* test is whether the briefing has the right shape:

- All 7 required section headings present, in order
- A risk-on / risk-off verdict appears in 1.1
- The four section-1.1 market-tape lines (Futures, Volatility, Sector tape, Commodities) are present
- A Dollar/Yields regime token (SCARED / GREEDY / GOLDILOCKS / NEUTRAL) appears in 1.1
- Economic events in 1.2 are impact-labeled
- Global Spillover lists the full index set and closes with a → US Spillover Read block (or its benign-tape fallback)
- Output is saved to `data/trade-journal/daily/YYYY-MM-DD/premarket.md`
- Header includes a US trading date in `YYYY-MM-DD` form

The three test prompts cover different trigger phrasings:

1. **`premarket briefing`** — the canonical, explicit trigger
2. **`what should I watch in the market today`** — casual, indirect
3. **`brief me on the upcoming US session`** — forward-framing, tests date logic

## Running the structural validator

The assertions above are enforced programmatically by `validators/validate_briefing.py` — a stdlib-only Python script that takes a generated `premarket.md` and runs twelve structural checks: file non-empty; header date; the seven section headings present and in order; a risk-on/off verdict in 1.1; a Dollar/Yields regime token in 1.1; the four section-1.1 market-tape lines (Futures, Volatility, Sector tape, Commodities); an impact-labeled (or light-calendar) section 1.2; the full Global Spillover index set; and a → US Spillover Read block (or its benign-tape fallback).

```bash
# From repo root:
python3 premarket-briefing-skill/evals/validators/validate_briefing.py \
  --briefing data/trade-journal/daily/2026-05-15/premarket.md \
  --json-out /tmp/validation.json
```

Exit code is `0` if all checks pass, `1` otherwise. The script prints a per-check `PASS`/`FAIL` table to stdout and (optionally) writes the same data as JSON for downstream tooling.

The validator deliberately does **not** assert on freshness or content (it can't — content varies daily). Those quality dimensions are reviewed live by Solid each morning. The validator catches the silent failure modes a human glance would miss: a renamed section, a section out of order, a dropped Global Spillover index, a stale date in the header.

Section 1.4 (Portfolio News) is no longer structurally checked: it now reports only the watchlist tickers that have a news item or catalyst, so there is no fixed ticker set to assert against. Its shape is reviewed live and via the qualitative assertions in `evals.json`.

## Model choice

This skill runs under **Opus 4.7** by default. The rationale (and the data from a 2026-05-16 head-to-head against Sonnet 4.6) lives in `MODEL_CHOICE.md` alongside this README. Re-run the study if you want to revisit — there's no standing automation.

## Why structural-only?

Two reasons. First, the briefing's value lies in *fresh* news — yesterday's headlines are worse than nothing. So a frozen assertion like "must mention NVDA earnings" is wrong half the time and right by accident the other half. Second, the user reviews the briefing every day anyway — qualitative quality control is already in his workflow. The evals just need to catch the failure modes that *aren't* obvious from a glance: a missing or renamed section, a stale date, a dropped Global Spillover index.

If the skill ever evolves to produce structured data (JSON output, a daily P&L attribution, etc.), then real content assertions become viable. Until then, structural is the right level.
