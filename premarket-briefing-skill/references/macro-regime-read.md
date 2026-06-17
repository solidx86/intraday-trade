# Macro Regime Read — Dollar + Yields

Use this to classify *why* money is moving and whether the `DXY → QQQ` inverse is
tradeable today. It enriches the section 1.1 `Market mood` verdict — it does not
replace it.

## Direction = overnight/pre-market net move

Measure each input as **current level vs the prior US cash-session close (16:00 ET)** —
the "prior close" / "Friday close" line already on the chart. This is a snapshot at
briefing time, not a forecast of the post-open trend.

**Evidenced-direction rule:** an arrow may only be written from a fetched
*prior-close → now* pair. Never infer direction from "the catalyst says the dollar
should be up." If the pair can't be fetched, write `NEUTRAL` and say the read is unconfirmed.

**Sourcing:** US10Y (and DXY when present) come from the Phase C market-tape pull
(`SKILL.md` Step 3a) — read direction off the Tape Table. If the tape missed a leg,
fetch it from CNBC `/quotes/.DXY` / `/quotes/US10Y` (browser) or investing.com before
falling back to `NEUTRAL`.

## The four regimes

| DXY | US10Y | Regime | Meaning | `DXY → QQQ` inverse |
|-----|-------|--------|---------|---------------------|
| ↑ | ↓ | **SCARED** | Money hiding in cash *and* bonds — genuine fear | **ON** — short-tell works |
| ↑ | ↑ | **GREEDY** | Money chasing US growth / rates — not hiding | **OFF** |
| ↓ | ↓ | **GOLDILOCKS** | Inflation fear leaving; cheap-money tailwind for tech | **OFF** |
| flat / mixed | flat / mixed | **NEUTRAL** | Move within noise of prior close, or signals conflict weakly | **OFF** — ignore DXY as a tell |

Only short QQQ off a strong dollar in **SCARED**. In every other regime the inverse is off.

## Divergence / alignment with the mood verdict

The mood verdict (RISK-ON/OFF) reads headlines + equity futures. The regime reads the
cross-asset money flow. When they disagree, the disagreement is the signal:

| Verdict | Regime | What it really is | Intraday posture |
|---------|--------|-------------------|------------------|
| RISK-ON | GOLDILOCKS | Real deal | Highest conviction; press strength |
| RISK-ON | GREEDY | Genuine, dollar ↑ on growth | Trade longs — inverse OFF, don't short QQQ off the dollar |
| RISK-OFF | SCARED | Genuine fear | Respect it; `DXY↑→short QQQ` works |
| **RISK-ON** | **SCARED** | ⚠️ Unconfirmed rally — money still in the bunker | Fade-prone; size down, demand confirmation |
| **RISK-OFF** | **GREEDY** | Rates-driven dip, not fear | Don't panic-short the open; pullbacks tend to get bought |
| either | NEUTRAL | Cross-asset tape not confirming | Trade the equity/level read alone; ignore DXY |

When verdict and regime disagree, the 1.1 `→` line must lead with `⚠️ MOOD/REGIME SPLIT`
and the fade/size-down guidance. When they agree, the `→` line states the aligned posture
(and fires the don't-short-QQQ-off-the-dollar caveat in GREEDY/GOLDILOCKS).
