"""One-command multi-library pipeline: discover -> decode -> hash -> catalog (+ galleries, blockers, source ledger).

``run(workspace)`` inspects every donor checkout found next to this repository, decodes what it can, and returns a
deterministic catalog document.  Absent sources are reported (MISSING / BLOCKED_INPUT / ``sources[*].present = false``),
never invented.  No donor bytes are embedded: only hashes, counts and budgets.
"""
from __future__ import annotations

import os
import subprocess
from collections import Counter
from pathlib import Path

from . import bundle as bd
from . import gb, gba, nitro2d as n2, nitro_library as nl, pmd_effect as pe, ranger_tex, spl
from .catalog import SCHEMA_VERSION, Unit, coverage, find_duplicates
from .common import (BLOCKED_INPUT, DECODED, MISSING, STRUCTURAL_ONLY, UNSUPPORTED, DecodeError, sha256_bytes,
                     sha256_file)
from .render import Frame, frames_hash

# library id -> (label, directory candidates relative to the workspace, role)
LIBRARIES = {
    "hgss": ("Pokemon HeartGold/SoulSilver (pokeheartgold)", ("pokeheartgold",), "priority F1"),
    "pmd_sky": ("Pokemon Mystery Dungeon: Explorers of Sky (pmd-sky)", ("pmd-sky",), "priority F2"),
    "ranger2": ("Pokemon Ranger: Shadows of Almia (pokeranger2)", ("pokeranger2",), "priority F3"),
    "ruby": ("Pokemon Ruby/Sapphire (pokeruby)", ("pokeruby", "79cbd8hmgj-wq/pokeruby"), "F4"),
    "emerald": ("Pokemon Emerald (pokeemerald)", ("pokeemerald",), "baseline donor"),
    "firered": ("Pokemon FireRed/LeafGreen (pokefirered)", ("pokefirered",), "baseline donor"),
    "crystal": ("Pokemon Crystal (pokecrystal)", ("pokecrystal",), "F5"),
    "yellow": ("Pokemon Yellow (pokeyellow)", ("pokeyellow",), "F5"),
    "diamond": ("Pokemon Diamond/Pearl (pokediamond)", ("pokediamond", "79cbd8hmgj-wq/pokediamond"), "extra DP-lineage donor"),
}


def find_root(ws: Path, cands: tuple[str, ...]) -> Path | None:
    for c in cands:
        p = ws / c
        if p.is_dir() and any(p.iterdir()):
            return p
    return None


def _git(root: Path, *args) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:                                    # noqa: BLE001
        return None


def source_ledger(lib: str, root: Path | None) -> dict:
    label, cands, role = LIBRARIES[lib]
    out = {"library": lib, "label": label, "role": role, "expected_paths": list(cands), "present": root is not None}
    if root is None:
        out["status"] = BLOCKED_INPUT
        out["note"] = "checkout not found in the workspace"
        return out
    lic = sorted(p.name for p in root.iterdir() if p.is_file() and p.name.upper().startswith(("LICENSE", "COPYING", "UNLICENSE")))
    out.update({"commit": _git(root, "rev-parse", "HEAD"), "origin": _git(root, "remote", "get-url", "origin"),
                "shallow": (_git(root, "rev-parse", "--is-shallow-repository") == "true"),
                "code_license_files": lic,
                "asset_license": "UNVERIFIED: decomp source licences do not grant redistribution rights over the original game artwork"})
    return out


def walk_files(root: Path, sub: str = "."):
    base = root / sub
    for dirpath, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for f in sorted(files):
            yield Path(dirpath) / f


# --------------------------------------------------------------------------------------- per library
def scan_hgss(root: Path):
    units, sheets, previews = [], {}, {}
    n_narc = 0
    for p in walk_files(root, "files"):
        try:
            with open(p, "rb") as fh:
                if fh.read(4) != b"NARC":
                    continue
            data = p.read_bytes()
        except OSError:
            continue
        n_narc += 1
        u, s, pv = nl.scan_container("hgss", p.relative_to(root).as_posix(), data)
        units += u
        sheets.update(s)
        previews.update(pv)
    # baserom-extracted files that the filesystem manifest lists but the checkout does not carry
    for sha1 in ("heartgold.us/filesystem.sha1",):
        f = root / sha1
        if f.exists():
            for line in f.read_text().splitlines():
                if " *" not in line:
                    continue
                h, rel = line.split(" *", 1)
                if not (root / rel).exists():
                    units.append(Unit(f"hgss:{rel}", "hgss", rel, None, "baserom_file", MISSING,
                                      error_reason=f"listed in {sha1} (sha1 {h}) but not in the checkout; supplied only by extracting a legally owned base ROM",
                                      extra={"expected_sha1": h}))
    return units, sheets, previews, n_narc


