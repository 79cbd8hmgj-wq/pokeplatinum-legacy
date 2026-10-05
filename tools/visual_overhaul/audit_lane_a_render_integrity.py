#!/usr/bin/env python3
"""Audit every Lane A render-ready asset for materialized image integrity.

This is a technical evidence pass. It does NOT change donor review_status because
DONOR_ASSET_DATABASE.md reserves valid_render/usable for visual review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

RANGER_ID_RE = re.compile(
    r"^ranger2:pokemon:(?P<species>\d{3}):(?P<variant>\d{2}):"
    r"(?P<group>[^:]+):(?P<frame>[^:]+)$"
)


def locate(row: dict, roots: dict[str, Path], ranger_render_root: Path, platinum_root: Path) -> tuple[Path | None, str]:
    source = row.get("source_id")
    asset_type = row.get("asset_type")

    if source == "ranger2" and asset_type == "pokemon_sprite_frame":
        m = RANGER_ID_RE.match(str(row.get("asset_id") or ""))
        if not m:
            return None, "unparseable_ranger_asset_id"
        path = (
            ranger_render_root
            / m.group("species")
            / m.group("variant")
            / m.group("group")
            / f"{m.group('frame')}.png"
        )
        return path, "rerendered_ranger_frame"

    root = roots.get(str(source))
    source_path = row.get("source_path")
    render_path = row.get("render_path")

    candidates: list[tuple[Path, str]] = []
    if root and source_path:
        candidates.append((root / str(source_path), "source_path"))
    if root and render_path and render_path != source_path:
        candidates.append((root / str(render_path), "source_render_path"))
    if render_path:
        rp = Path(str(render_path))
        if not rp.is_absolute():
            candidates.append((platinum_root / rp, "platinum_render_path"))

    for path, provenance in candidates:
        if path.is_file():
            return path, provenance
    if candidates:
        return candidates[0][0], "missing"
    return None, "no_candidate_path"


def inspect_image(path: Path) -> dict:
    try:
        with Image.open(path) as im:
            im.load()
            rgba = im.convert("RGBA")
            alpha = rgba.getchannel("A")
            bbox = alpha.getbbox()
            pixel_hash = hashlib.sha256(
                f"{rgba.width}x{rgba.height}|".encode() + rgba.tobytes()
            ).hexdigest()
            file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            colors = rgba.getcolors(maxcolors=1_000_000)
            return {
                "technical_state": "blank" if bbox is None else "verified_nonblank",
                "width": rgba.width,
                "height": rgba.height,
                "mode": im.mode,
                "alpha_bbox": list(bbox) if bbox else None,
                "pixel_sha256": pixel_hash,
                "file_sha256": file_hash,
                "unique_rgba_colors": len(colors) if colors is not None else None,
                "file_size": path.stat().st_size,
                "error": None,
            }
    except Exception as exc:
        return {
            "technical_state": "decode_error",
            "width": None,
            "height": None,
            "mode": None,
            "alpha_bbox": None,
            "pixel_sha256": None,
            "file_sha256": None,
            "unique_rgba_colors": None,
            "file_size": path.stat().st_size if path.exists() else None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--queue", required=True, type=Path)
    p.add_argument("--platinum-root", required=True, type=Path)
    p.add_argument("--ranger-render-root", required=True, type=Path)
    p.add_argument("--ranger-root", required=True, type=Path)
    p.add_argument("--hgss-root", required=True, type=Path)
    p.add_argument("--diamond-root", required=True, type=Path)
    p.add_argument("--pmd-sky-root", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    args = p.parse_args()

    queue = json.loads(args.queue.read_text())
    rows = [r for r in queue.get("records", []) if r.get("lane") == "A_render_ready"]
    roots = {
        "ranger2": args.ranger_root.resolve(),
        "hgss": args.hgss_root.resolve(),
        "diamond": args.diamond_root.resolve(),
        "pmd_sky": args.pmd_sky_root.resolve(),
    }
    platinum_root = args.platinum_root.resolve()
    ranger_render_root = args.ranger_render_root.resolve()

    results = []
    for row in rows:
        path, provenance = locate(row, roots, ranger_render_root, platinum_root)
        result = {
            "review_id": row.get("review_id"),
            "batch": row.get("batch"),
            "logical_group": row.get("logical_group"),
            "asset_id": row.get("asset_id"),
            "source_id": row.get("source_id"),
            "asset_type": row.get("asset_type"),
            "species_dex": row.get("species_dex"),
            "group": row.get("group"),
            "source_path": row.get("source_path"),
            "render_path": row.get("render_path"),
            "review_status": row.get("review_status"),
            "materialized_path": str(path) if path else None,
            "materialization": provenance,
        }
        if path is None or not path.is_file():
            result.update({
                "technical_state": "missing",
                "width": None,
                "height": None,
                "mode": None,
                "alpha_bbox": None,
                "pixel_sha256": None,
                "file_sha256": None,
                "unique_rgba_colors": None,
                "file_size": None,
                "error": "materialized image not found",
            })
        else:
            result.update(inspect_image(path))
        results.append(result)

    state_counts = Counter(r["technical_state"] for r in results)
    source_counts = Counter(r["source_id"] for r in results)
    source_state_counts: dict[str, Counter] = defaultdict(Counter)
    type_state_counts: dict[str, Counter] = defaultdict(Counter)
    for r in results:
        source_state_counts[str(r["source_id"])][r["technical_state"]] += 1
        type_state_counts[str(r["asset_type"])][r["technical_state"]] += 1

    hash_groups: dict[str, list[str]] = defaultdict(list)
    for r in results:
        if r.get("pixel_sha256"):
            hash_groups[r["pixel_sha256"]].append(r["asset_id"])
    duplicate_groups = [
        {"pixel_sha256": h, "count": len(ids), "asset_ids": ids}
        for h, ids in hash_groups.items()
        if len(ids) > 1
    ]
    duplicate_groups.sort(key=lambda x: (-x["count"], x["pixel_sha256"]))

    payload = {
        "schema_version": 1,
        "lane": "A_render_ready",
        "asset_count": len(results),
        "technical_state_counts": dict(sorted(state_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "source_state_counts": {
            source: dict(sorted(counts.items()))
            for source, counts in sorted(source_state_counts.items())
        },
        "asset_type_state_counts": {
            kind: dict(sorted(counts.items()))
            for kind, counts in sorted(type_state_counts.items())
        },
        "exact_visual_duplicate_groups": len(duplicate_groups),
        "exact_visual_duplicate_assets": sum(g["count"] for g in duplicate_groups),
        "duplicate_groups": duplicate_groups,
        "records": results,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane A Render Integrity Audit",
        "",
        "Technical evidence pass over every A_render_ready record.",
        "",
        "Boundary: this audit does not change donor review_status. A decodable,",
        "nonblank PNG is not automatically a visually confirmed valid_render or usable asset.",
        "",
        "## Summary",
        "",
        f"- Lane A assets: **{len(results)}**",
        f"- Exact visual duplicate groups: **{len(duplicate_groups)}**",
        f"- Assets participating in exact duplicate groups: **{sum(g['count'] for g in duplicate_groups)}**",
        "",
        "### Technical states",
        "",
        "| State | Assets |",
        "|---|---:|",
    ]
    for state, count in sorted(state_counts.items()):
        lines.append(f"| {state} | {count} |")

    lines += ["", "### By source", "", "| Source | Assets | States |", "|---|---:|---|"]
    for source, count in sorted(source_counts.items()):
        states = ", ".join(
            f"{state}={n}" for state, n in sorted(source_state_counts[source].items())
        )
        lines.append(f"| {source} | {count} | {states} |")

    lines += [
        "",
        "## Interpretation",
        "",
        "- verified_nonblank: file materialized, decoded successfully, and has visible pixels.",
        "- blank: file decoded but has no visible pixels.",
        "- decode_error: file exists but Pillow could not decode it as an image.",
        "- missing: queue record could not be materialized from the checked-out donor/render roots.",
        "- Exact duplicate grouping is evidence only; it does not choose preferred/alternate assets.",
    ]
    args.write_md.parent.mkdir(parents=True, exist_ok=True)
    args.write_md.write_text("\n".join(lines) + "\n")

    print("Lane A assets:", len(results))
    print("Technical states:", dict(state_counts))
    print("Exact duplicate groups:", len(duplicate_groups))

    unexpected = state_counts.get("missing", 0) + state_counts.get("decode_error", 0)
    return 1 if unexpected else 0


if __name__ == "__main__":
    raise SystemExit(main())
