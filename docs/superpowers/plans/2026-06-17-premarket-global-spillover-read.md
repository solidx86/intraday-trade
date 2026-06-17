# US Spillover Read Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a sector-level **→ US Spillover Read** synthesis block to the premarket briefing's Global Market Spillover section, and wire CNBC `asia-markets/` + `europe-markets/` in as browser sources so KOSPI (and other tape-missed indices) stop coming back `N/A`.

**Architecture:** Additive, not a redesign. The per-index data lines stay; a new closing block translates the overnight Asia/Europe tape into a US-open read across four transmission channels (China beta · yen carry · Europe→US · oil/rates) plus a `Net:` tilt line, gated to material moves and collapsing to one benign line on a quiet tape. A new reference file (`global-spillover-read.md`, sibling to `macro-regime-read.md`) holds the channel framework. The block is schema-enforced by a new validator check and exercised by both sample fixtures (one fired, one benign).

**Tech Stack:** Markdown skill specs + Python validator (`validate_briefing.py`) + pytest. No build step. Browser sourcing via Playwright MCP (`browser_navigate` → grep the saved snapshot).

**Spec:** `docs/superpowers/specs/2026-06-17-premarket-global-spillover-read-design.html`

**Conventions for every commit in this plan:**
- Commit with the repo git identity (`Shoo Kyuk Wei <1960463+solidx86@users.noreply.github.com>`).
- End each commit message with a blank line then `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Public-repo hygiene: the channel taxonomy is textbook macro spillover — no P1/P2/P3, no parameters, no tell-set, no course citation. Keep it that way.

---

## File structure

| File | Responsibility | Change |
|------|----------------|--------|
| `premarket-briefing-skill/references/global-spillover-read.md` | The transmission-channel framework + gating | **Create** |
| `premarket-briefing-skill/references/data-sources.md` | Source map | Modify — add the two CNBC regional pages + spillover-read pointers |
| `premarket-briefing-skill/SKILL.md` | Behavior spec + output template | Modify — add the block to the template; point Step 3c at the new pages + reference |
| `premarket-briefing-skill/evals/validators/validate_briefing.py` | Structural validator | Modify — add `check_spillover_read`, wire it, docstring item 9 |
| `tests/test_premarket_validator.py` | Validator bite tests | Modify — add spillover-read bite tests |
| `examples/sample-journal/daily/2026-04-06/premarket.md` | Sample corpus (fired path) | Modify — add a fired-channel block |
| `examples/sample-journal/daily/2026-04-08/premarket.md` | Sample corpus (benign path) | Modify — add the benign-fallback line |
| `premarket-briefing-skill/evals/evals.json` | Skill eval rubric | Modify — add one criterion |

---

## Task 1: Track the spec + plan docs

**Files:**
- Commit: `docs/superpowers/specs/2026-06-17-premarket-global-spillover-read-design.html`
- Commit: `docs/superpowers/plans/2026-06-17-premarket-global-spillover-read.md`
- Commit: `docs/superpowers/plans/2026-06-17-premarket-global-spillover-read.html`

- [ ] **Step 1: Confirm on the feature branch**

Run: `git branch --show-current`
Expected: `feat/premarket-global-spillover-read`

- [ ] **Step 2: Commit the design + plan artifacts**

```bash
git add docs/superpowers/specs/2026-06-17-premarket-global-spillover-read-design.html \
        docs/superpowers/plans/2026-06-17-premarket-global-spillover-read.md \
        docs/superpowers/plans/2026-06-17-premarket-global-spillover-read.html
git commit -m "docs: track 2026-06-17 global-spillover-read spec + plan

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: New reference — `global-spillover-read.md`

**Files:**
- Create: `premarket-briefing-skill/references/global-spillover-read.md`

- [ ] **Step 1: Create the reference file**

Write `premarket-briefing-skill/references/global-spillover-read.md` with exactly this content:

