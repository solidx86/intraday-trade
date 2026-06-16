#!/usr/bin/env python3
"""Structural validator for premarket-briefing output.

Checks a generated premarket.md file against the skill's structural contract:
  1. File non-empty
  2. Header has a YYYY-MM-DD date
  3. All 7 required section headings present in order
  4. Section 1.1 has a RISK-ON or RISK-OFF verdict
  5. Section 1.1 has a dollar/yields regime token (SCARED/GREEDY/GOLDILOCKS/NEUTRAL)
  6. Section 1.2 has impact labels OR the "Light calendar today" fallback
  7. Global Spillover lists all required Asia/Europe indices + USD/JPY

Exit code 0 if all pass, 1 otherwise.

Usage:
  python validate_briefing.py \
    --briefing data/trade-journal/daily/2026-05-15/premarket.md \
    [--json-out path/to/validation.json]
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

REQUIRED_SECTIONS = [
    "## 1.1 General Market News",
    "## 1.2 Economic Announcements Today",
    "## 1.3 Stock & Industry Catalysts",
    "## 1.4 Portfolio News",
    "## Quick Summary",
    "## Market News & Catalysts",
    "## Global Market Spillover",
]

REQUIRED_INDICES = ["Nikkei", "Hang Seng", "KOSPI", "Shanghai", "DAX", "FTSE", "STOXX", "USD/JPY"]

REGIME_TOKENS = ["SCARED", "GREEDY", "GOLDILOCKS", "NEUTRAL"]


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def split_sections(briefing_text: str) -> dict[str, str]:
    """Split briefing into sections keyed by their exact ## heading line."""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_body: list[str] = []
    for line in briefing_text.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_body)
            current_heading = line.strip()
            current_body = []
        else:
            current_body.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(current_body)
    return sections


def check_file_nonempty(briefing_path: Path) -> CheckResult:
    if not briefing_path.exists():
        return CheckResult("file_nonempty", False, f"File does not exist: {briefing_path}")
    size = briefing_path.stat().st_size
    if size < 500:
        return CheckResult("file_nonempty", False, f"File too small ({size} bytes, expected >=500)")
    return CheckResult("file_nonempty", True, f"{size} bytes")


def check_header_date(briefing_text: str) -> CheckResult:
    head = "\n".join(briefing_text.splitlines()[:10])
    m = re.search(r"# Pre-Market Briefing\s*[—-]\s*(\d{4}-\d{2}-\d{2})\s*\(US Session\)", head)
    if not m:
        return CheckResult(
            "header_date",
            False,
            "Header line `# Pre-Market Briefing — YYYY-MM-DD (US Session)` not found in first 10 lines",
        )
    return CheckResult("header_date", True, f"date={m.group(1)}")


def check_seven_sections(sections: dict[str, str], briefing_text: str) -> CheckResult:
    found_headings = [line.strip() for line in briefing_text.splitlines() if line.startswith("## ")]
    missing = [s for s in REQUIRED_SECTIONS if s not in sections]
    if missing:
        return CheckResult(
            "seven_sections",
            False,
            f"missing headings: {missing}",
        )
    indices = [found_headings.index(s) for s in REQUIRED_SECTIONS]
    if indices != sorted(indices):
        return CheckResult(
            "seven_sections",
            False,
            f"sections present but out of order. order found: {[found_headings[i] for i in sorted(indices)]}",
        )
    return CheckResult("seven_sections", True, "all 7 present in correct order")


def check_risk_verdict(sections: dict[str, str]) -> CheckResult:
    body = sections.get("## 1.1 General Market News", "")
    if "RISK-ON" in body or "RISK-OFF" in body:
        verdict = "RISK-ON" if "RISK-ON" in body else "RISK-OFF"
        return CheckResult("risk_verdict", True, f"verdict={verdict}")
    return CheckResult("risk_verdict", False, "no RISK-ON or RISK-OFF token in section 1.1")


def check_regime_read(sections: dict[str, str]) -> CheckResult:
    body = sections.get("## 1.1 General Market News", "")
    # Prefer the declared regime line so the detail reports the actual call,
    # not a token that the alignment line merely names while teaching
    # (e.g. "DXY only short-tells in the SCARED regime").
    declared = re.search(
        r"Dollar/Yields regime:\*\*\s*\**\s*(" + "|".join(REGIME_TOKENS) + r")\b",
        body,
    )
    if declared:
        return CheckResult("regime_read", True, f"regime={declared.group(1)}")
    found = [t for t in REGIME_TOKENS if t in body]
    if found:
        return CheckResult(
            "regime_read",
            True,
            f"regime token present ({found[0]}); no declared 'Dollar/Yields regime:' line",
        )
    return CheckResult(
        "regime_read",
        False,
        "no SCARED/GREEDY/GOLDILOCKS/NEUTRAL regime token in section 1.1",
    )


def check_econ_calendar(sections: dict[str, str]) -> CheckResult:
    body = sections.get("## 1.2 Economic Announcements Today", "")
    if "Light calendar today" in body:
        return CheckResult("econ_calendar_format", True, "uses Light-calendar fallback")
    if re.search(r"\b(HIGH|MED|LOW)\b", body):
        return CheckResult("econ_calendar_format", True, "has impact-labeled rows")
    return CheckResult(
        "econ_calendar_format",
        False,
        "section 1.2 has neither impact labels nor 'Light calendar today' fallback",
    )


def check_global_spillover(sections: dict[str, str]) -> CheckResult:
    body = sections.get("## Global Market Spillover", "")
    missing = [idx for idx in REQUIRED_INDICES if idx not in body]
    if missing:
        return CheckResult(
            "global_spillover_indices",
            False,
            f"missing indices/pairs: {missing}",
        )
    return CheckResult("global_spillover_indices", True, "all 8 required indices/pairs present")


def run_all_checks(briefing_path: Path) -> list[CheckResult]:
    nonempty = check_file_nonempty(briefing_path)
    if not nonempty.passed:
        return [nonempty]
    text = briefing_path.read_text()
    sections = split_sections(text)
    return [
        nonempty,
        check_header_date(text),
        check_seven_sections(sections, text),
        check_risk_verdict(sections),
        check_regime_read(sections),
        check_econ_calendar(sections),
        check_global_spillover(sections),
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--briefing", required=True, type=Path)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args()

    results = run_all_checks(args.briefing)
    all_passed = all(r.passed for r in results)

    print(f"\nValidator report — briefing: {args.briefing}")
    print("-" * 70)
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"  [{mark}] {r.name:30s} {r.detail}")
    print("-" * 70)
    passed = sum(1 for r in results if r.passed)
    print(f"  {passed}/{len(results)} checks passed.  Overall: {'PASS' if all_passed else 'FAIL'}")
    print()

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(
                {
                    "briefing": str(args.briefing),
                    "overall_passed": all_passed,
                    "passed_count": passed,
                    "total_count": len(results),
                    "checks": [asdict(r) for r in results],
                },
                indent=2,
            )
        )

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
