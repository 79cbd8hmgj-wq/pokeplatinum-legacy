"""Contact-sheet galleries of REAL decoded frames (full set stays local; a small evidence excerpt may be committed)."""
from __future__ import annotations

import json
from pathlib import Path

from .common import sha256_file
from .render import Frame, contact_sheet, save_png

# gallery name -> (library, unit-type filter, source-path substring filter or None, cell size, scale)
GALLERIES = [
    ("pmd_sky_effects", "pmd_sky", ("pmd_effect_wan",), None, 96, 1),
    ("hgss_spl_move_particles", "hgss", ("spl_particle_archive",), "files/a/0/2/9", 64, 1),
    ("hgss_spl_ball_particles", "hgss", ("spl_particle_archive",), "files/a/0/9/5", 64, 1),
    ("hgss_cell_banks", "hgss", ("nitro_cell_bank",), None, 80, 1),
    ("ranger2_effect_cells", "ranger2", ("nitro_cell_bank",), None, 80, 1),
    ("ranger2_textures", "ranger2", ("ds_ntft_texture",), None, 128, 1),
    ("diamond_wazaeffect_cells", "diamond", ("nitro_cell_bank",), "wazaeffect", 80, 1),
    ("diamond_spl_move_particles", "diamond", ("spl_particle_archive",), "waza_particle", 64, 1),
    ("crystal_battle_objects", "crystal", ("gb_recipe_object",), None, 48, 3),
]
PAGE = 120


def _label(uid: str) -> str:
    tail = uid.rsplit("#", 1)[-1] if "#" in uid else uid.rsplit("/", 1)[-1].split(".")[0]
    return tail[-6:]


def build_galleries(doc: dict, sheets: dict, out_dir: Path, evidence_dir: Path | None = None,
                    evidence_cells: int = 60) -> list[dict]:
    index = []
    units = {u["id"]: u for u in doc["units"]}
    for name, lib, types, path_filter, cell, scale in GALLERIES:
        per = sheets.get(lib, {})
        ids = [uid for uid in sorted(per) if units.get(uid, {}).get("type") in types and units[uid]["status"] == "DECODED"
               and (path_filter is None or path_filter in units[uid]["source"] or path_filter in uid)]
        if not ids:
            continue
        pages = [ids[i:i + PAGE] for i in range(0, len(ids), PAGE)]
        for pi, page in enumerate(pages, 1):
            frames: list[Frame] = [per[uid][0] for uid in page]
            img = contact_sheet(frames, [_label(u) for u in page], cell=cell, columns=12, scale=scale)
            fname = f"{name}_p{pi:02d}.png"
            save_png(img, out_dir / fname)
            index.append({"file": fname, "gallery": name, "library": lib, "page": pi, "pages": len(pages),
                          "cells": len(page), "first_unit": page[0], "last_unit": page[-1],
                          "sha256": sha256_file(out_dir / fname), "bytes": (out_dir / fname).stat().st_size,
                          "committed_excerpt": False})
        if evidence_dir is not None:
            ex = ids[:evidence_cells]
            img = contact_sheet([per[u][0] for u in ex], [_label(u) for u in ex], cell=cell, columns=10, scale=scale)
            save_png(img, evidence_dir / f"{name}_excerpt.png")
            index.append({"file": f"{name}_excerpt.png", "gallery": name, "library": lib, "page": 0, "pages": len(pages),
                          "cells": len(ex), "first_unit": ex[0], "last_unit": ex[-1],
                          "sha256": sha256_file(evidence_dir / f"{name}_excerpt.png"),
                          "bytes": (evidence_dir / f"{name}_excerpt.png").stat().st_size, "committed_excerpt": True})
    return index
