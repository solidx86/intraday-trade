"""Cross-skill drift check: the weekly-review skill's tag-canon mirror must
stay in lockstep with the mentor skill's canon (the journal-entry template's
"Available tags" line). The mentor owns the canon; the mirror exists so the
weekly review can interpret tags without the mentor installed. Drift between
them silently degrades weekly aggregation — this test makes drift loud."""

from journal_schema import canon_tags_from_mirror, canon_tags_from_template


def test_mirror_matches_upstream_canon():
    mirror = canon_tags_from_mirror()
    template = canon_tags_from_template()

    assert mirror and template, "failed to parse one of the canon sources"

    missing_in_mirror = template - mirror
    extra_in_mirror = mirror - template
    assert not missing_in_mirror and not extra_in_mirror, (
        f"tag canon drift — missing in mirror: {sorted(missing_in_mirror)}, "
        f"extra in mirror: {sorted(extra_in_mirror)}"
    )
