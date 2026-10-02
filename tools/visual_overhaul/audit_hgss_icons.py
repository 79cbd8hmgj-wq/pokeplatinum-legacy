#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLATINUM_SPECIES = ROOT / "generated" / "species.txt"
PLATINUM_ICON_ROOT = ROOT / "res" / "pokemon"
PLATINUM_SHARED_PALETTE = PLATINUM_ICON_ROOT / ".shared" / "pl_poke_icon.pal"
PLATINUM_STANDARD_CELL = PLATINUM_ICON_ROOT / ".shared" / "pl_poke_icon_cell_01.json"

HGSS_ICON_REL = Path("files/poketool/icongra/poke_icon")
HGSS_SHARED_PALETTE = "poke_icon_00000000.pal"
HGSS_STANDARD_CELL = "poke_icon_00000002.json"


def normalized_text(path: Path) -> str:
    return "\n".join(path.read_text().splitlines())


def load_json(path: Path):
    return json.loads(path.read_text())


def species_constants() -> list[str]:
    constants = [line.strip() for line in PLATINUM_SPECIES.read_text().splitlines() if line.strip()]
    arceus = constants.index("SPECIES_ARCEUS")
    return constants[: arceus + 1]


def species_dir(species_constant: str) -> str:
    return species_constant.removeprefix("SPECIES_").lower()


def icon_contract(path: Path) -> tuple[str, tuple[int, int], bytes, tuple[int, ...]]:
    image = Image.open(path)
    if image.mode != "P":
        raise ValueError(f"{path}: expected indexed PNG, found {image.mode}")
    palette = image.getpalette()
    if palette is None:
        raise ValueError(f"{path}: indexed PNG has no palette")
    return image.mode, image.size, image.tobytes(), tuple(palette)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare Platinum base-species party/box icons against an HGSS source checkout."
    )
    parser.add_argument(
        "--hgss-root",
        required=True,
        type=Path,
        help="Path to a pret/pokeheartgold checkout.",
    )
    parser.add_argument(
        "--write-manifest",
        type=Path,
        help="Optional JSON output path for the comparison results.",
    )
    args = parser.parse_args()

    hgss_icon_root = args.hgss_root / HGSS_ICON_REL
    if not hgss_icon_root.is_dir():
        raise SystemExit(f"HGSS icon directory not found: {hgss_icon_root}")

    palette_match = normalized_text(PLATINUM_SHARED_PALETTE) == normalized_text(
        hgss_icon_root / HGSS_SHARED_PALETTE
    )
    cell_match = load_json(PLATINUM_STANDARD_CELL) == load_json(hgss_icon_root / HGSS_STANDARD_CELL)

    results = []
    identical_pixels = 0
    contract_mismatches = 0
    missing = 0

    for species_index, constant in enumerate(species_constants()):
        dirname = species_dir(constant)
        platinum_path = PLATINUM_ICON_ROOT / dirname / "icon.png"
        hgss_member = species_index + 7
        hgss_path = hgss_icon_root / f"poke_icon_{hgss_member:08}.png"

        record = {
            "species_index": species_index,
            "species": constant,
            "platinum": str(platinum_path.relative_to(ROOT)),
            "hgss_member": hgss_member,
            "hgss": str(hgss_path.relative_to(args.hgss_root)),
        }

        if not platinum_path.is_file() or not hgss_path.is_file():
            record["status"] = "missing"
            record["platinum_exists"] = platinum_path.is_file()
            record["hgss_exists"] = hgss_path.is_file()
            missing += 1
            results.append(record)
            continue

        pt_mode, pt_size, pt_pixels, pt_palette = icon_contract(platinum_path)
        hg_mode, hg_size, hg_pixels, hg_palette = icon_contract(hgss_path)

        contract_ok = pt_mode == hg_mode == "P" and pt_size == hg_size == (32, 64)
        same_pixels = pt_pixels == hg_pixels
        same_embedded_palette = pt_palette == hg_palette

        if not contract_ok:
            contract_mismatches += 1
            status = "contract_mismatch"
        elif same_pixels:
            identical_pixels += 1
            status = "identical_pixels"
        else:
            status = "different_pixels"

        record.update(
            {
                "status": status,
                "platinum_size": list(pt_size),
                "hgss_size": list(hg_size),
                "same_pixels": same_pixels,
                "same_embedded_palette": same_embedded_palette,
            }
        )
        results.append(record)

    manifest = {
        "shared_palette_equal": palette_match,
        "standard_cell_json_equal": cell_match,
        "base_species_count": len(results),
        "identical_pixel_count": identical_pixels,
        "different_pixel_count": sum(r["status"] == "different_pixels" for r in results),
        "contract_mismatch_count": contract_mismatches,
        "missing_count": missing,
        "results": results,
    }

    print(f"Shared palette equal: {palette_match}")
    print(f"Standard cell contract equal: {cell_match}")
    print(f"Base species checked: {len(results)}")
    print(f"Pixel-identical: {identical_pixels}")
    print(f"Pixel-different: {manifest['different_pixel_count']}")
    print(f"Contract mismatches: {contract_mismatches}")
    print(f"Missing: {missing}")

    changed = [r["species"] for r in results if r["status"] == "different_pixels"]
    if changed:
        print("HGSS artwork differs for:")
        for species in changed:
            print(f"  {species}")

    if args.write_manifest:
        args.write_manifest.parent.mkdir(parents=True, exist_ok=True)
        args.write_manifest.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"Wrote manifest: {args.write_manifest}")


if __name__ == "__main__":
    main()
