"""Shared parsing helpers for the trade-journal schema validators.

The journal data contract is markdown, written by the intraday-trade-mentor
skill and read by the weekly-trade-review skill. These helpers parse the
tracked corpora (examples/sample-journal/ and the weekly-review eval fixtures)
into plain dicts so the tests can assert structural invariants
deterministically — no network, no LLM, stdlib only.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_JOURNAL = REPO_ROOT / "examples" / "sample-journal"
FIXTURE_ROOT = REPO_ROOT / "weekly-trade-review-skill" / "evals" / "fixtures"

TAG_CANON_MIRROR = REPO_ROOT / "weekly-trade-review-skill" / "references" / "tag-canon.md"
JOURNAL_TEMPLATE = REPO_ROOT / "intraday-trade-mentor-skill" / "templates" / "journal-entry.md"

TRADE_FILENAME_RE = re.compile(r"^([A-Z]{1,6})_(L|S|NT)_(W|L|BE|SKIP)\.md$")
GRADE_RE = re.compile(r"^[ABCDF][+\-−–]?$")  # ASCII or Unicode minus/dash
TITLE_RE = re.compile(r"^# Trade Journal Entry — (\d{4}-\d{2}-\d{2})")
LESSON_HEADING_RE = re.compile(
    r"^### L(\d{3}) · \[([^\]]+)\]\[([^\]]+)\] · (active|internalized|retired)$"
)
WEEKLY_FILENAME_RE = re.compile(r"^(\d{4}-W\d{2})_weekly\.md$")

DIRECTION_CODES = {
    "L": "L", "LONG": "L", "Long": "L",
    "S": "S", "SHORT": "S", "Short": "S",
    "NT": "NT", "NO TRADE": "NT", "No Trade": "NT", "NO-TRADE": "NT",
}
OUTCOME_CODES = {
    "Win": "W", "Loss": "L", "Breakeven": "BE", "BE": "BE",
    "Skip": "SKIP", "Still Open": "OPEN",
}


def journal_trees() -> list[Path]:
    """Every journal-shaped tree in the repo: the sample plus each fixture."""
    trees = [SAMPLE_JOURNAL]
    trees.extend(sorted(p / "trade-journal" for p in FIXTURE_ROOT.iterdir() if p.is_dir()))
    return [t for t in trees if t.exists()]


def trade_files(tree: Path) -> list[Path]:
    daily = tree / "daily"
    if not daily.exists():
        return []
    return sorted(
        f for f in daily.glob("*/*.md") if f.name != "premarket.md"
    )


def premarket_files(tree: Path) -> list[Path]:
    daily = tree / "daily"
    return sorted(daily.glob("*/premarket.md")) if daily.exists() else []


def weekly_files(tree: Path) -> list[Path]:
    weekly = tree / "weekly"
    return sorted(weekly.glob("*.md")) if weekly.exists() else []


def header_field(text: str, name: str) -> str | None:
    m = re.search(rf"^\*\*{re.escape(name)}:\*\*\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else None


def normalize_direction(raw: str) -> str | None:
    word = raw.split("(")[0].strip()
    return DIRECTION_CODES.get(word) or DIRECTION_CODES.get(word.upper())


def normalize_outcome(raw: str) -> str | None:
    word = raw.split("(")[0].strip()
    return OUTCOME_CODES.get(word)


def trade_tags(text: str) -> list[str]:
    m = re.search(r"^## Recurring Theme Tags\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    return re.findall(r"`([^`\s]+)`", m.group(1))


def section_headings(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.startswith("## ")]


def canon_tags_from_mirror() -> set[str]:
    tags = set()
    for line in TAG_CANON_MIRROR.read_text().splitlines():
        m = re.match(r"^\| `([^`]+)` \|", line)
        if m:
            tags.add(m.group(1))
    return tags


def canon_tags_from_template() -> set[str]:
    text = JOURNAL_TEMPLATE.read_text()
    m = re.search(r"^Available tags: (.+)$", text, re.MULTILINE)
    if not m:
        return set()
    return {t.strip() for t in m.group(1).split(",")}


def parse_index(tree: Path) -> list[dict]:
    """Parse INDEX.md table rows into dicts."""
    index = tree / "INDEX.md"
    rows = []
    for line in index.read_text().splitlines():
        if not line.startswith("|") or line.startswith("|--") or line.startswith("| Date"):
            continue
        if set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 7:
            rows.append({"malformed": line})
            continue
        rows.append({
            "date": cells[0], "ticker": cells[1], "dir": cells[2],
            "outcome": cells[3], "grade": cells[4], "setup": cells[5],
            "tags": [t.strip() for t in cells[6].split(",") if t.strip()],
        })
    return rows


def parse_lessons(path: Path) -> dict:
    """Parse LESSONS.md frontmatter + lesson headings."""
    text = path.read_text()
    fm: dict[str, str] = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
    lessons = []
    for line in text.splitlines():
        lm = LESSON_HEADING_RE.match(line.strip())
        if lm:
            lessons.append({
                "id": int(lm.group(1)),
                "category": lm.group(2),
                "subtag": lm.group(3),
                "status": lm.group(4),
            })
    return {"frontmatter": fm, "lessons": lessons, "text": text}
