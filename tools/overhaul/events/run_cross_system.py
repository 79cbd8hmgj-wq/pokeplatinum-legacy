#!/usr/bin/env python3
"""Re-run every overhaul validator and record the results in the D5 validation report.

Usage: python3 tools/overhaul/events/run_cross_system.py [--builds "Rev 0: success; Rev 1: success"]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

from lib import EVENTS_DIR, ROOT

VALIDATORS = [
    ("availability (ordinary + special + D5 Rotom update)", "tools/overhaul/availability/validate_availability.py"),
    ("evolution", "tools/overhaul/evolution/validate_evolutions.py"),
    ("C1 existing-move rebalance", "tools/overhaul/moves/validate_c1.py"),
    ("C2 mechanics", "tools/overhaul/c2/validate_c2.py"),
    ("breeding", "tools/overhaul/validate_breeding.py"),
    ("economy", "tools/overhaul/economy/validate_economy.py"),
    ("Poké Ball", "tools/overhaul/pokeballs/validate_pokeballs.py"),
    ("trainer", "tools/overhaul/trainers/validate_trainers.py"),
    ("D5 Legendary/Mythical availability", "tools/overhaul/validate_legendary_availability.py"),
]
BEGIN, END = "<!-- cross-system:begin -->", "<!-- cross-system:end -->"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builds", default="")
    args = ap.parse_args()
    rows, bad = [], 0
    for name, rel in VALIDATORS:
        cmd = [sys.executable, rel] + (["--no-report"] if rel.endswith("validate_legendary_availability.py") else [])
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip().splitlines()
        tail = next((l for l in reversed(out) if re.search(r"fail|pass|ok|error|RESULT|PASS", l, re.I)), out[-1] if out else "")
        ok = r.returncode == 0
        bad += not ok
        rows.append(f"| {name} | `{rel}` | {'PASS' if ok else 'FAIL'} | {tail.strip()[:110]} |")
    block = [BEGIN, "## Cross-system validators", "", "| System | Command | Result | Summary |", "|---|---|---|---|"] + rows
    if args.builds:
        block += ["", f"Builds: {args.builds}"]
    block += [END]
    rp = EVENTS_DIR / "LEGENDARY_EVENT_VALIDATION_REPORT.md"
    s = rp.read_text()
    if BEGIN in s:
        s = s[: s.index(BEGIN)] + "\n".join(block) + s[s.index(END) + len(END):]
    else:
        s = s.rstrip("\n") + "\n\n" + "\n".join(block) + "\n"
    rp.write_text(s)
    print("\n".join(block))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
