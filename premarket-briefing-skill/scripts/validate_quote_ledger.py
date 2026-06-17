"""Cross-check a saved premarket.md's tagged numbers against the .quote-ledger.json
sidecar. Exit 0 = clean; exit 1 = violations (printed to stderr)."""
import json, re, sys

TAG_RE = re.compile(r"\((pre-mkt|prior close|n/a[^)]*)\)", re.I)
TICKER_RE = re.compile(r"\*\*([A-Z]{1,5})\*\*")
PRICE_RE = re.compile(r"\$(\d[\d,]*\.?\d*)")
PCT_RE = re.compile(r"([+\-−]\d+\.?\d*)%")

def _tag_to_type(tag):
    t = tag.lower()
    if t.startswith("pre-mkt"): return "PRE-MKT"
    if t.startswith("prior"):   return "PRIOR-CLOSE"
    return "N/A"

def validate(briefing_md, ledger):
    by = {r["symbol"]: r for r in ledger}
    errors = []
    for lineno, line in enumerate(briefing_md.splitlines(), 1):
        nums = PRICE_RE.findall(line) + PCT_RE.findall(line)
        if not nums:
            continue
        tag_m = TAG_RE.search(line)
        if not tag_m:
            errors.append(f"line {lineno}: number(s) {nums} carry no session tag")
            continue
        qtype = _tag_to_type(tag_m.group(1))
        for tkr in TICKER_RE.findall(line):
            row = by.get(tkr)
            if row is None:
                continue
            if qtype != "N/A" and row["quote_type"] != qtype:
                errors.append(f"line {lineno}: {tkr} tagged {qtype} (\"{tag_m.group(1)}\") but ledger says {row['quote_type']}")
            for p in PRICE_RE.findall(line):
                val = float(p.replace(",", ""))
                last = row.get("last")
                if last is not None and abs(val - last) > max(0.05, 0.005 * last):
                    errors.append(f"line {lineno}: {tkr} price ${val} != ledger {last}")
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