```markdown
# Global Spillover Read — Asia/Europe → US

Use this to turn the overnight Asia/Europe tape into a **US-open read**: which way
the spillover leans and which US *sectors* it touches. It is the synthesis layer of
the **Global Market Spillover** section — the per-index lines are the data, this is
the "so what for the US today."

It is **sector-level only**: name sectors, not watchlist tickers, and no 1.1
mood/regime cross-reference. It introduces **no new numbers** — any % it cites must
already be in the Step 3a Tape Table or the Asia/Europe grep.

## The transmission channels

Walk all of these each run; **write only the ones that fired** (see Gating).

| Channel | Source signal | US read-through (sectors) |
|---------|---------------|---------------------------|
| **China beta** | Hang Seng / Shanghai / KOSPI on demand · property · stimulus · tech-policy · trade | China-revenue semis, materials & miners, machinery/industrials, luxury & casino, autos/EV — direction follows the China tape |
| **Yen carry / risk unwind** | USD/JPY + Nikkei 225 — sharp JPY *strengthening* or a Nikkei dump | High-beta growth & mega-cap tech first; broad risk-off tilt. Quiet default: "no unwind threat" |
| **Europe → US sectors** | DAX / FTSE / STOXX + European sector tape + ECB/BOE — the freshest leg (Europe is mid-session as US pre-market trades) | European banks → US financials; autos/industrials → US industrials & autos; energy/defense → US peers |
| **Cross-asset (oil / rates)** | Overnight WTI/Brent + global yield tape | Energy & transports (oil); rate-sensitives (yields). **Keep light** — only the overnight angle, never a re-quote of the 1.1 commodities/regime lines |

Then a closing **Net** line — the single-line punchline: net **tailwind / headwind /
neutral** for the US open + the one most-affected sector.

## Gating — fire only on a material move

A channel earns a bullet only when its signal is **material**:

- a regional index ≈ **≥1%** on an identifiable driver, **or**
- **USD/JPY ≈ ≥1%** or near a known intervention zone, **or**
- a **named overnight catalyst** (central-bank decision, major data surprise, geopolitical), **or**
- a **notable sector divergence** within a region (e.g. European banks +1.5% while the index is flat).

Anything inside the noise of the prior close stays **silent** — don't manufacture
spillover from a quiet tape.

**Benign tape → one line.** When nothing clears the bar, the whole block collapses to:

> Overnight tape benign — no material spillover into the US open.

## Output shape

\```
**→ US Spillover Read (what it means at the open):**
- [Channel]: [overnight tape] — [sector effect on the US open].
- **Net:** [tailwind / headwind / neutral] — [most-affected sector].
\```

Keep each bullet to one line. The block is the closer of the Global Market Spillover
section, after *Notable overnight catalysts*.
```

> Note: the fenced `\```` above is the literal triple-backtick block to write into the file (unescape it). The reference's own example uses a fenced code block.

- [ ] **Step 2: Commit**

```bash
git add premarket-briefing-skill/references/global-spillover-read.md
git commit -m "feat(premarket): add global-spillover-read channel reference

Sector-level transmission channels (China beta, yen carry, Europe->US,
oil/rates) + material-move gating for the new US Spillover Read block.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Wire CNBC `asia-markets/` + `europe-markets/` into `data-sources.md`

**Files:**
- Modify: `premarket-briefing-skill/references/data-sources.md` (the "Global Spillover — Asia Indices" and "— Europe Indices" subsections, ~lines 168–187)

- [ ] **Step 1: Replace the Asia Indices subsection**

Find this block:

```markdown
### Global Spillover — Asia Indices

**Step 3a first:** the CNBC tape pull already carries Nikkei, Hang Seng, Shanghai (and ASX/STI). Route from the Tape Table; only run the searches below for an index the tape missed (e.g. KOSPI, which CNBC may not list) or to get the *theme* behind a move.

- `WebSearch "Nikkei 225 close [DATE]"`
- `WebSearch "Hang Seng close [DATE]"`
- `WebSearch "KOSPI close [DATE]"`
- `WebSearch "Shanghai Composite close [DATE]"`
- `browser_navigate https://www.investing.com/indices/major-indices` (fallback — spot levels; Cloudflare-blocks WebFetch)

