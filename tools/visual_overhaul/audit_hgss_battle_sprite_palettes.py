#!/usr/bin/env python3

"""Audit HGSS battle-sprite pixel-index compatibility with Platinum palettes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLATINUM_POKEMON = ROOT / "res" / "pokemon"

VIEW_TO_DONOR = {
    "female_back.png": "female/back.png",
    "male_back.png": "male/back.png",
    "female_front.png": "female/front.png",
    "male_front.png": "male/front.png",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor-root", required=True, type=Path)
    parser.add_argument("--geometry-manifest", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    return parser.parse_args()


def parse_jasc(path: Path) -> list[tuple[int, int, int]]:
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if len(lines) < 4 or lines[0] != "JASC-PAL":
        raise ValueError(f"{path}: not a JASC palette")
    count = int(lines[2])
    colors = [tuple(map(int, line.split())) for line in lines[3:3 + count]]
    if len(colors) != count:
        raise ValueError(f"{path}: expected {count} colors, found {len(colors)}")
    return colors


def png_palette(path: Path) -> list[tuple[int, int, int]]:
    with Image.open(path) as image:
        palette = image.getpalette()
        if palette is None:
            raise ValueError(f"{path}: missing indexed palette")
        return [tuple(palette[i:i + 3]) for i in range(0, 48, 3)]


def used_indices(path: Path) -> list[int]:
    with Image.open(path) as image:
        if image.mode != "P":
            raise ValueError(f"{path}: expected indexed PNG, got {image.mode}")
        return sorted(set(image.getdata()) - {0})


def classify_view(donor: Path, target_palette: list[tuple[int, int, int]]) -> dict:
    donor_palette = png_palette(donor)
    used = used_indices(donor)

    same_index = all(
        idx < len(target_palette) and donor_palette[idx] == target_palette[idx]
        for idx in used
    )
    if same_index:
        return {
            "status": "direct-index-safe",
            "used_indices": used,
            "mapping": {str(idx): idx for idx in used},
            "missing_colors": [],
        }

    mapping: dict[str, int] = {}
    missing: list[dict] = []
    for idx in used:
        color = donor_palette[idx]
        matches = [i for i, target in enumerate(target_palette) if target == color]
        if matches:
            mapping[str(idx)] = idx if idx in matches else matches[0]
        else:
            missing.append({"donor_index": idx, "rgb": list(color)})

    if not missing:
        return {
            "status": "exact-normal-remap",
            "used_indices": used,
            "mapping": mapping,
            "missing_colors": [],
        }

    return {
        "status": "palette-mismatch",
        "used_indices": used,
        "mapping": mapping,
        "missing_colors": missing,
    }


def main() -> None:
    args = parse_args()
    geometry = json.loads(args.geometry_manifest.read_text())
    stage_species = set(geometry["geometry_close_species"])

    entries: list[dict] = []
    for result in geometry["art_diff_results"]:
        species = result["species"]
        if species not in stage_species:
            continue
        if result["geometry"]["status"] != "geometry-close":
            continue

        species_id = int(result["species_id"])
        species_dir = species.removeprefix("SPECIES_").lower()
        view = result["view"]
        donor_rel = VIEW_TO_DONOR[view]
        donor = args.donor_root / f"{species_id:04}" / donor_rel
        normal_pal = PLATINUM_POKEMON / species_dir / "normal.pal"

        classification = classify_view(donor, parse_jasc(normal_pal))
        entries.append(
            {
                "species_id": species_id,
                "species": species,
                "view": view,
                "donor_path": str(donor.relative_to(args.donor_root)),
                **classification,
            }
        )

    counts: dict[str, int] = {}
    by_species: dict[str, list[dict]] = {}
    for entry in entries:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
        by_species.setdefault(entry["species"], []).append(entry)

    direct_species = sorted(
        species for species, views in by_species.items()
        if views and all(view["status"] == "direct-index-safe" for view in views)
    )
    remap_species = sorted(
        species for species, views in by_species.items()
        if species not in direct_species
        and views
        and all(view["status"] in {"direct-index-safe", "exact-normal-remap"} for view in views)
    )
    mismatch_species = sorted(
        species for species, views in by_species.items()
        if any(view["status"] == "palette-mismatch" for view in views)
    )

    manifest = {
        "schema_version": 1,
        "donor_commit": "9d8b7591f09b65804da2fb2dfd56f320633e0d36",
        "policy": {
            "platinum_normal_palette_preserved": True,
            "platinum_shiny_palette_preserved": True,
            "direct_index_safe": "HGSS used pixel indices already resolve to the same RGB colors in Platinum's normal palette.",
            "exact_normal_remap": "Normal colors can be remapped exactly into Platinum's palette, but shiny-index semantics are not proven; do not bulk import automatically.",
            "palette_mismatch": "At least one donor color is absent from Platinum's normal palette; requires manual art/palette conversion or rejection.",
        },
        "summary": {
            "geometry_close_species_input": len(stage_species),
            "views_checked": len(entries),
            **counts,
            "direct_index_safe_species": len(direct_species),
            "exact_normal_remap_species": len(remap_species),
            "palette_mismatch_species": len(mismatch_species),
        },
        "direct_index_safe_species": direct_species,
        "exact_normal_remap_species": remap_species,
        "palette_mismatch_species": mismatch_species,
        "entries": entries,
    }

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")

    lines = [
        "# HGSS -> Platinum Battle Sprite Palette Contract Audit",
        "",
        "This is the second G3 battle-sprite safety gate. It runs only on the species",
        "whose changed HGSS views already passed the conservative frame-geometry triage.",
        "",
        "Platinum's existing normal and shiny palette files remain authoritative.",
        "The build packs sprite pixel indices separately from those palettes, so donor",
        "art must preserve Platinum's index/color contract rather than merely look correct",
        "inside the donor PNG.",
        "",
        "## Summary",
        "",
        f"- Geometry-close species input: **{len(stage_species)}**",
        f"- Art-diff views checked: **{len(entries)}**",
        f"- Direct-index-safe views: **{counts.get('direct-index-safe', 0)}**",
        f"- Exact-normal-remap views: **{counts.get('exact-normal-remap', 0)}**",
        f"- Palette-mismatch views: **{counts.get('palette-mismatch', 0)}**",
        f"- Fully direct-index-safe species: **{len(direct_species)}**",
        f"- Species requiring only exact normal-color remap: **{len(remap_species)}**",
        f"- Species with unresolved palette mismatch: **{len(mismatch_species)}**",
        "",
        "## Import policy",
        "",
        "- **direct-index-safe**: eligible for the next small runtime pilot.",
        "- **exact-normal-remap**: do not auto-import yet. Normal-color remapping is",
        "  possible, but the same index remap would also affect Platinum's shiny palette;",
        "  that semantic relationship must be reviewed first.",
        "- **palette-mismatch**: manual conversion/rejection path only.",
        "",
        "## Direct-index-safe species",
        "",
    ]
    lines.extend(f"- {s}" for s in direct_species or ["None"])
    lines.extend(["", "## Exact-normal-remap species", ""])
    lines.extend(f"- {s}" for s in remap_species or ["None"])
    lines.extend(["", "## Palette-mismatch species", ""])
    lines.extend(f"- {s}" for s in mismatch_species or ["None"])

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n")

    print(
        f"Checked {len(entries)} geometry-close art-diff views across {len(stage_species)} species: "
        f"{len(direct_species)} species direct-index-safe, "
        f"{len(remap_species)} exact-normal-remap, "
        f"{len(mismatch_species)} palette-mismatch."
    )


if __name__ == "__main__":
    main()
