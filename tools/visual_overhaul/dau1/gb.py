"""Game Boy Color (pokecrystal) battle-animation recipe reconstruction: 2bpp tile strip + assembly-defined layout.

Crystal stores each effect as
  * a 2bpp tile strip (``gfx/battle_anims/*.png``, 4 grey levels),
  * ``data/battle_anims/object_gfx.asm``  gfx id -> png,
  * ``data/battle_anims/objects.asm``     object -> frameset, palette, gfx id,
  * ``data/battle_anims/framesets.asm``   frameset -> [(oamset, duration)],
  * ``data/battle_anims/oam.asm``         oamset -> (vtile offset, sprite count, OAM data label); OAM data = 8x8 sprites,
  * ``gfx/battle_anims/battle_anims.pal`` named 4-colour palettes.
All of that is plain text, so a frame is reconstructed exactly (no coordinates are guessed).  Unknown inputs are reported.
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

from .common import DecodeError
from .render import Frame

GREY_TO_INDEX = {255: 0, 170: 1, 85: 2, 0: 3}       # pokecrystal 2bpp PNG convention (white = colour 0)


def _lines(path: Path) -> list[str]:
    return [re.sub(r";.*", "", ln).rstrip() for ln in path.read_text().splitlines()]


def parse_palettes(pal_file: Path) -> dict[str, list[tuple[int, int, int]]]:
    out, name, cur = {}, None, []
    for raw in pal_file.read_text().splitlines():
        m = re.match(r";\s*([A-Za-z0-9_ ]+)\s*$", raw.strip())
        if m and not cur:
            name = m.group(1).strip().upper().replace(" ", "_")
            continue
        m = re.match(r"\s*RGB\s+(\d+),\s*(\d+),\s*(\d+)", raw)
        if m and name:
            cur.append(tuple(int(m.group(i)) * 255 // 31 for i in (1, 2, 3)))
            if len(cur) == 4:
                out.setdefault(name, cur)
                cur, name = [], None
    return out


def parse_oam_sets(oam_asm: Path) -> dict[str, tuple[int, int, str]]:
    """BATTLE_ANIM_OAMSET_xx -> (vtile offset, sprite count, data label)."""
    out = {}
    for ln in oam_asm.read_text().splitlines():
        m = re.match(r"\s*battleanimoam\s+\$([0-9a-fA-F]+),\s*(\d+),\s*\.(\w+)\s*;\s*(BATTLE_ANIM_OAMSET_\w+)", ln)
        if m:
            out[m.group(4)] = (int(m.group(1), 16), int(m.group(2)), m.group(3))
    return out


def parse_oam_data(oam_asm: Path) -> dict[str, list[tuple[int, int, int, int]]]:
    """label -> [(x, y, tile, flags)] with x/y in pixels relative to the object origin (xflip=1, yflip=2)."""
    out, cur = {}, None
    for ln in _lines(oam_asm):
        m = re.match(r"\.(OAMData_\w+):", ln)
        if m:
            cur = out.setdefault(m.group(1), [])
            continue
        m = re.match(r"\s*dbsprite\s+(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(\$?\w+),\s*(.+)$", ln)
        if m and cur is not None:
            xt, yt, xo, yo = (int(m.group(i)) for i in range(1, 5))
            tile = int(m.group(5).lstrip("$"), 16) if m.group(5).startswith("$") else int(m.group(5))
            attr = m.group(6)
            flags = (1 if "OAM_XFLIP" in attr else 0) | (2 if "OAM_YFLIP" in attr else 0)
            cur.append((xt * 8 + xo, yt * 8 + yo, tile, flags))
    return out


def parse_framesets(fs_asm: Path) -> dict[str, list[tuple[str, int]]]:
    """frameset label ('Frameset_Ember') -> [(oamset const, duration)]; 'oamrestart' etc. are ignored."""
    out, cur = {}, None
    for ln in _lines(fs_asm):
        m = re.match(r"\.(Frameset_\w+):", ln)
        if m:
            cur = out.setdefault(m.group(1), [])
            continue
        m = re.match(r"\s*oamframe\s+(BATTLE_ANIM_OAMSET_\w+),\s*(\d+)", ln)
        if m and cur is not None:
            cur.append((m.group(1), int(m.group(2))))
    return out


def parse_frameset_names(fs_asm: Path) -> dict[str, str]:
    """BATTLE_ANIM_FRAMESET_X -> 'Frameset_Name' (from the pointer table comments)."""
    out = {}
    for ln in fs_asm.read_text().splitlines():
        m = re.match(r"\s*dw\s+\.(Frameset_\w+)\s*;\s*(BATTLE_ANIM_FRAMESET_\w+)", ln)
        if m:
            out[m.group(2)] = m.group(1)
    return out


def parse_objects(obj_asm: Path) -> list[tuple[str, str, str, str]]:
    """[(object const, frameset const, palette const, gfx const)]"""
    out, name = [], None
    for ln in obj_asm.read_text().splitlines():
        m = re.match(r";\s*(BATTLE_ANIM_OBJ_\w+)\s*$", ln)
        if m:
            name = m.group(1)
            continue
        m = re.match(r"\s*battleanimobj\s+\w+,\s*\$?\w+,\s*(\w+),\s*\w+,\s*(\w+),\s*(\w+)", ln)
        if m and name:
            out.append((name, m.group(1), m.group(2), m.group(3)))
            name = None
    return out


def parse_gfx_table(obj_gfx_asm: Path) -> dict[int, tuple[int, str]]:
    """gfx id -> (tile count, 'AnimObjFireGFX')  (order == BATTLE_ANIM_GFX_* constants)."""
    out = {}
    i = 0
    for ln in obj_gfx_asm.read_text().splitlines():
        m = re.match(r"\s*anim_obj_gfx\s+(\d+),\s*(\w+)", ln)
        if m:
            out[i] = (int(m.group(1)), m.group(2))
            i += 1
    return out


def load_strip(png: Path) -> list[bytes]:
    """Split a 2bpp PNG into 8x8 tiles of colour indices (column-major strip as stored: tiles row by row)."""
    im = Image.open(png)
    if im.mode not in ("L", "P"):
        raise DecodeError("UNSUPPORTED", f"{png.name}: mode {im.mode}")
    im = im.convert("L")
    w, h = im.size
    if w % 8 or h % 8:
        raise DecodeError("BAD_HEADER", f"{png.name}: {w}x{h} not tile aligned")
    px = im.load()
    tiles = []
    for ty in range(h // 8):
        for tx in range(w // 8):
            t = bytearray()
            for y in range(8):
                for x in range(8):
                    v = px[tx * 8 + x, ty * 8 + y]
                    if v not in GREY_TO_INDEX:
                        raise DecodeError("BAD_PALETTE_INDEX", f"{png.name}: grey level {v} is not one of the 4 Game Boy shades")
                    t.append(GREY_TO_INDEX[v])
            tiles.append(bytes(t))
    return tiles


def render_frameset(tiles: list[bytes], palette: list[tuple[int, int, int]], oamsets: dict, oamdata: dict,
                    frames: list[tuple[str, int]]):
    """Render every OAM set of a frameset.  Returns (frames, tile_budget, oam_budget).  Fails closed on any gap."""
    out, used, max_oam = [], set(), 0
    for oamset, _dur in frames:
        if oamset not in oamsets:
            raise DecodeError("BAD_OFFSET", f"unknown {oamset}")
        vt, n, label = oamsets[oamset]
        spr = oamdata.get(label)
        if spr is None or len(spr) < n:
            raise DecodeError("BAD_OFFSET", f"{label} holds {0 if spr is None else len(spr)} sprites, set wants {n}")
        spr = spr[:n]
        xs = [s[0] for s in spr] + [s[0] + 8 for s in spr]
        ys = [s[1] for s in spr] + [s[1] + 8 for s in spr]
        x0, y0, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
        rgba = bytearray(w * h * 4)
        for sx, sy, tile, fl in spr:
            ti = vt + tile
            if ti >= len(tiles):
                raise DecodeError("BAD_OFFSET", f"tile {ti} beyond the {len(tiles)}-tile strip")
            used.add(ti)
            t = tiles[ti]
            for y in range(8):
                for x in range(8):
                    v = t[(7 - y if fl & 2 else y) * 8 + (7 - x if fl & 1 else x)]
                    if v == 0:
                        continue              # colour 0 is transparent for OBJ
                    d = ((sy - y0 + y) * w + sx - x0 + x) * 4
                    rgba[d:d + 4] = bytes((*palette[v], 255))
        out.append(Frame(w, h, bytes(rgba)))
        max_oam = max(max_oam, n)
    return out, len(used), max_oam


# ------------------------------------------------------------------------------------- library scan
def scan_crystal(root: Path, library: str = "crystal"):
    """One unit per BATTLE_ANIM_OBJ_*: reconstructed from the assembly tables.  Returns (units, sheets)."""
    from .catalog import Unit
    from .common import DECODED, STRUCTURAL_ONLY, UNSUPPORTED, sha256_bytes, sha256_file
    from .render import frames_hash

    D = root / "data/battle_anims"
    pal = parse_palettes(root / "gfx/battle_anims/battle_anims.pal")
    oamsets, oamdata = parse_oam_sets(D / "oam.asm"), parse_oam_data(D / "oam.asm")
    fsets, fnames = parse_framesets(D / "framesets.asm"), parse_frameset_names(D / "framesets.asm")
    gfx_consts = [m.group(1) for ln in (root / "constants/battle_anim_constants.asm").read_text().splitlines()
                  if (m := re.match(r"\s*const\s+(BATTLE_ANIM_GFX_\w+)", ln))]
    gfx_tab = parse_gfx_table(D / "object_gfx.asm")
    incbin = {m.group(1): m.group(2) for ln in (root / "gfx/battle_anims.asm").read_text().splitlines()
              if (m := re.match(r"(\w+):\s+INCBIN\s+\"([^\"]+?)\.2bpp\.lz\"", ln))}
    units, sheets, cache = [], {}, {}
    for obj, fconst, palc, gfxc in parse_objects(D / "objects.asm"):
        uid = f"{library}:data/battle_anims/objects.asm#{obj}"
        base = dict(id=uid, library=library, source="data/battle_anims/objects.asm", type="gb_recipe_object")
        try:
            if gfxc not in gfx_consts:
                raise DecodeError("BAD_OFFSET", f"unknown {gfxc}")
            gi = gfx_consts.index(gfxc)
            ntiles, label = gfx_tab[gi]
            if label not in incbin:
                raise DecodeError("BAD_OFFSET", f"no INCBIN for {label} (placeholder gfx 0)")
            png = root / (incbin[label] + ".png")
            if not png.exists():
                raise DecodeError("MISSING", str(png.relative_to(root)))
            pname = palc.replace("PAL_BATTLE_OB_", "")
            if pname not in pal:
                raise DecodeError("UNSUPPORTED", f"{palc} is a run-time (party/enemy) palette, not defined in battle_anims.pal")
            if fconst not in fnames or fnames[fconst] not in fsets or not fsets[fnames[fconst]]:
                raise DecodeError("BAD_OFFSET", f"no frameset data for {fconst}")
            if png not in cache:
                cache[png] = load_strip(png)
            fr, tb, ob = render_frameset(cache[png], pal[pname], oamsets, oamdata, fsets[fnames[fconst]])
            if not any(f.opaque_pixels for f in fr):
                raise DecodeError("BLANK", "all frames blank")
            sha = sha256_file(png)
            u = Unit(**base, sha256=sha, status=DECODED, frame_count=len(fr), palette_size=4,
                     dimensions={"min": [min(f.width for f in fr), min(f.height for f in fr)],
                                 "max": [max(f.width for f in fr), max(f.height for f in fr)]},
                     tile_budget=tb, oam_budget=ob, visual_sha256=frames_hash(fr),
                     members=[{"name": str(png.relative_to(root)), "sha256": sha, "size": png.stat().st_size}])
            u.extra = {"frameset": fnames[fconst], "palette": palc, "gfx": gfxc, "durations": [d for _, d in fsets[fnames[fconst]]],
                       "reconstruction": "text tables (objects/framesets/oam/object_gfx) + 2bpp PNG; nothing inferred"}
            units.append(u)
            sheets[uid] = fr
        except DecodeError as e:
            st = UNSUPPORTED if e.code in ("UNSUPPORTED", "BAD_PALETTE_INDEX", "BLANK") else STRUCTURAL_ONLY
            units.append(Unit(**base, sha256=None, status=st, error_reason=f"{e.code}: {e.message}"))
    return units, sheets
