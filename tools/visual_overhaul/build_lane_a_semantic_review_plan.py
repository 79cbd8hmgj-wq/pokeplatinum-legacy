#!/usr/bin/env python3
"""Build a compact semantic-review plan for Lane A.

Planning only: no review_status mutation, preferred-donor choice, or Platinum writes.
P1 Ranger frames are summarized from the structural review ledger. P3 native
HGSS/Diamond PNGs are collapsed into semantic groups using review-queue metadata.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def path_family(path: str) -> str:
    parts = [p for p in str(path or "").replace("\\", "/").split("/") if p]
    return "/".join(parts[:3]) if parts else ""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", required=True, type=Path)
    p.add_argument("--queue", required=True, type=Path)
    p.add_argument("--priority", required=True, type=Path)
    p.add_argument("--p1-review", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    args = p.parse_args()

    catalog = json.loads(args.catalog.read_text())
    queue = json.loads(args.queue.read_text())
    priority = json.loads(args.priority.read_text())
    p1_review = json.loads(args.p1_review.read_text())

    catalog_assets = catalog.get("assets", [])
    queue_assets = {a["asset_id"]: a for a in queue.get("records", [])}
    priority_rows = priority.get("records", [])

    p1 = [r for r in priority_rows if r.get("priority") == "P1_ranger_species_render"]
    p3 = [r for r in priority_rows if r.get("priority") == "P3_native_source_png"]

    p1_decisions = {r["asset_id"]: r for r in p1_review.get("records", [])}
    if set(r["asset_id"] for r in p1) != set(p1_decisions):
        raise SystemExit("P1 priority/review coverage mismatch")

    p1_status = Counter(r.get("review_status") for r in p1_decisions.values())
    p1_species = defaultdict(Counter)
    for row in p1_decisions.values():
        p1_species[row.get("species_dex")][row.get("review_status")] += 1

    missing = [r["asset_id"] for r in p3 if r["asset_id"] not in queue_assets]
    if missing:
        raise SystemExit("P3 candidate missing from review queue: " + missing[0])

    grouped = defaultdict(list)
    for r in p3:
        a = queue_assets[r["asset_id"]]
        key = (
            a.get("source_id"),
            a.get("group"),
            tuple(sorted(a.get("target_tags") or [])),
            a.get("asset_type"),
            path_family(a.get("source_path")),
        )
        grouped[key].append((r, a))

    groups = []
    for key, rows in sorted(grouped.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        source, group, tags, asset_type, family = key
        widths = Counter((r.get("width"), r.get("height")) for r, _ in rows)
        statuses = Counter((a.get("review_status") or "unreviewed") for _, a in rows)
        groups.append({
            "source_id": source,
            "group": group,
            "asset_type": asset_type,
            "target_tags": list(tags),
            "path_family": family,
            "candidate_count": len(rows),
            "queue_status_counts": dict(sorted(statuses.items())),
            "dimension_counts": [
                {"width": wh[0], "height": wh[1], "count": count}
                for wh, count in sorted(widths.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1])))
            ],
            "examples": [
                {
                    "asset_id": r["asset_id"],
                    "source_path": a.get("source_path"),
                    "width": r.get("width"),
                    "height": r.get("height"),
                    "alpha_bbox": r.get("alpha_bbox"),
                }
                for r, a in rows[:8]
            ],
        })

    payload = {
        "schema_version": 1,
        "lane": "A_render_ready",
        "scope": "Semantic review planning only; no review_status mutation and no Platinum writes.",
        "catalog_asset_count": len(catalog_assets),
        "queue_asset_count": len(queue_assets),
        "lane_a_candidate_count": len(priority_rows),
        "p1": {
            "candidate_count": len(p1),
            "status_counts": dict(sorted(p1_status.items())),
            "species_count": len(p1_species),
        },
        "p3": {
            "candidate_count": len(p3),
            "semantic_group_count": len(groups),
            "source_counts": dict(sorted(Counter(r.get("source_id") for r in p3).items())),
            "groups": groups,
        },
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    tick = chr(96)
    lines = [
        "# Lane A Semantic Review Plan",
        "",
        "Compact semantic grouping for final Lane A curation. This file does not",
        "change donor review statuses or modify Platinum resources.",
        "",
        "## Coverage",
        "",
        f"- Unified catalog assets: **{len(catalog_assets)}**",
        f"- Review queue assets: **{len(queue_assets)}**",
        f"- Lane A unique candidates: **{len(priority_rows)}**",
        f"- P1 Ranger candidates: **{len(p1)}**",
        f"- P3 native HGSS/Diamond PNG candidates: **{len(p3)}**",
        f"- P3 semantic groups: **{len(groups)}**",
        "",
        "### P1 technical status",
        "",
        "| Status | Candidates |",
        "|---|---:|",
    ]
    for status, count in sorted(p1_status.items()):
        lines.append(f"| {status} | {count} |")

    lines += [
        "",
        "## P3 semantic groups",
        "",
        "| # | Source | Group | Tags | Path family | Candidates | Queue status |",
        "|---:|---|---|---|---|---:|---|",
    ]
    for i, g in enumerate(groups, 1):
        tags = ", ".join(g["target_tags"]) or "—"
        st = ", ".join(f"{k}={v}" for k, v in g["queue_status_counts"].items())
        lines.append(
            f"| {i} | {g['source_id']} | {g['group'] or '—'} | {tags} | "
            f"{tick}{g['path_family']}{tick} | {g['candidate_count']} | {st} |"
        )

    lines += [
        "",
        "## Curation boundary",
        "",
        "- P1 valid_render is reconstruction evidence, not automatically usable.",
        "- P3 native PNG status still requires visual/semantic review.",
        "- Grouping is for efficient review; decisions must remain traceable to asset_id.",
        "- Exact duplicates stay represented by their Lane A visual representative.",
        "- No preferred donor or Platinum replacement is selected here.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")

    print("Lane A candidates:", len(priority_rows))
    print("P1:", len(p1), dict(p1_status))
    print("P3:", len(p3), "semantic groups:", len(groups))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
