# Model Choice — `premarket-briefing` skill

> **⚠️ Superseded note (2026-05-21):** Section 1.4 was redesigned to report only the watchlist tickers that have a news item or catalyst — full per-ticker coverage is no longer produced, and the `watchlist_coverage` validator check has been removed. The silent-ticker-drop failure mode this study turned on **no longer applies**. The Opus-vs-Sonnet verdict below was decided almost entirely on that check, so it should be re-derived against the current 6-check validator before being relied on. This study is kept as a historical record of the 2026-05-16 run.

**TL;DR — use Opus 4.7 for daily runs.** Sonnet 4.6 had a 33% silent-ticker-drop rate on the watchlist coverage check (1/3 runs in a 2026-05-16 head-to-head; `AMAT` was silently omitted from section 1.4 of one Sonnet run). Reasoning, data, and the conditions under which Sonnet would become viable are below.

## Study setup (one-shot, 2026-05-16)

- **Date:** 2026-05-16 (Saturday MYT) → briefing target US trading day 2026-05-18 (Monday).
- **Trigger:** identical `premarket briefing` prompt for all 6 runs.
- **3× per model**, validator-checked, serial execution to avoid same-path clobbering.
- **Validator:** `validators/validate_briefing.py` — 7 structural checks, watchlist coverage is the headline one.
- **Note on Opus run 3:** first attempt hit an "API Error: Stream idle timeout — partial response received" after ~6.5 min and 16 web searches. That's an infrastructure transient, not a model-quality failure; retried successfully. Mentioned for completeness — does not change the verdict.
- **Raw per-run sandboxes (premarket.md / run.json / meta.json / validation.json for each of the 6 runs) were deleted after analysis** — the conclusion in this file is the durable artifact. To repeat the study, re-run `claude -p "premarket briefing" --model <id>` six times and feed each output to the validator.

---

## 1. Run matrix

| Check | opus/run1 | opus/run2 | opus/run3 | sonnet/run1 | sonnet/run2 | sonnet/run3 |
|---|---|---|---|---|---|---|
| file_nonempty            | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| header_date              | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| seven_sections           | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| risk_verdict             | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| econ_calendar_format     | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **watchlist_coverage**   | **✓** | **✓** | **✓** | **✓** | **✗ (AMAT missing)** | **✓** |
| global_spillover_indices | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Overall** | **PASS 7/7** | **PASS 7/7** | **PASS 7/7** | **PASS 7/7** | **FAIL 6/7** | **PASS 7/7** |

**Opus: 3/3 runs pass.  Sonnet: 2/3 runs pass — 33% failure rate on the headline check.**

### Failure detail — sonnet/run2 dropped AMAT

Section 1.4 of the failing Sonnet run listed the AI-infra block as: `CRWV` → `APLD` → `IONQ` → then jumped directly to `RBLX`. `AMAT` (4th entry in the AI-infrastructure / Compute group in `watchlist.md`) was silently omitted. The model produced a confident, well-structured 1.4 with 41 bullets — exactly the failure mode where a human glance won't catch the missing line, because nothing visibly looks wrong. The validator caught it; that's what it's for.

This matters because AMAT was the *most-cited* ticker across the *other* runs (record earnings 2026-05-14 AMC, Needham target $530, classic relative-strength tell). A real-trading-day briefing that drops it is materially worse than one that says "AMAT — Quiet today." And the failure is invisible to a casual glance: the bullet list looked confident and well-structured; only the validator caught the omission.

---

## 2. Quantitative comparison (per-run)

