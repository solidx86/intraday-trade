import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "premarket-briefing-skill" / "scripts"))
import fetch_market_data as fmd

FIX = pathlib.Path(__file__).parent / "fixtures" / "cnbc_quote_sample.json"

def test_parse_cnbc_premarket_row():
    rows = fmd.parse_cnbc(FIX.read_text(), ["NVDA", "GOOGL", "AVGO"])
    nvda = rows["NVDA"]
    assert nvda["quote_type"] == "PRE-MKT"
    assert nvda["last"] == 208.47
    assert nvda["chg_pct"] == 0.51
    assert nvda["prior_close"] == 207.41
    assert nvda["timestamp"] == "9:18 AM EDT"
    assert nvda["source"] == "CNBC"

def test_parse_cnbc_prior_close_when_no_ext():
    rows = fmd.parse_cnbc(FIX.read_text(), ["AVGO"])
    assert rows["AVGO"]["quote_type"] == "PRIOR-CLOSE"
    assert rows["AVGO"]["last"] == 376.71      # regular last, not ext
    assert rows["AVGO"]["chg_pct"] == -4.37

def test_parse_cnbc_symbol_echo_mismatch_is_na():
    # GOOGL is present and correct; a requested-but-absent symbol must be N/A,
    # never silently served another class (e.g. GOOG).
    rows = fmd.parse_cnbc(FIX.read_text(), ["GOOGL"])
    assert rows["GOOGL"]["quote_type"] == "PRE-MKT"
    rows2 = fmd.parse_cnbc(FIX.read_text(), ["MSFT"])
    assert rows2["MSFT"]["quote_type"] == "N/A"
    assert "not returned" in rows2["MSFT"]["note"]

def test_format_markdown_columns():
    ledger = [{"symbol":"NVDA","prior_close":207.41,"last":208.47,"chg_pct":0.51,
               "timestamp":"9:18 AM EDT","source":"CNBC","quote_type":"PRE-MKT","note":""}]
    md = fmd.format_markdown(ledger)
    assert "NVDA" in md and "PRE-MKT" in md and "208.47" in md
    assert md.splitlines()[0].startswith("| symbol")

def test_order_preserved():
    rows = {"B": {"symbol": "B"}, "A": {"symbol": "A"}}
    out = fmd.order_rows(rows, ["A", "B"])
    assert [r["symbol"] for r in out] == ["A", "B"]