def scan_diamond(root: Path):
    """pokediamond: loose Nitro files (stem-aligned across sibling dirs) and loose SPL archives."""
    units, sheets = [], {}
    by_dir: dict[Path, dict[str, dict[str, Path]]] = {}
    for p in walk_files(root, "files"):
        ext = p.suffix.lower()
        if ext in (".ncer", ".ncgr", ".nclr", ".nanr"):
            by_dir.setdefault(p.parent, {}).setdefault(p.stem, {})[ext] = p
        elif p.suffix == ".bin" and p.stat().st_size >= 32:
            with open(p, "rb") as fh:
                if fh.read(4) != b" APS":
                    continue
            rel = p.relative_to(root).as_posix()
            u, fr = spl.spl_unit("diamond", rel, p.read_bytes())
            units.append(u)
            if fr:
                sheets[u.id] = fr
    for d, stems in sorted(by_dir.items(), key=lambda kv: str(kv[0])):
        sib = [x for x in d.parent.iterdir() if x.is_dir()] if d.parent != root else []
        lookup: dict[str, dict[str, Path]] = {}
        for sd in [d] + sorted(sib):
            for stem, files in by_dir.get(sd, {}).items():
                for ext, path in files.items():
                    lookup.setdefault(stem, {}).setdefault(ext, path)
        for stem, files in sorted(stems.items()):
            if ".ncer" not in files:
                continue
            rel = files[".ncer"].relative_to(root).as_posix()
            uid = f"diamond:{rel}"
            got = lookup.get(stem, {})
            missing = [e for e in (".ncgr", ".nclr") if e not in got]
            if missing:
                units.append(Unit(uid, "diamond", rel, sha256_file(files[".ncer"]), "nitro_cell_bank", STRUCTURAL_ONLY,
                                  error_reason=f"no same-stem {', '.join(m.upper() for m in missing)} in the directory or its siblings"))
                continue
            parts = [got[".ncer"], got[".ncgr"], got[".nclr"]] + ([got[".nanr"]] if ".nanr" in got else [])
            res = bd.decode_cell_bundle(*(p.read_bytes() for p in parts[:3]), parts[3].read_bytes() if len(parts) > 3 else None)
            rows = [{"name": q.relative_to(root).as_posix(), "sha256": sha256_file(q), "size": q.stat().st_size} for q in parts]
            digest = sha256_bytes("".join(r["sha256"] for r in rows).encode())
            u = Unit(uid, "diamond", rel, digest, "nitro_cell_bank", res.status, members=rows)
            u.frame_count = res.valid_frames if res.status == DECODED else None
            u.palette_size, u.dimensions, u.tile_budget, u.oam_budget = res.palette_size, res.dimensions, res.tile_budget, res.oam_budget
            u.error_reason, u.warnings = res.reason, list(res.warnings)
            u.visual_sha256 = res.visual_sha256
            u.extra = {"pairing": "stem" if {q.parent for q in parts} == {d} else "stem-sibling-dirs",
                       "vram_mapping": res.mapping, "cells_total": res.cell_count, "anim_sequences": res.anim_sequences,
                       "anim_frames": res.anim_frames, "invalid_cells": res.invalid_cells, "blank_cells": res.blank_cells}
            units.append(u)
            if res.status == DECODED and res.valid_frames:
                sheets[uid] = [res.frames[i] for i in range(len(res.frames))
                               if i not in set(res.invalid_cells) and i not in set(res.blank_cells)]
    return units, sheets


