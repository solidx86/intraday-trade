# Lessons Ledger — Schema, Canon, and Update Rules

This is the canonical spec for `data/trade-journal/LESSONS.md` — the rolling lessons ledger Solid's mentor maintains across trades. Both the `intraday-trade-mentor` skill (writer + reader) and the `weekly-trade-review` skill (reader-only of the ledger, writer of its weekly stats) load this file.

The ledger answers one question per future trade: *did Solid exercise what he's already learned, or forget it?*

---

## Where it lives

- **Path:** `<repo-root>/data/trade-journal/LESSONS.md`
- **Owner:** the `intraday-trade-mentor` skill writes and edits it. The `weekly-trade-review` skill reads it and reports stats but does not edit lessons (it can only flag candidates for Solid to manually mark internalized).
- **Source of truth:** this file is the durable layer above the per-trade "Today's Discipline Statement." Discipline statements still live in each journal entry; the ledger is what compounds.

---

## File schema (lessons-ledger-v1)

```markdown
---
schema: lessons-ledger-v1
next_id: 24
total_active: 21
total_internalized: 2
total_retired: 0
last_updated: 2026-05-14
---

# Lessons Ledger

> Every lesson Solid has surfaced from his journaled trades. The mentor reads this before
> every new critique. HELD lessons get cited in "What You Did Right." FORGOT lessons get
> quoted in "What You Must Fix." Status changes only when Solid says so.

## Technical Lessons (Q1–Q9 axis)

### L007 · [Tech][Q2-pattern] · active
**Lesson:** HL needs flush → rally → pullback that holds above the prior low. A flat base on a level is not a HL.
**Origins:** 2026-05-11 CRM
**Reinforced:** 1 · **Slips:** 0
**Last reinforced:** 2026-05-11 · **Last violated:** —

## Psychological Lessons (8 enemies)

### L014 · [Psych][FOMO] · active
**Lesson:** "Seemed holding" is the giveaway — that's wanting it long, not seeing it hold. Holding looks like rejection wicks + green closes above.
**Origins:** 2026-05-11 CRM
**Reinforced:** 0 · **Slips:** 1
**Last reinforced:** — · **Last violated:** 2026-05-11

## Process & Discipline Lessons (Q1–Q9 axis)

### L020 · [Process][Q8-exit] · internalized
**Lesson:** Trail rule must be pre-written, not "tentatively." Write it explicitly before entry.
**Origins:** 2026-05-13 IWM
**Reinforced:** 4 · **Slips:** 0
**Status changed:** 2026-06-01 (Solid marked internalized)
**Last reinforced:** 2026-05-30 · **Last violated:** —
```

### Frontmatter fields

| Field | Type | Notes |
|---|---|---|
| `schema` | string | Always `lessons-ledger-v1` for now. Bump if the schema changes. |
| `next_id` | int | The next `L###` ID to allocate. Increments only when a NEW lesson is added (not on reinforce/slip of an existing one). |
| `total_active` | int | Count of lessons with `status: active`. Updated on every write. |
| `total_internalized` | int | Count of lessons Solid has marked internalized. |
| `total_retired` | int | Count of lessons Solid has explicitly retired (no longer relevant). |
| `last_updated` | date | YYYY-MM-DD of the last write. |

### Per-lesson fields

Each lesson is a `### L###` heading followed by labeled lines:

| Field | Required | Notes |
|---|---|---|
| `### L### · [Category][sub-tag] · status` | yes | Heading. ID is `L` + 3-digit zero-padded sequence. Category is one of `Tech` / `Psych` / `Process`. Sub-tag from the canon below. Status defaults to `active`. |
| `**Lesson:**` | yes | One sentence. Imperative or declarative, portable, quotable. No filler. |
| `**Origins:**` | yes | Comma-separated list of `YYYY-MM-DD TICKER` references — every trade that surfaced or reinforced this lesson. |
| `**Reinforced:**` | yes | Integer count. Incremented when a future trade HONORS this lesson. |
| `**Slips:**` | yes | Integer count. Incremented when a future trade VIOLATES this lesson. |
| `**Last reinforced:**` | yes | Date of the most recent HELD verdict, or `—` if never. |
| `**Last violated:**` | yes | Date of the most recent FORGOT verdict, or `—` if never. |
| `**Status changed:**` | only when status ≠ active | Date + reason: `2026-06-01 (Solid marked internalized)` or `2026-07-15 (Solid retired)`. |

### Sections (in this fixed order)

1. `## Technical Lessons (Q1–Q9 axis)`
2. `## Psychological Lessons (8 enemies)`
3. `## Process & Discipline Lessons (Q1–Q9 axis)`

