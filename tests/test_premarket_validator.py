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


def test_regime_read_detail_reports_declared_token_not_caveat():
    # The 1.1 body declares GREEDY, but the alignment line legitimately names
    # SCARED while teaching. The detail must report the DECLARED regime, not
    # the first token that happens to appear.
    sections = {
        SECTION_1_1: (
            "**Market mood:** **RISK-ON** — holding gains.\n\n"
            "**Dollar/Yields regime:** **GREEDY** — DXY up + US10Y up.\n\n"
            "→ DXY only short-tells QQQ in the **SCARED** regime, which is not today.\n"
        )
    }
    result = validate_briefing.check_regime_read(sections)
    assert result.passed
    assert "GREEDY" in result.detail
    assert "SCARED" not in result.detail


def test_run_all_checks_wires_in_regime_read():
    from journal_schema import journal_trees, premarket_files

    sample = next(
        f for tree in journal_trees() for f in premarket_files(tree)
    )
    results = validate_briefing.run_all_checks(sample)
    assert "regime_read" in {r.name for r in results}


# --- Tape lines (browser-sourced market tape) -----------------------------

TAPE_BODY = (
    "**Futures (implied open):** ES +0.4% · NQ +0.7% · Dow +0.2%\n\n"
    "**Volatility:** VIX 13.9 (−3.1%) · VXN 18.6 — **calm**\n\n"
    "**Sector tape:** Technology +1.3% lead · Staples −0.2% lag\n\n"
    "**Commodities:** WTI $68.4 · Gold $3,402 · NatGas $3.88\n\n"
    "**Market mood:** **RISK-ON** — semis leading.\n"
)

TAPE_CHECK_NAMES = ["futures_line", "volatility_line", "sector_tape_line", "commodities_line"]


def test_tape_lines_all_pass_when_present():
    results = validate_briefing.check_tape_lines({SECTION_1_1: TAPE_BODY})
    assert {r.name for r in results} == set(TAPE_CHECK_NAMES)
    assert all(r.passed for r in results), [r.detail for r in results if not r.passed]


@pytest.mark.parametrize(
    "label",
    ["**Futures (implied open):**", "**Volatility:**", "**Sector tape:**", "**Commodities:**"],
)
def test_each_tape_line_check_bites_when_its_line_is_missing(label):
    body = "\n".join(line for line in TAPE_BODY.splitlines() if label not in line)
    results = validate_briefing.check_tape_lines({SECTION_1_1: body})
    assert any(not r.passed for r in results), "removing a tape line should fail a check"


def test_tape_line_accepts_na_with_reason():
    # The N/A-+-reason form satisfies the check: the field showed up honestly.
    body = (
        "**Futures (implied open):** ES +0.4% · NQ +0.7% · Dow +0.2%\n\n"
        "**Volatility:** N/A — CNBC vol module didn't load this run\n\n"
        "**Sector tape:** Technology +1.3% lead · Staples −0.2% lag\n\n"
        "**Commodities:** WTI $68.4 · Gold $3,402 · NatGas $3.88\n"
    )
    results = validate_briefing.check_tape_lines({SECTION_1_1: body})
    assert all(r.passed for r in results), [r.detail for r in results if not r.passed]


def test_run_all_checks_wires_in_tape_lines():
    from journal_schema import journal_trees, premarket_files

    sample = next(
        f for tree in journal_trees() for f in premarket_files(tree)
    )
    results = validate_briefing.run_all_checks(sample)
    assert set(TAPE_CHECK_NAMES) <= {r.name for r in results}


# --- US Spillover Read (Global Spillover synthesis block) ------------------

SECTION_SPILLOVER = "## Global Market Spillover"

SPILLOVER_FIRED_BODY = (
    "**Nikkei 225**: +1.1% · **KOSPI**: +1.4% — chip-heavy, firm.\n"
    "**USD/JPY:** ~152.40 — stable.\n\n"
    "**→ US Spillover Read (what it means at the open):**\n"
    "- China beta: KOSPI +1.4% (chip-heavy) + Nikkei +1.1% — tailwind for US semis.\n"
    "- Yen carry: USD/JPY stable — no unwind threat to mega-cap tech.\n"
    "- **Net:** mild risk-on tailwind, led by chips — follow-through over fade.\n"
)

SPILLOVER_BENIGN_BODY = (
    "**Nikkei 225**: −0.4% · **KOSPI**: −0.6% — quiet, coiled.\n"
    "**USD/JPY:** ~152.90 — slightly firmer.\n\n"
    "**→ US Spillover Read (what it means at the open):**\n"
    "- Overnight tape benign — no material spillover into the US open.\n"
)


def test_spillover_read_passes_with_fired_block_and_net():
    result = validate_briefing.check_spillover_read({SECTION_SPILLOVER: SPILLOVER_FIRED_BODY})
    assert result.passed, result.detail


def test_spillover_read_passes_with_benign_fallback_without_net():
    result = validate_briefing.check_spillover_read({SECTION_SPILLOVER: SPILLOVER_BENIGN_BODY})
    assert result.passed, result.detail


def test_spillover_read_fails_when_block_absent():
    body = (
        "**Nikkei 225**: +1.1% · **KOSPI**: +1.4%\n"
        "**USD/JPY:** ~152.40 — stable.\n"
        "**Notable overnight catalysts:** none.\n"
    )
    result = validate_briefing.check_spillover_read({SECTION_SPILLOVER: body})
    assert not result.passed


def test_spillover_read_fails_when_fired_block_missing_net():
    body = (
        "**→ US Spillover Read (what it means at the open):**\n"
        "- China beta: HSI green — no drag on semis.\n"
        "- Yen carry: USD/JPY stable — no unwind threat.\n"
    )
    result = validate_briefing.check_spillover_read({SECTION_SPILLOVER: body})
    assert not result.passed


def test_spillover_read_scoped_to_global_spillover_only():
    # A spillover block in another section must not satisfy the check.
    sections = {
        SECTION_SPILLOVER: "**Nikkei 225**: +1.1% — no spillover read here.\n",
        "## Quick Summary": (
            "**→ US Spillover Read** **Net:** tailwind, but in the wrong section.\n"
        ),
    }
    result = validate_briefing.check_spillover_read(sections)
    assert not result.passed


def test_run_all_checks_wires_in_spillover_read():
    from journal_schema import journal_trees, premarket_files

    sample = next(
        f for tree in journal_trees() for f in premarket_files(tree)
    )
    results = validate_briefing.run_all_checks(sample)
    assert "spillover_read" in {r.name for r in results}
