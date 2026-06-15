"""LESSONS.md obeys the lessons-ledger spec: schema-versioned frontmatter
whose counters agree with the body, unique monotonically-assigned IDs, and
only the three legal statuses (transitions are user-gated in chat)."""

from journal_schema import SAMPLE_JOURNAL, parse_lessons

LEDGER = SAMPLE_JOURNAL / "LESSONS.md"
VALID_STATUSES = {"active", "internalized", "retired"}
VALID_CATEGORIES = {"Tech", "Psych", "Process"}

# The spec fixes the category sections and their order.
REQUIRED_SECTIONS = [
    "## Technical Lessons (Q1–Q9 axis)",
    "## Psychological Lessons (8 enemies)",
    "## Process & Discipline Lessons (Q1–Q9 axis)",
]


def test_frontmatter_schema_version():
    ledger = parse_lessons(LEDGER)
    assert ledger["frontmatter"].get("schema") == "lessons-ledger-v1"


def test_counters_match_body():
    ledger = parse_lessons(LEDGER)
    fm, lessons = ledger["frontmatter"], ledger["lessons"]
    by_status = {s: sum(1 for l in lessons if l["status"] == s) for s in VALID_STATUSES}
    assert int(fm["total_active"]) == by_status["active"]
    assert int(fm["total_internalized"]) == by_status["internalized"]
    assert int(fm["total_retired"]) == by_status["retired"]


def test_next_id_exceeds_all_assigned_ids():
    ledger = parse_lessons(LEDGER)
    ids = [l["id"] for l in ledger["lessons"]]
    assert ids, "ledger has no lessons"
    assert int(ledger["frontmatter"]["next_id"]) > max(ids)


def test_ids_unique_and_statuses_valid():
    ledger = parse_lessons(LEDGER)
    ids = [l["id"] for l in ledger["lessons"]]
    assert len(ids) == len(set(ids)), "duplicate lesson IDs"
    assert all(l["status"] in VALID_STATUSES for l in ledger["lessons"])
    assert all(l["category"] in VALID_CATEGORIES for l in ledger["lessons"])


def test_category_sections_present_in_spec_order():
    text = LEDGER.read_text()
    positions = [text.find(s) for s in REQUIRED_SECTIONS]
    assert all(p >= 0 for p in positions), (
        f"missing sections: {[s for s, p in zip(REQUIRED_SECTIONS, positions) if p < 0]}"
    )
    assert positions == sorted(positions), "category sections out of spec order"


def test_every_lesson_has_required_fields():
    text = LEDGER.read_text()
    for block_field in ("**Lesson:**", "**Origins:**", "**Reinforced:**"):
        count = text.count(block_field)
        n_lessons = len(parse_lessons(LEDGER)["lessons"])
        assert count == n_lessons, (
            f"{block_field} appears {count}x for {n_lessons} lessons"
        )
