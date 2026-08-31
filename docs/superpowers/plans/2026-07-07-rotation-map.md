# Rotation Map (qualitative destination read) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a qualitative **Rotation map + Regime check** block to section 1.1 of the pre-market briefing that names the sector/factor *groups* money is leaving and entering (the Tier-2 destination read), ranked on a uniform prior-close basis relative to SPY, enforced by the validator and proven by tests.

**Architecture:** Widen the scripted CNBC tape with sub-industry + factor ETFs and capture each row's completed-session move (`reg_chg_pct`) so the ranking has a uniform prior-close basis; put the ranking / materiality / regime-divergence *logic* in a new reference file the SKILL loads at write time (model-driven — no numbers reach the body, so the quote hook is untouched); add the two 1.1 lines to the output template; enforce their presence with a new validator check (`check_rotation_map`) proven by negative unit tests; conform the two sample briefings.

**Tech Stack:** Python 3 (stdlib `fetch_market_data.py`, `validate_briefing.py`), pytest, Markdown (SKILL spec + reference), JSON (evals).

## Global Constraints

- **Public-repo hygiene (leak test):** public files are token-only. The single methodology parameter — the rotation **materiality band** — lives in the private framework supplement (`data/framework/framework-full.md`) and is referenced opaquely; the ETF list, `reg_chg_pct` plumbing, block format, descriptive ETF→group labels, and the rank-vs-SPY method are generic market structure and stay public.
- **Number-provenance contract:** v1 emits **no `$`/`%` in the body** — the block names groups only. No line may introduce a ledger-backed number; the two lines carry a `(prior close)` **basis note**, not a per-number session tag.
- **Determinism:** every tape number still comes from the one scripted CNBC ledger. New ETF symbols that don't resolve emit `N/A` (never guessed).
- **Format consistency:** preserve section order and heading text; the block is additive under the existing `**Sector tape:**` line.

**Spec:** `docs/superpowers/specs/2026-07-07-rotation-map-design.html`

**Branch:** `feat/premarket-rotation-map` (already created)

---

## File Structure

- **Create** `premarket-briefing-skill/references/rotation-map-read.md` — the read: rotation-tape ETF set, ETF→group labels, rank-vs-SPY method, materiality/collapse rule, regime→expected-leadership table + divergence rule, the two-line format, leak-test note. Loaded at write time like `macro-regime-read.md`.
- **Modify** `premarket-briefing-skill/scripts/fetch_market_data.py` — add 12 rotation/benchmark ETFs to `TAPE_SYMBOLS`; capture `reg_last`/`reg_chg_pct` on every row; add `reg_chg_pct` to the printed ledger columns and the `N/A` row.
- **Create** `tests/test_fetch_market_data.py` — unit tests proving `reg_chg_pct` is preserved on a PRE-MKT row and the rotation symbols are in the tape.
- **Modify** `premarket-briefing-skill/evals/validators/validate_briefing.py` — add `check_rotation_map`, wire into `run_all_checks`, update docstring.
- **Modify** `tests/test_premarket_validator.py` — negative/unit tests proving the new check bites and is wired.
- **Modify** `premarket-briefing-skill/SKILL.md` — Step 3a Tape Table scratch (rotation ranking row), Step 4 build instruction, 1.1 output template (two lines), reference link.
- **Modify** `premarket-briefing-skill/references/data-sources.md` — sync the mirrored Tape Table scratch block.
- **Modify** `examples/sample-journal/daily/2026-04-06/premarket.md` and `.../2026-04-08/premarket.md` — add the Rotation map + Regime check lines.
- **Modify** `premarket-briefing-skill/evals/evals.json` — one rubric assertion.
- **(Private, optional)** `data/framework/framework-full.md` — the numeric materiality band. Only if the gitignored private symlink is present; v1 degrades to model judgment without it.

**Commit-green discipline:** the validator check is implemented (Task 3) *before* it is wired into `run_all_checks` (Task 4), so the data-driven `test_premarket.py` never goes red between commits. Sample data is updated in the same task that wires the check in.

