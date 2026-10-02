#!/usr/bin/env python3

"""Import compatible HGSS party/box Pokemon icons into Platinum.

The HGSS and Platinum icon archives share the same fundamental contract:
- seven shared palette/animation/cell resources before icon tiles
- 32x64 indexed 4bpp icon PNGs
- the same three 16-color shared palette banks
- the same base-species ordering (species ID + 7)

This importer copies donor *pixel art* while preserving each Platinum PNG's
palette. If a donor pixel color cannot be represented by the target palette,
the import fails instead of silently producing a miscolored icon.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLATINUM_POKEMON = ROOT / "res" / "pokemon"
SPECIES_LIST = ROOT / "generated" / "species.txt"
PLATINUM_SHARED_PALETTE = PLATINUM_POKEMON / ".shared" / "pl_poke_icon.pal"

EXPECTED_SIZE = (32, 64)
EXPECTED_MODE = "P"
HGSS_SHARED_PALETTE = "poke_icon_00000000.pal"


@dataclass(frozen=True)
class IconMapping:
    source_index: int
    target: Path
    label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import HGSS Pokemon icon art into the Platinum source tree."
    )
    parser.add_argument(
        "--donor-root",
        required=True,
        type=Path,
        help="Path to HGSS files/poketool/icongra/poke_icon",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate compatibility and report differences without writing files.",
    )
    return parser.parse_args()


def normalize_palette_text(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def species_dir_name(species_const: str) -> str:
    prefix = "SPECIES_"
    if not species_const.startswith(prefix):
        raise ValueError(f"Unexpected species constant: {species_const}")
    return species_const[len(prefix):].lower()


def build_mappings() -> list[IconMapping]:
    species = [line.strip() for line in SPECIES_LIST.read_text().splitlines() if line.strip()]
    mappings: list[IconMapping] = []

    # HGSS stores SPECIES_NONE through Arceus at archive index species_id + 7.
    for species_id, species_const in enumerate(species):
        if species_const == "SPECIES_EGG":
            break
        target = PLATINUM_POKEMON / species_dir_name(species_const) / "icon.png"
        mappings.append(
            IconMapping(
                source_index=species_id + 7,
                target=target,
                label=species_const,
            )
        )

    # Tail ordering matches the Platinum pl_poke_icon builder through Rotom-Mow.
    tail: list[tuple[int, str, str]] = [
        (501, "egg/icon.png", "EGG"),
        (502, "egg/forms/manaphy/icon.png", "MANAPHY_EGG"),
        (503, "deoxys/forms/attack/icon.png", "DEOXYS_ATTACK"),
        (504, "deoxys/forms/defense/icon.png", "DEOXYS_DEFENSE"),
        (505, "deoxys/forms/speed/icon.png", "DEOXYS_SPEED"),
    ]

    # Index 506 is HGSS's duplicate Unown-A archive entry. Platinum also emits
    # a duplicate of res/pokemon/unown/icon.png, so importing the base Unown
    # icon already updates both generated archive entries.
    unown_forms = [chr(code) for code in range(ord("b"), ord("z") + 1)]
    for index, form in enumerate(unown_forms, start=507):
        tail.append((index, f"unown/forms/{form}/icon.png", f"UNOWN_{form.upper()}"))
    tail.extend(
        [
            (532, "unown/forms/exc/icon.png", "UNOWN_EXCLAMATION"),
            (533, "unown/forms/que/icon.png", "UNOWN_QUESTION"),
            (534, "burmy/forms/sandy/icon.png", "BURMY_SANDY"),
            (535, "burmy/forms/trash/icon.png", "BURMY_TRASH"),
            (536, "wormadam/forms/sandy/icon.png", "WORMADAM_SANDY"),
            (537, "wormadam/forms/trash/icon.png", "WORMADAM_TRASH"),
            (538, "shellos/forms/east_sea/icon.png", "SHELLOS_EAST_SEA"),
            (539, "gastrodon/forms/east_sea/icon.png", "GASTRODON_EAST_SEA"),
            (540, "giratina/forms/origin/icon.png", "GIRATINA_ORIGIN"),
            (541, "shaymin/forms/sky/icon.png", "SHAYMIN_SKY"),
            (542, "rotom/forms/heat/icon.png", "ROTOM_HEAT"),
            (543, "rotom/forms/wash/icon.png", "ROTOM_WASH"),
            (544, "rotom/forms/frost/icon.png", "ROTOM_FROST"),
            (545, "rotom/forms/fan/icon.png", "ROTOM_FAN"),
            (546, "rotom/forms/mow/icon.png", "ROTOM_MOW"),
        ]
    )

    mappings.extend(
        IconMapping(index, PLATINUM_POKEMON / relpath, label)
        for index, relpath, label in tail
    )
    return mappings


def palette_colors(image: Image.Image) -> list[tuple[int, int, int]]:
    palette = image.getpalette()
    if palette is None:
        raise ValueError("Indexed image has no palette")
    return [
        tuple(palette[i:i + 3])
        for i in range(0, min(len(palette), 16 * 3), 3)
    ]


def remap_pixels(source: Image.Image, target: Image.Image, label: str) -> list[int]:
    source_colors = palette_colors(source)
    target_colors = palette_colors(target)

    source_pixels = list(source.getdata())
    used = sorted(set(source_pixels))
    mapping: dict[int, int] = {0: 0}

    for source_index in used:
        if source_index == 0:
            continue
        if source_index >= len(source_colors):
            raise ValueError(f"{label}: source palette index {source_index} is out of range")

        color = source_colors[source_index]
        candidates = [
            target_index
            for target_index, target_color in enumerate(target_colors)
            if target_index != 0 and target_color == color
        ]
        if not candidates:
            raise ValueError(
                f"{label}: donor color {color} at palette index {source_index} "
                "is not representable by the Platinum target palette"
            )
        mapping[source_index] = candidates[0]

    return [mapping[pixel] for pixel in source_pixels]


def validate_shared_palette(donor_root: Path) -> None:
    donor = donor_root / HGSS_SHARED_PALETTE
    if not donor.is_file():
        raise FileNotFoundError(f"Missing HGSS shared palette: {donor}")

    if normalize_palette_text(donor) != normalize_palette_text(PLATINUM_SHARED_PALETTE):
        raise ValueError("HGSS and Platinum shared Pokemon-icon palettes do not match")


def main() -> None:
    args = parse_args()
    donor_root = args.donor_root.resolve()
    validate_shared_palette(donor_root)

    mappings = build_mappings()
    changed = 0
    identical = 0

    for mapping in mappings:
        source = donor_root / f"poke_icon_{mapping.source_index:08}.png"
        target = mapping.target

        if not source.is_file():
            raise FileNotFoundError(f"{mapping.label}: missing donor icon {source}")
        if not target.is_file():
            raise FileNotFoundError(f"{mapping.label}: missing Platinum icon {target}")

        with Image.open(source) as donor_image, Image.open(target) as platinum_image:
            if donor_image.mode != EXPECTED_MODE or platinum_image.mode != EXPECTED_MODE:
                raise ValueError(
                    f"{mapping.label}: expected indexed PNG mode P; "
                    f"got donor={donor_image.mode}, target={platinum_image.mode}"
                )
            if donor_image.size != EXPECTED_SIZE or platinum_image.size != EXPECTED_SIZE:
                raise ValueError(
                    f"{mapping.label}: expected {EXPECTED_SIZE}; "
                    f"got donor={donor_image.size}, target={platinum_image.size}"
                )

            remapped = remap_pixels(donor_image, platinum_image, mapping.label)
            current = list(platinum_image.getdata())

            if remapped == current:
                identical += 1
                continue

            changed += 1
            if args.check_only:
                continue

            output = Image.new("P", EXPECTED_SIZE)
            target_palette = platinum_image.getpalette()
            if target_palette is None:
                raise ValueError(f"{mapping.label}: target palette unexpectedly missing")
            output.putpalette(target_palette)
            output.putdata(remapped)
            output.save(target)

    mode = "would change" if args.check_only else "changed"
    print(
        f"HGSS icon import validated {len(mappings)} Platinum icon targets: "
        f"{changed} {mode}, {identical} already pixel-identical."
    )


if __name__ == "__main__":
    main()
