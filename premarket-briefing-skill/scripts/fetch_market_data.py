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
            rows[sym] = {"symbol": sym, "quote_type": "PRE-MKT", "prior_close": prior,
                         "last": _to_float(ext.get("last")), "chg_pct": _to_float(ext.get("change_pct")),
                         "timestamp": ext.get("last_timedate"), "source": "CNBC", "note": ""}
        else:
            rows[sym] = {"symbol": sym, "quote_type": "PRIOR-CLOSE", "prior_close": prior,
                         "last": _to_float(q.get("last")), "chg_pct": _to_float(q.get("change_pct")),
                         "timestamp": q.get("last_timedate"), "source": "CNBC", "note": ""}
    return rows