---

## Task 1: Reference file `rotation-map-read.md`

**Files:**
- Create: `premarket-briefing-skill/references/rotation-map-read.md`

**Interfaces:**
- Produces: the single source of the rotation-map logic that `SKILL.md` points at (Task 5). No code interface.

Documentation file (no test). It is the self-contained cheat sheet the skill loads at write time, same pattern as `macro-regime-read.md`.

- [ ] **Step 1: Write the reference file**

Create `premarket-briefing-skill/references/rotation-map-read.md` with exactly this content:

````markdown
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
````

- [ ] **Step 2: Leak-test the file**

Re-read it. Confirm: no P1/P2/P3 patterns, no numeric parameters (the band is referenced opaquely, no value), no breakout tell-set, no course citations — generic market structure only. It stays public. No action needed if clean.

- [ ] **Step 3: Commit**

```bash
git add premarket-briefing-skill/references/rotation-map-read.md
git commit -m "docs: add rotation-map-read reference for premarket briefing"
```

---

## Task 2: Widen the tape + capture the completed-session move

**Files:**
- Modify: `premarket-briefing-skill/scripts/fetch_market_data.py`
- Create: `tests/test_fetch_market_data.py`

**Interfaces:**
- Produces: every ledger row now carries `reg_last: float|None` and `reg_chg_pct: float|None` (the last completed regular session), regardless of `quote_type`; `TAPE_SYMBOLS` includes the 12 rotation/benchmark ETFs; the printed ledger has a `reg_chg_pct` column. Consumed by the model at write time (Task 5) and the reference (Task 1).

TDD: write the parse tests first, watch them fail, implement.

- [ ] **Step 1: Write the failing unit tests**

Create `tests/test_fetch_market_data.py`:

```python
"""Unit tests for the pre-market fetch parser.

Prove the rotation-map plumbing: the completed regular-session move is captured
on EVERY row (even a live PRE-MKT row, which the parser otherwise overwrites),
so the rotation map can rank on a uniform prior-close basis; and the rotation
ETFs are in the scripted tape.
"""

import importlib.util
import json

from journal_schema import REPO_ROOT

FETCH_PATH = REPO_ROOT / "premarket-briefing-skill" / "scripts" / "fetch_market_data.py"
spec = importlib.util.spec_from_file_location("fetch_market_data", FETCH_PATH)
fetch_market_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch_market_data)


def _cnbc_json(symbol, prev_close, reg_last, reg_chg, premkt_last=None, premkt_chg=None):
    q = {
        "symbol": symbol,
        "previous_day_closing": str(prev_close),
        "last": str(reg_last),
        "change_pct": str(reg_chg),
        "last_timedate": "2026-07-06T16:00:00",
    }
    if premkt_last is not None:
        q["ExtendedMktQuote"] = {
            "type": "PRE_MKT",
            "last_time": "08:15",
            "last": str(premkt_last),
            "change_pct": str(premkt_chg),
            "last_timedate": "2026-07-07T08:15:00",
        }
    return json.dumps({"ITVQuoteResult": {"ITVQuote": [q]}})


def test_reg_session_captured_on_pre_mkt_row():
    # Liquid ETF with a live pre-market print: chg_pct is the pre-mkt move,
    # reg_chg_pct is the completed session — both present and distinct.
    text = _cnbc_json("SMH", prev_close=100.0, reg_last=98.0, reg_chg=-2.0,
                      premkt_last=99.0, premkt_chg=1.0)
    row = fetch_market_data.parse_cnbc(text, ["SMH"])["SMH"]
    assert row["quote_type"] == "PRE-MKT"
    assert row["chg_pct"] == 1.0        # today's pre-market move
    assert row["reg_chg_pct"] == -2.0   # yesterday's completed session
    assert row["reg_last"] == 98.0


def test_reg_session_captured_on_prior_close_row():
    # Thin ETF, no pre-market: chg_pct and reg_chg_pct agree (uniform basis).
    text = _cnbc_json("XBI", prev_close=90.0, reg_last=93.0, reg_chg=3.3)
    row = fetch_market_data.parse_cnbc(text, ["XBI"])["XBI"]
    assert row["quote_type"] == "PRIOR-CLOSE"
    assert row["chg_pct"] == 3.3
    assert row["reg_chg_pct"] == 3.3


def test_rotation_symbols_in_tape():
    for sym in ["SMH", "XBI", "KRE", "XRT", "XHB", "PEJ", "JETS",
                "RSP", "IWM", "USMV", "MTUM", "SPY"]:
        assert sym in fetch_market_data.TAPE_SYMBOLS
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest tests/test_fetch_market_data.py -v`
Expected: FAIL — `KeyError: 'reg_chg_pct'` on the first two tests, and the symbols assertion fails (feature missing, not a typo).

