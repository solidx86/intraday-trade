# Weekly Review Rubric — how to compute the numbers and pick the order

This is the standard the weekly review runs on. Don't freelance the math; use this.

## Grade → GPA map (for the weekly average)

Per-trade process grades are letters, sometimes with +/-. Convert to a number, average, convert back.

| Grade | GPA |
|-------|-----|
| A+ | 4.3 |
| A  | 4.0 |
| A− | 3.7 |
| B+ | 3.3 |
| B  | 3.0 |
| B− | 2.7 |
| C+ | 2.3 |
| C  | 2.0 |
| C− | 1.7 |
| D+ | 1.3 |
| D  | 1.0 |
| D− | 0.7 |
| F  | 0.0 |

- **Average process grade**: mean of the GPA values, rounded to one decimal, then mapped back to the nearest letter band for display (e.g. 3.8 → "A−", 2.9 → "B", 1.2 → "D"). Report both: "Average process grade: **B−** (2.8)".
- **Grade distribution**: count by *letter only* (collapse A+/A/A− into "A", etc.) — `A:1 B:2 C:1 D:1 F:0`. The +/- detail lives in the average, not the distribution.
- A losing trade can hold an A. A winning trade can be a C. The grade is process; never re-weight it by P&L in the aggregate.

## Win rate

- Win rate = (Wins) / (trades that had a resolved outcome: Win + Loss + BE). Breakevens count as not-a-win in the denominator and not-a-win in the numerator (i.e. they drag the rate down slightly — that's fine, it's not the metric).
- No-trades / skips are excluded from win rate entirely.
- **Always label it**: "Win rate (informational only — not the metric we optimize): X%". If anyone (including Solid) starts steering by win rate, that's a flag to call out in the closing word.

## Repeat-offender thresholds

Run against the negative theme tags (`references/tag-canon.md`).

- **≥3 occurrences of the same negative tag in one week** → repeat offender. Name it, escalate, and it's the front-runner to become next week's order.
- **A negative tag that also appeared in the previous week's review** (even once each week) → "this is a pattern, not a slip" — escalate harder regardless of count. Two weeks running beats three-in-one-week for seriousness.
- **A negative tag that was the subject of last week's order and recurred at all** → this is the headline of the verdict section: order SLIPPED, and the new order either repeats it verbatim ("same order, because you didn't follow it") or attacks the upstream cause (the routine, the screening step) rather than the symptom.
- **Two or more distinct negative tags each at ≥3** → the order targets the common upstream cause if there is one (usually: morning routine / pre-trade checklist not being run), not whichever tag happens to be most frequent.

## Escalation ladder

1. **First appearance, this week only**: note it, no drama. "One FOMO entry on Tuesday. Watch it."
2. **Recurring within the week (≥3×)**: direct order. "Three FOMO entries. The new order is about FOMO. Read it every morning."
3. **Recurring across weeks**: stop treating it as a discipline gap and treat it as a *system* gap. "FOMO again. The rule isn't the problem — you know the rule. Your attention is the problem. Fix the input, not the willpower: [specific routine change]."
4. **Recurring after it was an explicit order**: shortest, hardest register. "I gave you this order last week. You didn't follow it. Same order. No new analysis until the journal shows a week without it."

## Tone-register map (which sections are which voice)

| Section | Register | Example sentence |
|---|---|---|
| Last Week's Order — Verdict | Drill-sergeant | "Order was 'sector first, index second.' You SLIPPED — CRM, you checked QQQ and skipped IGV. Again." |
| Stats | Neutral / factual | "11 trades. 3 longs, 6 shorts, 2 skips. Average process grade B−." |
| Top Recurring Themes | Drill-sergeant on negatives, neutral on positives | "`weak_RS` shows up on 4 of 11. You keep buying the laggard." |
| Psychology Across the Week | Coach (observational, names the enemy) | "Across three reflections you used the word 'seemed' — 'seemed to be holding'. 'Seemed' is hope wearing a technical costume." |
| Setup-Selection Review | Head coach / strategist | "Your P3 rebounds grade B+ on average; your P2 breakouts grade C−. Until breakout execution tightens, weight the book toward rebounds and treat breakouts as 2nd-retest-only." |
| What's Working | Coach (reinforce, specific) | "Your invalidation exits are clean — three this week, all correctly read. That's the invalidation-exit skill landing. Keep it." |
| Single Discipline Focus | Drill-sergeant (the order) | "Before any entry: name the price-structure trigger out loud, confirm the sector ETF agrees, confirm your ticker is stronger than its sector. Three lights or no trade." |
| Closing Word | Drill-sergeant | — |