def scan_pmd(root: Path):
    units, sheets = [], {}
    pack = root / "files/EFFECT/effect.bin"
    rel = "files/EFFECT/effect.bin"
    if not pack.exists():
        return [Unit(f"pmd_sky:{rel}", "pmd_sky", rel, None, "pmd_pack", MISSING, error_reason="effect.bin not present")], sheets
    data = pack.read_bytes()
    try:
        ents = pe.parse_pack(data)
    except DecodeError as e:
        return [Unit(f"pmd_sky:{rel}", "pmd_sky", rel, sha256_bytes(data), "pmd_pack", UNSUPPORTED,
                     error_reason=f"{e.code}: {e.message}")], sheets
    for i, (o, l) in enumerate(ents):
        blob = data[o:o + l]
        uid = f"pmd_sky:{rel}#{i}"
        r = pe.decode_effect_entry(blob)
        u = Unit(uid, "pmd_sky", rel, sha256_bytes(blob), "pmd_effect_wan", r.status,
                 members=[{"name": f"entry {i}", "sha256": sha256_bytes(blob), "size": l}])
        u.error_reason = r.reason
        u.warnings = list(r.warnings)
        u.palette_size = r.palette_colors or None
        u.extra = {"entry": i, "offset": o, "image_type": r.image_type, "metaframes": r.metaframes,
                   "sequences": r.sequences, "palette_rows": r.palette_rows,
                   "invalid_metaframes": len(r.invalid_metaframes), "blank_metaframes": r.blank_metaframes}
        if r.status == DECODED:
            u.frame_count = len(r.frames)
            u.dimensions, u.tile_budget, u.oam_budget = r.dimensions, r.tile_budget, r.oam_budget
            u.visual_sha256 = frames_hash(r.frames)
            sheets[uid] = r.frames
        units.append(u)
    # other PMD sprite families are a different WAN flavour (character sprites) - inventory, do not claim
    fam = Counter()
    for sub in ("GROUND", "FONT", "DUNGEON", "MONSTER"):
        for p in walk_files(root, f"files/{sub}"):
            if p.suffix.lower() == ".wan":
                fam[sub] += 1
    if fam:
        units.append(Unit("pmd_sky:files/*.wan", "pmd_sky", "files/GROUND|FONT|DUNGEON", None, "pmd_character_wan_set",
                          UNSUPPORTED, error_reason=f"{sum(fam.values())} character/prop WAN sprites ({dict(fam)}); the chara-WAN layout is a different variant and is not decoded by DAU1",
                          extra={"counts": dict(fam)}))
    return units, sheets


def scan_ranger(root: Path):
    units, sheets, previews = [], {}, {}
    data_root = root / "res/prebuilt/data"
    for p in sorted(data_root.rglob("*_LZ.bin")) if data_root.exists() else []:
        rel = p.relative_to(root).as_posix()
        sub = p.relative_to(data_root).parts[0]
        if sub not in ("effect", "field"):                # effect packages (e*, ef*, ew*); other trees are not effect art
            continue
        u, s, pv = nl.scan_container("ranger2", rel, p.read_bytes(), ranger=True)
        units += u
        sheets.update(s)
        previews.update(pv)
    for p in sorted(data_root.rglob("*.ntft")) if data_root.exists() else []:
        rel = p.relative_to(root).as_posix()
        pal = p.with_suffix(".ntfp")
        u, f = ranger_tex.texture_unit("ranger2", rel, p.read_bytes(), pal.read_bytes() if pal.exists() else None)
        units.append(u)
        if f is not None and u.status == DECODED:
            sheets[u.id] = [f]
    return units, sheets, previews


def scan_gba(lib: str, root: Path):
    units, sheets = [], {}
    for p in sorted((root / "graphics/battle_anims/sprites").glob("*.png")) if (root / "graphics/battle_anims").exists() else []:
        u, f = gba.png_unit(lib, root, p.relative_to(root).as_posix())
        units.append(u)
        if f is not None:
            sheets[u.id] = [f]
    return units, sheets


def compare_gba(by_lib: dict[str, list[Unit]]):
    """Cross-library comparison by content (Ruby names its sprites by number, so names cannot be matched).

    For every Ruby / FireRed / Emerald sprite: ``identical`` (same file bytes), ``same_pixels`` (same RGBA after decode),
    ``same_indices_other_palette`` (same index art, recoloured) or ``unique`` (no counterpart in the other libraries).
    """
    libs = [l for l in ("emerald", "firered", "ruby") if l in by_lib]
    maps = {}
    for key in ("sha256", "visual_sha256", "index_sha256"):
        maps[key] = {}
        for lib in libs:
            for u in by_lib[lib]:
                v = u.sha256 if key == "sha256" else (u.visual_sha256 if key == "visual_sha256" else u.extra.get("index_sha256"))
                if v:
                    maps[key].setdefault(v, set()).add(lib)
    for lib in libs:
        others = [l for l in libs if l != lib]
        for u in by_lib[lib]:
            def seen(key, v):
                return bool(v) and bool(maps[key].get(v, set()) - {lib})
            if seen("sha256", u.sha256):
                kind = "identical"
            elif seen("visual_sha256", u.visual_sha256):
                kind = "same_pixels"
            elif seen("index_sha256", u.extra.get("index_sha256")):
                kind = "same_indices_other_palette"
            else:
                kind = "unique"
            u.extra["cross_library"] = kind
            u.extra["compared_against"] = others


