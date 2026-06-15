"""INDEX.md is consistent with the per-trade files it indexes.

The mentor skill appends one INDEX row per journaled trade. Cross-checks:
every row resolves to a trade file, every trade file has a row, and the
date / direction / outcome / grade agree between the two."""

import pytest

from journal_schema import (
    GRADE_RE,
    canon_tags_from_mirror,
    header_field,
    journal_trees,
    parse_index,
    trade_files,
)

OUTCOME_WORD_TO_CODE = {"Win": "W", "Loss": "L", "BE": "BE", "Breakeven": "BE", "Skip": "SKIP"}

TREES = journal_trees()


def _tree_id(tree):
    return tree.parent.name if tree.name == "trade-journal" else tree.name


@pytest.mark.parametrize("tree", TREES, ids=_tree_id)
def test_no_malformed_rows(tree):
    malformed = [r for r in parse_index(tree) if "malformed" in r]
    assert not malformed, f"{tree}: malformed INDEX rows: {malformed}"


@pytest.mark.parametrize("tree", TREES, ids=_tree_id)
def test_every_index_row_resolves_to_a_trade_file(tree):
    for row in parse_index(tree):
        key = f"{_tree_id(tree)}:{row['date']}_{row['ticker']}"
        code = OUTCOME_WORD_TO_CODE.get(row["outcome"], row["outcome"])
        expected = tree / "daily" / row["date"] / f"{row['ticker']}_{row['dir']}_{code}.md"
        assert expected.exists(), f"{tree}: INDEX row {key} has no file at {expected}"

        text = expected.read_text()
        grade = header_field(text, "Process Grade")
        assert grade == row["grade"], (
            f"{key}: INDEX grade {row['grade']!r} != journal grade {grade!r}"
        )


@pytest.mark.parametrize("tree", TREES, ids=_tree_id)
def test_every_trade_file_has_an_index_row(tree):
    indexed = {(r["date"], r["ticker"]) for r in parse_index(tree) if "malformed" not in r}
    for f in trade_files(tree):
        key = (f.parent.name, f.name.split("_")[0])
        assert key in indexed, f"{tree}: {f.parent.name}/{f.name} has no INDEX row"


@pytest.mark.parametrize("tree", TREES, ids=_tree_id)
def test_index_grades_and_tags_valid(tree):
    canon = canon_tags_from_mirror()
    for row in parse_index(tree):
        if "malformed" in row:
            continue
        key = f"{_tree_id(tree)}:{row['date']}_{row['ticker']}"
        assert GRADE_RE.match(row["grade"]), f"{key}: bad grade {row['grade']!r}"
        unknown = set(row["tags"]) - canon
        assert not unknown, f"{key}: uncanonized INDEX tags {sorted(unknown)}"
