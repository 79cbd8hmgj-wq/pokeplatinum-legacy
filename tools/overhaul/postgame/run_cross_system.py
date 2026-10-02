#!/usr/bin/env python3
"""Re-run every overhaul validator and record the results in the D6 validation report.

Usage: python3 tools/overhaul/postgame/run_cross_system.py [--builds "Rev 0: success; Rev 1: success"]
Run validate_postgame.py first (it rewrites the report); this appends the cross-system block.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REPORT = os.path.join(ROOT, "docs/overhaul/implementation/postgame/POSTGAME_VALIDATION_REPORT.md")
VALIDATORS = [
    ("D6 postgame mutation tests", "tools/overhaul/postgame/test_validate_postgame.py"),
    ("trainer", "tools/overhaul/trainers/validate_trainers.py"),
    ("economy", "tools/overhaul/economy/validate_economy.py"),
    ("C2 mechanics", "tools/overhaul/c2/validate_c2.py"),
    ("C1 existing-move rebalance", "tools/overhaul/moves/validate_c1.py"),
    ("availability", "tools/overhaul/availability/validate_availability.py"),
    ("evolution", "tools/overhaul/evolution/validate_evolutions.py"),
    ("breeding", "tools/overhaul/validate_breeding.py"),
    ("Poké Ball", "tools/overhaul/pokeballs/validate_pokeballs.py"),
    ("D5 Legendary/Mythical availability", "tools/overhaul/validate_legendary_availability.py"),
]
BEGIN, END = "<!-- cross-system:begin -->", "<!-- cross-system:end -->"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--builds", default="")
    args = ap.parse_args()
    rows, bad = [], 0
    for name, rel in VALIDATORS:
        cmd = [sys.executable, rel] + (["--no-report"] if rel.endswith("validate_legendary_availability.py") else [])
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip().splitlines()
        tail = next((l for l in reversed(out) if re.search(r"fail|pass|ok|error|RESULT|PASS|detected|baseline", l, re.I)), out[-1] if out else "")
        ok = r.returncode == 0
        bad += not ok
        rows.append(f"| {name} | `{rel}` | {'PASS' if ok else 'FAIL'} | {tail.strip()[:110]} |")
    block = [BEGIN, "## Cross-system validators", "", "| System | Command | Result | Summary |", "|---|---|---|---|"] + rows
    if args.builds:
        block += ["", f"Builds: {args.builds}"]
    block += [END]
    s = open(REPORT).read()
    if BEGIN in s:
        s = s[: s.index(BEGIN)] + "\n".join(block) + s[s.index(END) + len(END):]
    else:
        s = s.rstrip("\n") + "\n\n" + "\n".join(block) + "\n"
    open(REPORT, "w").write(s)
    print("\n".join(block))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
