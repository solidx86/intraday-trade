# weekly-trade-review — evals

Eval set for the `weekly-trade-review` skill. Mirrors the pattern used by `intraday-trade-mentor-skill/evals/`: one "logic works" case, one trap/edge case, one boundary case.

## Layout

```
evals/
├── evals.json            ← the eval definitions (3 cases)
├── README.md             ← this file
└── fixtures/             ← synthetic trade-journal trees the evals point the skill at
    ├── week-repeat-offender/trade-journal/   (4 entries under daily/<date>/, FOMO ×3, no prior review)
    ├── week-improvement/trade-journal/       (4 entries under daily/<date>/ that follow last week's order + weekly/2026-W19_weekly.md carrying that order)
    └── week-too-thin/trade-journal/          (1 entry under daily/<date>/, in range)
```

Each fixture's `trade-journal/` mirrors the real layout: per-trade journals at `daily/YYYY-MM-DD/TICKER_<L|S|NT>_<W|L|BE|SKIP>.md`, prior reviews at `weekly/`, plus the same `INDEX.md` at the fixture's `trade-journal/` root.

Why fixtures: the real `data/trade-journal/` has only a handful of entries from a single week — not enough to exercise a weekly review (stats, theme aggregation, repeat-offender detection, the carry-forward verdict, the <3-trade gate). The fixtures are hand-built to hit each of those paths. Paths in `evals.json` prompts are written relative to the `weekly-trade-review-skill/` skill directory (e.g. `evals/fixtures/week-repeat-offender/trade-journal/`).

## The three cases

1. **week-repeat-offender** — FOMO on 3 of 4 trades, no prior review. Checks: verdict = N/A (not a fabricated HELD/SLIPPED), FOMO flagged as a repeat offender, next-week order targets the FOMO/chase impulse (ideally the upstream routine), stats section present, review persisted to `trade-journal/weekly/2026-W19_weekly.md`, week not ranked by P&L.
2. **week-improvement** — prior review's order is "three lights or no trade"; this week's entries all run it. Checks: verdict = HELD with evidence quoting the order, a *fresh* order is still issued (targeting residual stop-width / R:R-floor weakness), the head-coach setup-selection section is present, tone does not go soft, review persisted to `trade-journal/weekly/2026-W20_weekly.md`.
3. **week-too-thin** — 1 trade in range. Checks: short decline (≤ ~130 words), names the insufficiency, no Stats / no next-week order, and crucially **no review file written**.

## Running

Use the skill-creator plugin's eval runner (the same one used for `intraday-trade-mentor`):

```bash
cd <repo>/weekly-trade-review-skill   # <repo> = wherever you cloned intraday-trade
# invoke the skill-creator skill and point it at evals/evals.json; run N=3 for variance
```

Cost note: 3 evals × N=3 = 9 runs per pass, plus baseline/no-skill runs if you want a comparison — budget ~18+ model calls per full iteration. Capture results in a `weekly-trade-review-skill-workspace/iteration-N/` folder (parallel to `intraday-trade-mentor-skill-workspace/`).

## Iteration history

See `iteration_history` in `evals.json`. iteration 0 = skill + eval set authored 2026-05-12; first runner pass still to do.

## Expanding the set

Add cases as real weeks accumulate: a shorts-heavy week, a multi-week recurrence (same negative tag two reviews running → "pattern, not a slip"), a catalyst-day week, a week where the INDEX.md disagrees with an entry file (the skill should flag the mismatch), and a week with an uncanonized tag (the skill should surface it rather than crash).
