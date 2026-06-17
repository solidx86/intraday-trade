# Browser-Sourced Market Tape — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the Playwright headless browser in as the primary path for the bot-walled structured-data sources (consolidated through one CNBC pre-markets "tape" load), add four enforced market-tape lines to section 1.1 (Futures, Volatility, Sector tape, Commodities), and unify the `N/A — reason` failure rule across tape numbers and per-ticker prices — keeping the 7-section output structure otherwise intact.

**Architecture:** A new gather phase (Phase C) runs first: `browser_navigate` to `cnbc.com/markets/pre-markets/`, grep the saved snapshot, build a Tape Table scratch artifact that anchors every tape number. The four 1.1 lines, the regime read's US10Y direction, and most of Global Spillover route from the Tape Table. Validator gains four line-present checks (`N/A` counts as present); bite-tests prove they fire; both sample briefings and the eval rubric are updated to conform.

**Tech Stack:** Markdown (skill spec + references), Playwright MCP (browser capture), Python 3 (stdlib `validate_briefing.py`), pytest, JSON (evals).

**Spec:** `docs/superpowers/specs/2026-06-17-premarket-browser-tape-design.html`

**Branch:** `feat/premarket-browser-tape`

---

## File Structure

- **Modify** `premarket-briefing-skill/SKILL.md` — new Step 3a (Phase C: market tape), four 1.1 template lines, unified `N/A — reason` rule, Step 4 + regime/Spillover notes.
- **Modify** `premarket-briefing-skill/references/data-sources.md` — Phase C section (capture recipe, grep patterns, VIX scale), browser/WebFetch tiering table, per-source browser-primary edits, graceful-degradation rewrite.
- **Modify** `premarket-briefing-skill/references/macro-regime-read.md` — tape-sourcing note for US10Y/DXY.
- **Modify** `premarket-briefing-skill/evals/validators/validate_briefing.py` — add `check_tape_lines`, wire into `run_all_checks`, update docstring.
- **Modify** `tests/test_premarket_validator.py` — bite-tests for the four tape checks.
- **Modify** `premarket-briefing-skill/evals/evals.json` — one rubric assertion.
- **Modify** `examples/sample-journal/daily/2026-04-06/premarket.md` and `.../2026-04-08/premarket.md` — add the four tape lines to 1.1.
- **Modify** `README.md` — data-flow node + tech-stack line.

**Commit-green discipline:** the new validator checks are additive and only pass once the sample fixtures carry the four lines — update the validator and both fixtures in the same task so `test_premarket.py` never goes red between commits.

---

## Task 1: Phase C in SKILL.md

**Files:** Modify `premarket-briefing-skill/SKILL.md`

- [x] **Step 1: Restructure Step 3** from two phases to three; document the C → A → B running order and the phase-letter-is-identity note.
- [x] **Step 2: Add Step 3a — Phase C: market tape (browser)** — the capture recipe (navigate → grep saved snapshot → never `browser_snapshot` without `filename`), the Tape Table scratch artifact, the anchor rule, and the `N/A — reason` miss rule. Note Phase C feeds the regime read and Global Spillover.
- [x] **Step 3: Rename** the old `Step 3a — Phase A` / `Step 3b — Phase B` headers to `3b` / `3c`; update the regime-read bullet to source US10Y/DXY from the Tape Table.

## Task 2: Four 1.1 tape lines + unified N/A rule

**Files:** Modify `premarket-briefing-skill/SKILL.md`

- [x] **Step 1: Output template** — insert the four bold tape lines between the news bullets and `Market mood`; extend the blank-line-separation note; add the Tape-Table/N-A/VIX-scale note.
- [x] **Step 2: Unify the failure rule** — rewrite Step 3.5's "directional language only" to `N/A — reason` for ticker prices; update the final self-check to reference the Tape Table.
- [x] **Step 3: Step 4** — instruct filling the four tape lines from the Tape Table before the regime classification.

## Task 3: data-sources.md

**Files:** Modify `premarket-briefing-skill/references/data-sources.md`

- [x] **Step 1:** Add the Phase C section (recipe, grep patterns, Tape Table, VIX scale, fallbacks) and a browser-vs-WebFetch tiering table.
- [x] **Step 2:** Mark CNBC/Reuters/investing.com/forexfactory sources browser-primary across Phase A, 1.2, earnings, and Global Spillover; add "Phase C first" notes to the Spillover sub-sections.
- [x] **Step 3:** Rewrite Graceful Degradation to escalate by tier and use `N/A — reason`.

## Task 4: macro-regime-read.md

**Files:** Modify `premarket-briefing-skill/references/macro-regime-read.md`

- [x] Add a sourcing note: US10Y/DXY direction comes from the Phase C Tape Table; fallbacks before `NEUTRAL`.

## Task 5: Validator + bite-tests (commit-green with fixtures)

**Files:** Modify `validate_briefing.py`, `tests/test_premarket_validator.py`, both sample fixtures

- [x] **Step 1:** Add `TAPE_LINES` and `check_tape_lines`; wire into `run_all_checks`; update docstring (7 → 8 logical checks, 11 emitted).
- [x] **Step 2:** Add the four tape lines to both sample briefings (1.1), consistent with each day's synthetic narrative.
- [x] **Step 3:** Add bite-tests — all-present passes, removing any line fails, `N/A — reason` passes, `run_all_checks` wires the four names.
- [x] **Step 4:** `pytest -q` green; validator reports 11/11 on both fixtures.

## Task 6: Eval rubric + README

**Files:** Modify `evals.json`, `README.md`

- [x] **Step 1:** Add the tape-lines rubric assertion to `evals.json`; confirm it parses.
- [x] **Step 2:** Update the README data-flow node and tech-stack line to mention the browser tape capture.

---

## Verification

- `pytest -q` from repo root — full suite green (142 tests), including the new bite-tests.
- `python3 premarket-briefing-skill/evals/validators/validate_briefing.py --briefing examples/sample-journal/daily/2026-04-08/premarket.md` → 11/11 PASS (and the 2026-04-06 fixture).
- Manual end-to-end: one `browser_navigate` to CNBC, a grep (not a raw snapshot dump), a populated Tape Table, and the four 1.1 lines rendering with live numbers or honest `N/A — reason`.
- Leak test: tape numbers are opaque market data — no methodology parameters introduced.

## Out of scope (deferred)

- Pre-market gappers/movers beyond the watchlist.
- Index technical levels (prior-day high/low vs implied open).
- Section order, numbering, and the other six sections — unchanged.
