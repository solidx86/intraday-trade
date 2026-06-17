# Deterministic Number Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove model-read numbers from the pre-market briefing — a script fetches every price/percent from CNBC's structured JSON into a machine ledger, and a validator (enforced by a hard hook) fails any briefing whose numbers don't trace to that ledger.

**Architecture:** A stdlib-only Python fetcher (`fetch_market_data.py`) pulls CNBC's `quote.htm` JSON (tape + per-ticker) and writes a `.quote-ledger.json` sidecar + a markdown ledger. A validator (`validate_quote_ledger.py`) cross-checks the saved `premarket.md`'s tagged numbers against that sidecar. A `PostToolUse` hook runs the validator on every briefing write and blocks on failure. SKILL.md / data-sources.md are rewritten to drive numbers from the script and tag each with its session.

**Tech Stack:** Python 3 stdlib only (`urllib`, `json`, `re`) — no `pip` (system python3 is PEP-668-locked). CNBC is the single structured source; it accepts a batched symbol list in one request, so no threadpool and no second-endpoint auth are needed. pytest for CI. Claude Code `settings.json` hooks.

**Spec:** `docs/superpowers/specs/2026-06-17-premarket-deterministic-number-pipeline-design.html`

**Sourcing decision:** **CNBC `quote.htm` only.** No Yahoo cross-check or fallback (dropped for simplicity — CNBC already provides typed pre-market, timestamp, prior close, and exact-symbol echo). On any CNBC miss the row is `N/A` (never guessed); the browser CNBC market pages remain a documented **manual** last-resort. The symbol-echo check (CNBC must return the exact symbol requested) is retained — it is what prevents a GOOG-for-GOOGL substitution.

**Endpoint facts verified live 2026-06-17 (build against these):**
- `GET https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols=<PIPE_LIST>&requestMethod=itv&exthrs=1&output=json` → `{"ITVQuoteResult":{"ITVQuote":[ {...} ]}}`. No auth. Per quote: `symbol`, `previous_day_closing`, `last`, `change_pct` (e.g. `"-0.50%"`), `curmktstatus` (`REG_MKT`/`PRE_MKT`/…), and `ExtendedMktQuote`: `{type:"PRE_MKT", last, change_pct, last_timedate:"9:30 AM EDT", last_time:"2026-06-17T09:30:00-0400"}`.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `premarket-briefing-skill/scripts/fetch_market_data.py` (NEW) | Fetch CNBC `quote.htm` (tape + per-ticker); emit ledger JSON sidecar + markdown to stdout. Pure parse function + orchestration + CLI. |
| `premarket-briefing-skill/scripts/validate_quote_ledger.py` (NEW) | Parse the briefing's tagged numbers; cross-check vs the ledger sidecar; CLI with exit codes. Single responsibility. |
| `premarket-briefing-skill/scripts/validate_quote_hook.py` (NEW) | PostToolUse wrapper: read stdin event JSON → match `daily/*/premarket.md` → locate sibling ledger → call the validator → emit block decision. |
| `tests/test_quote_ledger.py` (NEW) | CI: parse fixtures, validator pass/fail cases, hook stdin/path wrapper. Offline (recorded fixtures, no network). |
| `tests/fixtures/cnbc_quote_sample.json` (NEW) | Recorded CNBC response for deterministic parser tests. |
| `premarket-briefing-skill/SKILL.md` (MODIFY) | Step 3a + 3.5 rewrite; `(pre-mkt)`/`(prior close)`/`(N/A)` template tags; final self-check; incident note. |
| `premarket-briefing-skill/references/data-sources.md` (MODIFY) | Source reclassification: CNBC structured = price; finviz = non-price; Section 1.4 net-2 split. |
| `premarket-briefing-skill/evals/validators/validate_briefing.py` (MODIFY) | Thin call into `validate_quote_ledger` when a ledger sidecar is present. |
| `.claude/settings.json` (MODIFY) | Register the PostToolUse hook. |

