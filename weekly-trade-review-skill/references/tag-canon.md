# Theme Tag Canon (mirror)

**Source of truth:** `intraday-trade-mentor-skill/references/checklist.md` (and the "Journaling" section of `intraday-trade-mentor-skill/SKILL.md`). This file is a read-only mirror so the weekly-review skill can interpret tags without depending on the mentor skill being installed. If the two ever drift, the mentor's copy wins — and that drift is itself worth flagging in a review.

The intraday-trade-mentor writes one or more of these tags onto every journaled trade. The weekly review aggregates them.

## Negative tags (process violations)

| Tag | Meaning |
|---|---|
| `FOMO` | Entered chasing a move already underway / fear of missing out |
| `revenge` | Trade taken to recover a prior loss rather than on its own merit |
| `ego_hold` | Held a loser past stop / past invalidation because of need-to-be-right |
| `early_exit` | Fear-based exit — cut on volatility/wick alone, no structural invalidation |
| `late_exit` | Held past the planned target / past invalidation out of greed or hope |
| `no_plan` | Impromptu trade — no pre-defined entry/target/stop |
| `sloppy_win` | Won money but bent a rule (R:R, sizing, timing) — luck, not skill |
| `weak_RS` | Long on a name weaker than its sector/index, or short on a stronger one |
| `wrong_sentiment` | Took the trade with indices/VIX clearly working against the direction |
| `R:R_violation` | Reward/risk < 2, or PT/SL not pre-defined |
| `SL_too_wide` | Stop wider than the setup's technical guideline ("safety stop") |
| `SL_too_tight` | Stop so tight it was noise-stopped |
| `overtrading` | Too many trades in the session for no setup-driven reason |
| `held_past_12am` | Carried an intraday position past 12am Malaysia / 4am ET |
| `chased_breakout` | Entered a P2 on the breakout candle / on a wick, not on a confirmed close + retest |
| `wrong_sector_check` | Checked the broad index instead of the sector ETF for a single name |
| `no_catalyst` | No falsifiable catalyst named — a Trade Quality Triad leg missing |
| `triad_partial` | Only one or two Trade Quality Triad legs (catalyst / RS / pattern) stated before entry |
| `vague_pattern` | Pattern claimed but its trigger structure never actually printed |

## Positive tags (process wins — reinforce these)

| Tag | Meaning |
|---|---|
| `disciplined_skip` | No-trade decision because a check failed — correct restraint |
| `disciplined_exit` | Manual invalidation cut on a structural break (lower high, failed reclaim, distribution) — not fear |
| `clean_loss` | Followed the plan end-to-end, market took the stop; no foundational (Q1/Q2/Q3) fail |
| `clean_win` | Plan executed start to finish, target hit by the rules |
| `correct_RS_read` | Correctly identified relative strength (e.g. ticker held PDC while sector broke it) |
| `correct_sentiment_read` | Correctly read indices/VIX for or against the trade |
| `patient_entry` | Waited for the pullback / confirmation instead of chasing |
| `triad_complete` | All three Trade Quality Triad legs stated before entry |
| `catalyst_named` | Catalyst stated pre-trade, specific and falsifiable |

## Aggregation notes

- A trade can carry several tags. `clean_loss` + `correct_RS_read` on the same losing trade is normal and both get counted.
- If a tag contradicts the trade's checklist results (e.g. `clean_loss` on a D-grade trade with Q1/Q2 fails), trust the **checklist + grade**, not the tag, and note the mis-tag.
- Unknown tags (not in this list): count them, surface them as "uncanonized tags seen this week: …", and don't crash. They may be a sign the mentor is evolving its vocabulary — worth a note.
