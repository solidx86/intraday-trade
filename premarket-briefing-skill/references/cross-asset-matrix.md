# Cross-Asset Matrix — Dollar · Yields · QQQ · Oil · Gold

A pre-open bias tool for reading the five instruments together. Companion to
`macro-regime-read.md` (which covers the DXY×US10Y regime grid in depth); this
file adds oil and gold as the "why" layer and a combo cheat-sheet.

## How to use it (read this first)

- **Bias, not trigger.** These tell you which way to *lean* and when to *stand aside*.
  The chart and your levels still pull the trigger.
- **Why > direction.** Every instrument has two opposite meanings depending on the
  driver (growth vs inflation vs fear). The point of reading five at once is to
  resolve that ambiguity — one asset alone is a coin flip.
- **Speed > level.** A *gentle* yield drift down is a tech tailwind; a *crash* down
  is a growth scare that sells tech too. Same arrow, opposite trade.
- **Event days override everything.** Into a FOMC/CPI/NFP print, the whole matrix is
  provisional — the release resets every arrow at once. Don't carry size into it.

## Measuring ↑ / ↓ / muted (vs prior US cash close, 16:00 ET)

| Instrument | "Muted" band (ignore) | Read where |
|---|---|---|
| DXY | < ±0.15% | CNBC `/quotes/.DXY`, tape pull |
| US10Y | < ±3 bps | CNBC `/quotes/US10Y`, tape pull |
| Oil (WTI) | < ±0.75% | tape pull / investing.com |
| Gold | < ±0.4% | tape pull |
| QQQ / ES-NQ futures | < ±0.2% | pre-market futures |

Anything inside the band = no signal from that leg; don't manufacture a story.

---

## Table 1 — What each instrument is telling you

| Instrument | UP usually means | DOWN usually means | Muted |
|---|---|---|---|
| **DXY (dollar)** | Safe-haven demand *or* US growth/rate strength | Risk appetite / liquidity / soft US data | No FX signal |
| **US10Y (yield)** | Growth optimism *or* inflation/hawkish-Fed fear | Disinflation/dovish *or* flight-to-safety | Rates not driving |
| **QQQ (tech)** | Risk-on, growth bid | Risk-off / rate pressure / de-risk | Chop — levels lead |
| **Oil (WTI)** | Demand strength *or* supply shock | Demand fear (recession tell) *or* glut/peace | Energy quiet |
| **Gold** | Fear *or* falling real yields *or* weak $ | Risk-on rotation *or* strong $/rising real yields | No hedge bid |

The recurring "or" is the whole game — Tables 3–4 resolve it.

---

## Table 2 — Core regime grid (DXY × US10Y)

| DXY | US10Y | Regime | Money is… | QQQ posture | DXY→QQQ short tell |
|---|---|---|---|---|---|
| ↑ | ↓ | **SCARED** | hiding in cash *and* bonds — real fear | fade rallies, respect downside | **ON** (only here) |
| ↑ | ↑ | **GREEDY** | chasing US growth/rates, not hiding | longs OK; rate-spike caps tech | OFF |
| ↓ | ↓ | **GOLDILOCKS** | inflation fear leaving; cheap-money | highest-conviction longs | OFF |
| ↓ | ↑ | **REFLATION** | weak $ + rising yields, growth/inflation bid | favor cyclicals/financials/energy; QQQ laggard | OFF |
| flat | flat | **NEUTRAL** | not confirming | trade the chart alone | OFF |

> Note: the REFLATION row (DXY↓/yields↑) is not yet in `macro-regime-read.md`'s
> 4-regime table — candidate to add upstream.

---

## Table 3 — Oil & Gold resolve the "why" (growth vs inflation vs fear)

| Combo | Reading | Expect |
|---|---|---|
| Oil ↑ + Yields ↑ | demand/inflation reflation | energy + financials lead; tech wobbles on rates |
| Oil ↑ + Gold ↑ + DXY ↑ | supply-shock / geopolitical fear | risk-off; only energy & defensives, fade tech |
| Oil ↓ + Yields ↓ | disinflation / soft landing | tailwind QQQ, consumers, airlines; energy laggard |
| Oil ↓ + Gold ↓ + Stocks ↓ | demand destruction / growth scare | everything sells, cash is a position |
| Gold ↑ + Stocks ↑ | weak-$ liquidity, benign | broad risk-on; gold *not* a fear signal here |
| Gold ↑ + Stocks ↓ + DXY ↑ | genuine fear bid | SCARED confirmed — size down |

---

## Table 4 — High-signal combos (cheat sheet)

| If you see… | Lean | Why |
|---|---|---|
| DXY ↓ · Yields ↓ · Oil ↓ · Gold flat · QQQ ↑ | **press tech longs** | clean goldilocks, nothing fighting it |
| DXY ↑ · Yields ↓ · Gold ↑ · QQQ ↑ | **distrust the rally** | money in the bunker while equities rally — unconfirmed |
| Yields spiking fast (any $) · QQQ ↓ | **avoid tech longs** | fast rate spikes hit long-duration growth hardest |
| Oil spiking on geopolitics · DXY ↑ | **energy only, fade risk** | supply-shock inflation = headwind for all but energy |
| All five muted | **ignore macro, trade the chart** | no cross-asset edge today |

---

*Iteration backlog (not yet built): map combos to watchlist sectors/tickers;
turn into a step-by-step pre-open flowchart.*
