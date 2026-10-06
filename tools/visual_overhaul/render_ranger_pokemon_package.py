#!/usr/bin/env python3
"""One-command renderer for a Ranger Pokémon *_LZ.bin package.

The command performs the verified pipeline:
LZ10 -> NARC -> named members -> NCLR + RGCN + NCER -> PNG cells.

It intentionally does not interpret Ranger .cac files yet.
"""
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

from inspect_ranger_assets import extract_narc_members
from nitro_narc import lz10_decompress
from render_ranger_ncer_preview import (
    read_cells,
    read_chars,
    read_palette,
    render_cell,
    write_indexed_png,
)


def render_package(package: Path, output: Path, vram_stride_tiles: int) -> int:
    raw = package.read_bytes()
    if not raw or raw[0] != 0x10:
        raise ValueError(f"{package}: expected Nintendo DS LZ10 stream")

    payload = lz10_decompress(raw)
    if payload[:4] != b"NARC":
        raise ValueError(f"{package}: LZ10 payload is not NARC")

    with tempfile.TemporaryDirectory(prefix="ranger_pkg_") as tmp:
        extract_dir = Path(tmp)
        extract_narc_members(payload, extract_dir)

        palettes = sorted(extract_dir.glob("*.NCLR"))
        if not palettes:
            raise ValueError(f"{package}: no NCLR member found")

        # Main Ranger Pokémon packages normally share one palette.
        palette_path = palettes[0]
        palette = read_palette(palette_path)

        # NCGR (tile-ordered sheet) and NCBR (scanline raster) carry the same
        # image; prefer NCGR when a stem has both so the choice is explicit.
        graphics = {p.stem: p for p in sorted(extract_dir.glob("*.NCBR"))}
        graphics.update({p.stem: p for p in sorted(extract_dir.glob("*.NCGR"))})
        cells = {p.stem: p for p in sorted(extract_dir.glob("*.NCER"))}

        output.mkdir(parents=True, exist_ok=True)
        rendered = 0
        for stem in sorted(set(graphics) & set(cells)):
            gfx_path = graphics[stem]
            cell_path = cells[stem]
            cell_bank = read_cells(cell_path)
            sheet_width, _sheet_height, tiles = read_chars(gfx_path, cells=cell_bank)
            group_dir = output / stem
            group_dir.mkdir(parents=True, exist_ok=True)

            for index, oams in enumerate(cell_bank):
                width, height, pixels = render_cell(
                    oams,
                    sheet_width,
                    tiles,
                    vram_stride_tiles,
                )
                target = group_dir / f"cell_{index:03d}.png"
                write_indexed_png(target, width, height, pixels, palette)
                rendered += 1

            print(
                f"{stem}: {len(cell_bank)} cells "
                f"({gfx_path.name} + {cell_path.name})"
            )

        # Preserve the tiny CAC companions next to previews for later sequencing work.
        cac_dir = output / "_cac"
        cac_files = sorted(extract_dir.glob("*.cac"))
        if cac_files:
            cac_dir.mkdir(parents=True, exist_ok=True)
            for path in cac_files:
                shutil.copy2(path, cac_dir / path.name)

        if not rendered:
            raise ValueError(
                f"{package}: no graphics/cell pairs found after NARC extraction"
            )

        print(f"Rendered {rendered} cells to {output}")
        print(f"Palette: {palette_path.name}")
        print(f"CAC companions preserved: {len(cac_files)}")
        return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--vram-stride-tiles", type=int, default=32)
    args = parser.parse_args()

    render_package(
        args.package.expanduser().resolve(),
        args.output_dir.expanduser().resolve(),
        args.vram_stride_tiles,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
