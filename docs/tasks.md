# Tasks / Backlog

Working backlog for follow-up improvements. Tracked in-repo (public) as part of
the engineering record — it documents process, not the shipped behavior spec.

## Verify weekly-review computed stats (deterministic, not a priority)

**Problem.** The weekly review's stats block (trade count, L/S/NT split, grade
distribution, average GPA, win rate, tag tallies) is computed by the LLM in-head
across all in-range journals. Unlike the per-trade *write* path, these numbers
are verified by **nothing** — `test_weekly_review.py` checks filename/title,
section presence, and the verdict token, but never recomputes the figures. A
miscount or a wrong GPA average ships silently and looks plausible.

**Fix (cheap, on-thesis).** Extend the weekly test to recompute the stats from
the in-range fixture trades and assert the numbers in the weekly file match.
Keeps generation non-deterministic, verifies the arithmetic deterministically —
same philosophy as the rest of the suite. Pairs naturally with a committed
cross-skill golden-week fixture (known-correct trades to recompute against).

**Later, only at journal scale.** A runtime aggregator (`aggregate_week.py` the
skill calls to emit counts/distribution/GPA/tag-tallies/prior-order/ledger-join
as a structured digest, then the LLM *interprets* it) becomes worth it for
monthly/quarterly rollups (20–60 trades) where hand-aggregation degrades. For
3–5-trade weeks it's over-engineering — skip until longer-horizon reviews exist.

**Trigger to revisit:** adding monthly/quarterly review horizons, or a recurring
hand-fix of a wrong stat in a shipped weekly.
