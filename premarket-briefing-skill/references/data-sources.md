# Data Sources Reference

This file maps the briefing's data gathering to the sources that work best, and to the **two-phase** workflow `SKILL.md` Step 3 runs: a shared news harvest (Phase A) that feeds the narrative sections, then targeted lookups (Phase B) for the structured-data sections. Use it as a starting point — if a primary source fails or returns stale data, fall through to the alternates listed. **Never fabricate.** If a source is blocked or empty, say so in the output.

A note on date-scoping: always append the computed US trading date to your WebSearch queries (e.g., `"stock market today May 15 2026"`) so you don't get a year-old article ranked first.

---

## Phase A — Shared News Harvest

Fetch these four general-news pages **once each** and read each one broadly. Don't compose any output section while harvesting — extract what you find into the **catalyst inventory** (next section), then route from there.

- `WebFetch https://www.marketwatch.com/` (homepage — front page is curated for the trading day)
- `WebFetch https://www.cnbc.com/markets/`
- `WebFetch https://www.reuters.com/markets/us/`
- `WebFetch https://finviz.com/news.ashx` (news aggregator with timestamps)

**Fallback (use only when a page above is blocked — not routinely):**
- `WebSearch "stock market today [DATE]"`
- `WebSearch "S&P 500 pre-market [DATE]"`

**What this harvest feeds** — three output sections:
- **1.1 General Market News** — the 3 most-important things + a risk-on/risk-off verdict.
- **1.3 Stock & Industry Catalysts** — the biggest stock/sector moves with a clear reason.
- **Market News & Catalysts** — top-5 market-moving headlines + significant M&A / regulatory / geopolitical items.

It also **flags watchlist tickers** for Section 1.4 — see "The Catalyst Inventory" below.

---

## The Catalyst Inventory

The catalyst inventory is an **intermediate scratch artifact** — internal working notes, like the Step 1 date-anchor table. It does **not** appear in the final briefing.

As you read each Phase A page, record one row per distinct headline or mover:

```
Catalyst                          | Seen in        | Feeds section(s)      | Watchlist ticker
Fed minutes read hawkish          | MW, CNBC       | 1.1, Market News      | —
AVGO guidance raise, stock up     | MW, finviz     | 1.3 Tech, 1.4         | AVGO
Boeing 737 grounding              | CNBC           | 1.3 Airlines          | —
UNH in M&A talks                  | Reuters        | Market News (M&A)     | UNH
```

Rules:
- **One item can feed multiple sections** — list all of them in the "Feeds" column.
- **"Seen in" with 2+ sources = corroborated** — weight it higher in 1.1 and 1.3. A theme only one source mentions is weighted lower.
- **If an item names a watchlist ticker, record it** in the last column — that routes the story to Section 1.4. You have the watchlist in context from Step 2, so flag mentions as you read. This is additive to 1.4's full per-ticker scan; it does not replace it.
- **Numbers in the inventory are directional context only.** A homepage may show "AVGO +6%" — do not copy that figure into the briefing body. Every `$price` and `±%` in the body must come from the Step 3.5 price-anchor table via a live finviz fetch. The inventory captures the *story*; the anchor table captures the *number*.

Once the inventory is built, compose sections 1.1, 1.3, and Market News & Catalysts by routing from it.

---

## Phase B — Targeted Section Lookups

The structured-data sections can't be served by a homepage harvest — they need dedicated sources. The Phase A harvest feeds only 1.1, 1.3, and Market News & Catalysts; the sections below — 1.2, the finviz nets for 1.4, earnings actuals, and Global Spillover — each need their own Phase B lookup regardless of what the harvest surfaced.

### Section 1.2 — Economic Announcements Today

**Primary:**
- `WebFetch https://www.forexfactory.com/calendar` — filter mentally to US-only events, current day
- `WebFetch https://www.investing.com/economic-calendar/` — filterable by country and impact

**Fallback:**
- `WebSearch "US economic calendar [DATE] CPI PPI Fed FOMC"`
- `WebFetch https://www.bls.gov/schedule/news_release/` (official release schedule for BLS data)

**Goal:** every scheduled US data release or Fed event for the day, with time in ET, plain-English explanation, and impact rating. Flag anything HIGH impact with ⚠️. If genuinely light, just write "Light calendar today — no major data releases."

### Section 1.3 — Sector gap-check

Phase A's harvest is the **primary** source for Section 1.3. This gap-check catches a big sector mover the harvest didn't headline:

- `WebFetch https://finviz.com/groups.ashx?g=sector` — sector heat-map with the biggest movers per sector.

If the heatmap shows a notable mover with no story in the catalyst inventory, run **one** targeted search to find the catalyst — e.g. `WebSearch "[sector or ticker] news [DATE]"`. This is a gap-fill, not a routine per-sector sweep.