- [ ] **Step 3: Add the rotation ETFs to `TAPE_SYMBOLS`**

In `fetch_market_data.py`, find:

```python
    "XLK", "XLF", "XLE", "XLU", "XLP", "XLY", "XLI", "XLB", "XLV", "XLC", "XLRE",  # sector proxies
]
```

Replace with:

```python
    "XLK", "XLF", "XLE", "XLU", "XLP", "XLY", "XLI", "XLB", "XLV", "XLC", "XLRE",  # sector proxies
    "SMH", "XBI", "KRE", "XRT", "XHB", "PEJ", "JETS",   # rotation map: sub-industry
    "RSP", "IWM", "USMV", "MTUM", "SPY",                # rotation map: factor/breadth + SPY benchmark
]
```

- [ ] **Step 4: Capture the completed-session move on every row**

In `parse_cnbc`, find:

```python
                   "timestamp": q.get("last_timedate"), "source": "CNBC", "note": ""}
        # CNBC sometimes echoes a symbol with an empty quote object (no price).
```

Replace with:

```python
                   "timestamp": q.get("last_timedate"), "source": "CNBC", "note": ""}
        # Completed regular-session move — captured for EVERY row (even PRE-MKT, which
        # otherwise drops it), so the rotation map ranks on a uniform prior-close basis.
        row["reg_last"] = _to_float(q.get("last"))
        row["reg_chg_pct"] = _to_float(q.get("change_pct"))
        # CNBC sometimes echoes a symbol with an empty quote object (no price).
```

- [ ] **Step 5: Add `reg_chg_pct` to the `N/A` row and the printed columns**

Find:

```python
def _na(symbol, note):
    return {"symbol": symbol, "quote_type": "N/A", "prior_close": None, "last": None,
            "chg_pct": None, "timestamp": None, "source": "CNBC", "note": note}
```

Replace with:

```python
def _na(symbol, note):
    return {"symbol": symbol, "quote_type": "N/A", "prior_close": None, "last": None,
            "chg_pct": None, "reg_last": None, "reg_chg_pct": None,
            "timestamp": None, "source": "CNBC", "note": note}
```

Then find:

```python
_COLS = ["symbol", "prior_close", "last", "chg_pct", "timestamp", "source", "quote_type"]
```

Replace with:

```python
_COLS = ["symbol", "prior_close", "last", "chg_pct", "reg_chg_pct", "timestamp", "source", "quote_type"]
```

- [ ] **Step 6: Run the unit tests to verify they pass**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest tests/test_fetch_market_data.py -v`
Expected: PASS (3 tests).

- [ ] **Step 7: Confirm the full suite is still green**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest -q`
Expected: all pass. In particular the quote-ledger cross-check reads rows by key from the JSON sidecar, so the extra `reg_chg_pct` key/column is ignored by it. If any test asserts an exact ledger column-set and goes red, extend that fixture to include `reg_chg_pct` — no logic change.

- [ ] **Step 8: Commit**

```bash
git add premarket-briefing-skill/scripts/fetch_market_data.py tests/test_fetch_market_data.py
git commit -m "feat: widen tape with rotation ETFs and capture completed-session move"
```

---

## Task 3: Validator check `check_rotation_map` (not yet wired)

