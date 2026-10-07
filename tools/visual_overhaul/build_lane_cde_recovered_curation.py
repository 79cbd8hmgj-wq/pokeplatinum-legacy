#!/usr/bin/env python3
"""Overlay evidence-backed recovery ledgers onto the Lane C/D/E baseline curation.

Only explicit recovery decisions may replace a baseline decode_issue.  Every asset_id is
preserved; overlays may not touch the same asset twice.  No Platinum resource is modified.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True, type=Path)
    ap.add_argument("--overlay", action="append", type=Path, default=[])
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    a = ap.parse_args()
    base = json.loads(a.baseline.read_text())
    rows = {r["asset_id"]: dict(r) for r in base["records"]}
    touched: dict[str, str] = {}
    changes = Counter()
    for path in a.overlay:
        for d in json.loads(path.read_text()).get("decisions", []):
            aid = d["asset_id"]
            if aid not in rows:
                raise SystemExit(f"overlay asset missing from baseline: {aid}")
            if aid in touched:
                raise SystemExit(f"asset decided by two overlays: {aid} ({touched[aid]}, {path.name})")
            if rows[aid]["review_status"] != "decode_issue":
                raise SystemExit(f"overlay expected decode_issue baseline: {aid}")
            if d["review_status"] not in {"usable", "reject", "decode_issue"}:
                raise SystemExit(f"invalid status: {aid}")
            touched[aid] = path.name
            r = rows[aid]
            changes[(r["review_status"], d["review_status"])] += 1
            r["review_status"], r["reason_code"], r["reason"] = d["review_status"], d.get("reason_code"), d.get("reason")
            r["recovery_evidence"] = {"ledger": path.name, **{k: v for k, v in d.items()
                                      if k not in {"asset_id", "review_status", "reason_code", "reason", "source_id", "source_path"}}}
    recs = [rows[k] for k in sorted(rows)]
    if len(recs) != base["asset_count"] or any(r["review_status"] == "unreviewed" for r in recs):
        raise SystemExit("coverage mismatch")
    counts = Counter((r.get("lane", "A_render_ready"), r["review_status"]) for r in recs)
    src = Counter((r["source_id"], r["review_status"]) for r in recs)
    payload = {"schema_version": 1, "scope": "lanes C/D/E recovered state", "asset_count": len(recs),
               "lane_status_counts": {f"{l}:{s}": n for (l, s), n in sorted(counts.items())},
               "source_status_counts": {f"{l}:{s}": n for (l, s), n in sorted(src.items())},
               "recovery_changes": {f"{x}_to_{y}": n for (x, y), n in sorted(changes.items())}, "records": recs}
    a.write_json.write_text(json.dumps(payload, indent=1) + "\n")
    md = ["# Recovered Curation State", "", "Baseline plus evidence-backed recoveries. No Platinum resources are modified.", "",
          f"- Assets: **{len(recs)}**", "", "| Lane | Status | Assets |", "|---|---|---:|"]
    md += [f"| {l} | {s} | {n} |" for (l, s), n in sorted(counts.items())]
    md += ["", "| Source | Status | Assets |", "|---|---|---:|"] + [f"| {l} | {s} | {n} |" for (l, s), n in sorted(src.items())]
    a.write_md.write_text("\n".join(md) + "\n")
    print(dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
