# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A multi-skill Claude Skills repository for Solid's US-equities intraday-trading workflow. It ships **three production Claude skills** — `premarket-briefing-skill/`, `intraday-trade-mentor-skill/`, `weekly-trade-review-skill/` — that coordinate through a shared trade-journal data layer. Each skill's full behavior spec is its `SKILL.md`; start there when editing skill logic. The repo is public as a portfolio piece; see `README.md` for the visitor-facing overview.

There is no build step. The "code" is markdown (SKILL.md + `references/` + `templates/` + `evals/`) plus a Python validator test suite in `tests/`.

## The journal and framework live in a private repo

The real trade journal and the full-parameter methodology are **not in this repo**. Both live in the private repo `solidx86/intraday-trade-private`, split into `journal/` and `framework/`, and are mounted in via two gitignored symlinks on working machines: `data/trade-journal/` → `journal/` and `data/framework/` → `framework/`. Setup commands: `README.md` (*Public / private split*). Skill journal paths use `<repo-root>/data/trade-journal/...`; the mentor loads the full framework from `<repo-root>/data/framework/framework-full.md` when present and degrades gracefully when absent.

A fully **synthetic** sample of the journal layout lives in `examples/sample-journal/` — it is the showcase corpus and the validator-test target. Never put real trades, real psychology notes, or account figures anywhere in this repo; they belong in the private journal repo only.

## Architecture: three skills + one shared journal

The non-obvious "big picture" is the data contract over `data/trade-journal/`:

- **`premarket-briefing-skill/`** — forward-looking. Writes `daily/<US-date>/premarket.md`. Date is the **US trading day** computed from Malaysia local time (MYT→ET), not today's calendar date.
- **`intraday-trade-mentor-skill/`** — per-trade critique. Writes `daily/<trade-date>/TICKER_<L|S|NT>_<W|L|BE|SKIP>.md`, appends to `INDEX.md`, and (Phase 2, user-confirmed) writes `LESSONS.md`.
- **`weekly-trade-review-skill/`** — longitudinal, **read-only** against everything above. Writes `weekly/<YYYY>-W<ww>_weekly.md`.

Co-location in `daily/<date>/` is intentional: context (`premarket.md`) and execution (per-trade journals) live in one folder. Don't break that.

## Cross-skill ownership rules (the gotchas)

- **Theme-tag canon source-of-truth**: the mentor skill (the `Available tags` line in `intraday-trade-mentor-skill/templates/journal-entry.md`, documented in its SKILL.md). `weekly-trade-review-skill/references/tag-canon.md` is a **mirror** — edit upstream, then sync the mirror. `tests/test_tag_canon_mirror.py` fails CI on drift.
- **`LESSONS.md` is written only by `intraday-trade-mentor`**, and only after Solid confirms proposed lessons. Status transitions (`internalize L###`, `retire L###`) only happen when **Solid** types the command — never auto-graduate.
- **`weekly-trade-review` never writes to the journal or the ledger.** It may *propose* internalization candidates; it cannot transition them.

## Tests & CI

- `pytest -q` from the repo root (config in `pytest.ini`; needs only `pip install pytest`). The suite deterministically validates `examples/sample-journal/` and the weekly-review eval fixtures against the journal schema: filename grammar, required sections, grade bounds, INDEX↔file consistency, lessons-ledger counters, premarket structure (via the skill's own `validate_briefing.py`), tag-canon mirror sync.
- The suite holds all tracked outputs to the full schema with no exceptions — fix the data, don't add escape hatches.
- CI: `.github/workflows/ci.yml` runs the suite on every push. Keep the README badge green.
- Skill-level evals (`<skill>/evals/evals.json`) are separate — consumed by the external `skill-creator` runner; outputs land in gitignored `*-workspace/` dirs.

## Working in this repo

- **Editing a skill**: edit `SKILL.md` / `references/` / `templates/` directly — live via the `~/.claude/skills/` symlinks, no rebuild.
- **Session boundaries**: `git pull` at start, commit + push at end — in **both** repos (skills + private journal).
- **Trade-date discipline**: `daily/<date>/` is the trade date from the chart (journals) or the MYT→ET US trading date (premarket) — never today's calendar date. Anchor the date explicitly before writing.
- **Public-repo hygiene**: public files are **token-only** — no operative definitions, parameters, breakout tell-set, or course citations; all of that lives in the private framework supplement (`data/framework/framework-full.md`). Apply the **leak test**: text that lets a reader reconstruct a methodology rule (a parameter, a taxonomy, a pattern-entry rule, a course citation) belongs in the private supplement, not here; text that merely names an opaque token (P1/P2/P3) or narrates one trade is fine. Also: no real trades, no personal contact details.
- **Spec & plan artifact formats**: brainstorming **specs** are authored as a **standalone, self-contained HTML file** (inline CSS, no external assets) for browser review — not Markdown. Implementation **plans** are authored in **both Markdown and HTML**: the `.md` is the execution source of truth (implementation is driven from it), the `.html` is the review companion. Specs live in `docs/superpowers/specs/`; plans in `docs/superpowers/plans/`. Keep the two plan formats in sync when either changes.

## Where to look next

- `README.md` — visitor-facing overview, data provenance table, public/private split & first-time setup.
- `<skill>-skill/SKILL.md` — full behavior spec per skill.
- `<skill>-skill/references/` — runtime rule files (framework, checklist, ledger spec, rubric, data sources, trading-day logic).
- `docs/tasks.md` — public engineering backlog (follow-up improvements, process notes).
