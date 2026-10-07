#!/usr/bin/env python3
"""Build a compact semantic-review plan for Lane B Pokémon-facing donor assets.

Lane B contains Pokémon/trainer/icon/portrait/overworld/battle-facing candidates
that are not already render-ready. This pass groups all records by stable
source/group/type/tag/path semantics so decoding/curation can proceed in bounded
families instead of one file at a time.

Planning only: no review_status mutation, no preferred-donor choice, no Platinum writes.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def path_family(path: str) -> str:
    parts = [p for p in str(path or "").replace("\\", "/").split("/") if p]
    return "/".join(parts[:4]) if parts else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    args = ap.parse_args()

    queue = json.loads(args.queue.read_text())
    rows = [r for r in queue.get("records", []) if r.get("lane") == "B_pokemon_facing"]
    if len(rows) != 15157:
        raise SystemExit(f"Lane B count mismatch: {len(rows)} != 15157")

    grouped = defaultdict(list)
    for r in rows:
        key = (
            r.get("source_id"),
            r.get("group"),
            r.get("asset_type"),
            tuple(sorted(r.get("target_tags") or [])),
            path_family(r.get("source_path")),
        )
        grouped[key].append(r)

    groups = []
    for key, members in sorted(grouped.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        source, group, asset_type, tags, family = key
        groups.append({
            "source_id": source,
            "group": group,
            "asset_type": asset_type,
            "target_tags": list(tags),
            "path_family": family,
            "asset_count": len(members),
            "review_status_counts": dict(sorted(Counter(
                m.get("review_status") or "unreviewed" for m in members
            ).items())),
            "batch_counts": dict(sorted(Counter(int(m.get("batch") or 0) for m in members).items())),
            "examples": [
                {
                    "asset_id": m.get("asset_id"),
                    "source_path": m.get("source_path"),
                    "review_id": m.get("review_id"),
                }
                for m in members[:10]
            ],
        })

    payload = {
        "schema_version": 1,
        "lane": "B_pokemon_facing",
        "scope": "Semantic grouping only; no review_status mutation and no Platinum writes.",
        "asset_count": len(rows),
        "semantic_group_count": len(groups),
        "source_counts": dict(sorted(Counter(r.get("source_id") for r in rows).items())),
        "asset_type_counts": dict(sorted(Counter(r.get("asset_type") for r in rows).items())),
        "review_status_counts": dict(sorted(Counter(
            r.get("review_status") or "unreviewed" for r in rows
        ).items())),
        "groups": groups,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane B Semantic Review Plan",
        "",
        "Compact semantic grouping for Pokémon-facing donor assets that are not already render-ready.",
        "No review statuses or Platinum resources are changed.",
        "",
        "## Coverage",
        "",
        f"- Lane B assets: **{len(rows)}**",
        f"- Semantic groups: **{len(groups)}**",
        "",
        "### By source",
        "",
        "| Source | Assets |",
        "|---|---:|",
    ]
    for source, count in sorted(payload["source_counts"].items()):
        lines.append(f"| {source} | {count} |")

    lines += [
        "",
        "### By asset type",
        "",
        "| Asset type | Assets |",
        "|---|---:|",
    ]
    for kind, count in sorted(payload["asset_type_counts"].items()):
        lines.append(f"| {kind} | {count} |")

    lines += [
        "",
        "## Semantic groups",
        "",
        "| # | Source | Group | Type | Tags | Path family | Assets | Statuses |",
        "|---:|---|---|---|---|---|---:|---|",
    ]
    tick = chr(96)
    for i, g in enumerate(groups, 1):
        tags = ", ".join(g["target_tags"]) or "—"
        statuses = ", ".join(f"{k}={v}" for k, v in g["review_status_counts"].items())
        lines.append(
            f"| {i} | {g['source_id']} | {g['group'] or '—'} | {g['asset_type']} | "
            f"{tags} | {tick}{g['path_family']}{tick} | {g['asset_count']} | {statuses} |"
        )

    lines += [
        "",
        "## Next-pass policy",
        "",
        "- Render/decode families first where a deterministic decoder already exists or can be added.",
        "- Preserve opaque/container assets as decode_issue until their format/context is trustworthy.",
        "- Plausible Pokémon/trainer/icon/portrait/overworld assets become usable only after their",
        "  decoded visual form or source semantics support a real Platinum use.",
        "- Do not select preferred donors or write Platinum resources during Lane B curation.",
    ]

    args.write_md.write_text("\n".join(lines) + "\n")
    print("Lane B assets:", len(rows))
    print("Semantic groups:", len(groups))
    print("Sources:", payload["source_counts"])
    print("Types:", payload["asset_type_counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
