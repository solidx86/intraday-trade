# Data Sources Reference

This file maps the briefing's data gathering to the sources that work best, and to the **three-step** workflow `SKILL.md` Step 3 runs: a market-tape pull (Step 3a) for the structured numbers, a shared news harvest (Step 3b) that feeds the narrative sections, then targeted lookups (Step 3c) for the remaining structured-data sections. **Run Step 3a first** — it's the macro backdrop the others read against. Use this file as a starting point — if a primary source fails or returns stale data, fall through to the alternates listed. **Never fabricate.** If a source is blocked or empty, say so in the output (`N/A — reason`).

A note on date-scoping: always append the computed US trading date to your WebSearch queries (e.g., `"stock market today May 15 2026"`) so you don't get a year-old article ranked first.

### Browser vs WebFetch — which path per source

The bot-walled, JS-heavy structured sources return **403/Cloudflare to WebFetch** — reach them with the headless browser. The news/aggregator sources work fine with WebFetch and are cheaper, so keep them WebFetch-first.

| Source | Path | Note |
|--------|------|------|
| `cnbc.com` (pre-markets, quotes) | **browser-primary** | WebFetch 403s; the Step 3a dashboard |
| `reuters.com/markets/us` | **browser-primary** | bot wall |
| `investing.com` (calendar, indices, FX, earnings) | **browser-primary** | Cloudflare challenge |
| `forexfactory.com/calendar` | **browser-primary** | Cloudflare challenge |
| `finviz.com` (news, quote, groups, calendar) | WebFetch-first, browser fallback | quote.ashx stays the per-ticker price anchor |
| `marketwatch.com` | WebFetch-first, browser fallback | occasional paywall |

Don't waste a WebFetch round-trip on a known browser-primary source — go straight to the browser.

---

## Step 3a — Market Tape (browser)

One browser load of CNBC's pre-markets page yields almost every structured number the briefing needs — futures + implied open, VIX/VXN, sector performance, commodities, Treasury yields, FX, and Asia/Europe indices — so pull it **once, first**, and harvest the rest from the saved snapshot.

**Capture recipe (the raw page must never enter context):**

1. `browser_navigate https://www.cnbc.com/markets/pre-markets/` — writes the full snapshot to `.playwright-mcp/page-*.yml` on disk; returns only a tiny confirmation.
2. `grep` the saved file for the data rows. The numbers live in `row "<LABEL> <value> <chg> <%chg>"` lines, plus the per-index futures table blocks. Useful greps:
   - Commodities / vol / yields / FX / global:
     `grep -oE 'row "[^"]+"' <file> | grep -E 'GOLD|SILVER|OIL|NAT GAS|RBOB|VIX|VXN|US 10-YR|US 2-YR|US 30-YR|EUR/USD|USD/JPY|GBP/USD|NIKKEI|HSI|SHANGHAI|DAX|FTSE|STOXX|FINANCIALS|TECHNOLOGY|ENERGY'`
   - Futures + implied open: read the `Dow (mini)` / `S&P 500 (Mini)` / `NASDAQ (Mini)` blocks by line range — each carries an `IND Close / Future / Change` row and a `FAIR VALUE FUTURES` → `Impl Open` row.
3. **Never call `browser_snapshot` without a `filename`** — it returns the ~100k-char page into context. The navigate already saved the file; grep that.

**Build the Tape Table** (internal scratch, like the date-anchor and price-anchor tables; does not appear in the briefing). It is the **anchor** for every tape number — no futures %, VIX/VXN level, sector %, or commodity price reaches the body unless that exact figure is in the grep output.

```
Tape table (CNBC pre-markets, grepped HH:MM MYT):
  Futures:    ES <fut> (±%)  · NQ <fut> (±%)  · Dow <fut> (±%)  [implied-open Δ]
  Volatility: VIX <lvl> (±%) · VXN <lvl> (±%)
  Sectors:    <leader> +x% … <laggard> −y%
  Commodities:WTI <lvl> · Gold <lvl> · NatGas <lvl>
  Yields/FX:  US10Y <%> · DXY <dir> · EUR/USD <lvl> · USD/JPY <lvl>
  Global:     Nikkei <±%> · HSI <±%> · DAX <±%> · FTSE <±%> · STOXX <±%>
```