A section may be empty (heading only) if no lessons of that category exist yet. Within a section, lessons are listed in ID order (oldest first). Internalized and retired lessons stay in their category section — they don't move to a separate area, but their `· status` token makes them scannable.

---

## Sub-tag canon

Every lesson carries exactly one sub-tag, drawn from the category's canon. If two sub-tags seem to apply, pick the dominant one (the one whose checklist row failed most clearly, or the enemy most evident in self-talk).

### Technical & Process — Q1–Q9 axis

Both categories share this vocabulary (intentional — keeps cross-category filtering trivial).

| Sub-tag | checklist row it maps to |
|---|---|
| `Q1-trend` | Q1 Trend (daily direction) |
| `Q2-pattern` | Q2 Pattern (P1/P2/P3 + variants, Trend Continuation, etc.) |
| `Q3-RR` | Q3 Reward/Risk ≥ 2 |
| `Q4-sentiment` | Q4 Market sentiment alignment (QQQ/SPY/VIX) |
| `Q5-RS` | Q5 Relative strength (vs sector ETF + broad index) |
| `Q6-entry` | Q6 Entry execution (timing, location, confirmation) |
| `Q7-SL` | Q7 Stop loss placement |
| `Q8-exit` | Q8 Exit / profit-taking discipline (invalidation vs fear) |
| `Q9-timing` | Q9 Timing rule (first 2 hours, no past 12am MY) |

**Distinguishing Tech vs Process when the sub-tag is the same:**
- **Tech** lessons are about *reading the market correctly* — "HL needs flush→rally→pullback", "a wick into a level isn't a hold", "R:R requires both legs visible on the chart."
- **Process** lessons are about *the routine and discipline that surrounds the trade* — "sector ETF check before broad index", "read the actual catalyst", "trail rule pre-written, not tentative", "frame SL and target both visible on the screenshot."

When in doubt: if the lesson is "the rule for what counts as X", it's Tech. If the lesson is "the step in my routine that produces X", it's Process.

**Composite rules** (a single lesson that spans multiple sub-tags by design — e.g., the Trade Quality Triad which covers catalyst + RS + named pattern simultaneously) live as **one ledger entry under the dominant sub-tag**, not as three sibling entries. Keeps per-trade citations clean (one ID, one quote) and keeps slip/reinforce counters meaningful — splitting would dilute the signal across siblings that always co-vary.

### Psychological — 8 enemies

| Sub-tag | What it covers |
|---|---|
| `FOMO` | Fear of missing the move; chasing breakout candles; "I had to be in this." |
| `revenge` | Re-entering after a loss to "get it back" rather than on a fresh setup. |
| `ego_hold` | Holding past stop or past invalidation because being right matters more than the rule. |
| `hope` | "Seemed holding," "should reverse soon," widening stops, waiting for the bounce. |
| `fear` | Cutting on volatility/wick alone with no structural break; early exits driven by anxiety not signal. |
| `greed` | Holding past target for "just a little more"; widening targets after hitting them. |
| `self-worth` | P&L treated as identity; one bad trade = "I'm terrible"; one good trade = "I'm a pro." |
| `overtrading` | Trading because the screens are open, not because a setup is present. |

A lesson can be a *positive* psych anchor (locked-in discipline, not a distortion to reframe) — it still uses the same sub-tag canon. The text makes it clear (`"A disciplined skip is a Pass, not a miss"` is tagged `overtrading` because that's the enemy it counters).

---

## Status lifecycle

Three values: `active` (default) | `internalized` | `retired`.

**State machine:**
- New lessons start as `active`.
- Only Solid transitions a lesson — the mentor never auto-graduates.
- Trigger phrases: `"mark L007 internalized"`, `"internalize L007"`, `"retire L011"`, `"un-retire L011"`, `"reactivate L007"`. Mentor edits the entry and updates frontmatter counters, then confirms.
- A `retired` or `internalized` lesson can be reactivated back to `active` if it slips again — that's a regression and worth surfacing.

**How status changes affect citation:**
- `active` — fully cited in critiques (HELD into "What You Did Right", FORGOT into "What You Must Fix").
- `internalized` — silently held in context but **not cited in "What You Did Right"** under normal circumstances (Solid has graduated past needing the reminder). **Exception:** if an internalized lesson is violated on a trade, it MUST be cited in "What You Must Fix" with explicit regression language ("You slipped L020 *after* you internalized it. That's a regression — flipping back to active.") and its status flips back to `active`.
- `retired` — not loaded into critique context at all. Solid has decided this rule no longer applies to how he trades. Skipped silently.

---

## Update rules at ledger write

When the mentor writes lessons (typically in Phase 2 after Solid says `accept`), apply this logic per proposed lesson:

### 1. Detect existing match

Look for an existing lesson where BOTH:
- The sub-tag matches exactly, AND
- The proposed lesson's substance is the same rule (mentor judgment — conservative: only merge if it's substantially the same lesson, not just adjacent).