**Files:**
- Modify: `premarket-briefing-skill/evals/validators/validate_briefing.py`
- Modify: `tests/test_premarket_validator.py`

**Interfaces:**
- Produces: `check_rotation_map(sections: dict[str, str]) -> CheckResult` with name `"rotation_map"`; passes only when section 1.1 contains both a `**Rotation map` line and a `**Regime check:**` line. Consumed by `run_all_checks` in Task 4.

TDD: write the unit tests first, watch them fail, implement the function. Do **not** wire it into `run_all_checks` yet (keeps `test_premarket.py` green until sample data is updated in Task 4).

- [ ] **Step 1: Write the failing unit tests**

Append to `tests/test_premarket_validator.py`:

```python
def test_rotation_map_passes_with_both_lines():
    sections = {
        SECTION_1_1: (
            "**Sector tape:** XLK +0.5% lead · XLV -0.1% lag *(pre-mkt)*\n"
            "**Rotation map (prior close):** OUT → semis · INTO → homebuilders — "
            "money leaving semis is landing in rate-cut beneficiaries.\n"
            "**Regime check:** GOLDILOCKS expects QQQ to lead; standing rotation "
            "diverges — growth-scare undertone.\n"
        )
    }
    assert validate_briefing.check_rotation_map(sections).passed


def test_rotation_map_fails_without_regime_check():
    sections = {SECTION_1_1: "**Rotation map (prior close):** no material rotation.\n"}
    assert not validate_briefing.check_rotation_map(sections).passed


def test_rotation_map_fails_without_map_line():
    sections = {SECTION_1_1: "**Regime check:** GOLDILOCKS broadly aligned; no divergence flag.\n"}
    assert not validate_briefing.check_rotation_map(sections).passed


def test_rotation_map_scoped_to_section_1_1_only():
    sections = {
        SECTION_1_1: "**Market mood:** **RISK-ON** — no rotation block here.\n",
        "## Quick Summary": "**Rotation map** and **Regime check:** mentioned elsewhere.\n",
    }
    assert not validate_briefing.check_rotation_map(sections).passed
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest tests/test_premarket_validator.py -k rotation_map -v`
Expected: FAIL — `AttributeError: module 'validate_briefing' has no attribute 'check_rotation_map'`.

- [ ] **Step 3: Implement `check_rotation_map`**

In `validate_briefing.py`, add the check function immediately after `check_regime_read` (near ~line 152):

```python
def check_rotation_map(sections: dict[str, str]) -> CheckResult:
    body = sections.get("## 1.1 General Market News", "")
    has_map = "**Rotation map" in body
    has_regime = "**Regime check:**" in body
    if has_map and has_regime:
        return CheckResult("rotation_map", True, "rotation map + regime check present")
    missing = []
    if not has_map:
        missing.append("Rotation map")
    if not has_regime:
        missing.append("Regime check")
    return CheckResult(
        "rotation_map",
        False,
        f"section 1.1 missing: {', '.join(missing)}",
    )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest tests/test_premarket_validator.py -k rotation_map -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Confirm the existing suite is still green**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest -q`
Expected: all pass — `run_all_checks` is unchanged, so `test_premarket.py` is unaffected.

- [ ] **Step 6: Commit**

```bash
git add premarket-briefing-skill/evals/validators/validate_briefing.py tests/test_premarket_validator.py
git commit -m "feat: add check_rotation_map validator check with unit tests"
```

---

## Task 4: Wire the check in + conform sample briefings (single green commit)

**Files:**
- Modify: `premarket-briefing-skill/evals/validators/validate_briefing.py`
- Modify: `tests/test_premarket_validator.py`
- Modify: `examples/sample-journal/daily/2026-04-06/premarket.md`
- Modify: `examples/sample-journal/daily/2026-04-08/premarket.md`

**Interfaces:**
- Consumes: `check_rotation_map` (Task 3).
- Produces: `rotation_map` appears in `run_all_checks` output; both sample briefings satisfy it.

Wiring makes the data-driven `test_premarket.py` go red until the samples carry the block. Do both in one commit so the suite is green at the commit boundary.

