#!/usr/bin/env python3
"""Rank/select ONE subsystem: groups + evidence + rules -> ledgers/<subsystem>.json.

Usage: select_subsystem.py --subsystem pokemon_icons [--check]
`--check` re-derives and fails if the committed ledger differs (reproducibility check).
"""
from __future__ import annotations

import argparse
import collections
import sys

from common import *  # noqa: F401,F403
import rules as engine


def evidence_path(subsystem: str) -> Path:
    return SEL / "evidence" / f"{subsystem}.json"


def derive(subsystem: str) -> dict:
    subs = jload(SUBSYSTEMS_JSON)["subsystems"]
    if subsystem not in subs:
        raise SystemExit(f"unknown subsystem {subsystem}")
    rules = jload(RULES_JSON)
    gdoc = jload(GROUPS_JSON)
    groups = [g for g in gdoc["groups"] if g["subsystem"] == subsystem]
    ep = evidence_path(subsystem)
    evidence = jload(ep) if ep.is_file() else {"entries": {}}
    decisions, targets = engine.decide(groups, evidence, rules, subs)
    roles = collections.Counter(d["role"] for d in decisions)
    reasons = collections.Counter(f'{d["role"]}:{d["reason_code"]}' for d in decisions)
    by_src = collections.Counter(f'{d["source_id"]}:{d["role"]}' for d in decisions)
    res = collections.Counter("native" if t["resolution"] == "platinum_native" else "donor" for t in targets)
    return {
        "schema_version": 1,
        "subsystem": subsystem,
        "rules_version": rules["rules_version"],
        "inputs": {
            "subsystem_groups_digest": subsystem_groups_digest(groups),
            "recovered_ledger_sha256": gdoc["inputs"]["recovered_ledger_sha256"],
            "subsystems_sha256": file_sha256(SUBSYSTEMS_JSON),
            "rules_sha256": file_sha256(RULES_JSON),
            "evidence_file": str(ep.relative_to(ROOT)) if ep.is_file() else None,
            "evidence_sha256": file_sha256(ep) if ep.is_file() else None,
        },
        "summary": {
            "groups": len(decisions),
            "targets": len(targets),
            "roles": dict(sorted(roles.items())),
            "role_reason": dict(sorted(reasons.items())),
            "source_role": dict(sorted(by_src.items())),
            "target_resolution": dict(sorted(res.items())),
            "needs_evidence": sum(d["needs_evidence"] for d in decisions),
        },
        "targets": targets,
        "decisions": decisions,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subsystem", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    doc = derive(a.subsystem)
    out = SEL / "ledgers" / f"{a.subsystem}.json"
    if a.check:
        if not out.is_file() or jload(out) != doc:
            print(f"{out.name} missing or not reproducible", file=sys.stderr)
            return 1
        print(f"{out.name} reproducible")
        return 0
    jdump(out, doc)
    print(json.dumps(doc["summary"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
