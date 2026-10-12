"""Local, untracked review imagery: per-move side-by-side boards and indexed library contact sheets, from REAL decoded frames.

Every cell carries an index number; ``ASSET_INDEX.json`` (committed, metadata only) resolves each (sheet, cell) to an immutable asset id
and records the SHA-256 of the cell's *pixel data* (not of the PNG file, whose bytes depend on the zlib/Pillow build).  The images
themselves are written under ``build/dau2`` (git-ignored) and are never committed: they contain decoded Nintendo artwork.
"""
from __future__ import annotations

import hashlib

from PIL import Image, ImageDraw, ImageFont

CELL = 64
BG = (40, 42, 52)
CHECK_A, CHECK_B = (84, 86, 96), (100, 102, 112)
FONT = ImageFont.load_default()


def _checker(w, h):
    im = Image.new("RGB", (w, h), CHECK_A)
    d = ImageDraw.Draw(im)
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            if (x // 8 + y // 8) % 2:
                d.rectangle((x, y, x + 7, y + 7), fill=CHECK_B)
    return im


def fit(frame, cell=CELL) -> Image.Image:
    """One frame centred in a cell on a checker, integer up-scale (NEAREST) when it is small, crop-free down-scale otherwise."""
    img = frame.image()
    w, h = img.size
    k = max(1, min(cell // max(w, 1), cell // max(h, 1), 4))
    if w * k > cell or h * k > cell:                                  # larger than a cell: shrink (NEAREST keeps pixels crisp)
        s = cell / max(w, h)
        img = img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.NEAREST)
    elif k > 1:
        img = img.resize((w * k, h * k), Image.NEAREST)
    tile = _checker(cell, cell)
    tile.paste(img, ((cell - img.width) // 2, (cell - img.height) // 2), img)
    return tile


def pick_frames(frames, n):
    if len(frames) <= n:
        return list(frames)
    idx = sorted({round(i * (len(frames) - 1) / (n - 1)) for i in range(n)})
    return [frames[i] for i in idx]


def strip(frames, n=3) -> Image.Image:
    fs = pick_frames(frames, n)
    im = Image.new("RGB", (CELL * len(fs) + 2 * (len(fs) - 1), CELL), BG)
    for k, f in enumerate(fs):
        im.paste(fit(f), (k * (CELL + 2), 0))
    return im


def pixel_sha(im: Image.Image) -> str:
    return hashlib.sha256(f"{im.width}x{im.height}:".encode() + im.tobytes()).hexdigest()


def board(move: dict, frames_of, short) -> tuple[Image.Image, list[dict]]:
    """Side-by-side board: one row per component, candidates left-to-right (native baseline first)."""
    comps = []
    for r in move["candidates"]:
        if not comps or comps[-1][0] != r["component"]:
            comps.append((r["component"], []))
        comps[-1][1].append(r)
    cw = 3 * CELL + 4 + 8
    cols = max(len(c[1]) for c in comps)
    W, H = max(cols * cw + 12, 560), 46 + len(comps) * (CELL + 52)
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((8, 4), f"{move['move']}  [{move['tier'][:2]}]  {move['template']}: {move['visual_intent']}", fill=(235, 235, 240), font=FONT)
    d.text((8, 18), f"status {move['status']}   visual decision: {move['visual_decision']}   (heuristic = search aid, not approval)", fill=(190, 190, 120), font=FONT)
    cells, y = [], 40
    for name, rs in comps:
        d.text((8, y), name.upper(), fill=(140, 200, 255), font=FONT)
        y += 12
        for k, r in enumerate(rs):
            x = 6 + k * cw
            t = strip(frames_of(r["asset_id"]))
            im.paste(t, (x, y))
            col = {"named_move_particle": (120, 220, 140), "named_source": (120, 200, 230), "feature_heuristic": (230, 180, 110)}[r["evidence_basis"]]
            d.text((x, y + CELL + 2), f"#{r['board_cell_index']} {r['library']} {r['score']}", fill=col, font=FONT)
            d.text((x, y + CELL + 13), short(r["asset_id"])[:34], fill=(200, 200, 205), font=FONT)
            d.text((x, y + CELL + 24), r["evidence_basis"].replace("_", " ")[:30], fill=col, font=FONT)
            cells.append({"cell": r["board_cell_index"], "asset_id": r["asset_id"], "component": name, "thumb_pixel_sha256": pixel_sha(t)})
        y += CELL + 40
    return im, cells


def survey_page(ids, frames_of, short, title, cols=10) -> tuple[Image.Image, list[dict]]:
    rows = (len(ids) + cols - 1) // cols
    cw, ch = CELL + 6, CELL + 14
    im = Image.new("RGB", (cols * cw + 6, rows * ch + 20), BG)
    d = ImageDraw.Draw(im)
    d.text((6, 4), title, fill=(235, 235, 240), font=FONT)
    cells = []
    for n, i in enumerate(ids):
        x, y = 6 + (n % cols) * cw, 20 + (n // cols) * ch
        t = fit(frames_of(i)[0])
        im.paste(t, (x, y))
        d.text((x, y + CELL + 1), f"{n}", fill=(200, 200, 205), font=FONT)
        cells.append({"cell": n, "asset_id": i, "thumb_pixel_sha256": pixel_sha(t)})
    return im, cells
