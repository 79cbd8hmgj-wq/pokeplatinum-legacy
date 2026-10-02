#!/usr/bin/env python3
"""Guarded apply of the locked evolution manifest.  Fails closed unless each changed species is at expected-before or expected-after."""
import json
import os
import sys

from evo_lib import MANIFEST, ROOT


def main() -> int:
    with open(os.path.join(ROOT, MANIFEST), encoding="utf-8") as f:
        man = json.load(f)
    applied = already = 0
    for s in man["species"]:
        if not s["changed"]:
            continue
        path = os.path.join(ROOT, s["source"])
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        live = data.get("evolutions") or []
        if live == s["after"]:
            already += 1
            continue
        if live != s["before"]:
            print(f"FAIL-CLOSED {s['species']}: live {live} matches neither expected-before nor expected-after", file=sys.stderr)
            return 1
        data["evolutions"] = s["after"]
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
        applied += 1
    print(f"applied={applied} already_correct={already} expected_changed_species={man['summary']['species_with_changed_tables']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
