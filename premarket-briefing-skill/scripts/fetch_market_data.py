"""Deterministic market-data fetch for the pre-market briefing.

Numbers come from CNBC's structured JSON only, never from model-read pages.
stdlib only — runs under PEP-668-locked python3. On any miss a row is N/A
(never guessed); the browser CNBC pages are the manual last-resort.
"""
import json, re

def _to_float(s):
    if s is None:
        return None
    try:
        return float(str(s).replace(",", "").replace("%", "").replace("+", "").strip())
    except ValueError:
        return None

def _na(symbol, note):
    return {"symbol": symbol, "quote_type": "N/A", "prior_close": None, "last": None,
            "chg_pct": None, "timestamp": None, "source": "CNBC", "note": note}

def parse_cnbc(json_text, requested_symbols):
    """Map requested symbols -> ledger row. Symbol echo is verified: a requested
    symbol not present in the response (or a class mismatch like GOOG for GOOGL)
    becomes an N/A row rather than a wrong number."""
    data = json.loads(json_text)
    quotes = data.get("ITVQuoteResult", {}).get("ITVQuote", [])
    if isinstance(quotes, dict):
        quotes = [quotes]
    by_symbol = {q.get("symbol"): q for q in quotes}
    rows = {}
    for sym in requested_symbols:
        q = by_symbol.get(sym)
        if q is None:
            rows[sym] = _na(sym, "symbol not returned by CNBC")
            continue
        prior = _to_float(q.get("previous_day_closing"))
        ext = q.get("ExtendedMktQuote") or {}
        if ext.get("type") == "PRE_MKT" and ext.get("last_time"):
            row = {"symbol": sym, "quote_type": "PRE-MKT", "prior_close": prior,
                   "last": _to_float(ext.get("last")), "chg_pct": _to_float(ext.get("change_pct")),
                   "timestamp": ext.get("last_timedate"), "source": "CNBC", "note": ""}
        else:
            row = {"symbol": sym, "quote_type": "PRIOR-CLOSE", "prior_close": prior,
                   "last": _to_float(q.get("last")), "chg_pct": _to_float(q.get("change_pct")),
                   "timestamp": q.get("last_timedate"), "source": "CNBC", "note": ""}
        # CNBC sometimes echoes a symbol with an empty quote object (no price).
        # Treat that as a miss (N/A), never a None-valued row.
        if row["last"] is None:
            rows[sym] = _na(sym, "symbol returned without a usable price")
        else:
            rows[sym] = row
    return rows


import urllib.request, urllib.parse, ssl, sys, os

_UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
_CTX = ssl.create_default_context()

# CNBC tape symbology. VERIFY each against the live endpoint in Task 2 Step 5; any
# symbol that does not resolve is emitted as N/A (never guessed). Confirmed working
# 2026-06-17: AAPL-style tickers, .SPX, .VIX, @CL.1, .GDAXI, .N225, .KS11.
TAPE_SYMBOLS = [
    "@SP.1", "@ND.1", "@DJ.1",           # futures (S&P / Nasdaq / Dow) — verified 2026-06-18
    ".VIX", ".VXN",                       # volatility
    "US10Y",                              # 10-yr yield (verify symbol)
    "@CL.1", "@GC.1", "@NG.1",            # WTI, gold, natgas
    "EUR=", "JPY=", "GBP=",               # FX (verify symbols)
    ".N225", ".HSI", ".SSEC", ".KS11",    # Asia
    ".GDAXI", ".FTSE", ".STOXX50E",       # Europe
    "XLK", "XLF", "XLE", "XLU", "XLP", "XLY", "XLI", "XLB", "XLV", "XLC", "XLRE",  # sector proxies
]

def cnbc_url(symbols):
    q = urllib.parse.quote("|".join(symbols), safe="")
    return ("https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols="
            + q + "&requestMethod=itv&exthrs=1&output=json")

def _http_get(url, timeout=12):
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=_CTX))
    req = urllib.request.Request(url, headers=_UA)
    with op.open(req, timeout=timeout) as f:
        return f.read().decode("utf-8", "replace")

def cnbc_fetch(symbols, timeout=12):
    try:
        return parse_cnbc(_http_get(cnbc_url(symbols), timeout), symbols)
    except Exception as e:
        return {s: _na(s, f"CNBC fetch failed: {type(e).__name__}") for s in symbols}

def order_rows(rows_by_symbol, ordered_symbols):
    return [rows_by_symbol[s] for s in ordered_symbols if s in rows_by_symbol]

def build_ledger(ticker_symbols):
    """CNBC batch (tape + tickers) in one request. Deterministic output ordered
    by input; any miss is an N/A row."""
    all_syms = TAPE_SYMBOLS + list(ticker_symbols)
    rows = cnbc_fetch(all_syms)
    return order_rows(rows, all_syms)

_COLS = ["symbol", "prior_close", "last", "chg_pct", "timestamp", "source", "quote_type"]

def format_markdown(ledger):
    head = "| " + " | ".join(_COLS) + " |"
    sep = "| " + " | ".join(["---"] * len(_COLS)) + " |"
    body = ["| " + " | ".join(str(r.get(c, "")) for c in _COLS) + " |" for r in ledger]
    return "\n".join([head, sep] + body)

def read_watchlist(path):
    syms = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith(("#", "*", ">")):
            continue
        for tok in line.replace(",", " ").split():
            t = tok.strip().upper()
            if t.isalpha() and 1 <= len(t) <= 5:
                syms.append(t)
    return sorted(set(syms))

def main(argv=None):
    argv = argv or sys.argv[1:]
    sidecar = None
    if "--out" in argv:
        i = argv.index("--out"); sidecar = argv[i + 1]; del argv[i:i + 2]
    tickers = argv or read_watchlist(os.path.join(os.path.dirname(__file__), "..", "watchlist.md"))
    ledger = build_ledger(tickers)
    if sidecar:
        with open(sidecar, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2)
    print(format_markdown(ledger))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
