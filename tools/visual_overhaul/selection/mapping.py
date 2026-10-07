"""Deterministic mapping: curated record -> (subsystem, target, donor-group unit).

Every record maps to exactly one subsystem. A *target* is the Platinum-side thing a donor
competes for (a species, a trainer class, a resource family). A *unit* is the donor-side
bundle that is selected as one (a species' sprite set, a resource family, a package).
"""
from __future__ import annotations

import json
import os
import re

from common import SEL

ICON_MEMBER_BIAS = 7  # icon member = National Dex species index + 7 (G3 audit, HGSS+DP)
MAX_SPECIES = 493


def _stem(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def _species_target(n: int) -> str:
    return f"sp_{n:04d}"


def _icon(rec):
    m = re.search(r"(?:narc_|poke_icon_)(\d+)", rec["source_path"])
    member = int(m.group(1))
    si = member - ICON_MEMBER_BIAS
    if 0 <= si <= MAX_SPECIES:
        t = _species_target(si)
        kind = "species"
    else:
        t = f"icon_extra_{member:04d}"
        kind = "form_or_special"
    return "pokemon_icons", t, t, kind


def _dp_pokegra(rec):
    n = int(re.search(r"narc_(\d+)", rec["source_path"]).group(1))
    t = _species_target(n // 6)
    return "pokemon_battle_sprites", t, t, "species"


def _hgss_pokegra(rec):
    n = int(rec["source_path"].split("/pokegra/pokegra/")[1].split("/")[0])
    t = _species_target(n)
    return "pokemon_battle_sprites", t, t, "species"


def _hgss_other(rec):
    rel = rec["source_path"].split("/otherpoke/")[1].split("/")
    t = "form_" + "_".join(rel[:-1]) if len(rel) > 1 else "form_" + _stem(rec["source_path"])
    return "pokemon_battle_sprites", t, t, "special_form"


def _dp_other(rec):
    n = int(re.search(r"narc_(\d+)", rec["source_path"]).group(1))
    t = f"dp_otherpoke_{n:04d}"
    return "pokemon_battle_sprites", t, t, "special_form"


_ALIGN = None


def _align() -> dict:
    """Trainer class alignment (selection/alignment/trainer_classes.json), built by build_trainer_alignment.py."""
    global _ALIGN
    if _ALIGN is None:
        _ALIGN = json.loads((SEL / "alignment" / "trainer_classes.json").read_text())
    return _ALIGN


def _dp_trainer(rec):
    p = rec["source_path"]
    front = "/trfgra/" in p
    n = int(re.search(r"narc_(\d+)", p).group(1)) // 2
    e = _align()["diamond_front" if front else "diamond_back"][f"{n:03d}"]
    return "trainer_battle_sprites", e["target"], f"dp_{'trfgra' if front else 'trbgra'}_{n:03d}", "trainer_class"


def _hgss_trainer(rec):
    p = rec["source_path"]
    front = p.startswith("files/a/0/5/8#")
    idx = re.search(r"#class=(\d+)", p).group(1)
    e = _align()["hgss_front" if front else "hgss_back"][idx]
    return "trainer_battle_sprites", e["target"], f"hgss_{'front' if front else 'back'}_{idx}", "trainer_class"


def _family(subsystem: str, unit: str, kind: str = "family"):
    return subsystem, "family:" + subsystem, unit, kind


_FS_ALIGN = None


def _hgss_field_sprite(rec):
    global _FS_ALIGN
    if _FS_ALIGN is None:
        _FS_ALIGN = json.loads((SEL / "alignment" / "field_sprites.json").read_text())["hgss"]
    p = rec["source_path"]
    e = _FS_ALIGN[p]
    return "field_npc_player_sprites", e["target"], "hgss_" + _stem(p), "sprite_sheet"


FOLLOWER_MMODEL = set(range(201, 207)) | set(range(297, 863))  # MMODEL_FOLLOWER_MON, _2.._6 and MMODEL_FOLLOWER_MON_* (include/constants/mmodel.h)


def _hgss_field_3d(rec):
    """hgss_field_3d extension: building models, map texture sets, follower sheets (one group per model / texture set / sheet)."""
    p = rec["source_path"]
    if p.startswith("files/fielddata/build_model/"):
        m = re.match(r"files/fielddata/build_model/(bm_\w+)\.narc#member=(\d+)$", p)
        return "field_building_models", "family:field_building_models", f"hgss_{m.group(1)}_{m.group(2)}", "model"
    if p.startswith("files/a/0/4/4#"):
        m = re.match(r"files/a/0/4/4#set=(\d+)&tex=\d+$", p)
        return "field_texture_sets", "family:field_texture_sets", f"hgss_texset_{m.group(1)}", "texture_set"
    n = int(re.search(r"mmodel_(\d+)\.NSBTX$", p).group(1))
    return "overworld_pokemon_sheets", "family:overworld_pokemon_sheets", f"hgss_follower_{n:08d}", "sprite_sheet"


def _hgss(rec):
    p = rec["source_path"]
    if p.startswith("files/fielddata/build_model/") and "#member=" in p or p.startswith("files/a/0/4/4#"):
        return _hgss_field_3d(rec)
    if p.startswith("files/data/mmodel/mmodel/"):
        if int(re.search(r"mmodel_(\d+)\.NSBTX$", p).group(1)) in FOLLOWER_MMODEL:
            return _hgss_field_3d(rec)
        return _hgss_field_sprite(rec)
    if p.startswith(("files/a/0/5/8#", "files/a/0/0/6#")):
        return _hgss_trainer(rec)
    if "/poketool/icongra/poke_icon/" in p:
        return _icon(rec)
    if "/poketool/pokegra/pokegra/" in p:
        return _hgss_pokegra(rec)
    if "/poketool/pokegra/otherpoke/" in p:
        return _hgss_other(rec)
    if "/fielddata/graphic/preview_graphic" in p:
        stem = _stem(p).replace("preview_graphic_", "")
        area = re.sub(r"_(morning|day|evening|night)$", "", stem)
        return "field_environment_art", "family:field_environment_art", f"hgss_preview_{area}", "family"
    if "/graphic/zukan_gra" in p:
        return _family("pokedex_ui", "zukan_gra")
    if "/graphic/plist_gra" in p:
        return _family("party_summary_ui", "plist_gra")
    return _family("menu_ui_frames", "hgss_" + p.split("/")[-2])


def _diamond(rec):
    p = rec["source_path"]
    if "/poketool/icongra/poke_icon/" in p:
        return _icon(rec)
    if "/poketool/pokegra/pokegra/" in p:
        return _dp_pokegra(rec)
    if "/poketool/pokegra/otherpoke/" in p:
        return _dp_other(rec)
    if "/poketool/trgra/" in p:
        return _dp_trainer(rec)
    raise KeyError(f"unmapped diamond path {p}")


def _pmd(rec):
    p = rec["source_path"]
    top = p.split("/")[1]
    stem = re.sub(r"\.(bpc|bpl|bma|bpa|wan|wte|wtu|wat|wba|bgp|kao|chr|w16|dat|bin|pal)$", "", os.path.basename(p), flags=re.I)
    if top == "MAP_BG":
        return _family("field_environment_art", f"pmd_mapbg_{stem}")
    if top in ("GROUND", "EFFECT"):
        return _family("field_effects_overlays", f"pmd_{top.lower()}_{stem}")
    if top in ("FONT", "SYSTEM"):
        return _family("menu_ui_frames", f"pmd_{top.lower()}_{stem}")
    if top in ("BACK", "TOP"):
        return _family("title_and_presentation", f"pmd_{top.lower()}_{stem}")
    if top == "DUNGEON":
        return _family("field_environment_art", f"pmd_dungeon_{stem}")
    return _family("no_platinum_target", f"pmd_{top.lower()}_{stem}")


RANGER_PKG = re.compile(r"^p(\d{3})_(\d\d)_")


def _ranger(rec):
    g = rec["group"]
    m = RANGER_PKG.match(g)
    if m:
        return "pokemon_animation_reference", _species_target(int(m.group(1))), g, "species"
    p = rec["source_path"]
    stem = _stem(p)
    unit = f"{g}/{re.sub(r'_LZ$', '', stem)}"
    if g in ("npc", "player"):
        return _family("field_npc_player_sprites", unit)
    if g == "field":
        return _family("field_environment_art", "ranger_" + unit)
    if g in ("effect", "target", "targetOBJ"):
        return _family("battle_effects_particles", "ranger_" + unit)
    if g == "battle":
        return _family("battle_backgrounds_hud", "ranger_" + unit)
    if g in ("menu", "interface", "font", "eventicon", "_root", "system"):
        return _family("menu_ui_frames", "ranger_" + unit)
    if g in ("title", "opening", "ending", "uppict", "event"):
        return _family("title_and_presentation", "ranger_" + unit)
    if g == "pokeOBJ":
        return _family("no_platinum_target", "ranger_" + unit)
    raise KeyError(f"unmapped ranger group {g} ({p})")


def classify(rec: dict) -> dict:
    """Return {subsystem, target_id, unit, unit_kind} for a curated record."""
    src = rec["source_id"]
    fn = {"hgss": _hgss, "diamond": _diamond, "pmd_sky": _pmd, "ranger2": _ranger}[src]
    subsystem, target, unit, kind = fn(rec)
    return {"subsystem": subsystem, "target_id": f"{subsystem}/{target}", "unit": unit, "unit_kind": kind}
