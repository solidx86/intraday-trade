"""Unit tests for the pre-market fetch parser.

Prove the rotation-map plumbing: the completed regular-session move is captured
on EVERY row (even a live PRE-MKT row, which the parser otherwise overwrites),
so the rotation map can rank on a uniform prior-close basis; and the rotation
ETFs are in the scripted tape.
"""

import importlib.util
import json

from journal_schema import REPO_ROOT

FETCH_PATH = REPO_ROOT / "premarket-briefing-skill" / "scripts" / "fetch_market_data.py"
spec = importlib.util.spec_from_file_location("fetch_market_data", FETCH_PATH)
fetch_market_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch_market_data)


def _cnbc_json(symbol, prev_close, reg_last, reg_chg, premkt_last=None, premkt_chg=None):
    q = {
        "symbol": symbol,
        "previous_day_closing": str(prev_close),
        "last": str(reg_last),
        "change_pct": str(reg_chg),
        "last_timedate": "2026-07-06T16:00:00",
    }
    if premkt_last is not None:
        q["ExtendedMktQuote"] = {
            "type": "PRE_MKT",
            "last_time": "08:15",
            "last": str(premkt_last),
            "change_pct": str(premkt_chg),
            "last_timedate": "2026-07-07T08:15:00",
        }
    return json.dumps({"ITVQuoteResult": {"ITVQuote": [q]}})


def test_reg_session_captured_on_pre_mkt_row():
    # Liquid ETF with a live pre-market print: chg_pct is the pre-mkt move,
    # reg_chg_pct is the completed session — both present and distinct.
    text = _cnbc_json("SMH", prev_close=100.0, reg_last=98.0, reg_chg=-2.0,
                      premkt_last=99.0, premkt_chg=1.0)
    row = fetch_market_data.parse_cnbc(text, ["SMH"])["SMH"]
    assert row["quote_type"] == "PRE-MKT"
    assert row["chg_pct"] == 1.0        # today's pre-market move
    assert row["reg_chg_pct"] == -2.0   # yesterday's completed session
    assert row["reg_last"] == 98.0


def test_reg_session_captured_on_prior_close_row():
    # Thin ETF, no pre-market: chg_pct and reg_chg_pct agree (uniform basis).
    text = _cnbc_json("XBI", prev_close=90.0, reg_last=93.0, reg_chg=3.3)
    row = fetch_market_data.parse_cnbc(text, ["XBI"])["XBI"]
    assert row["quote_type"] == "PRIOR-CLOSE"
    assert row["chg_pct"] == 3.3
    assert row["reg_chg_pct"] == 3.3


def test_rotation_symbols_in_tape():
    for sym in ["SMH", "XBI", "KRE", "XRT", "XHB", "PEJ", "JETS",
                "RSP", "IWM", "USMV", "MTUM", "SPY"]:
        assert sym in fetch_market_data.TAPE_SYMBOLS
