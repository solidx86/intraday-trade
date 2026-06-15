# Evals for intraday-trade-mentor

This folder holds the eval set used to iterate on the mentor skill.

## Files

- `evals.json` — eval definitions with prompts, attached chart images, ground-truth notes, and assertions
- `assets/` — staged screenshot pairs from real trades (3-col ticker + 4-cell indices)
- `iteration-*/` — per-iteration run outputs (created when runs are executed)

## Current eval set (iteration 1)

| ID | Label | What it tests |
|----|-------|---------------|
| 1 | CRM long against trend — losing trade | Wrong-side-of-trend detection, sector RS check (IGV), VIX direction read, pre-market shading interpretation |
| 2 | SMH long in uptrend — invalidation exit | Correct grading of disciplined manual exits (NOT fear exit), recognition of leading-sector RS, invalidation-exit alignment |
| 3 | Missing 4-cell input | Refusal-to-grade discipline when required inputs absent |

## Running the evals

The skill-creator plugin ships scripts to run these formally:

```bash
SKILL_DIR=<repo>/intraday-trade-mentor-skill   # <repo> = wherever you cloned intraday-trade
SC=$HOME/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts

# Run all evals with the skill enabled (and a baseline without it)
python "$SC/run_loop.py" --skill-dir "$SKILL_DIR" --evals "$SKILL_DIR/evals/evals.json"

# Generate an HTML viewer for qualitative review
python "$SC/../eval-viewer/generate_review.py" --workspace "$SKILL_DIR-workspace/iteration-1"
```

Cost note: each eval spawns at least one Claude agent (with-skill + baseline = 2 per eval). For 3 evals that's 6 runs minimum; with N=3 for variance, 18. Image inputs are token-heavy. Run sparingly.

## Iteration 1 findings (from interactive testing 2026-05-12)

Already documented in `evals.json` under `iteration_history`. Summary:

1. **SKILL.md needs pre-market shading clarification** — peach zone = pre-market, not first-30-min. 9:30pm MY = market open. Skip first 3 candles by user convention.
2. **Tag canon needs additions** — `correct_RS_read`, `disciplined_exit`.
3. **Exit-grading needs explicit fear-vs-invalidation distinction** — name the invalidation-exit rule.
4. **Sector ETF mapping should be enumerated** — IGV/software, SMH/semis, XLF/fin, XLE/energy, etc.

These edits are queued for SKILL.md v2 once the user gives the go-ahead.
