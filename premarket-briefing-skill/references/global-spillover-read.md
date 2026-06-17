# Global Spillover Read — Asia/Europe → US

Use this to turn the overnight Asia/Europe tape into a **US-open read**: which way
the spillover leans and which US *sectors* it touches. It is the synthesis layer of
the **Global Market Spillover** section — the per-index lines are the data, this is
the "so what for the US today."

It is **sector-level only**: name sectors, not watchlist tickers, and no 1.1
mood/regime cross-reference. It introduces **no new numbers** — any % it cites must
already be in the Step 3a Tape Table or the Asia/Europe grep.

## The transmission channels

Walk all of these each run; **write only the ones that fired** (see Gating).

| Channel | Source signal | US read-through (sectors) |
|---------|---------------|---------------------------|
| **China beta** | Hang Seng / Shanghai / KOSPI on demand · property · stimulus · tech-policy · trade | China-revenue semis, materials & miners, machinery/industrials, luxury & casino, autos/EV — direction follows the China tape |
| **Yen carry / risk unwind** | USD/JPY + Nikkei 225 — sharp JPY *strengthening* or a Nikkei dump | High-beta growth & mega-cap tech first; broad risk-off tilt. Quiet default: "no unwind threat" |
| **Europe → US sectors** | DAX / FTSE / STOXX + European sector tape + ECB/BOE — the freshest leg (Europe is mid-session as US pre-market trades) | European banks → US financials; autos/industrials → US industrials & autos; energy/defense → US peers |
| **Cross-asset (oil / rates)** | Overnight WTI/Brent + global yield tape | Energy & transports (oil); rate-sensitives (yields). **Keep light** — only the overnight angle, never a re-quote of the 1.1 commodities/regime lines |

Then a closing **Net** line — the single-line punchline: net **tailwind / headwind /
neutral** for the US open + the one most-affected sector.

## Gating — fire only on a material move

A channel earns a bullet only when its signal is **material**:

- a regional index ≈ **≥1%** on an identifiable driver, **or**
- **USD/JPY ≈ ≥1%** or near a known intervention zone, **or**
- a **named overnight catalyst** (central-bank decision, major data surprise, geopolitical), **or**
- a **notable sector divergence** within a region (e.g. European banks +1.5% while the index is flat).

Anything inside the noise of the prior close stays **silent** — don't manufacture
spillover from a quiet tape.

**Benign tape → one line.** When nothing clears the bar, the whole block collapses to:

> Overnight tape benign — no material spillover into the US open.

## Output shape

```
**→ US Spillover Read (what it means at the open):**
- [Channel]: [overnight tape] — [sector effect on the US open].
- **Net:** [tailwind / headwind / neutral] — [most-affected sector].
```

Keep each bullet to one line. The block is the closer of the Global Market Spillover
section, after *Notable overnight catalysts*.