Examples:
- Proposed "Check sector ETF before broad index" + existing L011 "Sector ETF before broad index — sector tells the truth for a single name" → **merge** (same rule, different wording).
- Proposed "Read the actual catalyst from the release" + existing L011 → **do not merge** (Q5-RS vs Q4-sentiment, different rule even though both are pre-trade discipline).
- Proposed "Trail rule pre-written" + existing L020 "Trail rule pre-written, not tentative" → **merge**.

When in doubt, do NOT merge — duplicates are easier to clean up later than incorrectly-merged lessons that lose origin trade data.

### 2. If match found → update existing entry

- If this lesson is being **reinforced** (it shows up because Solid HONORED a past lesson on this trade):
  - Bump `Reinforced` counter by 1.
  - Append this trade to `Origins` if not already there.
  - Update `Last reinforced` to this trade's date.
- If this lesson is being **slipped** (it shows up because Solid VIOLATED a past lesson, OR a new "What You Must Fix" bullet restates the same rule):
  - Bump `Slips` counter by 1.
  - Append this trade to `Origins` if not already there.
  - Update `Last violated` to this trade's date.
  - If status was `internalized`, flip back to `active` and add a `Status changed:` line: `YYYY-MM-DD (regressed — slipped after internalization)`. Update frontmatter counters.

### 3. If no match → allocate new lesson

- Take the current `next_id` from frontmatter.
- Append a new `### L###` entry under the appropriate category section.
- Set `Reinforced: 0`, `Slips: 0`, `Last reinforced: —`, `Last violated: —` (for a brand-new lesson surfaced from "What You Must Fix" this trade — it's not reinforced yet, just born).
- Set `Origins:` to this trade.
- Increment `next_id` in frontmatter.
- Increment `total_active`.

### 4. Always update frontmatter

`last_updated` to today. Counter totals recomputed if any status changed or new lesson added.

---

## Reading the ledger (for the mentor)

When critiquing a new trade, the mentor:

1. **Loads the entire ledger** at the start of the critique. Active + internalized lessons are in working context; retired lessons are skipped at load.
2. **In Phase 1**, after producing the Checklist + Overall Grade, scans the ledger for lessons whose substance is concretely relevant to this trade. Relevance is mentor judgment — not mechanical tag-match. The two valid surfacings are:
   - **HELD** → cite in "What You Did Right" with `L### (origin date): "verbatim lesson text"` + one-line evidence of how this trade honored it.
   - **FORGOT** → cite in "What You Must Fix" with the same format + one-line evidence of how this trade violated it.
3. **Constraint:** Only cite a lesson if there's *concrete evidence* this trade honored or violated it. Do not cite every relevant lesson on every trade — silence on a lesson is fine if neither HELD nor FORGOT is evidenced.
4. **Constraint:** Quote the lesson text verbatim from the ledger. No paraphrasing. The lesson's exact wording is the anchor.
5. **Constraint:** `internalized` lessons are silent on HELD (no citation), but loud on FORGOT (cited with regression language and flipped back to `active`).

---

## Reading the ledger (for the weekly review)

The weekly review reads `LESSONS.md` once and produces a "Lessons This Week" section with four sub-blocks (see `weekly-trade-review-skill/SKILL.md` for the full spec):

1. **Added this week** — lessons whose newest origin date is in the review week.
2. **Held all week** — lessons cited as HELD on every relevant trade in the week (and not slipped at all).
3. **Slipped this week** — lessons whose `Last violated` is in the review week (with slip count from the ledger).
4. **Candidates to mark internalized** — `active` lessons where `Reinforced ≥ 5` AND `Slips = 0` AND `Last violated` is `—` or ≥ 30 days before today. Solid still has the final call.

The weekly review never edits lesson entries — at most it suggests candidates. Solid types `"internalize L007"` himself.

---

## Anti-patterns (do not do these)

- **Do not invent lessons.** Every entry must be traceable to a real trade's "What You Must Fix" bullet, Reframe, or Reinforcement section.
- **Do not paraphrase the lesson when citing it in a critique.** Quote verbatim.
- **Do not auto-graduate lessons.** Status only changes by Solid's explicit instruction.
- **Do not cite a lesson on every trade just because it's loaded.** Silence is fine; only cite on concrete HELD or FORGOT evidence.
- **Do not write to the ledger silently on Phase 1.** Lesson writes happen in Phase 2 after Solid sees the proposed lessons and says `accept`.
- **Do not delete origin entries when status changes.** History is the point.
- **Do not allow two lessons with the same `L###` ID.** IDs are monotonic; `next_id` only ever increments.