**Themes to watch for:** BOJ policy moves, China stimulus/property/tech crackdown, Japan/US trade tensions, yen interventions.
```

Replace it with:

```markdown
### Global Spillover — Asia Indices

**Step 3a first:** the CNBC pre-markets tape carries Nikkei, Hang Seng, Shanghai (and ASX/STI). Route those from the Tape Table.

**KOSPI + gaps — CNBC `asia-markets/` (browser):** the pre-markets tape does **not** list KOSPI. Top up from `browser_navigate https://www.cnbc.com/markets/asia-markets/` — grep the saved snapshot for the index rows and read the per-region driver headlines (BOJ/yen, China property/stimulus/tech-policy). Same capture recipe as Step 3a: never `browser_snapshot` without a `filename`. This is the **primary** KOSPI source; the WebSearches below are the fallback.

- `WebSearch "KOSPI close [DATE]"`
- `WebSearch "Nikkei 225 close [DATE]"`
- `WebSearch "Hang Seng close [DATE]"`
- `WebSearch "Shanghai Composite close [DATE]"`
- `browser_navigate https://www.investing.com/indices/major-indices` (fallback — spot levels; Cloudflare-blocks WebFetch)

**Themes to watch for:** BOJ policy moves, China stimulus/property/tech crackdown, Japan/US trade tensions, yen interventions.

**Feeds the → US Spillover Read** China-beta and yen-carry channels — see `references/global-spillover-read.md`.
```

- [ ] **Step 2: Replace the Europe Indices subsection**

Find this block:

```markdown
### Global Spillover — Europe Indices

**Step 3a first:** the CNBC tape pull carries DAX, FTSE, CAC, and STOXX. Route from the Tape Table; use the searches below only for a missing index or the driving theme.

- `WebSearch "DAX FTSE KOSPI KLCI STOXX [DATE]"`
- `browser_navigate https://www.investing.com/indices/europe-indices` (Cloudflare-blocks WebFetch)

**Goal:** mid-session levels and the dominant theme — usually ECB/BOE policy, energy prices, or a major European earnings story.
```

Replace it with:

```markdown
### Global Spillover — Europe Indices

**Step 3a first:** the CNBC pre-markets tape carries DAX, FTSE, CAC, and STOXX. Route from the Tape Table.

**Themes + gaps — CNBC `europe-markets/` (browser):** `browser_navigate https://www.cnbc.com/markets/europe-markets/` — grep the saved snapshot for the index rows and the driver headlines (ECB/BOE, European banks, energy/defense). Same capture recipe as Step 3a. Use for a missing index or the driving theme.

- `WebSearch "DAX FTSE KOSPI KLCI STOXX [DATE]"`
- `browser_navigate https://www.investing.com/indices/europe-indices` (Cloudflare-blocks WebFetch)

**Goal:** mid-session levels and the dominant theme — usually ECB/BOE policy, energy prices, or a major European earnings story. **Feeds the → US Spillover Read** Europe→US channel — see `references/global-spillover-read.md`.
```

- [ ] **Step 3: Commit**

```bash
git add premarket-briefing-skill/references/data-sources.md
git commit -m "feat(premarket): source KOSPI + Asia/Europe themes from CNBC regional pages

Add cnbc.com/markets/asia-markets and /europe-markets (browser-primary)
behind the Step 3a tape; KOSPI now sourced here instead of N/A.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: SKILL.md — template block + Step 3c pointer

**Files:**
- Modify: `premarket-briefing-skill/SKILL.md` (Output template Global Spillover, ~line 305; Step 3c Global Spillover bullet, ~line 118)

- [ ] **Step 1: Add the block to the Output template**

In the `## Global Market Spillover` template, find:

```
**Notable overnight catalysts:** [Geopolitical events, central bank decisions, macro surprises from non-US markets. "None notable" is a fine answer.]

---

*Briefing complete. Trade the plan, not the screen.*
```

