#!/usr/bin/env python3

"""Audit HGSS Pokemon battle sprites against Platinum source assets."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLATINUM_POKEMON = ROOT / "res" / "pokemon"
SPECIES_LIST = ROOT / "generated" / "species.txt"

EXPECTED_SIZE = (160, 80)
VIEWS = (
    ("female_back.png", "female/back.png"),
    ("male_back.png", "male/back.png"),
    ("female_front.png", "female/front.png"),
    ("male_front.png", "male/front.png"),
)


@dataclass
class Result:
    species_id: int
    species: str
    view: str
    status: str


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


def main() -> None:
    args = parse_args()
    donor_root = args.donor_root.resolve()
    report_path = args.report.resolve()

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

            results.append(
                Result(
                    species_id=species_id,
                    species=species_const,
                    view=pt_name,
                    status=classify(pt_path, hg_path),
                )
            )

    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1

    art_species = sorted(
        {
            result.species
            for result in results
            if result.status == "art-diff"
        }
    )
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
            "## Interpretation",
            "",
            "- identical: same indexed pixels and palette.",
            "- palette-metadata-only: indexed pixels match and rendered art is unchanged.",
            "- palette-only: indexed pixels match but rendered colors differ.",
            "- index-remap-only: index values differ but rendered art is visually identical.",
            "- art-diff: HGSS contains genuinely different rendered sprite art.",
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

    print(
        f"Audited {len(results)} battle-sprite files across "
        f"{len({r.species for r in results})} species; "
        f"{counts.get('art-diff', 0)} files have actual art differences, "
        f"{len(structural)} structural incompatibilities, "
        f"{len(missing)} missing paths."
    )


if __name__ == "__main__":
    main()
