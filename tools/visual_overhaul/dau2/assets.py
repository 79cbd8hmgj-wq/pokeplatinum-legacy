"""Asset layer: Platinum-native SPL units (the repository's own move particles), feature extraction, and the verified
name alignment of Diamond/HGSS move particles to Platinum move names.

Alignment evidence (all measured, none assumed): the Platinum particle list ``res/graphics/battle/particles/meson.build`` names
485 files in game order.  Diamond's ``waza_particle/narc_NNNN.bin`` and HGSS ``files/a/0/2/9#K`` are matched to it by *decoded texture
identity* (DAU1 ``visual_sha256``): an entry is ``TEXTURE_VERIFIED`` only if its decoded textures are pixel-identical to the Platinum file
it is aligned to; otherwise it stays ``UNVERIFIED_INDEX_ALIGNMENT`` (aligned by position only) and carries no name-based role.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from dau1 import fx_convert, spl as dspl
from dau1.catalog import Unit

PLAT_PARTICLES = "res/graphics/battle/particles"
HGSS_MOVE_NARC = "files/a/0/2/9"
DIAMOND_MOVE_DIR = "files/wazaeffect/effectdata/waza_particle/"
HGSS_OFFSET = 1          # measured: 341 of the matching HGSS entries sit at Platinum index + 1


def platinum_order(root: Path) -> list[str]:
    txt = (root / PLAT_PARTICLES / "meson.build").read_text()
    return [m[:-4] for m in re.findall(r"'([a-z0-9_]+\.spa)'", txt)]


def platinum_units(root: Path):
    """Decode every Platinum-native ``.spa`` under res/graphics/battle/particles (+ pokeballs). -> (units, frames_by_id)."""
    units, frames = [], {}
    base = root / PLAT_PARTICLES
    for p in sorted(base.rglob("*.spa")):
        rel = p.relative_to(root).as_posix()
        u, fr = dspl.spl_unit("platinum", rel, p.read_bytes())
        units.append(u)
        if fr:
            frames[u.id] = fr
            u.extra["opal_fx"] = fx_convert.estimate(fr)
    return units, frames


def spl_alignment(units: list[dict], order: list[str]) -> dict:
    """{unit_id: {'name': slug, 'basis': TEXTURE_VERIFIED|UNVERIFIED_INDEX_ALIGNMENT|EXACT_FILENAME}} for platinum/diamond/hgss move particles."""
    plat = {}
    for u in units:
        if u["library"] == "platinum" and u["source"].startswith(PLAT_PARTICLES + "/") and "/pokeballs/" not in u["source"]:
            plat[u["source"].rsplit("/", 1)[-1][:-4]] = u
    out = {}
    for name, u in plat.items():
        out[u["id"]] = {"name": name, "basis": "EXACT_FILENAME"}
    for u in units:
        lib, src = u["library"], u["source"]
        idx = None
        if lib == "diamond" and src.startswith(DIAMOND_MOVE_DIR):
            m = re.search(r"narc_(\d+)\.bin$", src)
            idx = int(m.group(1)) if m else None
        elif lib == "hgss" and src == HGSS_MOVE_NARC and "#" in u["id"]:
            idx = int(u["id"].rsplit("#", 1)[1]) - HGSS_OFFSET
        if idx is None or not 0 <= idx < len(order):
            continue
        name = order[idx]
        ref = plat.get(name)
        verified = bool(ref and u.get("visual_sha256") and u["visual_sha256"] == ref.get("visual_sha256"))
        out[u["id"]] = {"name": name, "basis": "TEXTURE_VERIFIED" if verified else "UNVERIFIED_INDEX_ALIGNMENT"}
    return out


def compact(f: dict) -> dict:
    """Drop bulky/rarely-needed keys so the committed feature file stays small."""
    if not f.get("usable"):
        return {"usable": False}
    return {"usable": True, **{k: f[k] for k in ("bw", "bh", "fill", "elong", "hollow", "components", "chromatic", "bright", "dominant_hues",
                              "neutral", "varies", "frames_sampled") if k in f}}


def build_features(ws: Path, root: Path, only=None):
    """Donor-dependent: decode everything, return (platinum_units(list of dict), {unit_id: features}, order). Needs numpy."""
    from dau1 import pipeline
    from . import features as F
    doc, sheets, _ = pipeline.run(ws, only)
    punits, pframes = platinum_units(root)
    feats = {}
    for lib, per in sheets.items():
        for uid, frames in per.items():
            feats[uid] = compact(F.unit_features(frames))
    for uid, frames in pframes.items():
        feats[uid] = compact(F.unit_features(frames))
    return doc, [u.to_json() for u in punits], feats, platinum_order(root), sheets, pframes