- [ ] **Step 1: Add the "wired" test**

Append to `tests/test_premarket_validator.py`:

```python
def test_run_all_checks_wires_in_rotation_map():
    sample = next(
        f for tree in journal_trees() for f in premarket_files(tree)
    )
    results = validate_briefing.run_all_checks(sample)
    assert "rotation_map" in {r.name for r in results}
```

(`journal_trees` / `premarket_files` are already imported at the bottom of this file by the regime-read tests; if not present, add `from journal_schema import journal_trees, premarket_files`.)

- [ ] **Step 2: Run the wired test to verify it fails**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest tests/test_premarket_validator.py::test_run_all_checks_wires_in_rotation_map -v`
Expected: FAIL — `rotation_map` not in the result names (not yet wired).

- [ ] **Step 3: Wire `check_rotation_map` into `run_all_checks`**

In `validate_briefing.py`, in the `run_all_checks` return list, add the rotation check immediately after `check_regime_read(sections)`:

```python
        check_regime_read(sections),
        check_rotation_map(sections),
```

Then update the module docstring numbered list — add after the four-tape-lines item:

```
  7. Section 1.1 carries a Rotation map + Regime check block (destination read)
```

(renumber the subsequent docstring lines accordingly).

- [ ] **Step 4: Conform the 2026-04-06 sample briefing**

In `examples/sample-journal/daily/2026-04-06/premarket.md`, find:

```
**Sector tape:** Technology +1.3% lead · Staples −0.2% lag — money chasing the semi follow-through.
```

Replace with:

```
**Sector tape:** Technology +1.3% lead · Staples −0.2% lag — money chasing the semi follow-through.
**Rotation map (prior close):** OUT → staples, utilities · INTO → semis, small-caps — money leaving defensives is landing in growth / rate-cut beneficiaries.
**Regime check:** GOLDILOCKS expects growth (QQQ) + rate-cut beneficiaries to lead; standing rotation confirms — no divergence.
```

- [ ] **Step 5: Conform the 2026-04-08 sample briefing**

In `examples/sample-journal/daily/2026-04-08/premarket.md`, find:

```
**Sector tape:** Utilities +0.4% lead · Energy −1.6% lag — defensive tilt; XLE still the week's weakest.
```

Replace with:

```
**Sector tape:** Utilities +0.4% lead · Energy −1.6% lag — defensive tilt; XLE still the week's weakest.
**Rotation map (prior close):** OUT → energy, cyclicals · INTO → utilities, min-vol — money leaving cyclicals is landing in defensives ahead of CPI.
**Regime check:** NEUTRAL sets no strong leadership expectation; standing rotation broadly aligned — no divergence flag.
```

- [ ] **Step 6: Run the full suite to verify green**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest -q`
Expected: all pass — the wired test passes, and both sample briefings now satisfy `check_rotation_map`.

- [ ] **Step 7: Commit**

```bash
git add premarket-briefing-skill/evals/validators/validate_briefing.py tests/test_premarket_validator.py examples/sample-journal/daily/2026-04-06/premarket.md examples/sample-journal/daily/2026-04-08/premarket.md
git commit -m "feat: enforce rotation map in validator and conform sample briefings"
```

---

## Task 5: SKILL.md — Tape Table, build instruction, output template, reference link

**Files:**
- Modify: `premarket-briefing-skill/SKILL.md`
- Modify: `premarket-briefing-skill/references/data-sources.md`

**Interfaces:**
- Consumes: `reg_chg_pct` ledger column (Task 2), `references/rotation-map-read.md` (Task 1).

Documentation change (no test); covered by the validator + evals at runtime.

- [ ] **Step 1: Add the rotation ranking row to the Step 3a Tape Table scratch**

In `SKILL.md`, find:

```
  Sectors:    <leader> +x% … <laggard> −y%   (from the XL* sector-ETF rows)
  Commodities:WTI <lvl> · Gold <lvl> · NatGas <lvl>
```

Replace with:

