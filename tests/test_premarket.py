"""Premarket briefings pass the premarket-briefing skill's own structural
validator (7 sections in order, RISK verdict, impact-labeled calendar,
global-spillover indices) plus folder/date consistency."""

import importlib.util

import pytest

from journal_schema import REPO_ROOT, journal_trees, premarket_files

VALIDATOR_PATH = (
    REPO_ROOT / "premarket-briefing-skill" / "evals" / "validators" / "validate_briefing.py"
)

spec = importlib.util.spec_from_file_location("validate_briefing", VALIDATOR_PATH)
validate_briefing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_briefing)

ALL_PREMARKET = [f for tree in journal_trees() for f in premarket_files(tree)]


@pytest.mark.parametrize(
    "f", ALL_PREMARKET, ids=lambda f: f"{f.parent.name}/premarket.md"
)
def test_briefing_passes_structural_validator(f):
    results = validate_briefing.run_all_checks(f)
    failures = [r for r in results if not r.passed]
    assert not failures, f"{f}: " + "; ".join(f"{r.name}: {r.detail}" for r in failures)


@pytest.mark.parametrize(
    "f", ALL_PREMARKET, ids=lambda f: f"{f.parent.name}/premarket.md"
)
def test_briefing_date_matches_folder(f):
    head = "\n".join(f.read_text().splitlines()[:5])
    assert f.parent.name in head, (
        f"{f}: header date does not match folder {f.parent.name}"
    )