**Branch:** already on `feat/premarket-deterministic-number-pipeline` (spec committed). All tasks commit here.

---

## Task 1: CNBC parser (pure function)

**Files:**
- Create: `premarket-briefing-skill/scripts/fetch_market_data.py`
- Create: `tests/fixtures/cnbc_quote_sample.json`
- Test: `tests/test_quote_ledger.py`

- [ ] **Step 1: Record the CNBC fixture.** Create `tests/fixtures/cnbc_quote_sample.json` with a trimmed real response (two pre-market names, one prior-close-only name, one wrong-class name):

```json
{"ITVQuoteResult":{"ITVQuote":[
  {"symbol":"NVDA","previous_day_closing":"207.41","last":"207.41","change_pct":"0%","curmktstatus":"PRE_MKT",
   "ExtendedMktQuote":{"type":"PRE_MKT","last":"208.47","change_pct":"+0.51%","last_timedate":"9:18 AM EDT","last_time":"2026-06-17T09:18:00-0400"}},
  {"symbol":"GOOGL","previous_day_closing":"373.25","last":"373.25","change_pct":"0%","curmktstatus":"PRE_MKT",
   "ExtendedMktQuote":{"type":"PRE_MKT","last":"371.34","change_pct":"-0.51%","last_timedate":"9:18 AM EDT","last_time":"2026-06-17T09:18:00-0400"}},
  {"symbol":"AVGO","previous_day_closing":"393.94","last":"376.71","change_pct":"-4.37%","curmktstatus":"REG_MKT"},
  {"symbol":"GOOG","previous_day_closing":"372.00","last":"372.00","change_pct":"0%","curmktstatus":"PRE_MKT",
   "ExtendedMktQuote":{"type":"PRE_MKT","last":"370.00","change_pct":"-0.54%","last_timedate":"9:18 AM EDT","last_time":"2026-06-17T09:18:00-0400"}}
]}}
```

- [ ] **Step 2: Write the failing test** in `tests/test_quote_ledger.py`:

```python
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
```

- [ ] **Step 3: Run it, expect failure.** Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m pytest tests/test_quote_ledger.py -q`. Expected: `ModuleNotFoundError: fetch_market_data` / `AttributeError: parse_cnbc`.

- [ ] **Step 4: Implement `parse_cnbc`** in `fetch_market_data.py`:

```python
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
```

- [ ] **Step 5: Run tests, expect pass.** Run: `python3 -m pytest tests/test_quote_ledger.py -q`. Expected: 3 passed.

- [ ] **Step 6: Commit.**

```bash
git add premarket-briefing-skill/scripts/fetch_market_data.py tests/test_quote_ledger.py tests/fixtures/cnbc_quote_sample.json
git commit -m "feat(premarket): deterministic CNBC quote parser + fixture"
```

---

## Task 2: Orchestration + CLI (batch, ordered output, sidecar, markdown)

**Files:**
- Modify: `premarket-briefing-skill/scripts/fetch_market_data.py`
- Test: `tests/test_quote_ledger.py`

- [ ] **Step 1: Write the failing test** (append to `tests/test_quote_ledger.py`):

```python
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
```

- [ ] **Step 2: Run, expect failure.** Run: `python3 -m pytest tests/test_quote_ledger.py -q`. Expected: FAIL (`format_markdown`/`order_rows` undefined).

- [ ] **Step 3: Implement** the symbol map, orchestration, and CLI in `fetch_market_data.py`:

```python
import urllib.request, urllib.parse, ssl, sys, os

_UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
_CTX = ssl.create_default_context()

