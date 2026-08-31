# Rotation Map — where money is going (Tier-2 destination read)

Adds a **Rotation map** + **Regime check** to section 1.1, one level below the
`Sector tape` line. It answers *where the money is going*, not just what is leading
into today's open. It is **qualitative** — it names groups, never prints
percentages — so no number reaches the body and the quote hook never fires.

## Basis: the last completed regular session, ranked vs SPY

Rotation is a multi-session, full-volume, close-to-close flow — not an overnight
gap. So the map reads the **completed session**, from the ledger's `reg_chg_pct`
column (present on every row, even when a live pre-market print exists). Thin
sector/factor ETFs have little or no pre-market; ranking their pre-market gaps
against liquid ETFs' gaps is apples-to-oranges and produces a wrong call. The
`reg_chg_pct` basis is uniform across all symbols by construction.

Measure each group **relative to SPY**: `rel = reg_chg_pct − SPY.reg_chg_pct`.
Rotation is dispersion *around the index*, so on a broad +2% day this still finds
who truly leads, not merely who is green.

## The rotation tape (sub-industry + factor ETFs)

| ETF  | Group label |
|------|-------------|
| SMH  | semis |
| XBI  | biotech |
| KRE  | regional banks |
| XRT  | retail |
| XHB  | homebuilders |
| PEJ  | leisure / restaurants / cruise |
| JETS | airlines |
| RSP  | equal-weight / breadth |
| IWM  | small-caps |
| USMV | min-vol / defensive |
| MTUM | momentum |
| SPY  | benchmark (the zero line — never named as a group) |

The eleven broad SPDRs (XLK…XLRE) already in the tape may also be named by their
usual sector labels when they are the material movers.

## Materiality — name a group only when it clears the band

- **INTO** = groups with `rel` at or beyond **+band**.
- **OUT** = groups with `rel` at or beyond **−band**.
- **Collapse** to the quiet-tape line when nothing clears the band (leadership is
  broad; dispersion is inside the band).

Skip any group whose reg_chg_pct is blank/None; if SPY.reg_chg_pct itself is unavailable, collapse to the quiet-tape line.

The **band** is the rotation materiality threshold. Apply the standardized value
from the private framework supplement when it is loaded; absent it, use judgment —
a group must be *meaningfully* beyond SPY for the session, not inside session
noise. Name at most the top ~3 INTO and bottom ~3 OUT groups.

## Regime check — does today's tape confirm the standing rotation?

The rotation is a *prior-close* read; the dollar/yields regime (section 1.1, from
`macro-regime-read.md`) is a *today pre-market* read. Compare them. Each regime has
an **expected leadership** (consistent with `cross-asset-matrix.md`):

| Regime      | Expected to lead | Expected to lag |
|-------------|------------------|-----------------|
| GOLDILOCKS  | growth / tech (QQQ), rate-cut beneficiaries (homebuilders, small-caps) | defensives (min-vol, staples) |
| GREEDY      | cyclicals, financials, semis | bond-proxies, defensives |
| SCARED      | defensives (min-vol, staples, healthcare) | high-beta growth, small-caps |
| REFLATION   | cyclicals, financials, energy | QQQ / long-duration growth |
| NEUTRAL     | (no strong expectation) | — |

The **divergence flag fires** when the standing INTO groups sit in the regime's
*expected-lag* set (or OUT groups in the expected-lead set) — e.g. defensives
leading under a GOLDILOCKS tape = a growth-scare undertone beneath a dovish bounce.
When they agree, say so briefly ("broadly aligned; no divergence flag").

## The two lines (always present; collapse on a quiet tape)

Material:

    **Rotation map (prior close):** OUT → [lagging groups] · INTO → [leading groups] — [money leaving <X> is landing in <Y>]
    **Regime check:** [regime] expects [expected leaders]; standing rotation [confirms / diverges] — [flag or "no divergence"]

Quiet:

    **Rotation map (prior close):** no material rotation — leadership broad, dispersion inside the band.
    **Regime check:** [regime] broadly aligned; no divergence flag.

`(prior close)` is a **basis note** (the whole block reads yesterday's session),
distinct from the pre-market `Sector tape` line above it. The lines carry group
names only — no `$`/`%` — so the quote hook never fires on them.

## Leak test

The ETF list, group labels, the rank-vs-SPY method, and the block format are
generic market structure — public. The one parameter, the **materiality band**, is
standardized in the private framework supplement and referenced opaquely here.
