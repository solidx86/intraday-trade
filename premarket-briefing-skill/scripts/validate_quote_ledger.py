"""Cross-check a saved premarket.md's tagged numbers against the .quote-ledger.json
sidecar. Exit 0 = clean; exit 1 = violations (printed to stderr).

Scope: the validator polices **price quotes for ledger (watchlist) tickers** — the
numbers that drove the 2026-05/06 incidents. A number is governed only when a
watchlist ticker is bolded (`**NVDA**`) on the line. This deliberately ignores:
  - deal sizes / fund flows / market caps ($60B, ~$444M) — magnitude-suffixed,
    never a per-share quote;
  - EPS, revenue, price targets, strikes — a $ figure far from the ledger last
    (outside the QUOTE_BAND) is a different quantity, not a quote;
  - tape lines (futures, VIX, commodities) and index lines — no bolded ledger
    ticker, so the validator can't map the display name to a ledger symbol. Their
    session tags are an authoring convention, enforced by review not by this script.

Authoring conventions the validator assumes (documented in SKILL.md Step 3.5):
  - A `**TICKER**`-anchored quote line carries that ticker's ledger quote and its
    session tag; put targets/EPS/deal sizes in prose without bolding the ticker.
  - Group lines share one session tag and the members under it share that session.
"""
import json, re, sys

TAG_RE = re.compile(r"\((pre-mkt|prior close|n/a[^)]*)\)", re.I)
TICKER_RE = re.compile(r"\*\*([A-Z]{1,5})\*\*")
# A $ figure, but NOT a magnitude-suffixed amount ($60B, $25M, $4bn, $1.2 trillion)
# — those are deal sizes / fund flows / market caps, never a per-share quote.
PRICE_RE = re.compile(
    r"\$(\d[\d,]*\.?\d*)(?!\s*(?:[KMBT]\b|bn|mn|billion|million|trillion|k\b))", re.I)
PCT_RE = re.compile(r"([+\-−]\d+\.?\d*)%")

# A $ figure within this fraction of a ledger `last` is treated as a price quote;
# anything further (EPS, price target, strike, fund flow) is a different quantity
# and is left alone.
QUOTE_BAND = 0.20

def _tag_to_type(tag):
    t = tag.lower()
    if t.startswith("pre-mkt"): return "PRE-MKT"
    if t.startswith("prior"):   return "PRIOR-CLOSE"
    return "N/A"

def _price_match(val, last):
    return last is not None and abs(val - last) <= max(0.05, 0.005 * last)

def validate(briefing_md, ledger):
    by = {r["symbol"]: r for r in ledger}
    errors = []
    for lineno, line in enumerate(briefing_md.splitlines(), 1):
        tickers = [t for t in TICKER_RE.findall(line) if t in by]
        if not tickers:
            continue
        lasts = [by[t]["last"] for t in tickers if by[t].get("last") is not None]
        prices = [float(p.replace(",", "")) for p in PRICE_RE.findall(line)]
        # A $ figure counts as a quote only if it sits near some on-line ticker's
        # last; EPS/targets/strikes/deal-sizes fall outside the band and are ignored.
        quote_prices = [v for v in prices
                        if any(l and abs(v - l) <= QUOTE_BAND * l for l in lasts)]
        pcts = PCT_RE.findall(line)
        if not quote_prices and not pcts:
            continue
        tag_m = TAG_RE.search(line)
        if not tag_m:
            errors.append(f"line {lineno}: quote for {tickers} carries no session tag")
            continue
        qtype = _tag_to_type(tag_m.group(1))
        for tkr in tickers:
            row = by[tkr]
            if qtype != "N/A" and row.get("quote_type") != qtype:
                errors.append(f"line {lineno}: {tkr} tagged {qtype} "
                              f"(\"{tag_m.group(1)}\") but ledger says {row.get('quote_type')}")
        for v in quote_prices:
            if not any(_price_match(v, l) for l in lasts):
                near = ", ".join(f"{by[t]['symbol']} {by[t].get('last')}" for t in tickers)
                errors.append(f"line {lineno}: price ${v} doesn't match any ledger quote ({near})")
    return errors

def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        print("usage: validate_quote_ledger.py <premarket.md> <ledger.json>", file=sys.stderr)
        return 2
    briefing = open(argv[0], encoding="utf-8").read()
    ledger = json.load(open(argv[1], encoding="utf-8"))
    errs = validate(briefing, ledger)
    for e in errs:
        print("LEDGER VIOLATION: " + e, file=sys.stderr)
    return 1 if errs else 0

if __name__ == "__main__":
    raise SystemExit(main())