Replace it with:

```
**Notable overnight catalysts:** [Geopolitical events, central bank decisions, macro surprises from non-US markets. "None notable" is a fine answer.]

**→ US Spillover Read (what it means at the open):**
- [Channel]: [overnight tape] — [sector effect on the US open]. *(only channels that cleared the material-move bar)*
- **Net:** [tailwind / headwind / neutral overnight] — [single most-affected US sector].

(Sector-level only — no watchlist tickers, and no number that isn't already in the Tape Table or the Asia/Europe grep. If nothing overnight clears the material-move bar, replace the bullets with one line: *"Overnight tape benign — no material spillover into the US open."* The channel set and gating are in `references/global-spillover-read.md`.)

---

*Briefing complete. Trade the plan, not the screen.*
```

- [ ] **Step 2: Point Step 3c at the new pages + reference**

In Step 3c (the targeted-lookups bullet list), find:

```
- **Global Market Spillover** — the Asia/Europe index searches and USD/JPY.
```

Replace it with:

```
- **Global Market Spillover** — Asia/Europe indices and USD/JPY from the Step 3a tape, topped up from CNBC `asia-markets/` + `europe-markets/` (browser) for indices the tape misses (KOSPI especially) and the per-region themes. Then compose the **→ US Spillover Read** block per `references/global-spillover-read.md` — sector-level transmission channels, gated to material moves, collapsing to one benign line on a quiet tape.
```

- [ ] **Step 3: Commit**

```bash
git add premarket-briefing-skill/SKILL.md
git commit -m "feat(premarket): add US Spillover Read block to the briefing template

Closes Global Market Spillover with a sector-level synthesis block;
Step 3c routes the two CNBC regional pages + the new reference.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Validator — bite tests + `check_spillover_read` (unwired)

**Files:**
- Modify: `tests/test_premarket_validator.py` (append a new test block)
- Modify: `premarket-briefing-skill/evals/validators/validate_briefing.py` (add `check_spillover_read` after `check_global_spillover`, ~line 188)
- Test: `pytest tests/test_premarket_validator.py`

- [ ] **Step 1: Write the failing bite tests**

Append to the end of `tests/test_premarket_validator.py`:

```python
# --- US Spillover Read (Global Spillover synthesis block) ------------------

SECTION_SPILLOVER = "## Global Market Spillover"

SPILLOVER_FIRED_BODY = (
    "**Nikkei 225**: +1.1% · **KOSPI**: +1.4% — chip-heavy, firm.\n"
    "**USD/JPY:** ~152.40 — stable.\n\n"
    "**→ US Spillover Read (what it means at the open):**\n"
    "- China beta: KOSPI +1.4% (chip-heavy) + Nikkei +1.1% — tailwind for US semis.\n"
    "- Yen carry: USD/JPY stable — no unwind threat to mega-cap tech.\n"
    "- **Net:** mild risk-on tailwind, led by chips — follow-through over fade.\n"
)

SPILLOVER_BENIGN_BODY = (
    "**Nikkei 225**: −0.4% · **KOSPI**: −0.6% — quiet, coiled.\n"
    "**USD/JPY:** ~152.90 — slightly firmer.\n\n"
    "**→ US Spillover Read (what it means at the open):**\n"
    "- Overnight tape benign — no material spillover into the US open.\n"
)


def test_spillover_read_passes_with_fired_block_and_net():
    result = validate_briefing.check_spillover_read({SECTION_SPILLOVER: SPILLOVER_FIRED_BODY})
    assert result.passed, result.detail


def test_spillover_read_passes_with_benign_fallback_without_net():
    result = validate_briefing.check_spillover_read({SECTION_SPILLOVER: SPILLOVER_BENIGN_BODY})
    assert result.passed, result.detail


def test_spillover_read_fails_when_block_absent():
    body = (
        "**Nikkei 225**: +1.1% · **KOSPI**: +1.4%\n"
        "**USD/JPY:** ~152.40 — stable.\n"
        "**Notable overnight catalysts:** none.\n"
    )
    result = validate_briefing.check_spillover_read({SECTION_SPILLOVER: body})
    assert not result.passed