def scan_gb(lib: str, root: Path):
    units, sheets = [], {}
    if lib == "crystal":
        if (root / "data/battle_anims/objects.asm").exists():
            units, sheets = gb.scan_crystal(root)
        return units, sheets
    for p in sorted((root / "gfx/battle").glob("move_anim_*.png")):
        rel = p.relative_to(root).as_posix()
        sha = sha256_file(p)
        try:
            tiles = gb.load_strip(p)
            units.append(Unit(f"{lib}:{rel}", lib, rel, sha, "gb_tile_sheet", STRUCTURAL_ONLY, palette_size=4,
                              tile_budget=sum(1 for t in tiles if any(t)),
                              error_reason="2bpp tile sheet decodes, but Yellow's subanimation/frame-block layout tables were not reconstructed in DAU1",
                              members=[{"name": rel, "sha256": sha, "size": p.stat().st_size}]))
        except DecodeError as e:
            units.append(Unit(f"{lib}:{rel}", lib, rel, sha, "gb_tile_sheet", UNSUPPORTED, error_reason=f"{e.code}: {e.message}"))
    return units, sheets


# --------------------------------------------------------------------------------------- run
ESTIMATE_TYPES = ("nitro_cell_bank", "pmd_effect_wan", "spl_particle_archive", "gb_recipe_object", "gba_indexed_png",
                  "ds_ntft_texture")


def annotate_opal_fx(units: list[Unit], sheets: dict) -> None:
    """Attach the Opal-FX conversion cost estimate (tiles / colours / translucency / hue hint) to decoded units."""
    from . import fx_convert
    for lib, per in sheets.items():
        for u in units:
            if u.library == lib and u.status == DECODED and u.type in ESTIMATE_TYPES and u.id in per:
                try:
                    u.extra["opal_fx"] = fx_convert.estimate(per[u.id])
                except Exception as e:                   # noqa: BLE001 - estimation must never abort the catalog
                    u.extra["opal_fx"] = {"convertible": False, "reason": f"estimate failed: {type(e).__name__}: {e}"}


def run(ws: Path, only: list[str] | None = None):
    """Return (catalog document, sheets {library: {unit id: [Frame]}})."""
    units: list[Unit] = []
    sheets: dict[str, dict[str, list[Frame]]] = {}
    previews: dict[str, dict[str, list[Frame]]] = {}
    ledger = []
    by_lib: dict[str, list[Unit]] = {}
    for lib in LIBRARIES:
        if only and lib not in only:
            continue
        root = find_root(ws, LIBRARIES[lib][1])
        ledger.append(source_ledger(lib, root))
        if root is None:
            continue
        if lib == "hgss":
            u, s, pv, _ = scan_hgss(root)
            previews[lib] = pv
        elif lib == "diamond":
            u, s = scan_diamond(root)
        elif lib == "pmd_sky":
            u, s = scan_pmd(root)
        elif lib == "ranger2":
            u, s, pv = scan_ranger(root)
            previews[lib] = pv
        elif lib in ("ruby", "emerald", "firered"):
            u, s = scan_gba(lib, root)
        else:
            u, s = scan_gb(lib, root)
        by_lib[lib] = u
        units += u
        sheets[lib] = s
    compare_gba(by_lib)
    annotate_opal_fx(units, sheets)
    units.sort(key=lambda x: x.id)
    ud = [u.to_json() for u in units]
    doc = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "tools/visual_overhaul/dau1_unlock.py catalog",
        "status_vocabulary": ["DECODED", "STRUCTURAL_ONLY", "UNSUPPORTED", "MISSING", "BLOCKED_INPUT"],
        "sources": ledger,
        "coverage": coverage(ud),
        "duplicates": find_duplicates(ud),
        "units": ud,
    }
    return doc, sheets, previews
