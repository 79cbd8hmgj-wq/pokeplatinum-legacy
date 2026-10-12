"""Decoded donor frames -> Opal FX cell/sheet format (the PR #110 ``build_opal_fx_sheet.py`` pipeline), with cost checks.

Path:  decoded RGBA frames (any library)
       -> alpha binarised at 128 (OBJ art has no partial alpha; the number of dropped translucent pixels is reported)
       -> one shared <=15-colour RGB555 palette (index 0 transparent; builder median-cut when more colours exist)
       -> indexed donor strip PNG + recipe JSON (``emerald_png`` source type, so the unchanged builder consumes it)
       -> build_opal_fx_sheet.build(): 8px-aligned cells covered by hardware-legal OAMs, cell/anim JSON, provenance.
Nothing is installed into ``res/`` - this is tooling only.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from PIL import Image

from .render import Frame

HERE = Path(__file__).resolve().parent
_BUILDER = None


def builder():
    global _BUILDER
    if _BUILDER is None:
        spec = importlib.util.spec_from_file_location("opal_fx_builder", HERE.parent / "opal_fx/build_opal_fx_sheet.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _BUILDER = mod
    return _BUILDER


def _bbox_crop(f: Frame) -> Image.Image | None:
    im = f.image()
    bb = im.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
    return im.crop(bb) if bb else None


def hue_bucket(rgb_sum: tuple[int, int, int], n: int) -> str:
    """Coarse dominant-colour name of the opaque pixels (a role *hint* for anonymous donors, never a classification)."""
    import colorsys
    r, g, b = (v / n / 255 for v in rgb_sum)
    h, l, sat = colorsys.rgb_to_hls(r, g, b)[0], colorsys.rgb_to_hls(r, g, b)[1], colorsys.rgb_to_hls(r, g, b)[2]
    if l < 0.18:
        return "black"
    if sat < 0.12:
        return "white" if l > 0.7 else "grey"
    h *= 360
    for hi, name in ((15, "red"), (45, "orange"), (70, "yellow"), (160, "green"), (200, "cyan"), (260, "blue"),
                     (310, "purple"), (345, "pink"), (361, "red")):
        if h < hi:
            return name
    return "red"


def estimate(frames: list[Frame], max_frames: int = 16) -> dict:
    """Cheap cost estimate (no files): OBJ tiles, max OAMs per cell, colours, translucent pixels, largest frame."""
    b = builder()
    cropped = [c for c in (_bbox_crop(f) for f in frames[:max_frames]) if c is not None]
    if not cropped:
        return {"convertible": False, "reason": "all frames fully transparent"}
    translucent, colours = 0, set()
    tiles = oams = 0
    rsum = [0, 0, 0]
    npx = 0
    for im in cropped:
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                a = px[x, y][3]
                if 0 < a < 128:
                    translucent += 1
                elif a >= 128:
                    colours.add(b.snap555(px[x, y][:3]))
                    rsum[0] += px[x, y][0]; rsum[1] += px[x, y][1]; rsum[2] += px[x, y][2]
                    npx += 1
        w8, h8 = (im.width + 7) // 8 * 8, (im.height + 7) // 8 * 8
        mask = [[any(px[tx * 8 + xx, ty * 8 + yy][3] >= 128
                     for yy in range(8) for xx in range(8)
                     if tx * 8 + xx < im.width and ty * 8 + yy < im.height)
                 for tx in range(w8 // 8)] for ty in range(h8 // 8)]
        cov = b.b1.cover(w8, h8, mask)
        oams = max(oams, len(cov))
        tiles += sum(sw * sh for (_, _, sw, sh, _) in cov)
    return {"convertible": True, "frames_estimated": len(cropped), "obj_tiles": tiles, "max_oams_per_cell": oams,
            "colours": len(colours), "translucent_pixels_dropped": translucent,
            "hue": hue_bucket(tuple(rsum), npx) if npx else None,
            "largest_frame": [max(i.width for i in cropped), max(i.height for i in cropped)]}


def to_donor_strip(frames: list[Frame], max_colors: int = 15):
    """Return (indexed PIL image, [(x, y, w, h)], report) stacking the frames vertically with 8px padding."""
    b = builder()
    cropped = [c for c in (_bbox_crop(f) for f in frames) if c is not None]
    if not cropped:
        raise ValueError("no visible frames")
    pal = b.fold_palette(cropped, max_colors)
    width = max((c.width + 7) // 8 * 8 for c in cropped)
    heights = [(c.height + 7) // 8 * 8 for c in cropped]
    strip = Image.new("P", (width, sum(heights)), 0)
    flat = [0, 0, 0]
    for c in pal:
        flat += list(c)
    flat += [0] * (768 - len(flat))
    strip.putpalette(flat)
    sp = strip.load()
    rects, y = [], 0
    dropped = 0
    for c, h in zip(cropped, heights):
        px = c.load()
        ox = (width - c.width) // 2
        for yy in range(c.height):
            for xx in range(c.width):
                p = px[xx, yy]
                if p[3] >= 128:
                    sp[ox + xx, y + yy] = 1 + b.nearest(pal, b.snap555(p[:3]))
                elif p[3] > 0:
                    dropped += 1
        rects.append((0, y, width, h))
        y += h
    return strip, rects, {"palette_colours": len(pal), "translucent_pixels_dropped": dropped}


def convert(name: str, frames: list[Frame], out_dir: Path, delays: list[int] | None = None, max_tiles: int = 192,
            source_note: dict | None = None) -> dict:
    """Run the full conversion.  Raises SystemExit (from the builder) when a hard budget is exceeded."""
    out_dir.mkdir(parents=True, exist_ok=True)
    donor = out_dir / "donor"
    donor.mkdir(exist_ok=True)
    strip, rects, rep = to_donor_strip(frames)
    strip_name = f"{name}_strip.png"
    strip.save(donor / strip_name, optimize=False)
    delays = delays or [4] * len(rects)
    recipe = {
        "name": name,
        "donor": "dau1 decoded frames (see provenance.dau1)",
        "sources": {"s": {"type": "emerald_png", "path": strip_name}},
        "frames": [{"id": f"f{i:02d}", "src": "s", "rect": list(r)} for i, r in enumerate(rects)],
        "sequences": [{"name": "play", "loop": False, "frames": [[f"f{i:02d}", delays[i % len(delays)]] for i in range(len(rects))]}],
        "max_colors": 15,
    }
    rp = out_dir / f"{name}.recipe.json"
    rp.write_text(json.dumps(recipe, indent=1) + "\n")
    try:
        prov = builder().build(rp, donor, out_dir, max_tiles)
    except SystemExit as e:                      # the builder fails closed on hard budgets
        rep_fail = {"name": name, "frames": len(rects), "ok": False, "error": str(e), "source": source_note or {}}
        (out_dir / f"{name}.dau1_conversion.json").write_text(json.dumps(rep_fail, indent=1, sort_keys=True) + "\n")
        return rep_fail
    cell = json.loads((out_dir / f"{name}_cell.json").read_text())
    oams = max((c["oamCount"] for c in cell["cells"]), default=0)
    sheet = Image.open(out_dir / f"{name}.png")
    checks = {
        "transparency": {"index0_transparent": True, "translucent_pixels_dropped": rep["translucent_pixels_dropped"]},
        "palette": {"colours": len(prov["palette_colours_rgb555"]), "limit": 15,
                    "ok": len(prov["palette_colours_rgb555"]) <= 15},
        "tiles": {"obj_tiles": prov["obj_tiles"], "budget": max_tiles, "ok": prov["obj_tiles"] <= max_tiles},
        "oam": {"max_oams_per_cell": oams, "limit": 128, "ok": oams <= 128},
        "sheet": {"size": list(sheet.size), "mode": sheet.mode},
    }
    report = {"name": name, "frames": len(rects), "checks": checks, "ok": all(c.get("ok", True) for c in checks.values()),
              "source": source_note or {}}
    (out_dir / f"{name}.dau1_conversion.json").write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    return report