def test_spillover_read_fails_when_fired_block_missing_net():
    body = (
        "**→ US Spillover Read (what it means at the open):**\n"
        "- China beta: HSI green — no drag on semis.\n"
        "- Yen carry: USD/JPY stable — no unwind threat.\n"
    )
    result = validate_briefing.check_spillover_read({SECTION_SPILLOVER: body})
    assert not result.passed


def test_spillover_read_scoped_to_global_spillover_only():
    # A spillover block in another section must not satisfy the check.
    sections = {
        SECTION_SPILLOVER: "**Nikkei 225**: +1.1% — no spillover read here.\n",
        "## Quick Summary": (
            "**→ US Spillover Read** **Net:** tailwind, but in the wrong section.\n"
        ),
    }
    result = validate_briefing.check_spillover_read(sections)
    assert not result.passed
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_premarket_validator.py -k spillover_read -q`
Expected: FAIL — `AttributeError: module 'validate_briefing' has no attribute 'check_spillover_read'`

- [ ] **Step 3: Implement `check_spillover_read`**

In `premarket-briefing-skill/evals/validators/validate_briefing.py`, immediately after the `check_global_spillover` function (after its `return CheckResult("global_spillover_indices", True, ...)` line, ~line 187), add:

```python
def check_spillover_read(sections: dict[str, str]) -> CheckResult:
    """Global Spillover must close with a → US Spillover Read synthesis block:
    a fired-channel block carrying a **Net:** line, or the benign-tape fallback
    ('no material spillover'). The benign line needs no Net line."""
    body = sections.get("## Global Market Spillover", "")
    has_marker = "US Spillover Read" in body
    benign = "no material spillover" in body
    if not has_marker and not benign:
        return CheckResult(
            "spillover_read",
            False,
            "no '→ US Spillover Read' block and no benign-tape fallback line",
        )
    if benign:
        return CheckResult("spillover_read", True, "benign-tape spillover read (no Net line required)")
    if re.search(r"\*\*Net:\*\*", body):
        return CheckResult("spillover_read", True, "US Spillover Read block with Net line")
    return CheckResult(
        "spillover_read",
        False,
        "US Spillover Read block present but missing a '**Net:**' line",
    )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_premarket_validator.py -k spillover_read -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Confirm the full suite is still green (check not yet wired)**

Run: `pytest -q`
Expected: PASS — the new function exists but isn't in `run_all_checks` yet, so the sample corpus is unaffected.

- [ ] **Step 6: Commit**

```bash
git add tests/test_premarket_validator.py premarket-briefing-skill/evals/validators/validate_briefing.py
git commit -m "test(premarket): add check_spillover_read + bite tests (unwired)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6: Sample fixtures — fired block (04-06) + benign fallback (04-08)

**Files:**
- Modify: `examples/sample-journal/daily/2026-04-06/premarket.md`
- Modify: `examples/sample-journal/daily/2026-04-08/premarket.md`

- [ ] **Step 1: Add the fired-channel block to 2026-04-06**

In `examples/sample-journal/daily/2026-04-06/premarket.md`, find:

```
**Notable overnight catalysts:** none beyond the earnings follow-through.

---

*Briefing complete. Trade the plan, not the screen.*
```

Replace it with:

```
**Notable overnight catalysts:** none beyond the earnings follow-through.

**→ US Spillover Read (what it means at the open):**
- China beta: KOSPI +1.4% (chip-heavy) and Nikkei +1.1% — firm overnight chip-risk appetite, tailwind for US semis at the open.
- Yen carry: USD/JPY ~152.40 stable — no unwind threat to mega-cap tech.
- **Net:** mild risk-on tailwind, led by chips — Asia echoed US tech strength overnight; follow-through over fade.

---