## Verdict logic — translating last week's order into something checkable

Most orders map to one of:
- **A negative tag should be absent this week** → HELD if it's absent, SLIPPED if it appears at all (and quote the entry).
- **A specific checklist line should be passing across the week** (e.g. "Q5 Relative Strength: Pass") → HELD if every in-range entry passed it (or N/A'd it for a legit reason), SLIPPED if any failed it.
- **A behavioral order** ("run the morning checklist", "skip catalyst days") → check the journal prose / `no_plan` / `held_past_12am` etc. for evidence; if it can't be evidenced either way from the journal, say so and ask Solid directly rather than guessing HELD.

Always quote the prior order verbatim in the verdict. Always cite specific entries as evidence. Never grade the verdict on P&L ("you made money so it HELD" is wrong — a profitable FOMO entry still SLIPPED the FOMO order).

## Lessons-ledger reading (Lessons This Week section)

The weekly review's **Lessons This Week** section reads `data/trade-journal/LESSONS.md` (schema: `intraday-trade-mentor-skill/references/lessons-ledger-spec.md`) and produces four sub-blocks. Math:

### Added this week
Every active lesson whose newest entry in `Origins:` is a `YYYY-MM-DD TICKER` reference that falls in the review week. Counts as "added" even if it was technically allocated mid-week and then reinforced later in the week (still its origin week).

### Held all week
A lesson belongs here when, across the in-range trades, it shows up on ≥1 trade as HELD (cited in "What You Did Right" by the per-trade mentor, or visible in the trade's `## Lessons This Trade` footer under "Reinforced") AND has 0 slips this week. Format: `L### — N/N relevant trades held it`, where the denominator is the count of trades where the lesson's sub-tag/theme came up at all (whether honored or violated). Pure-silence lessons (never came up this week) do NOT belong here — silence isn't holding.

### Slipped this week
A lesson belongs here when its `Last violated` in the ledger is within the review range, OR the per-trade footer under "Slipped" cites it on any in-range trade. Include the slip count from the ledger (lifetime) plus this week's slip count. Flags:
- `⚠ pattern, not slip` when slipped 2+ times this week.
- `⚠⚠ recurring across weeks` when it also appeared in last week's "Slipped this week" list.

### Candidates to mark internalized
Default gate — a lesson is a candidate when ALL of:
1. `status: active` (already internalized or retired → not a candidate)
2. `Reinforced ≥ 5`
3. `Slips = 0` (lifetime)
4. `Last violated` is `—` (never) OR `Last violated` is ≥ 30 days before today.

The gate is intentionally conservative. The math is over the *lifetime* of the lesson, not just this week — graduations are big deals and shouldn't be promoted on a hot streak. Solid always has the final call; the weekly review only suggests, never edits the ledger directly.

If zero lessons clear the gate, that sub-section reads `(none yet)` — that's fine, and not a failure.

## What "clean" tags should mean (so the aggregate isn't garbage)

The journal tag canon is in `references/tag-canon.md`. Two notes for aggregation honesty:
- `clean_loss` should mean *followed the plan, market took the stop* — i.e. a trade that did **not** have foundational (Q1/Q2/Q3) fails. If a D/F-graded trade carries `clean_loss`, that's a mis-tag; in the review, trust the **grade and the checklist results**, not the tag, and note the mis-tag in passing so it gets fixed.
- `disciplined_skip` is for no-trade decisions where a check failed; it has at times been stretched to cover *disciplined invalidation exits* — prefer `disciplined_exit` for those. When you see `disciplined_skip` on a trade with an Outcome of BE/Loss (not a skip), read it as `disciplined_exit` for the aggregate.
