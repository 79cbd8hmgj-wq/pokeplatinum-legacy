#!/usr/bin/env python3
"""Extract one deterministic donor-review batch into a compact manifest.

This does not alter review status or select winners. It prepares a bounded set
of records for human/visual inspection.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--queue", required=True, type=Path)
    p.add_argument("--lane", required=True)
    p.add_argument("--batch", required=True, type=int)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    args = p.parse_args()

    data = json.loads(args.queue.read_text())
    rows = [
        r for r in data.get("records", [])
        if r.get("lane") == args.lane and int(r.get("batch") or 0) == args.batch
    ]
    if not rows:
        raise SystemExit(f"No records found for {args.lane} batch {args.batch}")

    rows.sort(key=lambda r: str(r.get("review_id") or ""))
    sources = Counter(r.get("source_id") for r in rows)
    types = Counter(r.get("asset_type") for r in rows)
    statuses = Counter(r.get("review_status") for r in rows)

    payload = {
        "schema_version": 1,
        "lane": args.lane,
        "batch": args.batch,
        "count": len(rows),
        "source_counts": dict(sorted(sources.items())),
        "asset_type_counts": dict(sorted(types.items())),
        "review_status_counts": dict(sorted(statuses.items())),
        "records": rows,
    }
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        f"# Donor Review Batch — {args.lane} / {args.batch:04d}",
        "",
        "Prepared for visual review only. No review status or Platinum resource is changed.",
        "",
        f"- Assets: **{len(rows)}**",
        "",
        "## Sources",
        "",
        "| Source | Assets |",
        "|---|---:|",
    ]
    for source, count in sorted(sources.items()):
        lines.append(f"| {source} | {count} |")

    lines += ["", "## Asset types", "", "| Type | Assets |", "|---|---:|"]
    for kind, count in sorted(types.items()):
        lines.append(f"| {kind} | {count} |")

    lines += ["", "## Records", "", "| # | Source | Type | Group | Asset ID | Source/render path | Status |", "|---:|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        path = r.get("render_path") or r.get("source_path") or ""
        lines.append(
            f"| {i} | {r.get('source_id') or ''} | {r.get('asset_type') or ''} | "
            f"{r.get('group') or ''} | {r.get('asset_id') or ''} | {path} | "
            f"{r.get('review_status') or ''} |"
        )

    args.write_md.parent.mkdir(parents=True, exist_ok=True)
    args.write_md.write_text("\n".join(lines) + "\n")
    print(f"Prepared {len(rows)} records for {args.lane} batch {args.batch}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