*Briefing complete. Trade the plan, not the screen.*
```

- [ ] **Step 2: Add the benign-fallback line to 2026-04-08**

In `examples/sample-journal/daily/2026-04-08/premarket.md`, find:

```
**Notable overnight catalysts:** none — the session is a coiled spring around the 8:30 print.

---

*Briefing complete. Trade the plan, not the screen.*
```

Replace it with:

```
**Notable overnight catalysts:** none — the session is a coiled spring around the 8:30 print.

**→ US Spillover Read (what it means at the open):**
- Overnight tape benign — no material spillover into the US open; the session coils around the 8:30 CPI print.

---

*Briefing complete. Trade the plan, not the screen.*
```

- [ ] **Step 3: Verify both fixtures still pass the full suite**

Run: `pytest -q`
Expected: PASS — the block is currently extra content (the check isn't wired until Task 7); nothing should regress.

- [ ] **Step 4: Commit**

```bash
git add examples/sample-journal/daily/2026-04-06/premarket.md examples/sample-journal/daily/2026-04-08/premarket.md
git commit -m "data(premarket): add US Spillover Read to sample briefings

04-06 fires China-beta + yen-carry channels; 04-08 is sub-threshold and
uses the benign fallback line. Exercises both validator paths.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 7: Wire `check_spillover_read` into `run_all_checks` + docstring

**Files:**
- Modify: `premarket-briefing-skill/evals/validators/validate_briefing.py` (`run_all_checks` ~line 204; module docstring ~line 13)
- Modify: `tests/test_premarket_validator.py` (add the wiring test)
- Test: `pytest -q`

- [ ] **Step 1: Write the failing wiring test**

Append to `tests/test_premarket_validator.py`:

```python
def test_run_all_checks_wires_in_spillover_read():
    from journal_schema import journal_trees, premarket_files

    sample = next(
        f for tree in journal_trees() for f in premarket_files(tree)
    )
    results = validate_briefing.run_all_checks(sample)
    assert "spillover_read" in {r.name for r in results}
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pytest tests/test_premarket_validator.py::test_run_all_checks_wires_in_spillover_read -q`
Expected: FAIL — `spillover_read` not in the result names (not wired yet).

- [ ] **Step 3: Wire the check into `run_all_checks`**

In `validate_briefing.py`, find:

```python
        check_econ_calendar(sections),
        check_global_spillover(sections),
    ]
```

Replace it with:

```python
        check_econ_calendar(sections),
        check_global_spillover(sections),
        check_spillover_read(sections),
    ]
```

- [ ] **Step 4: Add docstring item 9**

In the module docstring, find:

```
  8. Global Spillover lists all required Asia/Europe indices + USD/JPY
```

Replace it with:

```
  8. Global Spillover lists all required Asia/Europe indices + USD/JPY
  9. Global Spillover closes with a → US Spillover Read block (a **Net:** line,
     or the 'no material spillover' benign-tape fallback)
```

- [ ] **Step 5: Run the full suite to verify green**

Run: `pytest -q`
Expected: PASS — the wiring test passes; both sample briefings now satisfy `check_spillover_read` (04-06 via Net, 04-08 via benign fallback).

- [ ] **Step 6: Manually confirm the validator now reports 12/12**

Run: `python premarket-briefing-skill/evals/validators/validate_briefing.py --briefing examples/sample-journal/daily/2026-04-06/premarket.md`
Expected: `12/12 checks passed.  Overall: PASS` (includes a `[PASS] spillover_read` row)

Run: `python premarket-briefing-skill/evals/validators/validate_briefing.py --briefing examples/sample-journal/daily/2026-04-08/premarket.md`
Expected: `12/12 checks passed.  Overall: PASS` (the `spillover_read` row reads "benign-tape spillover read")

- [ ] **Step 7: Commit**

