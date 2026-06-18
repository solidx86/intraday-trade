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
