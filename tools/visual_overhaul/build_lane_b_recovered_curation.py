#!/usr/bin/env python3
"""Overlay proven Lane B recoveries onto the baseline curation ledger.

This is the authoritative current Lane B state while decode recovery proceeds.
Only explicit evidence-backed recovery ledgers may replace a baseline decision.
No preferred donor is selected and no Platinum resource is modified.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load_decisions(path: Path, key: str) -> list[dict]:
    data = json.loads(path.read_text())
    return data.get(key, [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True, type=Path)
    ap.add_argument("--recovery-audit", required=True, type=Path)
    ap.add_argument("--source-png", required=True, type=Path)
    ap.add_argument("--diamond-icons", required=True, type=Path)
    ap.add_argument("--extra-overlay", type=Path, action="append", default=[])
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    args = ap.parse_args()

    baseline = json.loads(args.baseline.read_text())
    audit = json.loads(args.recovery_audit.read_text())
    rows = {r["asset_id"]: dict(r) for r in baseline["records"]}

    overlays = []
    for path in (args.source_png, args.diamond_icons, *args.extra_overlay):
        data = json.loads(path.read_text())
        overlays.extend(data.get("decisions", []))

    changed = Counter()
    for d in overlays:
        aid = d["asset_id"]
        if aid not in rows:
            raise SystemExit(f"recovery asset missing from Lane B baseline: {aid}")
        old = rows[aid]["review_status"]
        new = d["review_status"]
        if old != "decode_issue":
            raise SystemExit(f"recovery overlay expected decode_issue baseline: {aid}={old}")
        if new not in {"usable", "reject", "decode_issue"}:
            raise SystemExit(f"invalid recovery status: {aid}={new}")
        rows[aid]["review_status"] = new
        rows[aid]["reason_code"] = d.get("reason_code")
        rows[aid]["reason"] = d.get("reason")
        rows[aid]["recovery_evidence"] = {
            k: v for k, v in d.items()
            if k not in {"asset_id", "source_id", "group", "source_path", "review_status", "reason_code", "reason"}
        }
        changed[(old, new)] += 1

    audit_by_id = {r["asset_id"]: r for r in audit["records"]}
    unresolved_routes = Counter()
    unresolved_source_routes = defaultdict(Counter)
    for aid, r in rows.items():
        if r["review_status"] != "decode_issue":
            continue
        ar = audit_by_id.get(aid)
        if ar is None:
            raise SystemExit(f"decode_issue missing from recovery audit: {aid}")
        route = ar["recovery_route"]
        unresolved_routes[route] += 1
        unresolved_source_routes[r["source_id"]][route] += 1

    records = [rows[k] for k in sorted(rows)]
    counts = Counter(r["review_status"] for r in records)
    if len(records) != 15157 or sum(counts.values()) != 15157:
        raise SystemExit("Lane B recovered-state coverage mismatch")

    payload = {
        "schema_version": 1,
        "lane": "B_pokemon_facing",
        "asset_count": len(records),
        "status_counts": dict(sorted(counts.items())),
        "recovery_changes": {
            f"{a}_to_{b}": n for (a, b), n in sorted(changed.items())
        },
        "remaining_decode_routes": dict(sorted(unresolved_routes.items())),
        "remaining_decode_source_routes": {
            s: dict(sorted(c.items())) for s, c in sorted(unresolved_source_routes.items())
        },
        "records": records,
    }
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane B Recovered Curation State",
        "",
        "Current Lane B curation after applying completed decode-recovery evidence.",
        "No preferred donor is selected and no Platinum resources are modified.",
        "",
        "## Status",
        "",
        f"- Assets: **{len(records)}**",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: **{count}**")

    lines += [
        "",
        "## Recovery changes",
        "",
        "| Change | Assets |",
        "|---|---:|",
    ]
    for (old, new), count in sorted(changed.items()):
        lines.append(f"| {old} -> {new} | {count} |")

    lines += [
        "",
        "## Remaining decode routes",
        "",
        "| Route | Assets |",
        "|---|---:|",
    ]
    for route, count in sorted(unresolved_routes.items()):
        lines.append(f"| {route} | {count} |")

    lines += [
        "",
        "## Remaining routes by source",
        "",
        "| Source | Route | Assets |",
        "|---|---|---:|",
    ]
    for source, counts2 in sorted(unresolved_source_routes.items()):
        for route, count in sorted(counts2.items()):
            lines.append(f"| {source} | {route} | {count} |")

    args.write_md.write_text("\n".join(lines) + "\n")
    print("Lane B recovered state:", dict(counts))
    print("Recovery changes:", dict(changed))
    print("Remaining decode routes:", dict(unresolved_routes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
