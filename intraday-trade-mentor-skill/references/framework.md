# Intraday Framework — Condensed Reference (public copy)

This is the grading skeleton the mentor applies. It is deliberately **token-only**: it names the
dimensions and the pattern labels Solid trades, but the *operative definitions* — exact entry/stop/target
placements, the breakout tell-set, the intraday EMA convention, position-sizing parameters — are
proprietary (a private intraday-trading methodology) and are **not reproduced here by design**.

> **Private supplement:** when `<repo-root>/data/framework/framework-full.md` is mounted (private repo,
> see `README.md` setup), load it instead — it carries the full-parameter version. Absent that mount,
> grade the non-proprietary checks and treat the parameter-level and breakout-quality judgments as running
> on this condensed reference only; do not improvise the missing parameters.

## The 3 Questions (always, in order)

1. **What is the trend?** (1Y Daily chart) — Uptrend / Downtrend / Sideways, judged from daily EMAs,
   trendline structure, relative highs/lows. Long trades require an uptrend (or sideways-in-uptrend);
   shorts the mirror.
2. **Is there a pattern to trade?** — a named pattern (see token list) must be *forming or formed*, not
   "kind of looks like one."
3. **Is Reward/Risk ≥ 2?** — calculated from technical levels, not gut: Entry→PT vs Entry→SL. R:R < 2
   fails the question regardless of how good the chart looks.

A "fail" on any of the 3 Questions invalidates the trade entirely.

## Pattern tokens (labels, not definitions)

The methodology trades a small set of named patterns. The labels are public; their operative
entry/stop/target rules are proprietary and load from the private supplement.

- **Long:** P1 (rangebound), P2 (breakout), P3 (rebound).
- **Short:** P1a, P2a, P3a (mirror images), plus the failed-breakout setup.
- **Plus:** Trend Continuation, Triangles.

Grade *whether the named pattern actually printed* and whether execution matched its required confirmation
— the exact confirmation/placement rule comes from the supplement, not from this file.

## Breakout quality

Breakouts vary in quality; the strength of the structure into resistance is graded by a proprietary
tell-set (private supplement). The public principle: **mark a setup down when the structure into the level
is weak, even if the entry itself was clean.**

## Stop loss & sizing (principles only)

- **Always technical** — never "I'll just risk $X." The stop sits at a level the market must violate to
  invalidate the thesis. Location beats width.
- Stop width and position size scale with the setup off the daily range; the exact parameters are
  proprietary (private supplement).
- **Max 1% portfolio risk per trade**, sized off the stop distance with gap risk in mind.

## Profit targets (principles only)

- Technical levels first: next resistance/support, psychological round number.
- The daily range is the sanity gauge for how far a target may reasonably sit within the session.
- Partial profit-taking requires the banked portion to be better than 1R.

## Manual Exit Rules — Invalidation vs Fear

Manual exits at key price levels are part of the playbook — cutting fast when price action invalidates the
setup is professional behavior, not a deviation from the plan.

| Exit type | Trigger | Grade |
|-----------|---------|-------|
| **Invalidation exit** | Price action breaks the setup *before* SL: lower-high where higher-high was expected, double-top, failed reclaim, distribution volume against the trade, break of intraday trendline | **Pass** — endorsed manual cut |
| **Fear exit** | Volatility alone with no structural break: a single red candle, a noisy wick, "looks like it's falling" | **Fail** — sign-of-fear early exit |

**The distinguishing test**: ask "what *structural* signal triggered the exit?" A specific price-action
invalidation is discipline; an emotional answer is fear. The same small loss can be A-grade or F-grade
depending on the reason.

## Key Price Levels

- **Psychological round numbers** — major levels.
- **Dealer-positioning levels** — where option hedging clusters tend to act as S/R.
- **Daily S/R and daily EMAs.**
- **Recent intraday S/R ranges** (multi-day 3-minute structure).
- **Pre-market S/R** — price tends to react at pre-market high/low.
- **Today's open**, **Previous Day High/Low/Close**.

(The intraday EMA convention used to proxy the daily structure is a proprietary parameter — private
supplement.)

## Market Sentiment & Relative Strength

### Sentiment check (the 4-cell)
- **QQQ + SPY + RSP** all green and trending up → bullish sentiment, longs favored.
- All red/rolling over → bearish sentiment, shorts favored.
- Mixed (e.g., QQQ up, RSP flat) → narrow breadth, be selective.
- **VIX rising** during a long trade = headwind. VIX falling during a short = headwind.
- RSP rolling while QQQ holds = mega-cap covering broader weakness — high-risk environment.

### Relative strength
- Compare the ticker's % move and chart structure to QQQ/SPY (and its sector ETF) over the same intraday window.
- **High RS**: ticker holds while index drops, or rises more than index. Long candidate.
- **Low RS**: ticker drops while index rises, or rises less than index. Short candidate.
- A long entry into a ticker with **low** relative strength is a major rule violation regardless of the daily setup.

## Trade Timing Rules

- Prep ~30 min before market open.
- Active trading window: **first 30 min to 2 hours after open**.
- **No holding past 12am Malaysia time** (4am US ET) — extending hours is overtrading.
- Don't trade Fed announcement minutes — volatility spikes are not your friend.

## Catalysts — required, not optional

**A catalyst is one of the three legs of the Trade Quality Triad (L037).** Without one, the trade is
sub-quality regardless of how clean the chart looks. A "pretty bounce off support" with no catalyst is a
disciplined skip, not a setup. The other two Triad legs are strong relative strength (vs broader market AND
sector) and a named pattern.

A real catalyst is something specific and falsifiable — you can name the company / industry / peer / macro
driver in one sentence. "Looks oversold" is not a catalyst. A trade entered on a real catalyst with strong
RS into a named pattern is the A-grade setup; missing the catalyst leg caps the grade at B even with clean
execution.

## Position Sizing & Risk

- **Max 1% portfolio risk per trade**. Position size = (1% × portfolio) / Stop distance.
- Intraday size may exceed swing size only while the 1% risk cap still holds.

## Common Pitfalls — enforcement checklist

- ✗ No trading plan / impromptu trading.
- ✗ Chasing fast candles at open.
- ✗ Overtrading: too big a size, topping up past max risk, trading past 12am, trading just to trade.
- ✗ Keeping intraday positions overnight.
- ✗ Continuing to trade after losing focus.
- ✗ Premature entry (Greed) or premature exit (Fear).
- ✗ Revenge trading after a loss.
- ✗ Waiting for Fed announcement (sitting out is fine; trading the spike is not).

## The Multi-Year Apprenticeship

Consistency takes years, not months. The initial goal is to master the skills + psychology + market
behavior — NOT to make money. Once mastery is real, the money follows. Inverting that order is how accounts
blow up. This is the baseline reality you remind Solid of when he is catastrophizing a single trade.
