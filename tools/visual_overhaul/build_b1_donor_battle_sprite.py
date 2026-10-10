#!/usr/bin/env python3
"""Build a Platinum battle-move sprite (PNG + cell/anim JSON) from donor cells.

Input is a recipe JSON naming frames of already-rendered donor cells (output of
export_b1_ranger_effect_cells.py). Output is exactly what the existing
res/graphics/battle/moves pipeline consumes (nitrogfx -cell -> NCGR/NCER/NANR/NCLR):

  <name>.png        4bpp indexed "cell scan" sheet, cells stacked with 255 separator rows
  <name>_cell.json  one cell per frame, OAMs from hardware-legal sizes, 1D 64-byte mapping
  <name>_anim.json  a single forward, play-once sequence
  <name>.provenance.json  donor path + sha256 of every cell used

The sprite is rendered by the existing SPRITE_FUNC_OFFSET_AND_ANIMATE script function.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

# (width, height) in tiles -> (shape, size) for OBJ attribute encoding
SHAPES = {
    (1, 1): (0, 0), (2, 2): (0, 1), (4, 4): (0, 2), (8, 8): (0, 3),
    (2, 1): (1, 0), (4, 1): (1, 1), (4, 2): (1, 2), (8, 4): (1, 3),
    (1, 2): (2, 0), (1, 4): (2, 1), (2, 4): (2, 2), (4, 8): (2, 3),
}
MAX_TILES_DEFAULT = 256  # 8 KiB of OBJ char data per move sprite


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rgb555(px):
    r, g, b, _ = px
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


def expand555(v):
    r, g, b = v & 31, (v >> 5) & 31, (v >> 10) & 31
    return (r << 3 | r >> 2, g << 3 | g >> 2, b << 3 | b >> 2)


def pick_shape(wt, ht):
    best = None
    for (sw, sh), enc in SHAPES.items():
        if sw >= wt and sh >= ht and (best is None or sw * sh < best[0] * best[1]):
            best = (sw, sh, enc)
    return best


def cover(frame_w, frame_h, mask):
    """Cover the opaque tiles of an 8-px-aligned canvas with legal OAMs (<=32px blocks)."""
    wt, ht = frame_w // 8, frame_h // 8
    oams = []
    for by in range(0, ht, 4):
        for bx in range(0, wt, 4):
            cw, ch = min(4, wt - bx), min(4, ht - by)
            used = [(x, y) for y in range(by, by + ch) for x in range(bx, bx + cw) if mask[y][x]]
            if not used:
                continue
            # shrink the block to the used bounding box of tiles
            x0, x1 = min(u[0] for u in used), max(u[0] for u in used)
            y0, y1 = min(u[1] for u in used), max(u[1] for u in used)
            sw, sh, enc = pick_shape(x1 - x0 + 1, y1 - y0 + 1)
            oams.append((x0, y0, sw, sh, enc))
    return oams


def build(recipe_path: Path, donor_cells: Path, out_dir: Path, max_tiles: int):
    recipe = json.loads(recipe_path.read_text())
    name = recipe["name"]

    frames = []
    for f in recipe["frames"]:
        src = donor_cells / f["cell"]
        im = Image.open(src).convert("RGBA")
        bbox = im.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
        if bbox is None:
            raise SystemExit(f"{src}: fully transparent")
        im = im.crop(bbox)
        if f.get("hflip"):
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        frames.append({"img": im, "src": src, "spec": f})

    colours = sorted({rgb555(p) for fr in frames for p in fr["img"].convert("RGBA").get_flattened_data() if p[3] >= 128})
    if len(colours) > 15:
        raise SystemExit(f"{len(colours)} opaque colours > 15; quantize the recipe explicitly")
    index_of = {c: i + 1 for i, c in enumerate(colours)}

    cells, sheets, total_tiles, char_cursor = [], [], 0, 0
    for fr in frames:
        im = fr["img"]
        w8, h8 = (im.width + 7) // 8 * 8, (im.height + 7) // 8 * 8
        # centre the canvas on the sprite origin (defender centre + recipe offset)
        x0 = -(w8 // 2) // 8 * 8 + fr["spec"].get("dx", 0)
        y0 = -(h8 // 2) // 8 * 8 + fr["spec"].get("dy", 0)
        canvas = [[0] * w8 for _ in range(h8)]
        for y in range(im.height):
            for x in range(im.width):
                p = im.getpixel((x, y))
                if p[3] >= 128:
                    canvas[y][x] = index_of[rgb555(p)]
        mask = [[any(canvas[ty * 8 + yy][tx * 8 + xx] for yy in range(8) for xx in range(8))
                 for tx in range(w8 // 8)] for ty in range(h8 // 8)]
        oams = cover(w8, h8, mask)
        cell_oams, minx, miny, maxx, maxy = [], 10**6, 10**6, -10**6, -10**6
        for (tx, ty, sw, sh, (shape, size)) in oams:
            if char_cursor % 2:
                char_cursor += 1  # CharName unit is 64 bytes = 2 tiles
            cell_oams.append({
                "Attr0": {"YCoordinate": y0 + ty * 8, "Rotation": False, "SizeDisable": False,
                          "Mode": 0, "Mosaic": False, "Colours": 16, "Shape": shape},
                "Attr1": {"XCoordinate": x0 + tx * 8, "RotationScaling": 0, "Size": size},
                "Attr2": {"CharName": char_cursor // 2, "Priority": 0, "Palette": 0},
                "_rect": (tx, ty, sw, sh),
            })
            char_cursor += sw * sh
            total_tiles += sw * sh
            minx = min(minx, x0 + tx * 8); miny = min(miny, y0 + ty * 8)
            maxx = max(maxx, x0 + (tx + sw) * 8); maxy = max(maxy, y0 + (ty + sh) * 8)
        cells.append({"oams": cell_oams, "min": (minx, miny), "max": (maxx, maxy),
                      "canvas": canvas, "origin": (x0, y0)})

    if total_tiles > max_tiles:
        raise SystemExit(f"{total_tiles} OBJ tiles > budget {max_tiles}")

    # ---- cell scan sheet: cells stacked, 1 separator row of 255 ----
    sheet_w = max(c["max"][0] - c["min"][0] for c in cells)
    rows = []
    for c in cells:
        cw, chh = c["max"][0] - c["min"][0], c["max"][1] - c["min"][1]
        grid = [[0] * sheet_w for _ in range(chh)]
        ox, oy = c["origin"]
        for y, line in enumerate(c["canvas"]):
            for x, v in enumerate(line):
                gx, gy = ox + x - c["min"][0], oy + y - c["min"][1]
                if v and 0 <= gx < sheet_w and 0 <= gy < chh:
                    grid[gy][gx] = v
        rows.append(grid)
    sheet_h = sum(len(g) for g in rows) + len(rows) - 1
    sheet = Image.new("P", (sheet_w, sheet_h), 255)
    pal = [0, 0, 0]
    pal += [v for c in colours for v in expand555(c)]
    pal += [0] * (48 - len(pal))
    sheet.putpalette(pal)
    y = 0
    for gi, grid in enumerate(rows):
        for line in grid:
            for x, v in enumerate(line):
                sheet.putpixel((x, y), v)
            y += 1
        if gi != len(rows) - 1:
            for x in range(sheet_w):
                sheet.putpixel((x, y), 255)
            y += 1
    sheet.putpalette(pal)

    # ---- cell json ----
    cell_json = {"labelEnabled": True, "dontPadKbec": True, "extended": True,
                 "vramTransferEnabled": False, "cellCount": len(cells), "mappingType": 1, "cells": [],
                 "labels": [f"CellAnime{i}" for i in range(len(cells))], "labelCount": len(cells)}
    for c in cells:
        radius = int(max(abs(c["min"][0]), abs(c["min"][1]), abs(c["max"][0]), abs(c["max"][1])))
        cell_json["cells"].append({
            "cellAttrs": {"hFlip": False, "vFlip": False, "hvFlip": False, "boundingRect": True,
                          "boundingSphereRadius": radius},
            "maxX": c["max"][0], "maxY": c["max"][1], "minX": c["min"][0], "minY": c["min"][1],
            "oamCount": len(c["oams"]),
            "OAM": [{k: v for k, v in o.items() if k != "_rect"} for o in c["oams"]],
        })

    # ---- anim json ----
    anim_json = {
        "labelEnabled": True, "sequenceCount": 1, "frameCount": len(frames),
        "sequences": [{
            "frameCount": len(frames), "loopStartFrame": 0, "animationElement": 0,
            "animationType": 1, "playbackMode": 1,
            "frameData": [{"frameDelay": fr["spec"]["delay"], "resultId": i} for i, fr in enumerate(frames)],
        }],
        "animationResults": [{"resultType": 0, "index": i} for i in range(len(frames))],
        "resultCount": len(frames), "labels": ["CellAnime0"], "labelCount": 1,
    }

    provenance = {
        "name": name, "donor": recipe["donor"], "donor_package": recipe["donor_package"],
        "donor_commit_source": recipe.get("donor_commit_source"),
        "palette_colours_rgb555": colours, "obj_tiles": total_tiles, "tile_budget": max_tiles,
        "frames": [{"cell": str(fr["src"].relative_to(donor_cells)),
                    "cell_sha256": sha(fr["src"].read_bytes()),
                    "delay": fr["spec"]["delay"]} for fr in frames],
        "state": "installed_via_res/graphics/battle/moves NARC pipeline; rendered by SPRITE_FUNC_OFFSET_AND_ANIMATE",
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    sheet.save(out_dir / f"{name}.png", optimize=False)
    (out_dir / f"{name}_cell.json").write_text(json.dumps(cell_json, indent=1) + "\n")
    (out_dir / f"{name}_anim.json").write_text(json.dumps(anim_json, indent=1) + "\n")
    (out_dir / f"{name}.provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return provenance


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("recipe", type=Path)
    cli.add_argument("--donor-cells", type=Path, required=True)
    cli.add_argument("--out", type=Path, required=True)
    cli.add_argument("--max-tiles", type=int, default=MAX_TILES_DEFAULT)
    args = cli.parse_args()
    prov = build(args.recipe, args.donor_cells, args.out, args.max_tiles)
    print(json.dumps({"name": prov["name"], "obj_tiles": prov["obj_tiles"],
                      "colours": len(prov["palette_colours_rgb555"])}))


if __name__ == "__main__":
    sys.exit(main())
