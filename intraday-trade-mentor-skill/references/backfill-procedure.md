# LESSONS.md Backfill Procedure (one-shot at rollout)

This procedure runs **once**, when the lessons-ledger feature ships — it bootstraps `data/trade-journal/LESSONS.md` from the existing journaled trades so that the first new critique has real prior lessons to anchor against.

Per the approved plan: **auto-backfill, no chat review.** Solid can curate the ledger after the fact. Speed and minimal friction at rollout is the priority.

---

## When to run

- Once, the first time `intraday-trade-mentor` is invoked after the lessons-ledger feature ships.
- Detect by: `data/trade-journal/LESSONS.md` does not exist.
- If `data/trade-journal/LESSONS.md` already exists, the backfill has already run; skip and proceed normally.

This is **not** a recurring routine. Subsequent trades use the normal Phase 2 ledger-write flow defined in `SKILL.md`.

---

## Inputs

- Every per-trade journal file under `data/trade-journal/daily/*/[A-Z]*.md` (glob: any file inside any date subfolder whose name starts with an uppercase ticker letter — this excludes the `premarket.md` briefing files, which start lowercase).
- The lessons spec at `references/lessons-ledger-spec.md`.
- The Q1–Q9 axis from `references/checklist.md`.
- The reframe themes from `references/reframe-library.md` (the 8 enemies).

---

## Procedure

### Step 1 — Enumerate and sort chronologically

List every per-trade journal under `data/trade-journal/daily/*/[A-Z]*.md` (any file inside any date subfolder whose name starts with an uppercase ticker letter — excludes `premarket.md`). Skip `INDEX.md`, `LESSONS.md`, anything under `data/trade-journal/weekly/`, and any `premarket.md` file. Sort ascending by the parent date folder name (which encodes the trade date in `YYYY-MM-DD` form); tiebreak by filename alphabetically (so the order is deterministic across re-runs).

This ordering matters: dedup is based on "what's already in the ledger" — older trades' lessons must be allocated IDs first so newer trades can reinforce/slip them rather than duplicate them.

### Step 2 — Parse each entry

For each journal file, in chronological order, extract:

1. **`## What I Must Fix` bullets** — each bullet is a candidate lesson. Categorize as Tech / Process based on content:
   - Pattern / level / structure / R:R / SL placement / exit timing / market read → **Tech**.
   - Pre-trade routine / order of checks / catalyst reading / screenshot framing / playbook curation / trade-mgmt rules / journal hygiene → **Process**.
   - Self-talk / emotion / identity → **Psych** (rare from this section, more common in Reframe).

   Allocate a sub-tag from the Q1–Q9 axis (`references/lessons-ledger-spec.md` canon). When a bullet maps to a checklist row that the trade failed, use that row's sub-tag.

2. **`## Reframe` section** — each negative-self-talk → reframe pair is a candidate **Psych** lesson. Use the *reframe side* (the disciplined version) as the lesson text, since that's the anchor Solid wants to repeat. The negative side identifies the enemy (sub-tag).
   - Example: `"Seemed holding" → "Seemed" is the giveaway; holding looks like rejection wicks` → lesson: `"'Seemed holding' = wanting it long. Holding looks like rejection wicks + green closes."` sub-tag: `FOMO` or `hope` (whichever fits better — hope is closer).
   - Skip pairs where the negative is not actually self-talk Solid surfaced (i.e. if the journal's Reframe section appears to be inventing — there shouldn't be any of these, but if you spot one, skip it; do not propagate fabricated psych lessons).

3. **`## Reinforcement` section** (when present instead of Reframe) — this captures a *positive* discipline Solid demonstrated. Extract one positive **Psych** lesson per Reinforcement section: the "disciplined belief to lock in" sentence is the lesson. Sub-tag = the enemy this belief counters.
   - Example: `"A disciplined skip on a pattern outside my playbook is a Pass, not a miss"` → lesson text as-is, sub-tag: `overtrading` (the enemy a disciplined skip counters).

4. **`## What I Did Right` bullets** — most of these are trade-specific observations, not portable lessons. **Default: do not extract.** Exception: if a bullet states a clear portable rule that became a Reinforcement-style anchor (e.g. `"Trailed to a structural level (above PrML, broken-support-turned-resistance), not a fear level"`), extract it as a positive **Process** lesson under the appropriate Q-axis sub-tag (`Q8-exit` in this example).

5. **`## Today's Discipline Statement`** — this is *already* a sharpened lesson. If it's not already covered by an extracted "What I Must Fix" / Reinforcement lesson from the same trade, extract it as its own entry, categorized by content. (Often it overlaps; merge during dedup in Step 3.)

### Step 3 — Apply dedup as you walk

After parsing each trade, before appending to the in-memory ledger, check each candidate lesson against everything already added:

- Same sub-tag + substantially same rule → merge (bump `Reinforced` if the candidate came from a section signaling a HELD/positive context — Reinforcement, What I Did Right, or Discipline Statement on a clean trade — bump `Slips` if it came from "What I Must Fix" or a negative Reframe pair, since that signals a violation).
- Same sub-tag + different rule → new entry.
- Different sub-tag → new entry.

When in doubt, prefer NOT merging — duplicates can be cleaned up later, but merged-too-aggressively destroys origin-trade history.

For the **first** appearance of a lesson, `Reinforced` and `Slips` start at 0 — that trade is the *origin*, not a reinforcement or slip of itself. For *subsequent* appearances, increment the right counter.

### Step 4 — Write `data/trade-journal/LESSONS.md`

Use the schema in `lessons-ledger-spec.md`:

- Frontmatter: `schema: lessons-ledger-v1`, `next_id: <last_allocated + 1>`, `total_active: <count>`, `total_internalized: 0`, `total_retired: 0`, `last_updated: <today>`.
- Three category sections in the fixed order: Technical → Psychological → Process & Discipline.
- Within each section, lessons in ID order (oldest first).
- Each lesson includes `Origins:` listing every trade that surfaced or reinforced it (chronological).

### Step 5 — Confirm completion to Solid in chat

After writing, post a short message: `"Backfilled LESSONS.md from <N> existing journal entries → <M> unique lessons (<T> Tech, <P> Psych, <Pr> Process). Curate/edit anytime; mentor will use this on the next trade."`

Then proceed with the trade Solid actually came to discuss (the trigger for this run).

---

## Expected output volume

From 13 journaled trades (as of 2026-05-13), expect roughly **15–25 unique lessons after dedup**. The distribution will likely be:

- Tech: ~6–10 (pattern recognition, R:R, SL/target placement, level reading, structural exits)
- Psych: ~4–8 (FOMO, hope, ego_hold, self-worth) — fewer than tech because Reframe sections often share themes across trades
- Process: ~5–10 (sector-ETF order, catalyst reading, screenshot framing, trail-rule planning, playbook curation, concurrent-position discipline)

If the output is < 10 or > 40 unique lessons, something likely went wrong with dedup — review before writing the file.

---

## Anti-patterns

- **Do not fabricate lessons** to fill out a section. If a journal entry's "What I Must Fix" only has 2 bullets, only 2 candidate Tech/Process lessons come from it.
- **Do not auto-graduate lessons during backfill.** Everything starts as `active`. Solid graduates manually after rollout.
- **Do not skip the chronological order.** Doing trades in random order will explode the dedup logic and produce duplicate IDs.
- **Do not write to per-trade journal files during backfill.** The ledger is the only file created. Journal files are read-only during this procedure.
- **Do not run the backfill more than once.** If `LESSONS.md` exists, skip — even if it looks incomplete. Manual edits by Solid are sacred; never overwrite.
