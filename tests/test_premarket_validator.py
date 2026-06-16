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
