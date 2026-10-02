#!/usr/bin/env python3
"""Guarded apply of trainer_overhaul_manifest.json to res/trainers/data/*.json.

Fail closed: a record is rewritten only when its live bytes still hash to the manifest's before-guard
(or it already equals the target, which makes the tool idempotent).  Only `party` is replaced.
Usage: apply_manifest.py [--dry-run] [--category CAT[,CAT...]] [--only ID[,ID...]]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from trainer_lib import MANIFEST, TRAINER_DIR, dump_trainer, file_sha, load_trainer, p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--category")
    ap.add_argument("--only")
    a = ap.parse_args()
    with open(p(MANIFEST), encoding="utf-8") as f:
        man = json.load(f)
    cats = set(a.category.split(",")) if a.category else None
    only = set(a.only.split(",")) if a.only else None
    applied = skipped = 0
    errors = []
    for e in man["entries"]:
        if (cats and e["category"] not in cats) or (only and e["id"] not in only):
            continue
        rel = e["path"]
        live = load_trainer(e["id"])
        if live["party"] == e["target"]["party"]:
            skipped += 1
            continue
        if file_sha(rel) != e["before"]["sha256"]:
            errors.append(f"{e['id']}: live file drifted from the manifest before-guard")
            continue
        live["party"] = e["target"]["party"]
        if not a.dry_run:
            dump_trainer(e["id"], live)
        applied += 1
    print(f"applied={applied} already_target={skipped} errors={len(errors)}{' (dry-run)' if a.dry_run else ''}")
    for m in errors:
        print("ERROR", m)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
