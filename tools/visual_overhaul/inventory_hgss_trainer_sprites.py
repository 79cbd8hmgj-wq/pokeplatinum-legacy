#!/usr/bin/env python3
"""Targeted HGSS catalog extension: trainer battle sprites (front a/0/5/8, back a/0/0/6).

Writes, under docs/visual_overhaul/catalog_extensions/hgss_trainer_sprites/:
  CATALOG.json   catalog-schema records (one per class/view sprite set; exact NARC member provenance)
  CURATION.json  recovered-curation-schema records (usable/reject + render evidence)
  renders/*.png  decoded stacked-cell sheets (indexed) used as visual evidence
Read-only on the HGSS checkout. Nothing in Platinum is modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nitro_narc import read_narc  # noqa: E402
import hgss_trainer_sprite_lib as lib  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/visual_overhaul/catalog_extensions/hgss_trainer_sprites"
MEMBERS = ("ncgr", "nclr", "ncer", "nanr", "ncbr")


def class_names(hgss: Path) -> dict[int, str]:
    txt = (hgss / "include/constants/trainer_class.h").read_text()
    return {int(i): n for n, i in re.findall(r"define TRAINERCLASS_(\w+)\s+(\d+)", txt)}


def backpic_names(hgss: Path) -> dict[int, str]:
    txt = (hgss / "include/constants/trainer_class.h").read_text()
    return {int(i): n for n, i in re.findall(r"define TRAINER_BACKPIC_(\w+)\s+(\d+)", txt)}


def process(narc_rel: str, view: str, hgss: Path, names: dict[int, str], commit: str):
    bnames = backpic_names(hgss)
    members, _ = read_narc(hgss / narc_rel)
    if len(members) % 5:
        raise SystemExit(f"{narc_rel}: member count {len(members)} not a multiple of 5")
    cat, cur = [], []
    for c in range(len(members) // 5):
        m = dict(zip(MEMBERS, members[c * 5:c * 5 + 5]))
        idx = f"{c:03d}"
        aid = f"hgss:narc:{narc_rel.replace('/', ':')}:{view}_{idx}"
        spath = f"{narc_rel}#class={idx}"
        cname = names.get(c) if view == "front" else None
        meta = {
            "source_commit": commit,
            "narc": narc_rel,
            "narc_member_ids": {k: c * 5 + i for i, k in enumerate(MEMBERS)},
            "narc_member_sha256": {k: hashlib.sha256(v).hexdigest()[:16] for k, v in m.items()},
            "view": view,
            "trainer_class_index": c if view == "front" else None,
            "trainer_class_constant": ("TRAINERCLASS_" + cname) if cname else None,
            "backpic_index": c if view == "back" else None,
            "backpic_constant": ("TRAINER_BACKPIC_" + bnames[c]) if view == "back" and c in bnames else None,
            "loader_ref": "src/pokemon.c:sub_02070D3C",
        }
        issues = []
        render_rel = None
        w = h = opaque = bw = bh = cells_n = 0
        try:
            tiles = lib.parse_ncgr_tiles(m["ncgr"])
            pal = lib.parse_nclr(m["nclr"])
            cells = lib.parse_ncer(m["ncer"])
            cells_n = len(cells)
            shift = lib.ncgr_unit_shift(m["ncgr"])
            transfers = lib.parse_ncer_transfers(m["ncer"], len(cells))
            w, h, px, oob, dims = lib.render_sheet(cells, tiles, shift=shift, transfers=transfers)
            used = sorted(set(px) - {0})
            opaque = sum(1 for p in px if p)
            if oob:
                issues.append(f"{oob} OAM tile refs beyond NCGR")
            if not opaque:
                issues.append("blank render")
            if used and max(used) >= len(pal):
                issues.append("palette index beyond NCLR")
            if opaque:
                xs = [i % w for i, p in enumerate(px) if p]
                ys = [i // w for i, p in enumerate(px) if p]
                bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
            img = Image.new("P", (w, h))
            img.putdata(px)
            flat = [v for rgb in pal[:256] for v in rgb] + [0] * (768 - 3 * len(pal[:256]))
            img.putpalette(flat)
            render_rel = f"docs/visual_overhaul/catalog_extensions/hgss_trainer_sprites/renders/{view}_{idx}.png"
            (ROOT / render_rel).parent.mkdir(parents=True, exist_ok=True)
            img.save(ROOT / render_rel, optimize=True)
            meta.update({"char_unit_bytes": 32 << shift, "vram_transfer": [list(t) for t in transfers] if transfers else None, "palette_colors": len(pal), "palette_rows_used": sorted({p >> 4 for p in used}),
                         "cell_count": cells_n, "cell_dims": [list(d) for d in dims],
                         "render_sha256": hashlib.sha256(bytes(px)).hexdigest()[:16]})
        except Exception as e:  # fail closed: reject with evidence, never silently drop
            issues.append(f"decode error: {e}")
        ok = not issues
        cat.append({
            "asset_id": aid, "source_id": "hgss", "asset_type": "nitro_sprite_set",
            "species_dex": None, "form": None, "variant": (cname or bnames.get(c) if view == "back" else cname).lower() if (cname or (view == "back" and c in bnames)) else None,
            "group": "trainer_graphics", "frame": cells_n or None, "source_path": spath, "render_path": render_rel,
            "native_width": w or None, "native_height": h or None, "bbox_width": bw or None, "bbox_height": bh or None,
            "opaque_pixels": opaque or None, "geometry_class": ("single_cell" if cells_n == 1 else f"multi_cell_{cells_n}") if cells_n else None,
            "review_status": "unreviewed",
            "target_tags": ["trainer", "trainer_battle_sprite", "battle_front" if view == "front" else "battle_back"],
            "quality_notes": "HGSS trainer battle sprite set (NCGR+NCLR+NCER+NANR+NCBR) from a raw NARC member group; targeted catalog extension.",
            "source_metadata": meta,
        })
        cur.append({
            "asset_id": aid, "source_id": "hgss", "asset_type": "nitro_sprite_set", "group": "trainer_graphics",
            "source_path": spath, "render_path": render_rel, "species_dex": None,
            "target_tags": ["trainer", "trainer_battle_sprite", "battle_front" if view == "front" else "battle_back"],
            "lane": "X_hgss_trainer_sprites",
            "review_status": "usable" if ok else "reject",
            "reason_code": "hgss_trainer_sprite_set_valid_render" if ok else "hgss_trainer_sprite_set_invalid",
            "reason": ("All five NARC members parse; stacked NCER cells render nonblank with palette indices covered by the NCLR."
                       if ok else "; ".join(issues)),
            "decision_source": "HGSS_TRAINER_SPRITES_INVENTORY",
            "recovery_evidence": {"cell_count": cells_n, "render_size": [w, h], "opaque_pixels": opaque, "issues": issues},
        })
    return cat, cur


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", required=True, type=Path)
    a = ap.parse_args()
    hgss = a.hgss_root.resolve()
    commit = subprocess.check_output(["git", "-C", str(hgss), "rev-parse", "HEAD"], text=True).strip()
    names = class_names(hgss)
    cat, cur = [], []
    for rel, view in ((lib.NARC_FRONT, "front"), (lib.NARC_BACK, "back")):
        c1, c2 = process(rel, view, hgss, names, commit)
        cat += c1
        cur += c2
    cat.sort(key=lambda r: r["asset_id"])
    cur.sort(key=lambda r: r["asset_id"])
    catalog = {
        "schema_version": 1,
        "extension_id": "hgss_trainer_sprites",
        "sources": [{"source_id": "hgss", "source_game": "Pokemon HeartGold/SoulSilver", "source_repo": "79cbd8hmgj-wq/pokeheartgold",
                     "source_commit": commit, "notes": "Targeted extension: trainer battle sprite NARCs files/a/0/5/8 (front) and files/a/0/0/6 (back)."}],
        "assets": cat,
    }
    counts = {}
    for r in cur:
        counts[r["review_status"]] = counts.get(r["review_status"], 0) + 1
    curation = {"schema_version": 1, "lane": "X_hgss_trainer_sprites", "scope": "hgss trainer battle sprite catalog extension",
                "asset_count": len(cur), "status_counts": counts, "records": cur}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "CATALOG.json").write_text(json.dumps(catalog, indent=1, sort_keys=True) + "\n")
    (OUT / "CURATION.json").write_text(json.dumps(curation, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"assets": len(cat), "status": counts, "commit": commit}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
