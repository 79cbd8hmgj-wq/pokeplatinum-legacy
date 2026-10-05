#!/usr/bin/env python3
"""Deep structural inventory of Ranger visual packages.

Expands every LZ10 visual candidate found by inventory_ranger_visual_assets.py,
classifies the decompressed payload, and inventories NARC members without writing
bulk extracted binaries into the Platinum repository.

This is cataloging only. It does not select or import Platinum replacements.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from inspect_ranger_assets import inspect_file


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ranger-root", required=True, type=Path)
    p.add_argument("--inventory-json", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    args = p.parse_args()

    ranger_root = args.ranger_root.expanduser().resolve()
    inventory = json.loads(args.inventory_json.read_text())

    records = []
    statuses = Counter()
    payloads = Counter()
    member_types = Counter()
    packages_by_category = Counter()
    members_by_category = Counter()

    for row in inventory.get("records", []):
        if row.get("asset_type") != "compressed_visual_package":
            continue

        source_path = row["source_path"]
        path = ranger_root / source_path
        category = row.get("category") or "unknown"

        if not path.is_file():
            rec = {
                "path": source_path,
                "category": category,
                "status": "missing",
            }
        else:
            rec = inspect_file(path, ranger_root, None)
            rec["category"] = category
            rec["target_tags"] = row.get("target_tags", [])

        records.append(rec)
        packages_by_category[category] += 1
        statuses[rec.get("status", "unknown")] += 1

        payload_kind = rec.get("payload_kind")
        if payload_kind:
            payloads[payload_kind] += 1

        narc = rec.get("narc") or {}
        members_by_category[category] += int(narc.get("member_count", 0))
        for kind, count in narc.get("member_types", {}).items():
            member_types[kind] += count

    embedded_records = []
    for package in records:
        narc = package.get("narc")
        if not narc:
            continue
        for member in narc.get("members", []):
            embedded_records.append(
                {
                    "package_path": package["path"],
                    "category": package.get("category"),
                    "package_target_tags": package.get("target_tags", []),
                    "member_index": member.get("index"),
                    "member_name": member.get("name"),
                    "member_kind": member.get("kind"),
                    "member_size": member.get("size"),
                    "review_status": "unreviewed",
                }
            )

    report = {
        "schema_version": 1,
        "source_id": "ranger2",
        "packages": len(records),
        "status_counts": dict(sorted(statuses.items())),
        "payload_counts": dict(sorted(payloads.items())),
        "narc_member_type_counts": dict(sorted(member_types.items())),
        "packages_by_category": dict(sorted(packages_by_category.items())),
        "narc_members_by_category": dict(sorted(members_by_category.items())),
        "records": records,
        "embedded_resources": embedded_records,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(report, indent=2) + "\n")

    total_members = len(embedded_records)
    lines = [
        "# Ranger Deep Visual Package Inventory",
        "",
        "This report expands the compressed Ranger visual candidates structurally.",
        "It does not modify Platinum or choose replacement assets.",
        "",
        "## Summary",
        "",
        f"- Compressed visual packages scanned: **{len(records)}**",
        f"- Embedded NARC resources inventoried: **{total_members}**",
        "",
        "### Package status",
        "",
        "| Status | Packages |",
        "|---|---:|",
    ]
    for key, value in sorted(statuses.items()):
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "### Decompressed payload types",
        "",
        "| Payload | Packages |",
        "|---|---:|",
    ]
    for key, value in sorted(payloads.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "### Embedded NARC resource types",
        "",
        "| Resource kind | Members |",
        "|---|---:|",
    ]
    for key, value in sorted(member_types.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "### Category expansion",
        "",
        "| Category | Packages | Embedded NARC members |",
        "|---|---:|---:|",
    ]
    cats = sorted(set(packages_by_category) | set(members_by_category))
    for cat in cats:
        lines.append(
            f"| {cat} | {packages_by_category.get(cat, 0)} | "
            f"{members_by_category.get(cat, 0)} |"
        )

    args.write_md.parent.mkdir(parents=True, exist_ok=True)
    args.write_md.write_text("\n".join(lines) + "\n")

    print(
        f"Deep-scanned {len(records)} Ranger visual packages; "
        f"inventoried {total_members} embedded NARC resources."
    )
    return 1 if statuses.get("lz10_error") else 0


if __name__ == "__main__":
    raise SystemExit(main())