```
  Sectors:    <leader> +x% … <laggard> −y%   (from the XL* sector-ETF rows)
  Rotation:   rank all sector + rotation ETFs by reg_chg_pct − SPY.reg_chg_pct (prior-close basis); note top-3/bottom-3 groups   (see references/rotation-map-read.md)
  Commodities:WTI <lvl> · Gold <lvl> · NatGas <lvl>
```

- [ ] **Step 2: Sync the mirrored scratch block in `data-sources.md`**

In `premarket-briefing-skill/references/data-sources.md`, find the identical line:

```
  Sectors:    <leader> +x% … <laggard> −y%   (from the XL* sector-ETF rows)
```

Replace with:

```
  Sectors:    <leader> +x% … <laggard> −y%   (from the XL* sector-ETF rows)
  Rotation:   rank all sector + rotation ETFs by reg_chg_pct − SPY.reg_chg_pct (prior-close basis); note top-3/bottom-3 groups   (see references/rotation-map-read.md)
```

- [ ] **Step 3: Add the build instruction to Step 4**

In `SKILL.md`, find:

```
Fill section 1.1's four tape lines (Futures, Volatility, Sector tape, Commodities) from the Step 3a Tape Table — real grepped numbers or `N/A — reason`. Then classify the dollar/yields regime per `references/macro-regime-read.md` and write the regime + alignment lines into section 1.1.
```

Replace with:

```
Fill section 1.1's four tape lines (Futures, Volatility, Sector tape, Commodities) from the Step 3a Tape Table — real grepped numbers or `N/A — reason`. Then classify the dollar/yields regime per `references/macro-regime-read.md` and write the regime + alignment lines into section 1.1. Then build the **Rotation map + Regime check** block per `references/rotation-map-read.md` — rank the sector + rotation ETFs by `reg_chg_pct − SPY.reg_chg_pct` (prior-close basis), name the OUT/INTO groups that clear the materiality band (collapse to the quiet-tape line if none do), and flag regime divergence. This block names groups only — no numbers — so it adds no ledger-backed figures to the body.
```

- [ ] **Step 4: Add the two lines to the 1.1 output template**

In `SKILL.md`, find:

```
**Sector tape:** [leader] [+x%] lead · [laggard] [−y%] lag *([pre-mkt/prior close])* — [one clause: where the rotation is]
```

Replace with:

```
**Sector tape:** [leader] [+x%] lead · [laggard] [−y%] lag *([pre-mkt/prior close])* — [one clause: where the rotation is]
**Rotation map (prior close):** OUT → [lagging groups] · INTO → [leading groups] — [money leaving <X> is landing in <Y>]   (collapse to: no material rotation — leadership broad, dispersion inside the band)
**Regime check:** [regime] expects [expected leaders]; standing rotation [confirms / diverges] — [flag or "no divergence"]
```

- [ ] **Step 5: Verify internal consistency**

Re-read the edited `SKILL.md` and `data-sources.md` sections. Confirm: the rank formula (`reg_chg_pct − SPY.reg_chg_pct`) matches the reference; the two output-template lines match the reference's format and the validator's expected substrings (`**Rotation map`, `**Regime check:**`); the `(prior close)` basis note is present.

- [ ] **Step 6: Commit**

```bash
git add premarket-briefing-skill/SKILL.md premarket-briefing-skill/references/data-sources.md
git commit -m "feat: wire rotation map into briefing SKILL.md template and tape table"
```

---

## Task 6: Eval rubric line

**Files:**
- Modify: `premarket-briefing-skill/evals/evals.json`

- [ ] **Step 1: Add the rotation assertion to eval id 1**

In `evals.json`, in the `assertions` array of eval `id: 1` ("explicit-trigger-phrase"), immediately after the regime-read assertion object, insert:

```json
        {
          "text": "Section 1.1 includes a Rotation map (prior close) line naming OUT/INTO groups plus a Regime check line, or collapses to the 'no material rotation' quiet-tape line; the block names groups only and prints no price or percent.",
          "type": "qualitative"
        },
```

(Mind the trailing comma — the inserted object is followed by the next existing assertion object.)

