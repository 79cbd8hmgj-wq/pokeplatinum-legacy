#!/usr/bin/env python3

"""Audit HGSS Pokemon battle sprites against Platinum source assets.

The audit has two layers:

1. rendered-art classification (identical / palette-only / art-diff)
2. conservative frame-geometry triage for art-diff sprites

Geometry triage is intentionally not a runtime-safety claim. It only identifies donor
sprites whose two 80x80 frames remain close to Platinum's existing footprint, so they
can be prioritized for staged emulator validation while keeping Platinum's existing
sprite_data.json animation contract.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLATINUM_POKEMON = ROOT / "res" / "pokemon"
SPECIES_LIST = ROOT / "generated" / "species.txt"

EXPECTED_SIZE = (160, 80)
FRAME_SIZE = (80, 80)
VIEWS = (
    ("female_back.png", "female/back.png"),
    ("male_back.png", "male/back.png"),
    ("female_front.png", "female/front.png"),
    ("male_front.png", "male/front.png"),
)

# Conservative static-geometry thresholds. These only prioritize runtime test
# candidates; they do not automatically authorize an import.
MAX_BOTTOM_DELTA = 3
MAX_CENTER_DELTA = 4.0
MAX_SIZE_DELTA = 10
MAX_MOTION_DELTA = 5.0


@dataclass
class FrameGeometry:
    frame: int
    platinum_bbox: tuple[int, int, int, int] | None
    hgss_bbox: tuple[int, int, int, int] | None
    bottom_delta: int | None
    center_x_delta: float | None
    center_y_delta: float | None
    width_delta: int | None
    height_delta: int | None
    donor_touches_edge: bool


@dataclass
class GeometryResult:
    status: str
    reasons: list[str]
    frames: list[FrameGeometry]
    motion_delta_x: float | None
    motion_delta_y: float | None


@dataclass
class Result:
    species_id: int
    species: str
    view: str
    status: str
    geometry: GeometryResult | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--donor-root",
        required=True,
        type=Path,
        help="HGSS files/poketool/pokegra/pokegra directory",
    )
    parser.add_argument(
        "--report",
        required=True,
        type=Path,
        help="Markdown report output path",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Optional machine-readable JSON output path",
    )
    return parser.parse_args()


def species_dir_name(species_const: str) -> str:
    return species_const.removeprefix("SPECIES_").lower()


def palette_rgb(image: Image.Image) -> list[tuple[int, int, int]]:
    palette = image.getpalette()
    if palette is None:
        raise ValueError("indexed PNG is missing a palette")
    return [tuple(palette[i:i + 3]) for i in range(0, 48, 3)]


def rendered_rgba(image: Image.Image) -> bytes:
    palette = palette_rgb(image)
    out = bytearray()
    for index in image.getdata():
        if index == 0:
            out.extend((0, 0, 0, 0))
        else:
            r, g, b = palette[index]
            out.extend((r, g, b, 255))
    return bytes(out)


def classify(platinum: Path, hgss: Path) -> str:
    pt_empty = platinum.stat().st_size == 0
    hg_empty = hgss.stat().st_size == 0

    if pt_empty or hg_empty:
        if pt_empty and hg_empty:
            return "both-empty"
        return "structure-diff"

    with Image.open(platinum) as pt, Image.open(hgss) as hg:
        if pt.mode != "P" or hg.mode != "P":
            return f"mode-diff({pt.mode}/{hg.mode})"
        if pt.size != hg.size:
            return f"size-diff({pt.size[0]}x{pt.size[1]}/{hg.size[0]}x{hg.size[1]})"
        if pt.size != EXPECTED_SIZE:
            return f"unexpected-size({pt.size[0]}x{pt.size[1]})"

        pt_pixels = bytes(pt.getdata())
        hg_pixels = bytes(hg.getdata())

        if pt_pixels == hg_pixels:
            if palette_rgb(pt) == palette_rgb(hg):
                return "identical"
            if rendered_rgba(pt) == rendered_rgba(hg):
                return "palette-metadata-only"
            return "palette-only"

        if rendered_rgba(pt) == rendered_rgba(hg):
            return "index-remap-only"

        return "art-diff"


def frame_bbox(image: Image.Image, frame: int) -> tuple[int, int, int, int] | None:
    x0 = frame * FRAME_SIZE[0]
    crop = image.crop((x0, 0, x0 + FRAME_SIZE[0], FRAME_SIZE[1]))
    pixels = list(crop.getdata())
    xs: list[int] = []
    ys: list[int] = []
    for i, index in enumerate(pixels):
        if index == 0:
            continue
        xs.append(i % FRAME_SIZE[0])
        ys.append(i // FRAME_SIZE[0])
    if not xs:
        return None
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def bbox_center(bbox: tuple[int, int, int, int]) -> tuple[float, float]:
    left, top, right, bottom = bbox
    return ((left + right) / 2.0, (top + bottom) / 2.0)


def bbox_size(bbox: tuple[int, int, int, int]) -> tuple[int, int]:
    left, top, right, bottom = bbox
    return (right - left, bottom - top)


def touches_edge(bbox: tuple[int, int, int, int] | None) -> bool:
    if bbox is None:
        return False
    left, top, right, bottom = bbox
    return left == 0 or top == 0 or right == FRAME_SIZE[0] or bottom == FRAME_SIZE[1]


def geometry_compare(platinum: Path, hgss: Path) -> GeometryResult:
    frames: list[FrameGeometry] = []
    reasons: list[str] = []

    with Image.open(platinum) as pt, Image.open(hgss) as hg:
        pt.load()
        hg.load()

        for frame in range(2):
            pt_bbox = frame_bbox(pt, frame)
            hg_bbox = frame_bbox(hg, frame)

            if pt_bbox is None or hg_bbox is None:
                frames.append(
                    FrameGeometry(
                        frame=frame,
                        platinum_bbox=pt_bbox,
                        hgss_bbox=hg_bbox,
                        bottom_delta=None,
                        center_x_delta=None,
                        center_y_delta=None,
                        width_delta=None,
                        height_delta=None,
                        donor_touches_edge=touches_edge(hg_bbox),
                    )
                )
                reasons.append(f"frame {frame}: empty-frame mismatch")
                continue

            pt_center = bbox_center(pt_bbox)
            hg_center = bbox_center(hg_bbox)
            pt_size = bbox_size(pt_bbox)
            hg_size = bbox_size(hg_bbox)
            geom = FrameGeometry(
                frame=frame,
                platinum_bbox=pt_bbox,
                hgss_bbox=hg_bbox,
                bottom_delta=hg_bbox[3] - pt_bbox[3],
                center_x_delta=hg_center[0] - pt_center[0],
                center_y_delta=hg_center[1] - pt_center[1],
                width_delta=hg_size[0] - pt_size[0],
                height_delta=hg_size[1] - pt_size[1],
                donor_touches_edge=touches_edge(hg_bbox),
            )
            frames.append(geom)

            if geom.donor_touches_edge:
                reasons.append(f"frame {frame}: donor art touches 80x80 frame edge")
            if abs(geom.bottom_delta) > MAX_BOTTOM_DELTA:
                reasons.append(
                    f"frame {frame}: bottom shift {geom.bottom_delta:+d}px exceeds {MAX_BOTTOM_DELTA}px"
                )
            if abs(geom.center_x_delta) > MAX_CENTER_DELTA:
                reasons.append(
                    f"frame {frame}: x-center shift {geom.center_x_delta:+.1f}px exceeds {MAX_CENTER_DELTA:g}px"
                )
            if abs(geom.center_y_delta) > MAX_CENTER_DELTA:
                reasons.append(
                    f"frame {frame}: y-center shift {geom.center_y_delta:+.1f}px exceeds {MAX_CENTER_DELTA:g}px"
                )
            if abs(geom.width_delta) > MAX_SIZE_DELTA:
                reasons.append(
                    f"frame {frame}: width delta {geom.width_delta:+d}px exceeds {MAX_SIZE_DELTA}px"
                )
            if abs(geom.height_delta) > MAX_SIZE_DELTA:
                reasons.append(
                    f"frame {frame}: height delta {geom.height_delta:+d}px exceeds {MAX_SIZE_DELTA}px"
                )

    motion_delta_x: float | None = None
    motion_delta_y: float | None = None
    if len(frames) == 2 and all(f.platinum_bbox and f.hgss_bbox for f in frames):
        pt0 = bbox_center(frames[0].platinum_bbox)  # type: ignore[arg-type]
        pt1 = bbox_center(frames[1].platinum_bbox)  # type: ignore[arg-type]
        hg0 = bbox_center(frames[0].hgss_bbox)  # type: ignore[arg-type]
        hg1 = bbox_center(frames[1].hgss_bbox)  # type: ignore[arg-type]
        motion_delta_x = (hg1[0] - hg0[0]) - (pt1[0] - pt0[0])
        motion_delta_y = (hg1[1] - hg0[1]) - (pt1[1] - pt0[1])
        if abs(motion_delta_x) > MAX_MOTION_DELTA:
            reasons.append(
                f"frame-pair x-motion delta {motion_delta_x:+.1f}px exceeds {MAX_MOTION_DELTA:g}px"
            )
        if abs(motion_delta_y) > MAX_MOTION_DELTA:
            reasons.append(
                f"frame-pair y-motion delta {motion_delta_y:+.1f}px exceeds {MAX_MOTION_DELTA:g}px"
            )

    return GeometryResult(
        status="geometry-close" if not reasons else "geometry-review",
        reasons=reasons,
        frames=frames,
        motion_delta_x=motion_delta_x,
        motion_delta_y=motion_delta_y,
    )


def main() -> None:
    args = parse_args()
    donor_root = args.donor_root.resolve()
    report_path = args.report.resolve()
    manifest_path = args.manifest.resolve() if args.manifest else None

    species = [
        line.strip()
        for line in SPECIES_LIST.read_text().splitlines()
        if line.strip()
    ]

    results: list[Result] = []
    missing: list[str] = []

    for species_id, species_const in enumerate(species):
        if species_const == "SPECIES_EGG":
            break

        species_name = species_dir_name(species_const)
        pt_dir = PLATINUM_POKEMON / species_name
        hg_dir = donor_root / f"{species_id:04}"

        for pt_name, hg_rel in VIEWS:
            pt_path = pt_dir / pt_name
            hg_path = hg_dir / hg_rel

            if not pt_path.exists() or not hg_path.exists():
                missing.append(
                    f"{species_const}:{pt_name} "
                    f"target={pt_path.exists()} donor={hg_path.exists()}"
                )
                continue

            status = classify(pt_path, hg_path)
            geometry = geometry_compare(pt_path, hg_path) if status == "art-diff" else None
            results.append(
                Result(
                    species_id=species_id,
                    species=species_const,
                    view=pt_name,
                    status=status,
                    geometry=geometry,
                )
            )

    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1

    art_results = [r for r in results if r.status == "art-diff"]
    art_species = sorted({r.species for r in art_results})
    palette_species = sorted(
        {
            result.species
            for result in results
            if result.status in {"palette-only", "index-remap-only"}
        }
    )
    structural = [
        result
        for result in results
        if result.status.startswith(
            ("structure-diff", "mode-diff", "size-diff", "unexpected-size")
        )
    ]
    geometry_close = [
        r for r in art_results if r.geometry and r.geometry.status == "geometry-close"
    ]
    geometry_review = [
        r for r in art_results if r.geometry and r.geometry.status == "geometry-review"
    ]

    art_by_species: dict[str, list[Result]] = {}
    for result in art_results:
        art_by_species.setdefault(result.species, []).append(result)

    stage_species = sorted(
        species_name
        for species_name, species_results in art_by_species.items()
        if species_results
        and all(
            r.geometry is not None and r.geometry.status == "geometry-close"
            for r in species_results
        )
    )

    lines = [
        "# HGSS -> Platinum Battle Sprite Audit",
        "",
        "Pinned HGSS donor commit: 9d8b7591f09b65804da2fb2dfd56f320633e0d36.",
        "",
        "This report compares female_back, male_back, female_front, and male_front.",
        "Palette index 0 is treated as transparent for rendered comparisons.",
        "",
        "## Summary",
        "",
        f"- Species audited: **{len({r.species for r in results})}**",
        f"- Sprite files audited: **{len(results)}**",
    ]

    for status in sorted(counts):
        lines.append(f"- {status}: **{counts[status]}**")

    lines.extend(
        [
            f"- Species with actual art differences: **{len(art_species)}**",
            f"- Species with palette/index-only differences: **{len(palette_species)}**",
            f"- Missing paths: **{len(missing)}**",
            f"- Structural incompatibilities: **{len(structural)}**",
            "",
            "## Frame-geometry triage",
            "",
            "Art-diff files are additionally compared frame-by-frame as two 80x80 cells.",
            "This is a conservative staging filter, not proof of runtime animation safety.",
            "Platinum's existing sprite_data.json timing and shifts remain authoritative until",
            "a candidate is validated in-game.",
            "",
            f"- geometry-close art-diff files: **{len(geometry_close)}**",
            f"- geometry-review art-diff files: **{len(geometry_review)}**",
            f"- species whose every art-diff view is geometry-close: **{len(stage_species)}**",
            "",
            "Static staging thresholds:",
            f"- bottom-edge shift <= {MAX_BOTTOM_DELTA}px",
            f"- bbox center shift <= {MAX_CENTER_DELTA:g}px per axis",
            f"- bbox width/height delta <= {MAX_SIZE_DELTA}px",
            f"- frame-to-frame motion delta <= {MAX_MOTION_DELTA:g}px per axis",
            "- donor opaque pixels must retain at least one pixel of margin from every 80x80 edge",
            "",
            "A geometry-close result means only that the donor frames are spatially close enough",
            "to prioritize for a runtime pilot. It does not authorize a bulk import.",
            "",
            "## Geometry-close species staging candidates",
            "",
        ]
    )

    if stage_species:
        lines.extend(f"- {species_name}" for species_name in stage_species)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- identical: same indexed pixels and palette.",
            "- palette-metadata-only: indexed pixels match and rendered art is unchanged.",
            "- palette-only: indexed pixels match but rendered colors differ.",
            "- index-remap-only: index values differ but rendered art is visually identical.",
            "- art-diff: HGSS contains genuinely different rendered sprite art.",
            "- geometry-close: static frame footprint is close enough for staged runtime testing.",
            "- geometry-review: one or more static frame metrics exceed conservative staging thresholds.",
            "",
            "## Species with actual HGSS art differences",
            "",
        ]
    )

    if art_species:
        lines.extend(f"- {species_name}" for species_name in art_species)
    else:
        lines.append("- None")

    lines.extend(["", "## Palette/index-only species", ""])
    if palette_species:
        lines.extend(f"- {species_name}" for species_name in palette_species)
    else:
        lines.append("- None")

    if structural:
        lines.extend(["", "## Structural incompatibilities", ""])
        lines.extend(
            f"- {r.species} / {r.view}: {r.status}"
            for r in structural
        )

    if missing:
        lines.extend(["", "## Missing paths", ""])
        lines.extend(f"- {entry}" for entry in missing)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n")

    if manifest_path is not None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "schema_version": 1,
            "donor_commit": "9d8b7591f09b65804da2fb2dfd56f320633e0d36",
            "frame_size": list(FRAME_SIZE),
            "thresholds": {
                "max_bottom_delta": MAX_BOTTOM_DELTA,
                "max_center_delta": MAX_CENTER_DELTA,
                "max_size_delta": MAX_SIZE_DELTA,
                "max_motion_delta": MAX_MOTION_DELTA,
                "require_edge_margin": True,
            },
            "summary": {
                "species_audited": len({r.species for r in results}),
                "sprite_files_audited": len(results),
                "art_diff_files": len(art_results),
                "art_diff_species": len(art_species),
                "geometry_close_files": len(geometry_close),
                "geometry_review_files": len(geometry_review),
                "geometry_close_species": len(stage_species),
                "missing_paths": len(missing),
                "structural_incompatibilities": len(structural),
            },
            "geometry_close_species": stage_species,
            "art_diff_results": [asdict(r) for r in art_results],
            "missing_paths": missing,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print(
        f"Audited {len(results)} battle-sprite files across "
        f"{len({r.species for r in results})} species; "
        f"{counts.get('art-diff', 0)} files have actual art differences, "
        f"{len(geometry_close)} are geometry-close, "
        f"{len(stage_species)} species qualify for staged runtime testing, "
        f"{len(structural)} structural incompatibilities, "
        f"{len(missing)} missing paths."
    )


if __name__ == "__main__":
    main()
