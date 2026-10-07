#!/usr/bin/env python3
"""Audit Lane B decode_issue records for concrete recovery routes.

This does not change curation states. It determines whether each unresolved
Pokémon-facing visual record can be recovered from:
- an already-present source-native PNG sibling;
- a Nitro 2D resource family that can be rendered from NCGR/NCLR/NCER/NANR;
- a NARC/container that should be unpacked first;
- a PMD-specific WAN/WTE/WTU/WAT/WBA decoder path;
- a Ranger package/embedded-resource decoder path;
- or genuinely unknown format/context.

The audit is deterministic and source-backed. No Platinum resources are written.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

NITRO_SUFFIXES = {".ncgr", ".nclr", ".ncer", ".nanr", ".nscr"}
NITRO_3D_SUFFIXES = {".nsbmd", ".nsbtx", ".nsbca", ".nsbta", ".nsbtp", ".nsbma"}
PMD_SUFFIXES = {".wan", ".wte", ".wtu", ".wat", ".wba"}
ARCHIVE_SUFFIXES = {".narc"}
PNG_SUFFIX = ".png"


def sibling_png(root: Path | None, source_path: str) -> str | None:
    if root is None:
        return None
    p = root / source_path
    candidates = [
        p.with_suffix(".png"),
        p.with_suffix(".PNG"),
    ]
    # Some decomps replace narc_NNNN.NCGR with narc_NNNN.png exactly.
    for c in candidates:
        if c.exists() and c.is_file():
            return str(c.relative_to(root))
    return None


def classify(source: str, asset_type: str, source_path: str, root: Path | None) -> tuple[str, str | None]:
    path = str(source_path or "")
    suffix = Path(path).suffix.lower()
    sib = sibling_png(root, path)
    if sib:
        return "source_png_equivalent", sib
    if suffix in NITRO_SUFFIXES:
        return "nitro_2d_decode", None
    if suffix in NITRO_3D_SUFFIXES:
        return "nitro_3d_decode", None
    if suffix in ARCHIVE_SUFFIXES or asset_type in {"visual_container", "compressed_visual_package"}:
        return "container_unpack_then_decode", None
    if source == "pmd_sky" and suffix in PMD_SUFFIXES:
        return "pmd_format_decode", None
    if source == "ranger2":
        return "ranger_embedded_decode", None
    if asset_type in {"embedded_visual_resource", "nitro_visual_resource", "raw_visual_resource"}:
        return "resource_decode_unknown_pairing", None
    return "format_context_unknown", None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curation", required=True, type=Path)
    ap.add_argument("--diamond-root", type=Path)
    ap.add_argument("--hgss-root", type=Path)
    ap.add_argument("--pmd-root", type=Path)
    ap.add_argument("--ranger-root", type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    args = ap.parse_args()

    roots = {
        "diamond": args.diamond_root,
        "hgss": args.hgss_root,
        "pmd_sky": args.pmd_root,
        "ranger2": args.ranger_root,
    }

    data = json.loads(args.curation.read_text())
    unresolved = [r for r in data["records"] if r["review_status"] == "decode_issue"]
    if len(unresolved) != data["status_counts"].get("decode_issue"):
        raise SystemExit("decode_issue count mismatch")

    records = []
    for r in unresolved:
        route, png = classify(
            r.get("source_id") or "",
            r.get("asset_type") or "",
            r.get("source_path") or "",
            roots.get(r.get("source_id")),
        )
        records.append({
            "asset_id": r["asset_id"],
            "source_id": r.get("source_id"),
            "asset_type": r.get("asset_type"),
            "group": r.get("group"),
            "source_path": r.get("source_path"),
            "suffix": Path(str(r.get("source_path") or "")).suffix.lower(),
            "recovery_route": route,
            "source_png_equivalent": png,
        })

    route_counts = Counter(r["recovery_route"] for r in records)
    source_route = defaultdict(Counter)
    type_route = defaultdict(Counter)
    for r in records:
        source_route[r["source_id"]][r["recovery_route"]] += 1
        type_route[r["asset_type"]][r["recovery_route"]] += 1

    payload = {
        "schema_version": 1,
        "lane": "B_pokemon_facing",
        "scope": "Recovery-route audit only; does not mutate curation state or write Platinum resources.",
        "decode_issue_count": len(records),
        "route_counts": dict(sorted(route_counts.items())),
        "source_route_counts": {k: dict(sorted(v.items())) for k, v in sorted(source_route.items())},
        "asset_type_route_counts": {k: dict(sorted(v.items())) for k, v in sorted(type_route.items())},
        "records": sorted(records, key=lambda x: x["asset_id"]),
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane B Decode Recovery Audit",
        "",
        "Recovery-route audit for every Lane B decode_issue record.",
        "No curation states or Platinum resources are modified.",
        "",
        f"- Decode issues audited: **{len(records)}**",
        "",
        "## Recovery routes",
        "",
        "| Route | Assets |",
        "|---|---:|",
    ]
    for route, count in sorted(route_counts.items()):
        lines.append(f"| {route} | {count} |")

    lines += [
        "",
        "## By source",
        "",
        "| Source | Route | Assets |",
        "|---|---|---:|",
    ]
    for source, counts in sorted(source_route.items()):
        for route, count in sorted(counts.items()):
            lines.append(f"| {source} | {route} | {count} |")

    lines += [
        "",
        "## Recovery policy",
        "",
        "- source_png_equivalent: verify equivalence and inherit/merge visual curation evidence.",
        "- nitro_2d_decode: pair NCGR/NCLR/NCER/NANR and render deterministically.",
        "- container_unpack_then_decode: unpack NARC/package first, then classify internal resources.",
        "- pmd_format_decode: use or add PMD WAN/WTE/WTU/WAT/WBA decoder.",
        "- ranger_embedded_decode: use Ranger package/resource reconstruction tooling.",
        "- unknown routes remain decode_issue until format/context is resolved.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")

    print("Decode issues:", len(records))
    print("Routes:", dict(route_counts))
    print("By source:", {k: dict(v) for k, v in source_route.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
