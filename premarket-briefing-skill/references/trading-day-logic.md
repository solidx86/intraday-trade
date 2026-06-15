# Trading-Day Logic (Malaysia → US Eastern)

The user is in Malaysia (UTC+8) and trades the US session, which runs 09:30–16:00 ET. The pre-market window the user cares about (when this briefing is most useful) is roughly the few hours before the US open — which is **5:00 PM – 9:30 PM Malaysia time** (DST-dependent).

Goal of this file: a clear, mechanical rule for "given the user's current local time, which US trading date does this briefing cover?"

---

## Timezone facts

- **Malaysia (MYT):** UTC+8, year-round, no DST.
- **US Eastern Time:** UTC−5 in winter (EST), UTC−4 in summer (EDT).
- **Malaysia is 12 hours ahead of ET in summer, 13 hours ahead in winter.**
- US DST: starts second Sunday of March, ends first Sunday of November.

---

## Mapping rule

Let `MYT_HH` = Malaysia local hour at the moment of invocation (24-hour clock). Let `MYT_DATE` = Malaysia local calendar date.

| Malaysia local time | US trading day to brief |
|---------------------|-------------------------|
| **17:00 – 23:59 MYT** | Same calendar date as `MYT_DATE` *(the US session is opening that night MYT, but it's still "today" in ET — e.g., Friday 9 PM MYT = Friday 9 AM ET = Friday US session)* |
| **00:00 – 05:00 MYT** | Previous Malaysia calendar date *(still the same US session that started the prior evening MYT — e.g., Saturday 2 AM MYT = Friday 2 PM ET, still Friday's US session)* |
| **05:00 – 17:00 MYT** | Next US trading day from `MYT_DATE` *(the US session today already ended hours ago — this briefing is forward-looking to the next session)* |

Pseudo-logic:

```
if 17 <= MYT_HH <= 23:
    candidate = MYT_DATE
elif 0 <= MYT_HH < 5:
    candidate = MYT_DATE - 1 day
else:  # 5 <= MYT_HH < 17
    candidate = MYT_DATE + (next weekday adjustment)

# Then skip weekends and US market holidays:
while candidate is Saturday, Sunday, or in US_HOLIDAYS:
    candidate += 1 day

us_trading_day = candidate
```

---

## Weekday anchor — verify before writing any date

Bugs in this briefing almost always come from saying "Tuesday" when the actual date was Wednesday. Compute the weekday explicitly using a known anchor; don't guess.

**Verified anchors for 2026:**

| Date | Weekday |
|------|---------|
| 2026-01-01 | Thursday |
| 2026-02-01 | Sunday |
| 2026-03-01 | Sunday |
| 2026-04-01 | Wednesday |
| 2026-05-01 | Friday |
| 2026-06-01 | Monday |
| 2026-07-01 | Wednesday |
| 2026-08-01 | Saturday |
| 2026-09-01 | Tuesday |
| 2026-10-01 | Thursday |
| 2026-11-01 | Sunday |
| 2026-12-01 | Tuesday |

To compute the weekday for any 2026 date: take the month's 1st-of-the-month weekday from the table above, add `(day - 1)` days modulo 7. Do this arithmetic twice and check both runs match.

**Useful sanity-check landmarks in 2026:**

- 2026-05-01 = Fri → 2026-05-04 = Mon, 2026-05-11 = Mon, 2026-05-15 = Fri, 2026-05-18 = Mon
- 2026-05-12 = Tue, 2026-05-13 = Wed, 2026-05-14 = Thu, 2026-05-15 = Fri, 2026-05-16 = Sat

If the briefing's "today" is one of those landmark dates, you can read the weekday off directly. For any other date, do the modulo arithmetic from the nearest table entry.

---

## US market holidays 2026

Full closures (NYSE/NASDAQ closed):

| Date | Holiday |
|------|---------|
| 2026-01-01 (Thu) | New Year's Day |
| 2026-01-19 (Mon) | Martin Luther King Jr. Day |
| 2026-02-16 (Mon) | Presidents' Day |
| 2026-04-03 (Fri) | Good Friday |
| 2026-05-25 (Mon) | Memorial Day |
| 2026-06-19 (Fri) | Juneteenth |
| 2026-07-03 (Fri) | Independence Day (observed; July 4 is Saturday) |
| 2026-09-07 (Mon) | Labor Day |
| 2026-11-26 (Thu) | Thanksgiving |
| 2026-12-25 (Fri) | Christmas Day |

Early closes (1:00 PM ET, half-day) — usually still useful to brief on:
- 2026-07-02 (Thu, day before July 3 observance) — sometimes
- 2026-11-27 (Fri, day after Thanksgiving)
- 2026-12-24 (Thu, Christmas Eve)

For early-close days, brief as normal but mention the 1:00 PM ET close in section 1.2.

---

## Examples

| Invocation moment (MYT) | Computed US trading day | Notes |
|--------------------------|--------------------------|-------|
| Fri 2026-05-15 20:00 MYT | Fri 2026-05-15 | 17:00–23:59 → same date |
| Sat 2026-05-16 02:30 MYT | Fri 2026-05-15 | Past midnight, still Friday's US session |
| Sat 2026-05-16 10:00 MYT | Mon 2026-05-18 | 05:00–17:00, skip weekend |
| Sun 2026-05-17 20:00 MYT | Mon 2026-05-18 | 17:00–23:59 but `MYT_DATE` is Sunday → skip to Monday |
| Mon 2026-05-25 18:00 MYT | Tue 2026-05-26 | Memorial Day holiday — skip to next trading day |
| Thu 2026-04-02 21:00 MYT | Thu 2026-04-02 | Good Friday is next day, but today still trades |
| Fri 2026-04-03 09:00 MYT | Mon 2026-04-06 | Good Friday closed, skip weekend, land on Monday |

---

## Sunday edge case

If `MYT_DATE` is Sunday and `MYT_HH` is between 17:00 and 23:59, the rule "same date" would pick Sunday — but US markets don't trade Sunday. Always run the weekend/holiday skip step after the initial mapping. The example above (Sun 8 PM MYT → Mon US session) is the correct resolution.

---

## State it in the header

Always print the computed US trading date in the briefing header in `YYYY-MM-DD` form, plus the Malaysia generation timestamp. This is the user's safety check — if you ever map wrong, he sees it immediately.

```
*Generated 2026-05-15 20:30 MYT · briefing for US trading day 2026-05-15*
```

If you're uncertain about the user's actual local hour (e.g., environment metadata only gives the date, not the hour), it's fine to make a reasonable assumption based on the trigger context and state it: *"Assuming Malaysia evening run; briefing for tonight's US session."* The user can correct you if needed.