**VIX classification** (for the Volatility line's tag): `<15 calm · 15–20 normal · 20–25 elevated · >25 high`. Report VXN's level alongside — it runs a few points higher than VIX; use VIX for the tag.

**On a missing row** (page layout changed, module didn't load, navigation blocked): write the field as **`N/A — <one-clause reason>`**. Never guess, never substitute directional prose for a tape number.

**What Step 3a feeds:** the four section-1.1 tape lines; the 1.1 dollar/yields **regime read** (US10Y direction, DXY when present); and most of **Global Market Spillover** (Asia/Europe indices, FX, USD/JPY). When the tape pull succeeds, route those from the Tape Table instead of running separate WebSearches.

**Fallback (only if the CNBC load fails entirely):**
- Per-source browser fetches / WebSearches listed under Step 3c and Global Spillover below.
- DXY/US10Y direction: CNBC `/quotes/.DXY` and `/quotes/US10Y` (browser), or investing.com.
- Say in the affected lines that the tape pull failed and the number is from a fallback (or `N/A — reason`).

---

## Step 3b — Shared News Harvest

Fetch these four general-news pages **once each** and read each one broadly. Don't compose any output section while harvesting — extract what you find into the **catalyst inventory** (next section), then route from there.

- `WebFetch https://www.marketwatch.com/` (homepage — front page is curated for the trading day)
- `browser_navigate https://www.cnbc.com/markets/` (WebFetch 403s — use the browser; grep the saved snapshot)
- `browser_navigate https://www.reuters.com/markets/us/` (bot wall — use the browser)
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

As you read each Step 3b page, record one row per distinct headline or mover:

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

## Step 3c — Targeted Section Lookups

The structured-data sections can't be served by a homepage harvest — they need dedicated sources. The Step 3b harvest feeds only 1.1, 1.3, and Market News & Catalysts; the sections below — 1.2, the finviz nets for 1.4, earnings actuals, and Global Spillover — each need their own Step 3c lookup regardless of what the harvest surfaced.

### Section 1.2 — Economic Announcements Today

**Primary (browser — both Cloudflare-block WebFetch):**
- `browser_navigate https://www.forexfactory.com/calendar` — grep the saved snapshot; filter to US-only events, current day
- `browser_navigate https://www.investing.com/economic-calendar/` — filterable by country and impact

**Fallback:**
- `WebSearch "US economic calendar [DATE] CPI PPI Fed FOMC"`
- `WebFetch https://www.bls.gov/schedule/news_release/` (official release schedule for BLS data)

**Goal:** every scheduled US data release or Fed event for the day, with time in ET, plain-English explanation, and impact rating. Flag anything HIGH impact with ⚠️. If genuinely light, just write "Light calendar today — no major data releases."

### Section 1.3 — Sector gap-check

Step 3b's harvest is the **primary** source for Section 1.3. This gap-check catches a big sector mover the harvest didn't headline:

- `WebFetch https://finviz.com/groups.ashx?g=sector` — sector heat-map with the biggest movers per sector.

If the heatmap shows a notable mover with no story in the catalyst inventory, run **one** targeted search to find the catalyst — e.g. `WebSearch "[sector or ticker] news [DATE]"`. This is a gap-fill, not a routine per-sector sweep.

**Goal:** the biggest mover in each sector with a clear catalyst. Skip sectors with no real news — don't pad. Mention the obvious contagion (e.g., "AVGO up on guidance — watch NVDA, AMD for sympathy").

### Section 1.4 — Portfolio News (Per-Ticker)

Section 1.4 is fed by **three nets**. A ticker reaches the 1.4 output if **any one** of them flags it:

1. **Step 3b harvest** — any watchlist ticker flagged in the catalyst inventory. Catches a CNBC / MarketWatch / Reuters front-page story finviz's quote page never lists.
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

The rest of **Market News & Catalysts** — the top-5 headlines and the M&A / regulatory / geopolitical items — comes from the Step 3b harvest. Only this earnings sub-section needs a dedicated calendar lookup.

**Primary:**
- `browser_navigate https://www.investing.com/earnings-calendar/` — Cloudflare-blocks WebFetch; grep the saved snapshot, filter to today, US-only
- `WebSearch "earnings today [DATE] pre-market"`
- `WebSearch "after-hours earnings [PRIOR_DATE]"` (for the prior session's after-hours)

**Fallback:**
- `WebFetch https://finviz.com/calendar.ashx` (compact calendar — usually works with WebFetch)
- `WebFetch https://finance.yahoo.com/calendar/earnings`

**Goal:** notable companies reporting pre-market today AND after-hours from the prior session. Note actual vs estimate (EPS and revenue) and guidance direction when available. "Notable" means: large-cap, sector bellwether, or a name on Solid's watchlist.

### Global Spillover — Asia Indices

**Step 3a first:** the CNBC pre-markets tape carries Nikkei, Hang Seng, Shanghai (and ASX/STI). Route those from the Tape Table.

**KOSPI + gaps — CNBC `asia-markets/` (browser):** the pre-markets tape does **not** list KOSPI. Top up from `browser_navigate https://www.cnbc.com/markets/asia-markets/` — grep the saved snapshot for the index rows and read the per-region driver headlines (BOJ/yen, China property/stimulus/tech-policy). Same capture recipe as Step 3a: never `browser_snapshot` without a `filename`. This is the **primary** KOSPI source; the WebSearches below are the fallback.

- `WebSearch "KOSPI close [DATE]"`
- `WebSearch "Nikkei 225 close [DATE]"`
- `WebSearch "Hang Seng close [DATE]"`
- `WebSearch "Shanghai Composite close [DATE]"`
- `browser_navigate https://www.investing.com/indices/major-indices` (fallback — spot levels; Cloudflare-blocks WebFetch)

**Themes to watch for:** BOJ policy moves, China stimulus/property/tech crackdown, Japan/US trade tensions, yen interventions.

**Feeds the → US Spillover Read** China-beta and yen-carry channels — see `references/global-spillover-read.md`.

### Global Spillover — Europe Indices

**Step 3a first:** the CNBC pre-markets tape carries DAX, FTSE, CAC, and STOXX. Route from the Tape Table.

**Themes + gaps — CNBC `europe-markets/` (browser):** `browser_navigate https://www.cnbc.com/markets/europe-markets/` — grep the saved snapshot for the index rows and the driver headlines (ECB/BOE, European banks, energy/defense). Same capture recipe as Step 3a. Use for a missing index or the driving theme.

- `WebSearch "DAX FTSE KOSPI KLCI STOXX [DATE]"`
- `browser_navigate https://www.investing.com/indices/europe-indices` (Cloudflare-blocks WebFetch)

**Goal:** mid-session levels and the dominant theme — usually ECB/BOE policy, energy prices, or a major European earnings story. **Feeds the → US Spillover Read** Europe→US channel — see `references/global-spillover-read.md`.

### Global Spillover — USD/JPY

**Step 3a first:** USD/JPY (and EUR/USD, etc.) come from the CNBC tape pull. Use the sources below only if the tape missed the pair.

- `WebSearch "USD JPY [DATE]"`
- `browser_navigate https://www.investing.com/currencies/usd-jpy` (Cloudflare-blocks WebFetch)

**Why it matters:** sharp JPY strengthening can trigger carry-trade unwinds that hit US risk assets (especially tech). If USD/JPY is dropping >1% intraday or near a known intervention zone, note it. Otherwise: "stable, no carry-trade concern."

---

## Graceful Degradation

If a primary source is blocked or returns no useful data:
1. **Escalate by tier:** WebFetch → **browser** (`browser_navigate` + grep the saved snapshot) → WebSearch. For sources already marked browser-primary, start at the browser tier — don't burn a WebFetch 403 first.
2. If every tier fails, write what was missing explicitly. For the **section-1.1 tape lines and any quoted price**, use the structured **`N/A — <one-clause reason>`** form (e.g., *"VIX N/A — CNBC vol module didn't load this run"*). For prose sections, a plain sentence is fine (e.g., *"Could not fetch live DAX levels — investing.com blocked; Asia data below is from search results, may be slightly stale."*).
3. **Never invent numbers, headlines, or analyst names.** A briefing with one missing section is useful. A briefing with fabricated data destroys the user's edge.