| Run | Duration | Cost (USD) | Turns | Web searches (via Haiku) | Words | Lines | Bytes | Validator |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| opus/run1   | 314 s |  $2.18 | 41 | 19 | 1961 | 176 | 12,698 | PASS |
| opus/run2   | 333 s |  $1.95 | 33 | 24 | 2244 | 184 | 14,158 | PASS |
| opus/run3   | 338 s |  $2.25 | 36 | 29 | 2301 | 174 | 14,478 | PASS |
| sonnet/run1 | 767 s |  $1.53 | 40 | 19 | 2504 | 191 | 16,079 | PASS |
| sonnet/run2 | 516 s |  $1.48 | 40 | 24 | 2176 | 190 | 13,756 | **FAIL** |
| sonnet/run3 | 607 s |  $1.66 | 48 | 20 | 2800 | 215 | 18,217 | PASS |

### Per-model averages

|  | Opus 4.7 | Sonnet 4.6 |
|---|---:|---:|
| Validator pass rate (n=3) | **3 / 3 = 100%** | **2 / 3 = 67%** |
| Avg duration | **328 s (~5.5 min)** | 630 s (~10.5 min) |
| Avg cost (per briefing) | $2.13 | **$1.56** |
| Avg word count | 2169 | 2493 |
| Avg web searches (Haiku subagent) | 24 | 21 |
| Cost premium of Opus over Sonnet | — | +$0.57 (+37%) |
| Speed premium of Opus | **~2× faster** | — |

### Architecture note (from `run.json` model usage breakdown)

Every briefing runs as a two-tier pipeline:
- A **Haiku 4.5** subagent does all the WebSearch calls (19–29 per run) and returns digests. Haiku does the I/O — searches, fetches.
- The **main model** (Opus 4.7 or Sonnet 4.6) synthesizes the digests into the briefing. The main model issues **zero** direct web searches (`server_tool_use.web_search_requests: 0` in every run).

That's why per-run cost is comparable between models despite Opus's higher per-token price — both runs spend roughly $0.65–$0.95 on Haiku for the searches, and the difference is dominated by main-model token volume. Sonnet's longer outputs (2493 vs 2169 avg words) eat back some of its per-token price advantage.

---

## 3. Qualitative read

Read both `opus/run1/premarket.md` and `sonnet/run1/premarket.md` end-to-end against the SKILL.md voice and structure rules.

### Date-anchor correctness — both PASS

Both runs correctly:
- Identified 2026-05-18 (Monday) as the target US trading day.
- Identified Friday 2026-05-15 as the prior session.
- Anchored Friday close numbers (S&P 7,408.50, NVDA $225.32, AAPL ~$300, AMD $424.10) consistently across cells. No "Wednesday close mislabeled as Friday" bug from the trading-day-logic anti-bug rules.

### Plain-English voice — Opus marginally tighter

| Dimension | Opus | Sonnet |
|---|---|---|
| Bullet length | 1–2 sentences, dense | 1–3 sentences, occasionally drifts to 4 |
| Jargon | Light — uses "relative strength tell", "coil setup" but explains via context | Slightly heavier — "Mag-7", "Strait of Hormuz disruption", "structurally impaired" used without explanation |
| Hedging | Concrete: "Search results returned data only up to 2026-05-12 — could not confirm Friday or Monday levels" | More verbose: "specific level unavailable from searches", "down ~3 to −5% in sympathy with COIN (estimate)" — actually GOOD; honest about uncertainty per skill's guidance |
| "Quiet today" pattern | Compact ("**ACN** — Quiet today.") | Slightly inflated ("ACN — Quiet today. No news found.") — adds the "No news found" tail across many tickers |

Net: both adhere to the skill's voice rules. Sonnet is wordier but its hedging is honest in a way the skill explicitly encourages.

### Depth of analysis — Sonnet has the edge when it commits

When Sonnet has data, it gives more — e.g., on `MSTR` it noted "Purchased 535 more BTC at $80,340 average (May 11 disclosure), total holdings now 818,869 BTC. Q1 2026: $12.54B unrealized loss as BTC fell 23% in Q1. Saylor initially signaled possible BTC sales (tax/accounting driven under FASB fair-value rules), then walked the narrative back." Opus gave just "Down 5.11% to $177.42. $1.5B convertible bond buyback announcement; potential BTC sales hinted."

