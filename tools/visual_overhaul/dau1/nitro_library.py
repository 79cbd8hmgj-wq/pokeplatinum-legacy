"""Scan Nitro containers (NARC, LZ-wrapped NARC) into catalog units + renderable frames.

Used for HeartGold/SoulSilver (anonymous NARC members, paired by proximity + validity) and Pokemon Ranger 2 packages
(named members, paired by stem).  Also performs SPL (.spa) particle-archive detection so the HGSS "move particle
archive" question is answered from evidence rather than assumption.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from . import bundle as bd
from . import nitro2d as n2
from .catalog import Unit
from .common import (BLOCKED_INPUT, DECODED, MISSING, STRUCTURAL_ONLY, UNSUPPORTED, DecodeError, lz_decompress,
                     sha256_bytes, sha256_file)
from .render import Frame, frames_hash, indexed_to_frame

SPL_MAGICS = (b" APS",)                         # "SPA " stored little-endian; followed by the version string "12_1"
MAX_SHEET_FRAMES = 96
AGGREGATE_OVER = 48          # per-container member count above which sprite/BG sets fold into one summary unit


def sniff(data: bytes) -> str:
    """Cheap content kind: NARC / LZ / NCER / ... / SPL / SDAT / other (looks through one LZ layer)."""
    if data[:4] == b"NARC":
        return "NARC"
    if data[:4] in SPL_MAGICS:
        return "SPL"
    k = bd.classify(data)
    if k:
        return k
    if data[:4] == b"SDAT":
        return "SDAT"
    if data[:4] in (b"BTX0", b"BMD0", b"BCA0", b"BTA0", b"BTP0", b"BMA0"):
        return data[:4].decode()
    if len(data) > 8 and data[0] in (0x10, 0x11):
        try:
            inner = lz_decompress(data)
        except DecodeError:
            return "LZ?"
        return "LZ+" + sniff(inner)
    return "other"


def _member_rows(members: list[bd.Member]) -> list[dict]:
    return [{"name": m.name or f"#{m.index}", "kind": m.kind, "sha256": sha256_bytes(m.data), "size": len(m.data)}
            for m in members]


def scan_container(library: str, rel: str, data: bytes, *, ranger: bool = False, uid_prefix: str | None = None):
    """Decode every cell bundle / orphan character sheet in one container.

    Returns (units, sheets, previews): unit id -> valid frames (DECODED) / frames rendered with an unverified palette.
    """
    uid = uid_prefix or f"{library}:{rel}"
    file_sha = sha256_bytes(data)
    units: list[Unit] = []
    sheets: dict[str, list[Frame]] = {}
    previews: dict[str, list[Frame]] = {}      # rendered but NOT trustworthy (guessed palette): never counted as decoded
    payload = data
    if payload[:1] in (b"\x10", b"\x11"):
        try:
            payload = lz_decompress(payload)
        except DecodeError as e:
            return [Unit(uid, library, rel, file_sha, "lz_container", UNSUPPORTED, error_reason=f"{e.code}: {e.message}")], sheets, previews
    if payload[:4] != b"NARC":
        return [Unit(uid, library, rel, file_sha, "nitro_loose", STRUCTURAL_ONLY,
                     error_reason=f"not a NARC (content kind {sniff(payload)}); loose files need their pairing from the build rules")], sheets, previews
    try:
        narc = n2.parse_narc(payload, rel)
    except DecodeError as e:
        return [Unit(uid, library, rel, file_sha, "narc", UNSUPPORTED, error_reason=f"{e.code}: {e.message}")], sheets, previews
    members = bd.classify_members(narc)
    pairs = list(bd.pair_bundles(members))
    used_chars: set[int] = set()
    used_pals: set[int] = set()
    for ncer, ncgr, nclr, nanr, how in pairs:
        mid = f"{uid}#{ncer.index}"
        parts = [m for m in (ncer, ncgr, nclr, nanr) if m is not None]
        mrows = _member_rows(parts)
        if ncgr is None or nclr is None:
            units.append(Unit(mid, library, rel, sha256_bytes(ncer.data), "nitro_cell_bank", STRUCTURAL_ONLY,
                              members=mrows, error_reason=("no character data" if ncgr is None else "no palette") +
                              f" could be paired with NCER member #{ncer.index} ({how})"))
            continue
        used_chars.add(ncgr.index)
        used_pals.add(nclr.index)
        res = bd.decode_cell_bundle(ncer.data, ncgr.data, nclr.data, nanr.data if nanr else None,
                                    trust_scan_header=not ranger)
        digest = sha256_bytes("".join(r["sha256"] for r in mrows).encode())
        status, reason = res.status, res.reason
        if how == "proximity-distant" and status == DECODED:
            status = STRUCTURAL_ONLY
            reason = (f"palette (member #{nclr.index}) is {abs(nclr.index - ncer.index)} members away from the cell bank; "
                      "graphic<->palette pairing is defined outside the archive, so colours are a guess")
        u = Unit(mid, library, rel, digest, "nitro_cell_bank", status, members=mrows)
        u.frame_count = res.valid_frames if status == DECODED else None
        u.palette_size = res.palette_size
        u.dimensions = res.dimensions
        u.tile_budget = res.tile_budget
        u.oam_budget = res.oam_budget
        u.error_reason = reason
        u.warnings = list(res.warnings)
        u.visual_sha256 = res.visual_sha256 if status == DECODED else None
        u.extra = {"pairing": how, "vram_mapping": res.mapping, "cells_total": res.cell_count,
                   "anim_sequences": res.anim_sequences, "anim_frames": res.anim_frames,
                   "invalid_cells": res.invalid_cells, "blank_cells": res.blank_cells}
        if status != DECODED and res.valid_frames:
            u.extra["preview_frames"] = res.valid_frames
        units.append(u)
        if res.valid_frames and res.status == DECODED:
            good = [res.frames[i] for i in range(len(res.frames))
                    if i not in set(res.invalid_cells) and i not in set(res.blank_cells)]
            (sheets if status == DECODED else previews)[mid] = good
    # Character sheets with no cell bank (BG tilesets, sprite libraries, pokemon graphics ...)
    orphans = [m for m in members if m.kind == "NCGR" and m.index not in used_chars]
    pals = [m for m in members if m.kind == "NCLR"]
    cs_sheets: dict[str, list[Frame]] = {}
    cs_units = _char_sheet_units(library, rel, uid, orphans, pals, cs_sheets)
    if len(cs_units) > AGGREGATE_OVER:
        units.append(_aggregate(library, rel, f"{uid}#chars", "nitro_char_sheet_set", cs_units, cs_sheets, sheets))
    else:
        units.extend(cs_units)
        sheets.update(cs_sheets)
    # Surface other recognised-but-undecoded kinds so nothing is silently dropped.
    scr = [m for m in members if m.kind == "NSCR"]
    scr_units = [Unit(f"{uid}#{m.index}", library, rel, sha256_bytes(m.data), "nitro_screen", UNSUPPORTED,
                      members=_member_rows([m]),
                      error_reason="NSCR tile-map screens are background compositions, not effect animation; "
                                   "decoder not implemented in DAU1") for m in scr]
    if scr_units:
        units.append(_aggregate(library, rel, f"{uid}#screens", "nitro_screen_set", scr_units, {}, sheets))
    # SPL particle archives (.spa) carried as NARC members (optionally LZ-wrapped)
    from . import spl as _spl
    for m in narc:
        raw = bd.maybe_decompress(m.data) if m.data[:1] in (b"\x10", b"\x11") else m.data
        if raw[:4] in SPL_MAGICS:
            su, sf = _spl.spl_unit(library, rel, raw)
            su.id = f"{uid}#{m.index}"
            units.append(su)
            if sf:
                sheets[su.id] = sf
    return units, sheets, previews


def _aggregate(library, rel, aid, atype, parts: list[Unit], part_sheets: dict, sheets: dict) -> Unit:
    """Fold a large homogeneous set into one honest summary unit (status counts + first frames for a sheet)."""
    ok = [p for p in parts if p.status == DECODED]
    by = Counter(p.status for p in parts)
    reasons = Counter((p.error_reason or "")[:80] for p in parts if p.status != DECODED)
    digest = sha256_bytes("".join(sorted(p.sha256 or "" for p in parts)).encode())
    u = Unit(aid, library, rel, digest, atype, DECODED if len(ok) == len(parts) else
             (STRUCTURAL_ONLY if ok else (parts[0].status if len({p.status for p in parts}) == 1 else STRUCTURAL_ONLY)))
    if ok:
        u.frame_count = sum(p.frame_count or 0 for p in ok)
        dims = [p.dimensions for p in ok if p.dimensions]
        if dims:
            u.dimensions = {"min": [min(d["min"][0] for d in dims), min(d["min"][1] for d in dims)],
                            "max": [max(d["max"][0] for d in dims), max(d["max"][1] for d in dims)]}
        u.palette_size = max((p.palette_size or 0) for p in ok) or None
        u.tile_budget = sum(p.tile_budget or 0 for p in ok)
        u.visual_sha256 = sha256_bytes("".join(sorted(p.visual_sha256 or "" for p in ok)).encode())
    if u.status != DECODED:
        u.error_reason = (f"{len(ok)}/{len(parts)} members decoded; " +
                          "; ".join(f"{n}x {r}" for r, n in reasons.most_common(3)))
    u.extra = {"members_total": len(parts), "members_by_status": dict(sorted(by.items()))}
    frames = [f for p in parts if p.status == DECODED for f in part_sheets.get(p.id, [])[:1]][:MAX_SHEET_FRAMES]
    if frames:
        sheets[aid] = frames
    return u


def _nearest_pal(m: bd.Member, pals: list[bd.Member]):
    best = None
    for p in sorted(pals, key=lambda x: (abs(x.index - m.index), x.index > m.index))[:6]:
        try:
            pal = n2.parse_nclr(p.data)
        except DecodeError:
            continue
        best = best or (p, pal)
        if pal.rows >= 1:
            return p, pal
    return best


def _char_sheet_units(library, rel, uid, orphans, pals, sheets):
    out = []
    for m in orphans:
        mid = f"{uid}#{m.index}"
        mrows = _member_rows([m])
        try:
            chars = n2.parse_ncgr(m.data)
        except DecodeError as e:
            out.append(Unit(mid, library, rel, sha256_bytes(m.data), "nitro_char_sheet", UNSUPPORTED,
                            members=mrows, error_reason=f"{e.code}: {e.message}"))
            continue
        near = _nearest_pal(m, pals)
        if near is None:
            out.append(Unit(mid, library, rel, sha256_bytes(m.data), "nitro_char_sheet", STRUCTURAL_ONLY, members=mrows,
                            error_reason="no NCLR in the same archive to colour the tiles"))
            continue
        pm, pal = near
        distant = len(pals) > 1 and abs(pm.index - m.index) > bd.ADJACENT
        try:
            width = chars.tiles_x or min(chars.tile_count, 16) or 1
            if chars.scanned and chars.tiles_x:
                sheet_w, tiles = chars.tiles(chars.tiles_x)
            else:
                sheet_w, tiles = chars.tiles()
                sheet_w = chars.tiles_x or width
        except DecodeError as e:
            out.append(Unit(mid, library, rel, sha256_bytes(m.data), "nitro_char_sheet", UNSUPPORTED, members=mrows,
                            error_reason=f"{e.code}: {e.message}"))
            continue
        rows = (len(tiles) + sheet_w - 1) // sheet_w
        w, h = sheet_w * 8, rows * 8
        if w * h > 1 << 20 or not tiles:
            out.append(Unit(mid, library, rel, sha256_bytes(m.data), "nitro_char_sheet", UNSUPPORTED, members=mrows,
                            error_reason=f"unreasonable sheet geometry {w}x{h}"))
            continue
        px = bytearray(w * h)
        for i, t in enumerate(tiles):
            tx, ty = (i % sheet_w) * 8, (i // sheet_w) * 8
            for y in range(8):
                px[(ty + y) * w + tx:(ty + y) * w + tx + 8] = t[y * 8:y * 8 + 8]
        rgb = pal.rgb()
        hi = max(px) if px else 0
        if hi >= len(rgb):
            out.append(Unit(mid, library, rel, sha256_bytes(m.data), "nitro_char_sheet", STRUCTURAL_ONLY, members=mrows,
                            error_reason=f"tiles index colour {hi} but the nearest palette (member #{pm.index}) has {len(rgb)} entries"))
            continue
        frame = indexed_to_frame(w, h, bytes(px), rgb)
        if not frame.opaque_pixels:
            out.append(Unit(mid, library, rel, sha256_bytes(m.data), "nitro_char_sheet", STRUCTURAL_ONLY, members=mrows,
                            error_reason="character sheet is entirely transparent with the paired palette"))
            continue
        if distant:
            out.append(Unit(mid, library, rel, sha256_bytes(m.data), "nitro_char_sheet", STRUCTURAL_ONLY, members=mrows + _member_rows([pm]),
                            palette_size=len(rgb), dimensions={"min": [w, h], "max": [w, h]}, tile_budget=len(tiles),
                            error_reason=f"nearest palette (member #{pm.index}) is {abs(pm.index - m.index)} members away; "
                                         "pairing is defined outside the archive so colours are a guess"))
            continue
        u = Unit(mid, library, rel, sha256_bytes(m.data), "nitro_char_sheet", DECODED, frame_count=1,
                 palette_size=len(rgb), dimensions={"min": [w, h], "max": [w, h]}, tile_budget=len(tiles), oam_budget=None,
                 members=mrows + _member_rows([pm]), visual_sha256=frames_hash([frame]))
        u.extra = {"palette_member": pm.index, "bpp": chars.bpp, "palette_pairing": "nearest"}
        out.append(u)
        sheets[mid] = [frame]
    return out
