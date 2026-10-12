#!/usr/bin/env python3
"""Build a multi-sequence Platinum battle-move FX sheet (PNG + cell/anim JSON + palette variants).

Used by the Opal B2 batch.  A recipe describes donor sprite sources (pokeemerald battle-anim PNGs and/or
procedurally generated pixel-art primitives), the frames cut from them, and named animation sequences.
Output is exactly what res/graphics/battle/moves consumes (nitrogfx -cell -> NCGR/NCER/NANR/NCLR):

  <name>.png                 4bpp indexed "cell scan" sheet (cells stacked with 255 separator rows)
  <name>_cell.json           one cell per frame, 1D 64-byte mapping, hardware-legal OAM sizes
  <name>_anim.json           one sequence per recipe sequence (play-once or loop)
  <name>_<variant>.png       palette-only variants (same pixels, remapped palette) -> extra NCLRs
  <name>.provenance.json     donor path + sha256 of every donor file, per-frame rects, palette, tile count

Rendered by SPRITE_FUNC_OPAL_FX (src/battle_anim/opal_cinematic.c).
Colour policy: all donor colours are folded into ONE shared <=15 colour palette (index 0 = transparent) by
deterministic median-cut + nearest-colour mapping; this is the documented "recolor/convert" step.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("b1builder", HERE.parent / "build_b1_donor_battle_sprite.py")
b1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b1)

MAX_TILES_DEFAULT = 192  # conservative per-sheet OBJ char budget (6 KiB); B1 limit was 256


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hexrgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def snap555(c):
    return b1.expand555(b1.rgb555(c + (255,)))


# ---------------------------------------------------------------- sources
def load_indexed_png(path: Path) -> Image.Image:
    """GBA-style indexed PNG: palette index 0 is transparent."""
    im = Image.open(path)
    if im.mode != "P":
        raise SystemExit(f"{path}: expected indexed PNG")
    pal = im.getpalette()
    out = Image.new("RGBA", im.size)
    px, op = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            v = px[x, y]
            op[x, y] = (0, 0, 0, 0) if v == 0 else (pal[v * 3], pal[v * 3 + 1], pal[v * 3 + 2], 255)
    return out


def recolor_ramp(im: Image.Image, ramp):
    """Map every opaque pixel to the ramp by luminance (dark->light), preserving shading."""
    ramp = [hexrgb(c) for c in ramp]
    px = im.load()
    lums = [lum(px[x, y][:3]) for y in range(im.height) for x in range(im.width) if px[x, y][3]]
    if not lums:
        return im
    lo, hi = min(lums), max(lums)
    out = im.copy()
    op = out.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3]:
                t = 0.0 if hi == lo else (lum(p[:3]) - lo) / (hi - lo)
                f = t * (len(ramp) - 1)
                i = min(int(f), len(ramp) - 2)
                a, b = ramp[i], ramp[i + 1]
                u = f - i
                op[x, y] = tuple(int(round(a[k] + (b[k] - a[k]) * u)) for k in range(3)) + (255,)
    return out


def proc_ring(spec) -> Image.Image:
    """Procedural pixel-art ring: elliptical outline with a soft inner shade, drawn with a 4-step ramp."""
    w, h = spec["w"], spec["h"]
    rx, ry, th = spec["rx"], spec["ry"], spec.get("thickness", 2.0)
    ramp = [hexrgb(c) for c in spec["ramp"]]  # dark -> light, 4 entries
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - cx) / rx, (y - cy) / ry)  # 1.0 on the ring centre line
            dist = abs(d - 1.0) * min(rx, ry)
            if dist <= th * 0.5:
                op[x, y] = ramp[3] + (255,)
            elif dist <= th * 0.5 + 1.0:
                op[x, y] = ramp[2] + (255,)
            elif dist <= th * 0.5 + 2.0 and d < 1.0:
                op[x, y] = ramp[1] + (255,)
            elif dist <= th * 0.5 + 2.2 and d >= 1.0:
                op[x, y] = ramp[0] + (255,)
    return out


def proc_star(spec) -> Image.Image:
    """Four-point sparkle."""
    n = spec["size"]
    ramp = [hexrgb(c) for c in spec["ramp"]]
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    op = out.load()
    c = (n - 1) / 2.0
    for y in range(n):
        for x in range(n):
            dx, dy = abs(x - c), abs(y - c)
            arm = min(dx, dy)
            reach = max(dx, dy)
            if arm <= 0.6 and reach <= c:
                op[x, y] = ramp[3 if reach <= c * 0.45 else 2] + (255,)
            elif arm <= 1.1 and reach <= c * 0.55:
                op[x, y] = ramp[1] + (255,)
    return out


def proc_dot(spec) -> Image.Image:
    n = spec["size"]
    ramp = [hexrgb(c) for c in spec["ramp"]]
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    op = out.load()
    c = (n - 1) / 2.0
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - c, y - c) / (n / 2.0)
            if d <= 0.35:
                op[x, y] = ramp[3] + (255,)
            elif d <= 0.65:
                op[x, y] = ramp[2] + (255,)
            elif d <= 0.95:
                op[x, y] = ramp[1] + (255,)
    return out


PROC = {"ring": proc_ring, "star": proc_star, "dot": proc_dot}


# ---------------------------------------------------------------- palette
def fold_palette(images, max_colors):
    """Return (palette list of RGB tuples (snapped to RGB555), mapper)."""
    counts = {}
    for im in images:
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                p = px[x, y]
                if p[3] >= 128:
                    c = snap555(p[:3])
                    counts[c] = counts.get(c, 0) + 1
    cols = sorted(counts)
    if len(cols) <= max_colors:
        pal = sorted(cols, key=lum)
    else:
        pal = median_cut(counts, max_colors)
    return pal


def median_cut(counts, k):
    boxes = [sorted(counts)]
    while len(boxes) < k:
        # split the box with the widest channel range * population
        best, bi = -1, -1
        for i, box in enumerate(boxes):
            if len(box) < 2:
                continue
            rng = max(max(c[ch] for c in box) - min(c[ch] for c in box) for ch in range(3))
            score = rng * sum(counts[c] for c in box) ** 0.5
            if score > best:
                best, bi = score, i
        if bi < 0:
            break
        box = boxes.pop(bi)
        ch = max(range(3), key=lambda ch: max(c[ch] for c in box) - min(c[ch] for c in box))
        box.sort(key=lambda c: (c[ch], c))
        total, acc = sum(counts[c] for c in box), 0
        cut = 1
        for i, c in enumerate(box):
            acc += counts[c]
            if acc * 2 >= total:
                cut = max(1, min(len(box) - 1, i + 1))
                break
        boxes += [box[:cut], box[cut:]]
    pal = []
    for box in boxes:
        tot = sum(counts[c] for c in box)
        avg = tuple(int(round(sum(c[ch] * counts[c] for c in box) / tot)) for ch in range(3))
        pal.append(snap555(avg))
    return sorted(set(pal), key=lum)


def nearest(pal, c):
    return min(range(len(pal)), key=lambda i: (pal[i][0] - c[0]) ** 2 + (pal[i][1] - c[1]) ** 2 + (pal[i][2] - c[2]) ** 2)


def variant_palette(pal, ramp):
    """Remap an ordered base palette onto a dark->light ramp, entry-by-entry by luminance rank."""
    ramp = [hexrgb(c) for c in ramp]
    order = sorted(range(len(pal)), key=lambda i: lum(pal[i]))
    out = [None] * len(pal)
    n = len(pal)
    for rank, i in enumerate(order):
        t = 0.0 if n == 1 else rank / (n - 1)
        f = t * (len(ramp) - 1)
        j = min(int(f), len(ramp) - 2)
        u = f - j
        a, b = ramp[j], ramp[j + 1]
        out[i] = snap555(tuple(int(round(a[k] + (b[k] - a[k]) * u)) for k in range(3)))
    return out


def write_indexed(path: Path, img_idx, size, palette, bg=255):
    im = Image.new("P", size, bg)
    pal = [0, 0, 0]
    for c in palette:
        pal += list(c)
    pal += [0] * (48 - len(pal))
    im.putpalette(pal)
    px = im.load()
    for (x, y), v in img_idx.items():
        px[x, y] = v
    im.putpalette(pal)
    im.save(path, optimize=False)


# ---------------------------------------------------------------- build
def build(recipe_path: Path, donor_root: Path, out_dir: Path, max_tiles: int):
    recipe = json.loads(recipe_path.read_text())
    name = recipe["name"]
    sources, donor_files = {}, {}
    for sid, s in recipe["sources"].items():
        if s["type"] == "emerald_png":
            p = donor_root / s["path"]
            im = load_indexed_png(p)
            donor_files[sid] = {"path": s["path"], "sha256": sha(p.read_bytes())}
            if "ramp" in s:
                im = recolor_ramp(im, s["ramp"])
        else:
            im = PROC[s["type"]](s)
            donor_files[sid] = {"procedural": s["type"], "params": {k: v for k, v in s.items() if k != "type"}}
        sources[sid] = im

    frames = {}
    for f in recipe["frames"]:
        im = sources[f["src"]]
        if "rect" in f:
            x, y, w, h = f["rect"]
            im = im.crop((x, y, x + w, y + h))
        if f.get("hflip"):
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if f.get("vflip"):
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
        if im.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox() is None:
            raise SystemExit(f"frame {f['id']}: fully transparent")
        frames[f["id"]] = {"img": im, "spec": f}

    max_colors = recipe.get("max_colors", 15)
    pal = fold_palette([fr["img"] for fr in frames.values()], max_colors)
    if len(pal) > 15:
        raise SystemExit("palette fold failed")

    cells, total_tiles, char_cursor = [], 0, 0
    order = list(frames)
    for fid in order:
        fr = frames[fid]
        im = fr["img"]
        w8, h8 = (im.width + 7) // 8 * 8, (im.height + 7) // 8 * 8
        ox, oy = fr["spec"].get("dx", 0), fr["spec"].get("dy", 0)
        x0 = -(w8 // 2) // 8 * 8 + ox
        y0 = -(h8 // 2) // 8 * 8 + oy
        canvas = [[0] * w8 for _ in range(h8)]
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                p = px[x, y]
                if p[3] >= 128:
                    canvas[y][x] = 1 + nearest(pal, snap555(p[:3]))
        mask = [[any(canvas[ty * 8 + yy][tx * 8 + xx] for yy in range(8) for xx in range(8))
                 for tx in range(w8 // 8)] for ty in range(h8 // 8)]
        oams = b1.cover(w8, h8, mask)
        cell_oams, minx, miny, maxx, maxy = [], 10**6, 10**6, -10**6, -10**6
        for (tx, ty, sw, sh, (shape, size)) in oams:
            if char_cursor % 2:
                char_cursor += 1
            cell_oams.append({
                "Attr0": {"YCoordinate": y0 + ty * 8, "Rotation": False, "SizeDisable": False,
                          "Mode": 0, "Mosaic": False, "Colours": 16, "Shape": shape},
                "Attr1": {"XCoordinate": x0 + tx * 8, "RotationScaling": 0, "Size": size},
                "Attr2": {"CharName": char_cursor // 2, "Priority": 0, "Palette": 0},
            })
            char_cursor += sw * sh
            total_tiles += sw * sh
            minx = min(minx, x0 + tx * 8); miny = min(miny, y0 + ty * 8)
            maxx = max(maxx, x0 + (tx + sw) * 8); maxy = max(maxy, y0 + (ty + sh) * 8)
        cells.append({"oams": cell_oams, "min": (minx, miny), "max": (maxx, maxy), "canvas": canvas,
                      "origin": (x0, y0), "id": fid})

    if total_tiles > max_tiles:
        raise SystemExit(f"{name}: {total_tiles} OBJ tiles > budget {max_tiles}")

    # ---- cell-scan sheet (identical layout rules to the B1 builder) ----
    sheet_w = max(c["max"][0] - c["min"][0] for c in cells)
    rows = []
    for c in cells:
        chh = c["max"][1] - c["min"][1]
        grid = [[0] * sheet_w for _ in range(chh)]
        ox, oy = c["origin"]
        for y, line in enumerate(c["canvas"]):
            for x, v in enumerate(line):
                gx, gy = ox + x - c["min"][0], oy + y - c["min"][1]
                if v and 0 <= gx < sheet_w and 0 <= gy < chh:
                    grid[gy][gx] = v
        rows.append(grid)
    sheet_h = sum(len(g) for g in rows) + len(rows) - 1
    pix = {}
    y = 0
    for gi, grid in enumerate(rows):
        for line in grid:
            for x, v in enumerate(line):
                pix[(x, y)] = v
            y += 1
        if gi != len(rows) - 1:
            for x in range(sheet_w):
                pix[(x, y)] = 255
            y += 1
    out_dir.mkdir(parents=True, exist_ok=True)
    write_indexed(out_dir / f"{name}.png", pix, (sheet_w, sheet_h), pal)

    variants = {}
    for vname, vspec in recipe.get("palette_variants", {}).items():
        vpal = variant_palette(pal, vspec["ramp"])
        write_indexed(out_dir / f"{name}_{vname}.png", pix, (sheet_w, sheet_h), vpal)
        variants[vname] = [b1.rgb555(c + (255,)) for c in vpal]

    cell_json = {"labelEnabled": True, "dontPadKbec": True, "extended": True, "vramTransferEnabled": False,
                 "cellCount": len(cells), "mappingType": 1, "cells": [],
                 "labels": [f"CellAnime{i}" for i in range(len(cells))], "labelCount": len(cells)}
    for c in cells:
        radius = int(max(abs(c["min"][0]), abs(c["min"][1]), abs(c["max"][0]), abs(c["max"][1])))
        cell_json["cells"].append({
            "cellAttrs": {"hFlip": False, "vFlip": False, "hvFlip": False, "boundingRect": True,
                          "boundingSphereRadius": radius},
            "maxX": c["max"][0], "maxY": c["max"][1], "minX": c["min"][0], "minY": c["min"][1],
            "oamCount": len(c["oams"]), "OAM": c["oams"]})

    idx_of = {fid: i for i, fid in enumerate(order)}
    seqs, results = [], []
    for sq in recipe["sequences"]:
        fd = []
        for fid, delay in sq["frames"]:
            results.append({"resultType": 0, "index": idx_of[fid]})
            fd.append({"frameDelay": delay, "resultId": len(results) - 1})
        seqs.append({"frameCount": len(fd), "loopStartFrame": 0, "animationElement": 0, "animationType": 1,
                     "playbackMode": 2 if sq.get("loop") else 1, "frameData": fd})
    anim_json = {"labelEnabled": True, "sequenceCount": len(seqs), "frameCount": len(results),
                 "sequences": seqs, "animationResults": results, "resultCount": len(results),
                 "labels": [f"CellAnime{i}" for i in range(len(seqs))], "labelCount": len(seqs)}

    prov = {
        "name": name, "state": "installed via res/graphics/battle/moves NARC pipeline; drawn by SPRITE_FUNC_OPAL_FX",
        "donor_sources": donor_files,
        "frames": [{"id": fid, "src": frames[fid]["spec"]["src"], "rect": frames[fid]["spec"].get("rect"),
                    "hflip": frames[fid]["spec"].get("hflip", False)} for fid in order],
        "sequences": [{"index": i, "name": sq.get("name"), "loop": bool(sq.get("loop")),
                       "frames": [f for f, _ in sq["frames"]], "total_delay": sum(d for _, d in sq["frames"])}
                      for i, sq in enumerate(recipe["sequences"])],
        "palette_colours_rgb555": [b1.rgb555(c + (255,)) for c in pal],
        "palette_variants_rgb555": variants,
        "obj_tiles": total_tiles, "tile_budget": max_tiles,
        "conversion": "indexed donor PNG (index 0 transparent) -> RGBA -> optional luminance ramp recolor -> "
                      "median-cut fold to one shared <=15 colour RGB555 palette -> 8px-aligned cells covered by "
                      "hardware-legal OAMs (B1 cover()) -> nitrogfx",
        "recipe": str(recipe_path.name),
    }
    (out_dir / f"{name}_cell.json").write_text(json.dumps(cell_json, indent=1) + "\n")
    (out_dir / f"{name}_anim.json").write_text(json.dumps(anim_json, indent=1) + "\n")
    (out_dir / f"{name}.provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    return prov


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("recipe", type=Path)
    ap.add_argument("--donor-root", type=Path, default=Path("/home/user/pokeemerald"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--max-tiles", type=int, default=MAX_TILES_DEFAULT)
    a = ap.parse_args()
    p = build(a.recipe, a.donor_root, a.out, a.max_tiles)
    print(json.dumps({"name": p["name"], "obj_tiles": p["obj_tiles"], "colours": len(p["palette_colours_rgb555"]),
                      "sequences": len(p["sequences"]), "variants": list(p["palette_variants_rgb555"])}))


if __name__ == "__main__":
    sys.exit(main())