When Sonnet doesn't have data, it falls back to "Quiet today. No news found." liberally. **In sonnet/run2 this fallback misfired into omission — instead of writing "AMAT — Quiet today." it skipped the line entirely.**

### Section 1.4 grouping — Opus organizes, Sonnet runs flat

- Opus run1 groups 1.4 tickers under bolded sub-headers (`**Mega-cap Tech**`, `**Semis**`, `**AI Infrastructure / Compute**`, etc.) mirroring `watchlist.md`. This is the format the skill template implies but doesn't mandate.
- Sonnet runs use a flat bullet list with no sub-headers.

Opus's grouped format is materially better for the user's portfolio-review use case — it's the same shape as `watchlist.md`, so missing tickers are easier to spot visually. **It's also probably *why* Opus didn't drop a ticker: the grouping forces the model to walk each section header by header, while a flat list invites the "moved on after IONQ" pattern Sonnet hit.**

### What each model is genuinely good at

**Opus 4.7:**
- More reliable on completeness (3/3 watchlist pass rate in this sample)
- ~2× faster (~5.5 min vs ~10.5 min per briefing)
- Tighter, denser prose — gets the core read across in fewer words
- Self-organizes section 1.4 by watchlist theme without being asked
- Better at flagging "this is RS leadership / this is to chase / this is to fade" verdicts in 1-2 words

**Sonnet 4.6:**
- ~37% cheaper per briefing ($1.56 vs $2.13)
- More analytical depth per ticker *when* it commits to one — quotes specific share counts, prior-quarter financials, conviction notes
- More upfront honesty when it lacks data ("specific level unavailable from searches" — this is good)
- Higher word count means more raw context to skim, though it dilutes per-bullet signal density

---

## 4. Verdict

### Overall winner on structural compliance: **Opus 4.7**

3/3 vs 2/3 on the headline watchlist-coverage check is the deciding gap. Everything else (header, sections, calendar format, indices) was flawless on both models — the only check that differentiated them is the one Solid called crucial.

### Is Sonnet 4.6 good enough for daily use? **Not without a guardrail.**

A 33% silent-omission rate on a portfolio-review checklist is unacceptable on its own — the missing ticker reads as "you don't need to look at this" when the model just forgot. For a trader using the briefing as a discipline aid, that's exactly the kind of small-but-systematic failure that erodes trust in the tool.

**Two paths to "Sonnet good enough":**

1. **Add a watchlist-completeness self-check to the skill itself.** After the briefing is written but before it's saved, the skill should run the equivalent of `validate_briefing.py::check_watchlist_coverage` inline (or just have the model re-scan section 1.4 against `watchlist.md` and add any missing tickers with "Quiet today."). This is the cheap fix — it makes Sonnet's omissions self-healing, and the cost saving (~$0.57/run × ~22 trading days = ~$12.50/month) becomes real money over a year. This is the recommended upgrade if Solid wants to use Sonnet.

2. **Force grouped 1.4 output in the template.** Sonnet ran a flat bullet list in 1.4 — that's the format that invited the AMAT skip. Tightening SKILL.md to mandate the same `**Mega-cap Tech** / **Semis** / **AI Infrastructure**...` grouping Opus produces would probably close most of the gap without touching the model. (This is independently worth doing for readability.)

**Current recommendation for daily use, without code changes: stick with Opus 4.7.** The cost delta is ~$0.57/run = ~$12.50/month at daily frequency — small relative to a full-time intraday trader's monthly costs, and you're paying for measured reliability on the check Solid explicitly cares about. Opus is also ~2× faster, so the briefing is ready sooner relative to market open.

**Switch to Sonnet 4.6** *if and when* path (1) or (2) above is implemented — and verify with a fresh 3-run validation. The 33% miss rate is from a small sample; the structural fix above should drive it toward 0%.