**Goal:** the biggest mover in each sector with a clear catalyst. Skip sectors with no real news — don't pad. Mention the obvious contagion (e.g., "AVGO up on guidance — watch NVDA, AMD for sympathy").

### Section 1.4 — Portfolio News (Per-Ticker)

Section 1.4 is fed by **three nets**. A ticker reaches the 1.4 output if **any one** of them flags it:

1. **Phase A harvest** — any watchlist ticker flagged in the catalyst inventory. Catches a CNBC / MarketWatch / Reuters front-page story finviz's quote page never lists.
2. **finviz per-ticker sweep** — `WebFetch https://finviz.com/quote.ashx?t=[TICKER]` for every watchlist ticker. One page gives recent headlines, analyst actions, earnings dates, pre-market % move, and key levels. This is the systematic full-watchlist scan **and** the Step 3.5 price-anchor pull.
3. **Supplemental per-ticker WebSearch** — for any ticker flagged with news by net 1 or net 2:
   - `WebSearch "[TICKER] stock news [DATE]"`
   - `WebSearch "[TICKER] pre-market [DATE]"` for tickers showing notable pre-market movement
   - `WebSearch "[TICKER] earnings [DATE]"` if it's near their reporting window

   WebSearch is source-agnostic — it surfaces CNBC, Reuters, Bloomberg, etc., not just finviz.

**finviz is the systematic sweep and the price anchor — it is NOT the sole gate on whether a ticker has news.** Don't waste a deep WebSearch on a quiet ticker: if a ticker shows no recent news in any net and no notable pre-market move, it's quiet — drop it from the output and move on.

**Section 1.4 reports only watchlist tickers with news or a catalyst**, grouped by the watchlist's theme sections. Quiet tickers are dropped — no "Quiet today." lines. You still scan every ticker; the filter is on the output, not the scan.

**Anchor table is mandatory for any ticker you'll quote with a number** — see Step 3.5 in `SKILL.md`. The finviz fetch in net 2 IS the anchor pull for that ticker; record prior close, current/pre-market price, and Δ% in the anchor table before writing the number anywhere in the body. Do not propagate the same price across sections from prose — re-check the anchor table at every mention.

### Earnings Reports (inside "Market News & Catalysts")

The rest of **Market News & Catalysts** — the top-5 headlines and the M&A / regulatory / geopolitical items — comes from the Phase A harvest. Only this earnings sub-section needs a dedicated calendar lookup.

**Primary:**
- `WebFetch https://www.investing.com/earnings-calendar/` — filter to today, US-only
- `WebSearch "earnings today [DATE] pre-market"`
- `WebSearch "after-hours earnings [PRIOR_DATE]"` (for the prior session's after-hours)

**Fallback:**
- `WebFetch https://finance.yahoo.com/calendar/earnings`
- `WebFetch https://finviz.com/calendar.ashx` (compact calendar)

**Goal:** notable companies reporting pre-market today AND after-hours from the prior session. Note actual vs estimate (EPS and revenue) and guidance direction when available. "Notable" means: large-cap, sector bellwether, or a name on Solid's watchlist.

### Global Spillover — Asia Indices

- `WebSearch "Nikkei 225 close [DATE]"`
- `WebSearch "Hang Seng close [DATE]"`
- `WebSearch "KOSPI close [DATE]"`
- `WebSearch "Shanghai Composite close [DATE]"`
- `WebFetch https://www.investing.com/indices/major-indices` (fallback — spot levels)

**Themes to watch for:** BOJ policy moves, China stimulus/property/tech crackdown, Japan/US trade tensions, yen interventions.

### Global Spillover — Europe Indices

- `WebSearch "DAX FTSE KOSPI KLCI STOXX [DATE]"`
- `WebFetch https://www.investing.com/indices/europe-indices`

**Goal:** mid-session levels and the dominant theme — usually ECB/BOE policy, energy prices, or a major European earnings story.

### Global Spillover — USD/JPY

- `WebSearch "USD JPY [DATE]"`
- `WebFetch https://www.investing.com/currencies/usd-jpy`

**Why it matters:** sharp JPY strengthening can trigger carry-trade unwinds that hit US risk assets (especially tech). If USD/JPY is dropping >1% intraday or near a known intervention zone, note it. Otherwise: "stable, no carry-trade concern."

---

## Graceful Degradation

If a primary source is blocked or returns no useful data:
1. Try the listed fallback.
2. If the fallback also fails, write what was missing explicitly in the output (e.g., *"Could not fetch live DAX levels — investing.com blocked. Asia/USD-JPY data below is from search results, may be slightly stale."*)
3. **Never invent numbers, headlines, or analyst names.** A briefing with one missing section is useful. A briefing with fabricated data destroys the user's edge.