# CNBC tape symbology. VERIFY each against the live endpoint in Step 5; any symbol
# that does not resolve is emitted as N/A (never guessed). Confirmed working
# 2026-06-17: AAPL-style tickers, .SPX, .VIX, @CL.1, .GDAXI, .N225, .KS11.
TAPE_SYMBOLS = [
    "@ES.1", "@NQ.1", "@YM.1",           # futures
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
```

- [ ] **Step 4: Run tests, expect pass.** Run: `python3 -m pytest tests/test_quote_ledger.py -q`. Expected: 5 passed.

- [ ] **Step 5: Live smoke test + verify the tape symbol map.** Run: `python3 premarket-briefing-skill/scripts/fetch_market_data.py NVDA AAPL --out /tmp/ledger.json` and inspect: every `TAPE_SYMBOLS` entry should resolve to `PRE-MKT`/`PRIOR-CLOSE`, not `N/A`. For any tape symbol showing `N/A`, find its correct CNBC symbol (load `https://www.cnbc.com/markets/pre-markets/` and read the `/quotes/<SYM>` links) and fix `TAPE_SYMBOLS`; re-run until only legitimately-unavailable rows are `N/A`. Document any unresolved symbol with an inline comment.

- [ ] **Step 6: Commit.**

```bash
git add premarket-briefing-skill/scripts/fetch_market_data.py tests/test_quote_ledger.py
git commit -m "feat(premarket): CNBC-only ledger orchestration + CLI"
```

---

## Task 3: The ledger validator

**Files:**
- Create: `premarket-briefing-skill/scripts/validate_quote_ledger.py`
- Test: `tests/test_quote_ledger.py`

- [ ] **Step 1: Write the failing test** (append):

```python
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
```

- [ ] **Step 2: Run, expect failure.** Run: `python3 -m pytest tests/test_quote_ledger.py -q`. Expected: FAIL (`No module named validate_quote_ledger`).

- [ ] **Step 3: Implement** `validate_quote_ledger.py`:

```python
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
                errors.append(f"line {lineno}: {tkr} tagged ({tag_m.group(1)}) but ledger says {row['quote_type']}")
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
```

- [ ] **Step 4: Run tests, expect pass.** Run: `python3 -m pytest tests/test_quote_ledger.py -q`. Expected: 10 passed.

- [ ] **Step 5: Commit.**

```bash
git add premarket-briefing-skill/scripts/validate_quote_ledger.py tests/test_quote_ledger.py
git commit -m "feat(premarket): quote-ledger validator (tag/value/type cross-check)"
```

---

## Task 4: PostToolUse hook wrapper

**Files:**
- Create: `premarket-briefing-skill/scripts/validate_quote_hook.py`
- Test: `tests/test_quote_ledger.py`

- [ ] **Step 1: Write the failing test** (append):

```python
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
```

- [ ] **Step 2: Run, expect failure.** Run: `python3 -m pytest tests/test_quote_ledger.py -q`. Expected: FAIL (hook file missing).

- [ ] **Step 3: Implement** `validate_quote_hook.py`:

```python
"""PostToolUse hook: gate every premarket.md write against its ledger sidecar.
Exit 2 + stderr message = block (Claude Code surfaces it to the agent). Exit 0 = allow.
Inert for any write that is not a daily/<date>/premarket.md."""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import validate_quote_ledger as vql

PATH_RE = re.compile(r"/daily/\d{4}-\d{2}-\d{2}/premarket\.md$")

def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    if event.get("tool_name") not in ("Write", "Edit"):
        return 0
    path = (event.get("tool_input") or {}).get("file_path", "")
    if not PATH_RE.search(path.replace(os.sep, "/")):
        return 0
    if not os.path.exists(path):
        return 0
    ledger_path = os.path.join(os.path.dirname(path), ".quote-ledger.json")
    if not os.path.exists(ledger_path):
        print("BLOCK: no ledger sidecar (.quote-ledger.json) — run fetch_market_data.py "
              "before writing the briefing; numbers cannot be verified.", file=sys.stderr)
        return 2
    briefing = open(path, encoding="utf-8").read()
    ledger = json.load(open(ledger_path, encoding="utf-8"))
    errs = vql.validate(briefing, ledger)
    if errs:
        print("BLOCK: briefing numbers fail ledger validation:\n" + "\n".join(errs), file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests, expect pass.** Run: `python3 -m pytest tests/test_quote_ledger.py -q`. Expected: 13 passed.

- [ ] **Step 5: Commit.**

```bash
git add premarket-briefing-skill/scripts/validate_quote_hook.py tests/test_quote_ledger.py
git commit -m "feat(premarket): PostToolUse hook wrapper for ledger validation"
```

---

## Task 5: Register the hook in settings.json

**Files:**
- Modify: `.claude/settings.json`

- [ ] **Step 1: Inspect current settings.** Run: `cat .claude/settings.json 2>/dev/null || echo "{}"`. Note any existing `hooks` key so it isn't clobbered.

- [ ] **Step 2: Add the PostToolUse hook.** Merge this into `.claude/settings.json` (preserve existing keys; `$CLAUDE_PROJECT_DIR` resolves to the repo root):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/premarket-briefing-skill/scripts/validate_quote_hook.py\""
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Verify hook fires + blocks.** Confirm the block path with a throwaway briefing that has no ledger:

```bash
mkdir -p /tmp/hooktest/daily/2026-06-17
echo '- **NVDA** +0.51% ($208.47) *(pre-mkt)*' > /tmp/hooktest/daily/2026-06-17/premarket.md
echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/hooktest/daily/2026-06-17/premarket.md"}}' \
  | python3 premarket-briefing-skill/scripts/validate_quote_hook.py; echo "exit=$?"
```
Expected: `BLOCK: no ledger sidecar …` and `exit=2`.

- [ ] **Step 4: Commit.**

```bash
git add .claude/settings.json
git commit -m "chore(premarket): register PostToolUse ledger-validation hook"
```

---

## Task 6: SKILL.md + data-sources.md rewrite

**Files:**
- Modify: `premarket-briefing-skill/SKILL.md`
- Modify: `premarket-briefing-skill/references/data-sources.md`

- [ ] **Step 1: Rewrite Step 3a (market tape) in SKILL.md.** Replace the browser-grep tape capture with: "Run `python3 scripts/fetch_market_data.py <watchlist symbols> --out data/trade-journal/daily/<US-date>/.quote-ledger.json`. The script fetches the tape (futures, VIX/VXN, sectors, commodities, US yields, FX, global indices) and per-ticker quotes from CNBC JSON and writes the ledger sidecar + prints the markdown ledger. The browser pre-markets page is now a **manual last-resort** for numbers and remains the source for news/themes (Step 3b)." Source the Tape Table from the ledger.

- [ ] **Step 2: Rewrite Step 3.5 in SKILL.md.** Replace the finviz-anchor procedure with the three gates against the ledger: (1) pre-market gate — print as today's move only if `quote_type==PRE-MKT`; a `PRIOR-CLOSE` row is tagged `(prior close)` or `N/A`; (2) symbol/class gate — the script echo-verifies, so quote only ledger symbols; (3) provenance gate — every body number comes from the ledger, never a WebSearch snippet or finviz price. State: the model consumes the printed ledger verbatim and never reads a price off a page.

- [ ] **Step 3: Add the output-tag convention to the template section.** Every per-ticker and tape number carries `(pre-mkt)` / `(prior close)` / `(N/A — reason)`; group tags scope to their bullet. Include worked examples (NVDA `(pre-mkt)`, AVGO `(prior close)`, LUNR `(N/A — no pre-market quote)`).

- [ ] **Step 4: Add the final self-check items.** Append to the Step 3.5 self-check: "every number has a ledger row of the matching `quote_type`; every ticker matches the watchlist symbol exactly; no number traces to a WebSearch snippet; run `validate_quote_ledger.py <briefing> <ledger>` and fix/`N/A` any violation before presenting."

- [ ] **Step 5: Add the incident note.** Under Step 3.5, add a dated note mirroring the existing NVDA-confabulation note:

```markdown
**Why this step is scripted (the 2026-06-17 incident):** finviz's free `quote.ashx`
serves the prior *closed* session, so Tuesday's close-to-close moves were printed as
Wednesday "pre-market" (AAPL "+0.95%", GOOGL "+1.06%" were the prior day). A cross-check
then pulled a number from a WebSearch snippet that was the wrong share class — GOOG (Class C)
for GOOGL (Class A). Fix: numbers now come only from the scripted CNBC ledger (exact-symbol
verified, pre-market typed), and a validator + hook reject any unbacked number.
```

- [ ] **Step 6: Reclassify sources in data-sources.md.** finviz `quote.ashx` → "headlines / analyst actions / earnings dates ONLY; its price is the prior session's close — never the printed number." Add CNBC `quote.htm` JSON as the structured price/tape source (document the endpoint); note the browser CNBC pages as the manual last-resort. Split Section 1.4 "net 2": finviz = the news/earnings sweep; the script = the price anchor. State WebSearch snippets are never a printed price.

- [ ] **Step 7: Run the full test suite.** Run: `python3 -m pytest tests/ -q`. Expected: all pass (existing premarket/tag-canon/etc. + new `test_quote_ledger.py`). If any existing premarket test assumed finviz-as-price, update it to the ledger model.

- [ ] **Step 8: Commit.**

```bash
git add premarket-briefing-skill/SKILL.md premarket-briefing-skill/references/data-sources.md
git commit -m "docs(premarket): drive numbers from the scripted CNBC ledger; reclassify sources; incident note"
```

---

## Task 7: Wire the ledger validator into the eval validator

**Files:**
- Modify: `premarket-briefing-skill/evals/validators/validate_briefing.py`

- [ ] **Step 1: Read the existing validator's entry point.** Run: `sed -n '1,40p' premarket-briefing-skill/evals/validators/validate_briefing.py` to see its `main()`/CLI shape and how it reports failures.

- [ ] **Step 2: Add an optional ledger cross-check.** After its existing structural checks, if a `.quote-ledger.json` sits beside the briefing being validated, import and call the ledger validator and merge its errors into the existing failure list (match the file's existing error-reporting style):

```python
# near the other checks, given `briefing_path` and the loaded `text`:
import os, json
_ledger = os.path.join(os.path.dirname(briefing_path), ".quote-ledger.json")
if os.path.exists(_ledger):
    import importlib.util, pathlib
    _spec = importlib.util.spec_from_file_location(
        "validate_quote_ledger",
        pathlib.Path(__file__).resolve().parents[2] / "scripts" / "validate_quote_ledger.py")
    _vql = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_vql)
    errors.extend(_vql.validate(text, json.load(open(_ledger, encoding="utf-8"))))
```

(Adapt variable names — `briefing_path`, `text`, `errors` — to whatever the existing file uses.)

- [ ] **Step 3: Run the suite.** Run: `python3 -m pytest tests/ -q`. Expected: all pass.

- [ ] **Step 4: Commit.**

```bash
git add premarket-briefing-skill/evals/validators/validate_briefing.py
git commit -m "feat(premarket): eval validator picks up the quote-ledger cross-check"
```

---

## Final verification

- [ ] Run the whole suite: `python3 -m pytest tests/ -q` → all green.
- [ ] Live end-to-end: `python3 premarket-briefing-skill/scripts/fetch_market_data.py AAPL NVDA GOOGL --out /tmp/le.json` → ledger has no unexpected `N/A`; the GOOGL row is `GOOGL` (not `GOOG`).
- [ ] Confirm README CI badge stays green after push.
- [ ] Open a PR from `feat/premarket-deterministic-number-pipeline` (do not merge without user say-so).
