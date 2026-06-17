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


import importlib
vql = None
def _load_vql():
    global vql
    if vql is None:
        vql = importlib.import_module("validate_quote_ledger")
    return vql

LEDGER = [
    {"symbol": "NVDA", "last": 208.47, "chg_pct": 0.51, "quote_type": "PRE-MKT"},
    {"symbol": "AVGO", "last": 376.71, "chg_pct": -4.37, "quote_type": "PRIOR-CLOSE"},
]

def test_validator_passes_matching_tagged_numbers():
    v = _load_vql()
    md = ("- **NVDA** +0.51% ($208.47) *(pre-mkt)* — bounce.\n"
          "- **AVGO** -4.37% ($376.71) *(prior close)* — context.\n")
    assert v.validate(md, LEDGER) == []

def test_validator_fails_premkt_tag_without_premkt_row():
    v = _load_vql()
    md = "- **AVGO** -4.37% ($376.71) *(pre-mkt)* — wrong tag.\n"
    assert any("AVGO" in e and "PRE-MKT" in e for e in v.validate(md, LEDGER))

def test_validator_fails_value_mismatch():
    v = _load_vql()
    md = "- **NVDA** +0.51% ($222.00) *(pre-mkt)* — wrong price.\n"
    assert any("NVDA" in e and "208.47" in e for e in v.validate(md, LEDGER))

def test_validator_fails_untagged_number():
    v = _load_vql()
    md = "- **NVDA** $208.47 — no tag.\n"
    assert any("no session tag" in e.lower() for e in v.validate(md, LEDGER))

def test_validator_group_tag_scopes_bullet():
    v = _load_vql()
    md = "- Semis **(pre-mkt)**: NVDA +0.51% ($208.47), and others.\n"
    assert v.validate(md, LEDGER) == []

# --- hardening against real-briefing non-quote $ figures (multi-ticker lines,
# --- EPS, deal sizes, fund flows, price targets). See validate_quote_ledger docstring.
LEDGER2 = [
    {"symbol": "AVGO", "last": 376.71, "chg_pct": -4.37, "quote_type": "PRIOR-CLOSE"},
    {"symbol": "MRVL", "last": 278.67, "chg_pct": -9.78, "quote_type": "PRIOR-CLOSE"},
    {"symbol": "LRCX", "last": 369.34, "chg_pct": -5.03, "quote_type": "PRIOR-CLOSE"},
    {"symbol": "QCOM", "last": 214.07, "chg_pct": -3.05, "quote_type": "PRIOR-CLOSE"},
    {"symbol": "TSLA", "last": 402.07, "chg_pct": -0.64, "quote_type": "PRE-MKT"},
    {"symbol": "AMD",  "last": 520.85, "chg_pct": 2.67,  "quote_type": "PRE-MKT"},
]

def test_validator_multiticker_shared_tag_line_passes():
    # Real pattern: several bolded tickers, each with its own price, one shared tag.
    v = _load_vql()
    md = ("- **AVGO** ($376.71) , **MRVL** ($278.67) , **LRCX** ($369.34) , "
          "**QCOM** ($214.07) *(prior close)* — group bounce.\n")
    assert v.validate(md, LEDGER2) == []

def test_validator_ignores_eps_dollar_figure():
    # EPS is a $ figure wildly outside the price band — not a quote, no tag needed.
    v = _load_vql()
    md = "- **AMD** beat with EPS $2.10 vs $1.95 estimate.\n"
    assert v.validate(md, LEDGER2) == []

def test_validator_ignores_deal_size_and_fund_flow():
    # Magnitude-suffixed amounts ($60B, ~$444M) are never quotes.
    v = _load_vql()
    md = "- **TSLA** ($402.07) *(pre-mkt)* — ARK shifted ~$444M into a $60B deal.\n"
    assert v.validate(md, LEDGER2) == []

def test_validator_still_catches_fabricated_price_on_clean_line():
    # The incident class: a near-but-wrong price on a clean ticker quote line.
    v = _load_vql()
    md = "- **TSLA** +1.0% ($419.00) *(pre-mkt)* — fabricated gap.\n"
    assert any("TSLA" in e and "419" in e for e in v.validate(md, LEDGER2))


import subprocess

HOOK = ROOT / "premarket-briefing-skill" / "scripts" / "validate_quote_hook.py"

def _run_hook(event):
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(event),
                          capture_output=True, text=True)

def test_hook_ignores_non_premarket_write():
    r = _run_hook({"tool_name": "Write", "tool_input": {"file_path": "/x/notes.md"}})
    assert r.returncode == 0

def test_hook_blocks_when_no_ledger(tmp_path):
    bm = tmp_path / "daily" / "2026-06-17" / "premarket.md"
    bm.parent.mkdir(parents=True); bm.write_text("- **NVDA** +0.51% ($208.47) *(pre-mkt)*\n")
    r = _run_hook({"tool_name": "Write", "tool_input": {"file_path": str(bm)}})
    assert r.returncode == 2
    assert "no ledger" in (r.stdout + r.stderr).lower()

def test_hook_passes_with_valid_ledger(tmp_path):
    d = tmp_path / "daily" / "2026-06-17"; d.mkdir(parents=True)
    (d / "premarket.md").write_text("- **NVDA** +0.51% ($208.47) *(pre-mkt)*\n")
    (d / ".quote-ledger.json").write_text(json.dumps(
        [{"symbol": "NVDA", "last": 208.47, "chg_pct": 0.51, "quote_type": "PRE-MKT"}]))
    r = _run_hook({"tool_name": "Write", "tool_input": {"file_path": str(d / "premarket.md")}})
    assert r.returncode == 0
