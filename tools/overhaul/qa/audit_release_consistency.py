#!/usr/bin/env python3
"""D7 release-consistency audit: classify every authority-marker hit in active repo documentation.

Searches tracked files under AGENTS.md, CLAUDE.md and docs/overhaul (excluding docs/overhaul/qa, which documents the
audit itself) for TODO / DRAFT PLAN / USER_DECISION_REQUIRED / UNRESOLVED / BLOCKED / PENDING|AWAITING IMPLEMENTATION /
superseded. Every hit must classify as non-actionable; an unclassified hit (ACTIVE) fails the audit. Also asserts the
stale-state strings D7 cleaned up do not return.

    python3 tools/overhaul/qa/audit_release_consistency.py [--write]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PAT = re.compile(r"TODO|DRAFT PLAN|USER_DECISION_REQUIRED|UNRESOLVED|BLOCKED|PENDING IMPLEMENTATION|AWAITING IMPLEMENTATION|[Ss]uperseded")
REPORT = "docs/overhaul/qa/RELEASE_CONSISTENCY_AUDIT.md"
JSON_OUT = "docs/overhaul/qa/release_consistency_audit.json"

# (class, path regex, line regex or None, reason) - first match wins.
RULES = [
    ("POLICY_DEFINITION", r"^(AGENTS|CLAUDE)\.md$", None, "defines how authority labels are interpreted; not gameplay authority"),
    ("ZERO_COUNT_RESOLVED", r".*", r"(0\s+UNRESOLVED|UNRESOLVED_AUTHORITY|USER_DECISION_REQUIRED families: 0|unresolved(_| )authority)",
     "records that the count is zero / resolved"),
    ("RESOLVED_DECISION_KEY", r"^docs/overhaul/implementation/(special_acquisitions|availability_families)\.json$", None,
     "key/label of a decision already resolved by SPECIAL_ACQUISITION.md (0 remain)"),
    ("HISTORICAL_SNAPSHOT", r"^docs/overhaul/implementation/(AVAILABILITY_IMPLEMENTATION_REPORT|AVAILABILITY_SOURCE_AUDIT|EVOLUTION_RECOVERY_AUDIT|SPECIAL_ACQUISITION)\.md$",
     None, "dated implementation/audit record; carries a historical or 'superseded/resolved' banner"),
    ("PROVENANCE", r"^docs/overhaul/(RECOVERY_INDEX\.md|EMERALD_PORT_PLAN\.md|implementation/(ledgers|archive)/|implementation/c1_move_edit_membership_recovery\.json|species/C3_IMPLEMENTATION_AUTHORITY\.md)",
     None, "recovery/provenance or non-Platinum reference material that explicitly labels itself non-authoritative"),
    ("SUPERSEDED_MARKER", r"^docs/overhaul/(evolution/EVOLUTION_SPEC\.md|implementation/evolution_manifest\.json|implementation/trainers/trainer_validation_rules\.json|trainers/.*\.md)$",
     None, "section/key that lists superseded alternatives so they are NOT implemented (or is an empty list / checklist item)"),
    ("BANNERED_NON_AUTHORITY", r"^docs/overhaul/events/LEGENDARY_MYTHICAL_EVENT_SPEC\.md$", None,
     "duplicate spec explicitly bannered NON-AUTHORITATIVE (D7)"),
    ("RESOLVED_HEADER", r"^docs/overhaul/AVAILABILITY_ARCHITECTURE\.md$", None, "historical note: formerly DRAFT PLAN, now bannered APPROVED/IMPLEMENTED"),
    ("STATUS_NOTE", r"^docs/overhaul/STATUS\.md$", None, "status text recording a resolved/zero state"),
]
# Stale-state assertions (file, regex that must NOT match).
STALE = [
    ("docs/overhaul/STATUS.md", r"Full QA/release \|\s*PLANNED", "QA still marked PLANNED"),
    ("docs/overhaul/STATUS.md", r"needs its locked spec \+ (implementation )?plan in the repo first", "D7 spec described as missing"),
    ("docs/overhaul/STATUS.md", r"Draft PR: \*\*#8\*\*", "canonical-docs draft PR listed as current"),
    ("docs/overhaul/DESIGN_PIPELINE.md", r"### D7[^\n]*\nStatus: `LOCKED SPEC`", "D7 still LOCKED SPEC only"),
    ("docs/overhaul/DESIGN_PIPELINE.md", r"### D2[^\n]*\nStatus: `LOCKED SPEC`", "D2 still LOCKED SPEC only"),
    ("docs/overhaul/DESIGN_PIPELINE.md", r"LEGENDARY_MYTHICAL_EVENT_SPEC", "points at the non-authoritative duplicate spec"),
    ("docs/overhaul/STATUS.md", r"Status:[^\n]*(CORE 1\.0 VERIFIED|RELEASE CANDIDATE)(?![^\n]*(NOT|not))", "premature VERIFIED / release-candidate claim"),
    ("docs/overhaul/STATUS.md", r"executes after subsystem implementation\*\*", "QA section still says it executes later"),
    ("docs/overhaul/AVAILABILITY_ARCHITECTURE.md", r"^> \*\*DRAFT PLAN — requires user approval\*\*", "stale DRAFT PLAN header"),
]


def tracked_hits():
    out = subprocess.run(["git", "grep", "-n", "-I", "-E", PAT.pattern, "--", "AGENTS.md", "CLAUDE.md", "docs/overhaul",
                          ":(exclude)docs/overhaul/qa"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    for l in out:
        path, ln, text = l.split(":", 2)
        yield path, int(ln), text


def classify(path, text):
    for cls, prx, lrx, why in RULES:
        if re.search(prx, path) and (lrx is None or re.search(lrx, text)):
            return cls, why
    return "ACTIVE", "unclassified - needs a banner, fix or owner decision"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    hits, counts = [], {}
    for path, ln, text in tracked_hits():
        cls, why = classify(path, text)
        counts[cls] = counts.get(cls, 0) + 1
        hits.append({"path": path, "line": ln, "class": cls, "reason": why, "text": text.strip()[:140]})
    stale = []
    for path, rx, why in STALE:
        try:
            body = open(os.path.join(ROOT, path), encoding="utf-8").read()
        except OSError:
            stale.append(f"{path}: missing")
            continue
        if re.search(rx, body, re.M):
            stale.append(f"{path}: {why}")
    active = [h for h in hits if h["class"] == "ACTIVE"]
    summary = {"hits": len(hits), "by_class": dict(sorted(counts.items())), "active_unclassified": len(active), "stale_state": stale}
    if a.write:
        with open(os.path.join(ROOT, JSON_OUT), "w", encoding="utf-8") as f:
            json.dump({"summary": summary, "hits": hits}, f, indent=1, sort_keys=True)
            f.write("\n")
        rows = "\n".join(f"| `{h['path']}:{h['line']}` | {h['class']} | {h['reason']} |" for h in hits)
        with open(os.path.join(ROOT, REPORT), "w", encoding="utf-8") as f:
            f.write("# Release Consistency Audit (D7 Phase 4)\n\nGenerated by `tools/overhaul/qa/audit_release_consistency.py --write`; "
                    "scope: `AGENTS.md`, `CLAUDE.md`, `docs/overhaul/**` excluding `docs/overhaul/qa/` (which describes this audit). "
                    "Search terms: `TODO`, `DRAFT PLAN`, `USER_DECISION_REQUIRED`, `UNRESOLVED`, `BLOCKED`, "
                    "`PENDING IMPLEMENTATION`, `AWAITING IMPLEMENTATION`, `superseded`.\n\n"
                    f"**Result:** {summary['hits']} hits; unclassified/active: **{summary['active_unclassified']}**; "
                    f"stale-state regressions: **{len(stale)}**.\n\n"
                    f"By class: `{json.dumps(summary['by_class'])}`\n\n"
                    "Fixes made by D7: replaced the stale `DRAFT PLAN` header in `AVAILABILITY_ARCHITECTURE.md`; added historical banner to "
                    "`AVAILABILITY_IMPLEMENTATION_REPORT.md`; bannered `events/LEGENDARY_MYTHICAL_EVENT_SPEC.md` as a non-authoritative duplicate "
                    "of `LEGENDARY_MYTHICAL_SPEC.md`; refreshed `STATUS.md` / `DESIGN_PIPELINE.md` (D2, D6 merged; D7 in progress).\n\n"
                    "| Location | Class | Reason |\n|---|---|---|\n" + rows + "\n")
    for h in active:
        print(f"ACTIVE {h['path']}:{h['line']}: {h['text']}")
    for s in stale:
        print("STALE", s)
    print(f"release consistency: {summary['hits']} hits, {len(active)} unclassified, {len(stale)} stale-state issue(s)")
    return 1 if active or stale else 0


if __name__ == "__main__":
    sys.exit(main())