- [ ] **Step 2: Validate JSON**

Run: `cd /Users/solid/Code/intraday-trade && python -c "import json; json.load(open('premarket-briefing-skill/evals/evals.json')); print('valid json')"`
Expected: `valid json`

- [ ] **Step 3: Commit**

```bash
git add premarket-briefing-skill/evals/evals.json
git commit -m "test: add rotation-map assertion to premarket eval rubric"
```

---

## Task 7: Final verification

- [ ] **Step 1: Run the full suite**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest -q`
Expected: all green.

- [ ] **Step 2: Run the validator directly against both samples**

Run:
```bash
cd /Users/solid/Code/intraday-trade
python premarket-briefing-skill/evals/validators/validate_briefing.py --briefing examples/sample-journal/daily/2026-04-06/premarket.md
python premarket-briefing-skill/evals/validators/validate_briefing.py --briefing examples/sample-journal/daily/2026-04-08/premarket.md
```
Expected: `Overall: PASS` for each, and `rotation_map` appears among the passed checks.

- [ ] **Step 3: Confirm the rotation ETFs resolve on the live CNBC endpoint**

Run: `cd /Users/solid/Code/intraday-trade && python premarket-briefing-skill/scripts/fetch_market_data.py 2>/dev/null | grep -E "SMH|XBI|KRE|XRT|XHB|PEJ|JETS|RSP|IWM|USMV|MTUM|SPY"`
Expected: each symbol prints a ledger row with a non-`N/A` `reg_chg_pct` (during/after a US session). Any that come back `N/A` are recorded as such and are non-blocking — note them for a symbol-symbology fix, don't guess a number.

- [ ] **Step 4: Final leak-test + consistency read**

Re-read `rotation-map-read.md` and the SKILL.md edits once more for the leak test and format consistency: no numeric band value in public files, no course citations, no real trades. The two template lines match the validator substrings.

---

## Task 8 (private, optional): standardize the materiality band

**Files:**
- Modify: `data/framework/framework-full.md` (gitignored symlink to the private repo)

Only if the private symlink is present on the working machine. v1 already degrades to model judgment without it (Task 1 reference), so this is a hardening step, not a blocker — and it is committed in the **private** repo, never here.

- [ ] **Step 1: Add the band**

In `data/framework/framework-full.md`, add a short entry defining the rotation **materiality band** (the `rel = reg_chg_pct − SPY.reg_chg_pct` magnitude at/beyond which a group is named OUT/INTO, and below which the map collapses). Keep the value in this private file only; the public reference points at it opaquely.

- [ ] **Step 2: Commit in the private repo**

```bash
git -C data/framework add framework-full.md
git -C data/framework commit -m "framework: add rotation-map materiality band"
```

---

## Self-review (author checklist — completed)

- **Spec coverage:** reference file (Task 1) ↔ spec §B/§C; tape widening + `reg_chg_pct` (Task 2) ↔ spec §A; validator check + negative tests (Tasks 3–4) ↔ spec §D; SKILL.md template + tape table + build instruction (Task 5) ↔ spec §A/§B/§C; eval rubric (Task 6) ↔ spec §D; private band (Task 8) ↔ spec §B materiality + leak test. All spec sections map to a task.
- **Placeholder scan:** none — every code/markdown/JSON step shows literal content; sample-data edits use exact find/replace strings captured from the files.
- **Type/name consistency:** `reg_chg_pct` / `reg_last` identical across Task 2 code, tests, and Task 5 formula; `check_rotation_map(sections)` and the `"rotation_map"` result name identical across Tasks 3, 4, and the wired test; the validator substrings (`**Rotation map`, `**Regime check:**`) identical across the check (Task 3), the output template (Task 5), and the sample briefings (Task 4).
- **Commit-green:** check implemented (Task 3) before wiring (Task 4); samples conformed in the wiring commit; the fetch column change is verified against the full suite (Task 2 Step 7).
- **Hygiene:** the only parameter (materiality band) is isolated to the private Task 8; all public artifacts pass the leak test.
