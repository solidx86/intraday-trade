"""Weekly reviews conform to the weekly-trade-review template: filename and
title agree on the ISO week, required sections present, and the prior-order
verdict is one of HELD / SLIPPED / N/A."""

import re

import pytest

from journal_schema import WEEKLY_FILENAME_RE, journal_trees, weekly_files

REQUIRED_SECTIONS = [
    "## Last Week's Order — Verdict",
    "## Stats (Process, not P&L)",
    "## Top Recurring Themes",
    "## Lessons This Week",
    "## Psychology Across the Week",
    "## Setup-Selection Review (head coach)",
    "## What's Working",
    "## Single Discipline Focus for Next Week",
    "## Specific Trades to Re-Read",
    "## Closing Word",
]

VERDICT_RE = re.compile(r"\*\*Verdict: (HELD|SLIPPED|N/A)\*\*")

ALL_WEEKLY = [f for tree in journal_trees() for f in weekly_files(tree)]


@pytest.mark.parametrize("f", ALL_WEEKLY, ids=lambda f: f.name)
def test_filename_and_title_week_agree(f):
    m = WEEKLY_FILENAME_RE.match(f.name)
    assert m, f"{f.name}: not YYYY-Www_weekly.md"
    first_line = f.read_text().splitlines()[0]
    assert m.group(1) in first_line, (
        f"{f.name}: title {first_line!r} does not carry week {m.group(1)}"
    )


@pytest.mark.parametrize("f", ALL_WEEKLY, ids=lambda f: f.name)
def test_required_sections_present(f):
    text = f.read_text()
    missing = [s for s in REQUIRED_SECTIONS if s not in text]
    assert not missing, f"{f.name}: missing sections {missing}"


@pytest.mark.parametrize("f", ALL_WEEKLY, ids=lambda f: f.name)
def test_verdict_token_present(f):
    assert VERDICT_RE.search(f.read_text()), (
        f"{f.name}: no '**Verdict: HELD|SLIPPED|N/A**' token"
    )
