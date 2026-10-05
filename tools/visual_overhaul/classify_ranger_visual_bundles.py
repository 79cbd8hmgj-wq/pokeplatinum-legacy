#!/usr/bin/env python3
"""Classify Ranger visual packages into reusable visual-resource bundle families.

Consumes the deep structural inventory and assigns package-level bundle profiles.
This is source cataloging only; it does not render, choose, or import Platinum art.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


STANDARD_VISUAL = {"ncgr", "nclr", "ncer", "nanr", "nscr"}
THREE_D = {"nsbmd", "nsbtx", "nsbca", "nsbta", "nsbtp", "nsbma"}


def package_profile(record: dict) -> tuple[str, list[str]]:
    payload = record.get("payload_kind")
    path = record.get("path", "")
    narc = record.get("narc") or {}
    counts = Counter()
    for member in narc.get("members", []):
        counts[member.get("kind", "unknown")] += 1

    kinds = set(counts)
    tags: list[str] = []

    if payload == "nscr":
        return "standalone_screen_map", ["background", "screen_map"]

    if payload == "54455800":
        if ".tex." in path.lower() or path.lower().endswith(".tex.lz"):
            return "ranger_texture_payload", ["field", "texture"]
        return "ranger_tex_payload", ["texture"]

    if payload != "narc":
        return "other_payload", []

    has_ncgr = counts["ncgr"] > 0
    has_nclr = counts["nclr"] > 0
    has_ncer = counts["ncer"] > 0
    has_nanr = counts["nanr"] > 0
    has_nscr = counts["nscr"] > 0
    has_3d = bool(kinds & THREE_D)

    if has_ncgr and has_nclr and has_ncer and has_nanr:
        tags += ["sprite", "animated"]
        return "animated_cell_sprite_bundle", tags
    if has_ncgr and has_nclr and has_ncer:
        tags += ["sprite"]
        return "cell_sprite_bundle", tags
    if has_ncgr and has_nclr and has_nscr:
        tags += ["background", "tilemap"]
        return "tiled_background_bundle", tags
    if has_ncgr and has_nclr:
        tags += ["graphics", "palette"]
        return "graphics_palette_bundle", tags
    if has_3d:
        tags += ["3d"]
        return "nitro_3d_bundle", tags
    if kinds & STANDARD_VISUAL:
        tags += ["partial_visual_bundle"]
        return "partial_standard_visual_bundle", tags
    return "opaque_narc_bundle", []


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--deep-inventory", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    args = p.parse_args()

    data = json.loads(args.deep_inventory.read_text())
    rows = []
    profiles = Counter()
    by_category = defaultdict(Counter)

    for rec in data.get("records", []):
        profile, tags = package_profile(rec)
        row = {
            "path": rec.get("path"),
            "category": rec.get("category"),
            "payload_kind": rec.get("payload_kind"),
            "profile": profile,
            "target_tags": sorted(set((rec.get("target_tags") or []) + tags)),
            "member_count": (rec.get("narc") or {}).get("member_count", 0),
            "member_types": (rec.get("narc") or {}).get("member_types", {}),
            "review_status": "unreviewed",
        }
        rows.append(row)
        profiles[profile] += 1
        by_category[row["category"] or "unknown"][profile] += 1

    report = {
        "schema_version": 1,
        "source_id": "ranger2",
        "packages": len(rows),
        "profile_counts": dict(sorted(profiles.items())),
        "rows": rows,
    }
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# Ranger Visual Bundle Classification",
        "",
        "Package-level classification derived from the deep Ranger structural inventory.",
        "No Platinum resources are modified or selected.",
        "",
        "## Bundle profiles",
        "",
        "| Profile | Packages |",
        "|---|---:|",
    ]
    for key, value in sorted(profiles.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "## Categories",
        "",
        "| Category | Profile | Packages |",
        "|---|---|---:|",
    ]
    for category in sorted(by_category):
        for profile, value in sorted(by_category[category].items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"| {category} | {profile} | {value} |")

    lines += [
        "",
        "## Notes",
        "",
        "- animated_cell_sprite_bundle: NCGR + NCLR + NCER + NANR present.",
        "- cell_sprite_bundle: NCGR + NCLR + NCER present.",
        "- tiled_background_bundle: NCGR + NCLR + NSCR present.",
        "- graphics_palette_bundle: NCGR + NCLR present without a complete cell/tilemap contract.",
        "- ranger_texture_payload: decompressed payload begins with TEX\\0 and source naming identifies a texture payload.",
        "- opaque_narc_bundle: NARC members exist but the package lacks a recognized complete standard visual bundle.",
        "- Classification is structural, not a usability decision.",
    ]

    args.write_md.parent.mkdir(parents=True, exist_ok=True)
    args.write_md.write_text("\n".join(lines) + "\n")
    print(f"Classified {len(rows)} Ranger visual packages into {len(profiles)} profiles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
