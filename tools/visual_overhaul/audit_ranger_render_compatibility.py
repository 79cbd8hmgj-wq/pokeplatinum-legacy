#!/usr/bin/env python3
"""Audit rendered Ranger candidates against Platinum's 80x80 battle-sprite geometry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image

TARGET_W = 80
TARGET_H = 80


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--render-manifest", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--report", type=Path)
    return p.parse_args()


def bbox_rgba(path: Path) -> tuple[tuple[int, int, int, int] | None, int, tuple[int, int]]:
    with Image.open(path) as im:
        rgba = im.convert("RGBA")
        alpha = rgba.getchannel("A")
        bbox = alpha.getbbox()
        opaque = sum(1 for v in alpha.getdata() if v)
        return bbox, opaque, rgba.size


def classify(width: int, height: int) -> str:
    # These are deliberately coarse census classes, not final resize policy.
    # Exact transform thresholds must be data-derived from the full corpus.
    if width <= 56 and height <= 56:
        return "fits_small"
    if width <= TARGET_W and height <= TARGET_H:
        return "fits"
    if width <= 96 and height <= 96:
        return "geometry_close"
    return "oversize"


def main() -> None:
    args = parse_args()
    source = json.loads(args.render_manifest.read_text())
    out_records: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    missing = 0

    base = args.render_manifest.resolve().parent
    for pkg in source.get("packages", []):
        for candidate in pkg.get("renders", []):
            raw_path = candidate.get("render_path")
            row: dict[str, Any] = {
                "national_dex": pkg.get("national_dex"),
                "package_variant": pkg.get("package_variant"),
                **candidate,
            }
            if not raw_path:
                row["status"] = "failed"
                row["warnings"] = ["render_path missing"]
                missing += 1
                out_records.append(row)
                continue

            path = Path(raw_path)
            if not path.is_absolute():
                path = (base / path).resolve()
            if not path.exists():
                row["status"] = "failed"
                row["warnings"] = [f"render_path not found: {path}"]
                missing += 1
                out_records.append(row)
                continue

            bbox, opaque, canvas = bbox_rgba(path)
            row["native_canvas_width"] = canvas[0]
            row["native_canvas_height"] = canvas[1]
            row["opaque_pixel_count"] = opaque
            if bbox is None:
                row.update({
                    "bbox_x": None,
                    "bbox_y": None,
                    "bbox_width": 0,
                    "bbox_height": 0,
                    "width_ratio": 0.0,
                    "height_ratio": 0.0,
                    "max_axis_ratio": 0.0,
                    "compatibility_class": "fits_small",
                    "status": "blank",
                })
                row.setdefault("warnings", []).append("render is fully transparent")
            else:
                l, t, r, b = bbox
                w, h = r - l, b - t
                wr = w / TARGET_W
                hr = h / TARGET_H
                row.update({
                    "bbox_x": l,
                    "bbox_y": t,
                    "bbox_width": w,
                    "bbox_height": h,
                    "width_ratio": round(wr, 6),
                    "height_ratio": round(hr, 6),
                    "max_axis_ratio": round(max(wr, hr), 6),
                    "compatibility_class": classify(w, h),
                    "status": "ok",
                })
                counts[row["compatibility_class"]] = counts.get(row["compatibility_class"], 0) + 1
            out_records.append(row)

    payload = {
        "schema_version": 1,
        "target": {"width": TARGET_W, "height": TARGET_H},
        "policy": "Compatibility classes are census labels only; final scaling/anchoring thresholds remain data-derived.",
        "summary": {
            "candidates": len(out_records),
            "missing_or_invalid": missing,
            "classes": dict(sorted(counts.items())),
        },
        "candidates": out_records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    if args.report:
        lines = [
            "# Ranger -> Platinum Render Compatibility Census",
            "",
            "Target battle-sprite cell: **80x80**.",
            "",
            "These classes are triage labels, not final automatic conversion thresholds.",
            "",
            "## Summary",
            "",
            f"- Candidates: **{len(out_records)}**",
            f"- Missing/invalid renders: **{missing}**",
        ]
        for key in ("fits_small", "fits", "geometry_close", "oversize"):
            lines.append(f"- {key}: **{counts.get(key, 0)}**")
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("\n".join(lines) + "\n")

    print(f"Audited {len(out_records)} Ranger render candidates; {missing} invalid.")


if __name__ == "__main__":
    main()
