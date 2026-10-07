"""Deterministic mapping: curated record -> (subsystem, target, donor-group unit).

Every record maps to exactly one subsystem. A *target* is the Platinum-side thing a donor
competes for (a species, a trainer class, a resource family). A *unit* is the donor-side
bundle that is selected as one (a species' sprite set, a resource family, a package).
"""
from __future__ import annotations

import os
import re

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


def _dp_trainer(rec):
    p = rec["source_path"]
    pool = "trfgra" if "/trfgra/" in p else "trbgra"
    n = int(re.search(r"narc_(\d+)", p).group(1))
    t = f"{pool}_{n // 2:03d}"
    return "trainer_battle_sprites", t, t, "trainer_class"


def _family(subsystem: str, unit: str, kind: str = "family"):
    return subsystem, "family:" + subsystem, unit, kind


def _hgss(rec):
    p = rec["source_path"]
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
