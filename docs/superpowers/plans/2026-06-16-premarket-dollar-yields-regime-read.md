# Dollar/Yields Regime Read — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a cross-asset dollar/yields regime read (SCARED / GREEDY / GOLDILOCKS / NEUTRAL) to section 1.1 of the pre-market briefing, enforced by the validator and proven by tests.

**Architecture:** Enrich the existing 1.1 `Market mood` verdict with a regime line + alignment line driven by a new reference file; fetch DXY + US10Y as evidenced prior-close→now pairs; enforce the regime token with a new validator check (#7) and prove the check bites with new negative unit tests; update the two sample briefings to conform.

**Tech Stack:** Markdown (skill spec + reference), Python 3 (stdlib `validate_briefing.py`), pytest, JSON (evals).

**Spec:** `docs/superpowers/specs/2026-06-16-premarket-dollar-yields-regime-read-design.html`

**Branch:** `feat/premarket-regime-read` (already created)

---

## File Structure

- **Create** `premarket-briefing-skill/references/macro-regime-read.md` — the regime cheat-sheet (4-regime table, DXY→QQQ caveat, divergence matrix, evidenced-direction rule). Loaded at write time like `data-sources.md`.
- **Modify** `premarket-briefing-skill/evals/validators/validate_briefing.py` — add `check_regime_read`, wire into `run_all_checks`, update docstring.
- **Create** `tests/test_premarket_validator.py` — negative/unit tests proving the new check bites and is wired.
- **Modify** `premarket-briefing-skill/SKILL.md` — Step 3b fetch, 1.1 output template, Global Spillover tape lines, reference link.
- **Modify** `premarket-briefing-skill/evals/evals.json` — one rubric assertion.
- **Modify** `examples/sample-journal/daily/2026-04-06/premarket.md` and `.../2026-04-08/premarket.md` — add regime line + DXY/US10Y tape lines.

**Commit-green discipline:** the validator check is implemented (Task 2) *before* it is wired into `run_all_checks` (Task 4), so the data-driven `test_premarket.py` never goes red between commits. Sample data is updated in the same task that wires the check in.

---

## Task 1: Reference file `macro-regime-read.md`

**Files:**
- Create: `premarket-briefing-skill/references/macro-regime-read.md`

This is a documentation file (no test). It is the single source of the regime logic that SKILL.md points at.

- [ ] **Step 1: Write the reference file**

Create `premarket-briefing-skill/references/macro-regime-read.md` with exactly this content:

```markdown
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
```

- [ ] **Step 2: Leak-test the file**

Re-read it. Confirm: no P1/P2/P3 patterns, no parameters, no breakout tell-set, no course citations — textbook macro only. It stays public. No action needed if clean.

- [ ] **Step 3: Commit**

```bash
git add premarket-briefing-skill/references/macro-regime-read.md
git commit -m "docs: add macro-regime-read reference for premarket briefing"
```

---

## Task 2: Validator check `check_regime_read` (not yet wired)

**Files:**
- Modify: `premarket-briefing-skill/evals/validators/validate_briefing.py`
- Create: `tests/test_premarket_validator.py`

TDD: write the unit tests for the function first, watch them fail, implement the function. Do **not** wire it into `run_all_checks` yet (keeps `test_premarket.py` green until sample data is updated in Task 4).

- [ ] **Step 1: Write the failing unit tests**

Create `tests/test_premarket_validator.py`:

```python
"""Unit tests for the premarket-briefing validator's own logic.

Unlike test_premarket.py (which asserts the sample corpus *passes*), these
tests prove individual checks actually *bite* — i.e. reject a briefing that
violates the contract. Added alongside the dollar/yields regime read so the
validated-lite enforcement of the regime token is provably real, not a
check that silently always passes.
"""

import importlib.util

import pytest

from journal_schema import REPO_ROOT

VALIDATOR_PATH = (
    REPO_ROOT / "premarket-briefing-skill" / "evals" / "validators" / "validate_briefing.py"
)

spec = importlib.util.spec_from_file_location("validate_briefing", VALIDATOR_PATH)
validate_briefing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_briefing)

SECTION_1_1 = "## 1.1 General Market News"
REGIME_TOKENS = ["SCARED", "GREEDY", "GOLDILOCKS", "NEUTRAL"]


@pytest.mark.parametrize("token", REGIME_TOKENS)
def test_regime_read_passes_with_any_valid_token(token):
    sections = {
        SECTION_1_1: (
            "**Market mood:** **RISK-ON** — relief rally.\n"
            f"**Dollar/Yields regime:** {token} — DXY up / US10Y up.\n"
        )
    }
    result = validate_briefing.check_regime_read(sections)
    assert result.passed, result.detail


def test_regime_read_fails_when_token_absent():
    sections = {
        SECTION_1_1: (
            "**Market mood:** **RISK-ON** — relief rally.\n"
            "No cross-asset regime classification anywhere in this section.\n"
        )
    }
    result = validate_briefing.check_regime_read(sections)
    assert not result.passed


def test_regime_read_scoped_to_section_1_1_only():
    sections = {
        SECTION_1_1: "**Market mood:** **RISK-ON** — no regime label here.\n",
        "## Quick Summary": "Markets look GREEDY elsewhere.\n",
    }
    result = validate_briefing.check_regime_read(sections)
    assert not result.passed
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest tests/test_premarket_validator.py -v`
Expected: FAIL — `AttributeError: module 'validate_briefing' has no attribute 'check_regime_read'` (feature missing, not a typo).

- [ ] **Step 3: Implement `check_regime_read`**

In `validate_briefing.py`, add the token constant near the other module constants (after `REQUIRED_INDICES`, ~line 37):

```python
REGIME_TOKENS = ["SCARED", "GREEDY", "GOLDILOCKS", "NEUTRAL"]
```

Add the check function next to `check_risk_verdict` (after it, ~line 111):

```python
def check_regime_read(sections: dict[str, str]) -> CheckResult:
    body = sections.get("## 1.1 General Market News", "")
    found = [t for t in REGIME_TOKENS if t in body]
    if found:
        return CheckResult("regime_read", True, f"regime={found[0]}")
    return CheckResult(
        "regime_read",
        False,
        "no SCARED/GREEDY/GOLDILOCKS/NEUTRAL regime token in section 1.1",
    )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest tests/test_premarket_validator.py -v`
Expected: PASS (5 tests: 4 parametrized + fail-case + scoped-case → actually 6 test invocations: 4 token params, 1 absent, 1 scoped).

- [ ] **Step 5: Confirm the existing suite is still green**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest -q`
Expected: all pass — `run_all_checks` is unchanged, so `test_premarket.py` is unaffected.

- [ ] **Step 6: Commit**

```bash
git add premarket-briefing-skill/evals/validators/validate_briefing.py tests/test_premarket_validator.py
git commit -m "feat: add check_regime_read validator check with unit tests"
```

---

## Task 3: Wire the check in + update sample data (single green commit)

**Files:**
- Modify: `premarket-briefing-skill/evals/validators/validate_briefing.py`
- Modify: `tests/test_premarket_validator.py`
- Modify: `examples/sample-journal/daily/2026-04-06/premarket.md`
- Modify: `examples/sample-journal/daily/2026-04-08/premarket.md`

Wiring the check makes the data-driven `test_premarket.py` go red until the sample data carries the token. Do both in one commit so the suite is green at the commit boundary.

- [ ] **Step 1: Add the "wired" test**

Append to `tests/test_premarket_validator.py`:

```python
from journal_schema import journal_trees, premarket_files


def test_run_all_checks_wires_in_regime_read():
    sample = next(
        f for tree in journal_trees() for f in premarket_files(tree)
    )
    results = validate_briefing.run_all_checks(sample)
    assert "regime_read" in {r.name for r in results}
```

- [ ] **Step 2: Run the wired test to verify it fails**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest tests/test_premarket_validator.py::test_run_all_checks_wires_in_regime_read -v`
Expected: FAIL — `regime_read` not in the result names (not yet wired).

- [ ] **Step 3: Wire `check_regime_read` into `run_all_checks`**

In `validate_briefing.py`, in the `run_all_checks` return list, add the regime check immediately after `check_risk_verdict(sections)`:

```python
    return [
        nonempty,
        check_header_date(text),
        check_seven_sections(sections, text),
        check_risk_verdict(sections),
        check_regime_read(sections),
        check_econ_calendar(sections),
        check_global_spillover(sections),
    ]
```

Also update the module docstring numbered list — add after the RISK verdict line:

```
  5. Section 1.1 has a dollar/yields regime token (SCARED/GREEDY/GOLDILOCKS/NEUTRAL)
```

(and renumber the subsequent docstring lines 5→6, 6→7).

- [ ] **Step 4: Update the 2026-04-06 sample briefing**

In `examples/sample-journal/daily/2026-04-06/premarket.md`, replace the `Market mood` line in section 1.1:

Find:
```
**Market mood:** **RISK-ON** — earnings tailwind plus easing yields; semis leading, breadth supportive pre-open.
```
Replace with:
```
**Market mood:** **RISK-ON** — earnings tailwind plus easing yields; semis leading, breadth supportive pre-open.
**Dollar/Yields regime:** **GOLDILOCKS** — DXY ↓ (prior close 103.20 → 102.85) + US10Y ↓ (4.18% → 4.12%). Softer dollar with easing yields is a disinflation tailwind, not fear; risk-on is confirmed.
→ Inverse is OFF: the falling dollar isn't the driver today — trade the semi leadership on its own merits.
```

Then in the Global Market Spillover section, find:
```
**USD/JPY:** ~152.40 — stable; no carry-trade stress signals.
```
Replace with:
```
**USD/JPY:** ~152.40 — stable; no carry-trade stress signals.
**DXY:** ~102.85 — drifting lower overnight; dollar soft as yields ease.
**US10Y:** ~4.12% — down ~6 bp after the soft survey data.
```

- [ ] **Step 5: Update the 2026-04-08 sample briefing**

In `examples/sample-journal/daily/2026-04-08/premarket.md`, replace the `Market mood` line in section 1.1:

Find:
```
**Market mood:** **MIXED, leaning RISK-OFF until CPI clears** — positioning is cautious; expect a fast, two-sided open.
```
Replace with:
```
**Market mood:** **MIXED, leaning RISK-OFF until CPI clears** — positioning is cautious; expect a fast, two-sided open.
**Dollar/Yields regime:** **NEUTRAL** — DXY ↑ (prior close 104.05 → 104.20) + US10Y ↔ (4.34% → 4.35%). A tiny pre-CPI drift, both within noise; the cross-asset tape isn't confirming a regime.
→ Ignore DXY as a QQQ tell today — trade the CPI reaction and levels, not the dollar.
```

Then in the Global Market Spillover section, find:
```
**USD/JPY:** ~152.90 — slightly firmer; nothing disorderly.
```
Replace with:
```
**USD/JPY:** ~152.90 — slightly firmer; nothing disorderly.
**DXY:** ~104.20 — marginally firmer into CPI; nothing disorderly.
**US10Y:** ~4.35% — flat, coiled ahead of the 8:30 print.
```

- [ ] **Step 6: Run the full suite to verify green**

Run: `cd /Users/solid/Code/intraday-trade && python -m pytest -q`
Expected: all pass — the wired test passes, and both sample briefings now satisfy `check_regime_read` (7/7 each).

- [ ] **Step 7: Commit**

```bash
git add premarket-briefing-skill/evals/validators/validate_briefing.py tests/test_premarket_validator.py examples/sample-journal/daily/2026-04-06/premarket.md examples/sample-journal/daily/2026-04-08/premarket.md
git commit -m "feat: enforce regime read in validator and conform sample briefings"
```

---

## Task 4: SKILL.md — fetch, output template, spillover, reference link

**Files:**
- Modify: `premarket-briefing-skill/SKILL.md`

Documentation change (no test); covered by the validator + evals at runtime.

- [ ] **Step 1: Add the DXY/US10Y fetch to Step 3b**

In the Step 3b bullet list ("For the structured-data sections, run the dedicated sources..."), add a bullet:

```
- **Dollar & yields regime read** — fetch **DXY** and **US10Y** as evidenced *prior-close → now* pairs (direction vs the prior US cash-session close, 16:00 ET). Direction is what the read needs; an exact level is optional. See `references/macro-regime-read.md`. Feeds the 1.1 regime line and the Global Spillover tape.
```

- [ ] **Step 2: Upgrade the 1.1 output template**

In the Output template, section 1.1, find:
```
**Market mood:** **RISK-ON** / **RISK-OFF** — [one sentence why]
```
Replace with:
```
**Market mood:** **RISK-ON** / **RISK-OFF** — [one sentence why]
**Dollar/Yields regime:** **SCARED** / **GREEDY** / **GOLDILOCKS** / **NEUTRAL** — [one-clause rationale] ([DXY arrow + prior-close → now] + [US10Y arrow + prior-close → now])
→ [Alignment line. If mood and regime disagree, lead with **⚠️ MOOD/REGIME SPLIT** and fade/size-down guidance. If they agree, state the aligned posture — and in GREEDY/GOLDILOCKS fire the "don't short QQQ off a strong dollar" caveat. See references/macro-regime-read.md.]
```

- [ ] **Step 3: Add DXY/US10Y tape lines to the Global Spillover template**

In the Output template, Global Market Spillover, find:
```
**USD/JPY:** [level] — [one sentence on yen carry-trade unwind risk if JPY strengthening sharply, else "stable, no carry-trade concern"]
```
Replace with:
```
**USD/JPY:** [level] — [one sentence on yen carry-trade unwind risk if JPY strengthening sharply, else "stable, no carry-trade concern"]
**DXY:** [level] — [direction vs prior US close, one sentence]
**US10Y:** [level/%] — [direction vs prior US close, one sentence]
```

- [ ] **Step 4: Point Step 4 (Fill the template) at the reference**

In Step 4, after the first sentence, add:
```
Classify the dollar/yields regime per `references/macro-regime-read.md` and write the regime + alignment lines into section 1.1.
```

- [ ] **Step 5: Verify internal consistency**

Re-read the edited SKILL.md sections. Confirm: the token set matches the reference file (SCARED/GREEDY/GOLDILOCKS/NEUTRAL), the evidenced-pair wording matches, and the `→` alignment behavior matches the divergence matrix.

- [ ] **Step 6: Commit**

```bash
git add premarket-briefing-skill/SKILL.md
git commit -m "feat: wire dollar/yields regime read into briefing SKILL.md template"
```

---

## Task 5: Eval rubric line

**Files:**
- Modify: `premarket-briefing-skill/evals/evals.json`

- [ ] **Step 1: Add the regime assertion to eval id 1**

In `evals.json`, in the `assertions` array of eval `id: 1` ("explicit-trigger-phrase"), immediately after the RISK-ON/RISK-OFF assertion object, insert:

```json
        {
          "text": "Section 1.1 includes a Dollar/Yields regime classification — one of SCARED / GREEDY / GOLDILOCKS / NEUTRAL — with an evidenced prior-close → now direction for DXY and US10Y, and flags a MOOD/REGIME SPLIT when the regime contradicts the RISK-ON/OFF verdict.",
          "type": "qualitative"
        },
```

(Mind the trailing comma — the inserted object is followed by the existing 1.2 assertion object.)

- [ ] **Step 2: Validate JSON**

Run: `cd /Users/solid/Code/intraday-trade && python -c "import json; json.load(open('premarket-briefing-skill/evals/evals.json')); print('valid json')"`
Expected: `valid json`

- [ ] **Step 3: Commit**

```bash
git add premarket-briefing-skill/evals/evals.json
git commit -m "test: add regime-read assertion to premarket eval rubric"
```

---

## Task 6: Final verification

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
Expected: `7/7 checks passed. Overall: PASS` for each.

- [ ] **Step 3: Final leak-test + consistency read**

Re-read `macro-regime-read.md` and the SKILL.md edits once more for the leak test and token consistency. No real trades, no parameters, no course citations.

---

## Self-review (author checklist — completed)

- **Spec coverage:** reference file (Task 1), validator check #7 (Task 2+4), negative tests (Task 2+3), sample data (Task 3), SKILL.md fetch+template+spillover+link (Task 4), eval rubric (Task 5), CLAUDE.md artifact-format rule (already applied pre-plan). All spec sections map to a task.
- **Placeholder scan:** none — every code/markdown/JSON step shows literal content.
- **Type consistency:** `check_regime_read(sections)` signature and the `REGIME_TOKENS` list are identical across Tasks 2, 3, and the tests; `CheckResult("regime_read", ...)` name matches the wired-in assertion.
- **Commit-green:** check implemented before wiring; data updated in the wiring commit.