```bash
git add premarket-briefing-skill/evals/validators/validate_briefing.py tests/test_premarket_validator.py
git commit -m "feat(premarket): enforce the US Spillover Read block in the validator

check_spillover_read wired into run_all_checks (12 rows); benign fallback
satisfies it without a Net line. Docstring item 9 added.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 8: evals.json — rubric criterion

**Files:**
- Modify: `premarket-briefing-skill/evals/evals.json` (scenario id 1, the `criteria` array; after the Global Spillover indices criterion, ~line 47)

- [ ] **Step 1: Add the criterion**

In `premarket-briefing-skill/evals/evals.json`, find the Global Spillover indices criterion and the array close:

```json
        {
          "text": "Global Spillover section covers Asia (Nikkei, Hang Seng, KOSPI, Shanghai), Europe (DAX, FTSE, STOXX), and USD/JPY",
          "type": "structural"
        }
      ]
```

Replace it with (adds one object, keeps the array close):

```json
        {
          "text": "Global Spillover section covers Asia (Nikkei, Hang Seng, KOSPI, Shanghai), Europe (DAX, FTSE, STOXX), and USD/JPY",
          "type": "structural"
        },
        {
          "text": "Global Spillover closes with a '→ US Spillover Read' block — sector-level transmission channels (China beta, yen carry, Europe→US, oil/rates) that translate the overnight tape into a US-open read, with a '**Net:**' tilt line — or, on a quiet overnight, collapses to the benign-tape fallback ('no material spillover into the US open'). Sector-level only: no watchlist tickers, no number that isn't already in the Tape Table or the Asia/Europe grep.",
          "type": "qualitative"
        }
      ]
```

- [ ] **Step 2: Verify the JSON still parses**

Run: `python -c "import json; json.load(open('premarket-briefing-skill/evals/evals.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add premarket-briefing-skill/evals/evals.json
git commit -m "eval(premarket): add US Spillover Read rubric criterion

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 9: Final verification

**Files:** none (verification only)

- [ ] **Step 1: Full suite green**

Run: `pytest -q`
Expected: PASS, 0 failures. The new spillover-read bite tests and the wiring test are included.

- [ ] **Step 2: Validator end-to-end on both fixtures**

Run:
```bash
python premarket-briefing-skill/evals/validators/validate_briefing.py --briefing examples/sample-journal/daily/2026-04-06/premarket.md
python premarket-briefing-skill/evals/validators/validate_briefing.py --briefing examples/sample-journal/daily/2026-04-08/premarket.md
```
Expected: both `12/12 checks passed.  Overall: PASS`.

- [ ] **Step 3: Leak-test the new reference**

Run: `cat premarket-briefing-skill/references/global-spillover-read.md`
Confirm by eye: no P1/P2/P3, no breakout tell-set, no numeric trade parameters, no course citation — only generic macro-spillover mechanics (carry trade, China beta, Europe→US). Same genre as the public `macro-regime-read.md`.

- [ ] **Step 4: Confirm the branch is ready**

Run: `git status && git log --oneline main..HEAD`
Expected: clean tree; the commits from Tasks 1–8 listed.

---

## Self-review — spec coverage

| Spec requirement | Task |
|------------------|------|
| CNBC asia-markets + europe-markets wired as browser sources | Task 3 |
| KOSPI sourced from asia-markets (no longer N/A) | Task 3 |
| → US Spillover Read block, sector-level, after Notable catalysts | Tasks 2, 4 |
| Channel framework (China beta, yen carry, Europe→US, oil/rates, Net) | Task 2 |
| Gating: material-move only; benign fallback; no new numbers; no tickers; no 1.1 cross-ref | Tasks 2, 4 |
| New reference `global-spillover-read.md` | Task 2 |
| Validator `check_spillover_read` + run_all_checks (11→12) + docstring item 9 | Tasks 5, 7 |
| Bite tests (fired pass, benign pass, absent fail, missing-Net fail, scoped) | Tasks 5, 7 |
| Both sample fixtures updated (fired + benign) | Task 6 |
| evals.json rubric criterion | Task 8 |
| Leak test | Task 9 |

Out of scope (deferred, per spec): watchlist-ticker attribution, 1.1 mood/regime cross-reference, quantitative spillover scoring, README (no spillover reference present).
