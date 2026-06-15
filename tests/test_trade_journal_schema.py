"""Per-trade journal files conform to the schema the mentor skill writes.

Full schema (all 12 sections) is enforced on examples/sample-journal/.
Fixture journals (weekly-review evals) predate the full template and are
checked against the core contract only: filename grammar, header fields,
date consistency, grade bounds, checklist table, canonical tags.
"""

import re

import pytest

from journal_schema import (
    GRADE_RE,
    SAMPLE_JOURNAL,
    TITLE_RE,
    TRADE_FILENAME_RE,
    canon_tags_from_mirror,
    header_field,
    journal_trees,
    normalize_direction,
    normalize_outcome,
    section_headings,
    trade_files,
    trade_tags,
)

# Sections the journal-entry template requires, in order.
FULL_SECTIONS = [
    "## Screenshots",
    "## Pre-Trade Inputs (collected before analysis)",
    "## Setup Read",
    "## Checklist Results",
    "## What I Did Right",
    "## What I Must Fix",
    "## Reflection (my own words)",
    "## Reframe",
    "## Today's Discipline Statement",
    "## Recurring Theme Tags",
    "## Lessons This Trade",
]

# The checklist table writes the Triad row plus the 9 graded points.
CHECKLIST_MIN_ROWS = 10

ALL_TRADE_FILES = [(tree, f) for tree in journal_trees() for f in trade_files(tree)]
SAMPLE_TRADE_FILES = [f for tree, f in ALL_TRADE_FILES if tree == SAMPLE_JOURNAL]

CANON = canon_tags_from_mirror()


def _param_id(pair):
    tree, f = pair
    return f"{tree.parent.name}/{f.parent.name}/{f.name}"


@pytest.mark.parametrize("pair", ALL_TRADE_FILES, ids=_param_id)
def test_filename_grammar(pair):
    _, f = pair
    assert TRADE_FILENAME_RE.match(f.name), (
        f"{f.name} does not match TICKER_<L|S|NT>_<W|L|BE|SKIP>.md"
    )


@pytest.mark.parametrize("pair", ALL_TRADE_FILES, ids=_param_id)
def test_title_date_matches_folder(pair):
    _, f = pair
    m = TITLE_RE.match(f.read_text().splitlines()[0])
    assert m, f"{f}: first line is not '# Trade Journal Entry — YYYY-MM-DD'"
    assert m.group(1) == f.parent.name, (
        f"{f}: title date {m.group(1)} != folder {f.parent.name}"
    )


@pytest.mark.parametrize("pair", ALL_TRADE_FILES, ids=_param_id)
def test_header_fields_consistent_with_filename(pair):
    _, f = pair
    text = f.read_text()
    fn_ticker, fn_dir, fn_outcome = TRADE_FILENAME_RE.match(f.name).groups()

    ticker = header_field(text, "Ticker")
    assert ticker and ticker.split()[0].split("(")[0] == fn_ticker, (
        f"{f}: header ticker {ticker!r} != filename ticker {fn_ticker}"
    )

    direction = header_field(text, "Direction")
    assert direction and normalize_direction(direction) == fn_dir, (
        f"{f}: header direction {direction!r} != filename code {fn_dir}"
    )

    outcome = header_field(text, "Outcome")
    assert outcome and normalize_outcome(outcome) == fn_outcome, (
        f"{f}: header outcome {outcome!r} != filename code {fn_outcome}"
    )


@pytest.mark.parametrize("pair", ALL_TRADE_FILES, ids=_param_id)
def test_grade_within_rubric_bounds(pair):
    _, f = pair
    grade = header_field(f.read_text(), "Process Grade")
    assert grade is not None, f"{f}: missing **Process Grade:** field"
    assert GRADE_RE.match(grade), f"{f}: grade {grade!r} not a rubric letter A–F (±)"


@pytest.mark.parametrize("pair", ALL_TRADE_FILES, ids=_param_id)
def test_checklist_table_present(pair):
    tree, f = pair
    text = f.read_text()
    assert "## Checklist Results" in text, f"{f}: missing checklist section"
    if tree == SAMPLE_JOURNAL:
        body = text.split("## Checklist Results", 1)[1]
        rows = [
            line for line in body.splitlines()
            if line.startswith("|") and "---" not in line and "Check" not in line
        ]
        assert len(rows) >= CHECKLIST_MIN_ROWS, (
            f"{f}: checklist has {len(rows)} rows, expected >= {CHECKLIST_MIN_ROWS}"
        )


@pytest.mark.parametrize("pair", ALL_TRADE_FILES, ids=_param_id)
def test_tags_are_canonical(pair):
    _, f = pair
    tags = trade_tags(f.read_text())
    assert tags, f"{f}: no theme tags found"
    unknown = set(tags) - CANON
    assert not unknown, f"{f}: uncanonized tags {sorted(unknown)}"


@pytest.mark.parametrize(
    "f", SAMPLE_TRADE_FILES, ids=lambda f: f"{f.parent.name}/{f.name}"
)
def test_sample_journal_has_full_sections_in_order(f):
    headings = section_headings(f.read_text())
    positions = []
    for section in FULL_SECTIONS:
        assert section in headings, f"{f}: missing section {section!r}"
        positions.append(headings.index(section))
    assert positions == sorted(positions), f"{f}: sections out of template order"


@pytest.mark.parametrize(
    "f", SAMPLE_TRADE_FILES, ids=lambda f: f"{f.parent.name}/{f.name}"
)
def test_sample_journal_reflection_is_answered(f):
    text = f.read_text()
    reflection = re.search(
        r"^## Reflection \(my own words\)\n(.*?)(?=^## )", text, re.MULTILINE | re.DOTALL
    )
    assert reflection, f"{f}: missing reflection section"
    answers = re.findall(r"^> (.+)$", reflection.group(1), re.MULTILINE)
    assert len(answers) >= 3, f"{f}: reflection has {len(answers)} answers, expected >= 3"
    assert not any("{{" in a for a in answers), f"{f}: unfilled template placeholder"
