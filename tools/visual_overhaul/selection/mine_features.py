"""Mining pass 1: deterministic per-group feature extraction from the EXISTING curated catalog, curation ledgers,
selection ledgers and evidence. No donor repo is opened and no asset is decoded here."""
from __future__ import annotations

import collections
import re

from common import *  # noqa: F401,F403
import build_candidate_groups as BCG
import outcomes
import mine_x3d as X3

R_PMD_FRAMES = re.compile(r"(\d+)/(\d+) nonblank frames, (\d+) animation groups")
R_CELLS = re.compile(r"(\d+)/(\d+) nonblank cells")
R_MAP = re.compile(r"composed (\d+)x(\d+) map from (\d+) quad layer\(s\), (\d+) quads")
R_TEX = re.compile(r"(\d+) texture chips decode nonblank")
R_BG = re.compile(r"(\d+)x(\d+) (?:composed )?background")
TOD = re.compile(r"(?<![a-z])(morning|day|evening|night|dawn|dusk)(?![a-z])")


def family_of(g: dict) -> str:
    u = g["unit"]
    src = g["source_id"]
    m = re.match(r"p\d+_\d+_([a-z]+)\d*$", u)
    if g["subsystem"] == "pokemon_animation_reference" and m:
        return f"ranger_poke_{m.group(1)}"
    if g["subsystem"] == "pokemon_battle_sprites":
        return f"{src}_battle_sprites" if u.startswith("sp_") else f"{src}_battle_forms"
    if g["subsystem"] == "pokemon_icons":
        return f"{src}_icons"
    if src == "hgss" and u.startswith("hgss_preview"):
        return "hgss_preview"
    for pre in ("hgss_front", "hgss_back", "hgss_mmodel", "dp_trfgra", "dp_trbgra", "dp_otherpoke"):
        if u.startswith(pre):
            return pre
    if src == "pmd_sky":
        if m := re.match(r"(pmd_[a-z]+_[a-z]+?)(?=\d)", u):
            return m.group(1)
    base = u.split("/")[0] if "/" in u and src == "ranger2" else u
    if "/" in u and src == "ranger2":
        base = u.split("/")[0] + "/" + re.sub(r"[\d_.]+.*$", "", u.split("/", 1)[1])
    base = re.sub(r"\d+", "", base)
    return re.sub(r"[_.]+$", "", base)[:40] or "misc"


def domain_of(g: dict, f: dict) -> str:
    s, src, u = g["subsystem"], g["source_id"], g["unit"]
    if s == "trainer_battle_sprites":
        return "trainer_sprites"
    if s == "pokemon_battle_sprites":
        return "pokemon_sprites"
    if s == "pokemon_animation_reference" or s == "no_platinum_target":
        return "pokemon_animation"
    if s == "pokemon_icons":
        return "icons"
    if s == "field_npc_player_sprites":
        return "npc_player_sprites"
    if s == "field_environment_art":
        if src == "hgss":
            return "location_area"
        if src == "pmd_sky":
            return "environmental_effects" if f["has_animated_tiles"] else "backgrounds"
        return "textures" if f["tex_chips"] and not f["map_w"] else ("environmental_effects" if re.search(r"/ef\d", u) else "field_graphics")
    if s == "field_effects_overlays":
        return "field_effects"
    if s == "battle_effects_particles":
        return "battle_effects"
    if s == "battle_backgrounds_hud":
        return "backgrounds" if "capbg" in u else "ui_menus_hud"
    if s in ("menu_ui_frames", "party_summary_ui", "pokedex_ui"):
        return "interface_embellishments" if u.startswith("ranger_interface") else "ui_menus_hud"
    if s == "title_and_presentation":
        return "transitions_presentation"
    return "misc"


def build() -> dict:
    doc = BCG.build(want_membership=True)
    mem = doc.pop("_membership")
    cat = outcomes.catalog_index()
    rec = load_recovered_records()
    led = {p.stem: jload(p) for p in sorted((SEL / "ledgers").glob("*.json"))}
    dec = {d["group_id"]: d for l in led.values() for d in l["decisions"]}
    tgt = {(s, t["target_id"]): t for s, l in led.items() for t in l["targets"]}
    members: dict[str, list[str]] = collections.defaultdict(list)
    for aid, gid in mem.items():
        members[gid].append(aid)
    fam_size: collections.Counter = collections.Counter()
    feats: dict[str, dict] = {}
    for g in doc["groups"]:
        gid = g["group_id"]
        ids = sorted(members[gid])
        kinds: collections.Counter = collections.Counter()
        f = {"frames_ok": 0, "frames_total": 0, "anim_groups": 0, "cells_ok": 0, "cells_total": 0, "map_w": 0, "map_h": 0, "quad_layers": 0, "tex_chips": 0,
             "bg_w": 0, "bg_h": 0, "bytes": 0, "cell_count": 0, "opaque": 0, "has_animated_tiles": False, "companion_only": True, "tod": False,
             "geom": collections.Counter(), "max_w": 0, "max_h": 0}
        for aid in ids:
            a, r = cat[aid], rec[aid]
            sm = a.get("source_metadata") or {}
            kinds[sm.get("member_kind") or sm.get("suffix") or a["asset_type"]] += 1
            f["bytes"] += sm.get("member_size") or sm.get("size_bytes") or 0
            re_ = r.get("recovery_evidence") or {}
            d = re_.get("detail") if isinstance(re_.get("detail"), str) else ""
            if "companion" not in r["reason_code"] and "tiles_in_sibling" not in r["reason_code"]:
                f["companion_only"] = False
            if m := R_PMD_FRAMES.search(d):
                f["frames_ok"] += int(m[1]); f["frames_total"] += int(m[2]); f["anim_groups"] = max(f["anim_groups"], int(m[3]))
            if m := R_CELLS.search(d):
                f["cells_ok"] += int(m[1]); f["cells_total"] += int(m[2])
            if m := R_MAP.search(d):
                f["map_w"], f["map_h"], f["quad_layers"] = max(f["map_w"], int(m[1])), max(f["map_h"], int(m[2])), max(f["quad_layers"], int(m[3]))
            if m := R_TEX.search(d):
                f["tex_chips"] += int(m[1])
            if m := R_BG.search(d):
                f["bg_w"], f["bg_h"] = int(m[1]), int(m[2])
            if "animated-tile (BPA)" in d:
                f["has_animated_tiles"] = True
            f["cell_count"] = max(f["cell_count"], re_.get("cell_count") or a.get("source_metadata", {}).get("cell_count") or 0)
            f["opaque"] += re_.get("opaque_pixels") or a.get("opaque_pixels") or 0
            if a.get("geometry_class"):
                f["geom"][a["geometry_class"]] += 1
            f["max_w"], f["max_h"] = max(f["max_w"], a.get("native_width") or a.get("bbox_width") or 0), max(f["max_h"], a.get("native_height") or a.get("bbox_height") or 0)
            if re_.get("frames"):
                f["frames_ok"] = max(f["frames_ok"], re_["frames"] if isinstance(re_["frames"], int) else 0)
        if g["subsystem"] in X3.SUBSYSTEM_DOMAIN:  # hgss_field_3d: measured metadata lives in the extension catalog (no donor access)
            f["x3d"] = X3.aggregate(g["subsystem"], g["unit"], [cat[i].get("source_metadata") or {} for i in ids], [cat[i] for i in ids])
        f["kinds"] = dict(sorted(kinds.items()))
        f["geom"] = dict(f["geom"])
        f["has_nanr"] = any(k in kinds for k in ("nanr", ".nanr")) or any("cac" in k or k == "4c020000" for k in kinds)
        f["has_tilemap"] = any(k in kinds for k in ("nscr", ".nscr", ".bma", ".bpc"))
        f["n_palettes"] = sum(v for k, v in kinds.items() if k in ("nclr", ".nclr", ".bpl", ".pal"))
        f["tod"] = bool(TOD.search(" ".join(g["sample_paths"]).lower()))
        d = dec[gid]
        ev = d["visual_evidence"]
        t = tgt.get((g["subsystem"], g["target_id"]))
        f["ledger_role"], f["ledger_reason"] = d["role"], d["reason_code"]
        f["native_relation"] = ev.get("native_relation")
        f["needs_evidence"] = bool(d["needs_evidence"]) and f["native_relation"] != "contract_mismatch"  # contract_mismatch is a measured disqualifier, not missing evidence
        f["needs_runtime_validation"] = bool(d["needs_runtime_validation"])
        f["has_native_target"] = f["native_relation"] not in ("missing_in_native",) and d["reason_code"] not in ("no_native_target", "source_not_relevant_to_subsystem") and g["subsystem"] != "no_platinum_target"
        f["target_resolution"] = t["resolution"] if t else None
        f["scores"] = d["scores"]
        f["decode_issues"] = g["unresolved_decode_issue_members"]
        f["family"] = family_of(g)
        f["domain"] = domain_of(g, f)
        if "x3d" in f:
            f["family"], f["domain"] = f["x3d"]["family"], X3.SUBSYSTEM_DOMAIN[g["subsystem"]]
        fam_size[(g["source_id"], f["domain"], f["family"])] += 1
        f["n_members"] = len(ids)
        f["member_ids"] = ids
        feats[gid] = f
    by_fam: dict[tuple, list] = collections.defaultdict(list)
    for g in doc["groups"]:
        f = feats[g["group_id"]]
        f["family_size"] = fam_size[(g["source_id"], f["domain"], f["family"])]
        dom = f["domain"]
        f["metric"] = float({"battle_effects": f["cells_total"], "interface_embellishments": f["cells_total"], "field_effects": f["frames_total"] + 4 * f["anim_groups"],
                             "field_graphics": f["map_w"] * f["map_h"] * max(f["quad_layers"], 1), "textures": f["tex_chips"] * 1000 + f["bytes"], "backgrounds": f["bytes"] + f["bg_w"] * f["bg_h"],
                             "models": (f["x3d"]["meta"]["tris"] if f.get("x3d", {}).get("kind") == "model" else 0), "textures": (sum(v for k, v in f["x3d"]["uses"].items() if k in ("directly_reusable", "convertible", "component_region", "enhancement_input")) if f.get("x3d", {}).get("kind") == "texture_set" else 0),
                             "overworld_pokemon": f["opaque"], "trainer_sprites": f["opaque"] + 1000 * (f["scores"]["visual_gain"] or 0), "npc_player_sprites": f["opaque"], "pokemon_sprites": 1000 * (f["scores"]["visual_gain"] or 0) + f["n_members"], "transitions_presentation": f["bytes"]}.get(dom, f["n_members"]))
        by_fam[(g["source_id"], dom, f["family"])].append(g["group_id"])
    for key, gids in by_fam.items():  # percentile of the richness metric inside the family (deterministic, ties share the lower rank)
        vals = sorted(feats[x]["metric"] for x in gids)
        for x in gids:
            m = feats[x]["metric"]
            feats[x]["rich_pct"] = round((sum(v < m for v in vals) + 0.5 * sum(v == m for v in vals)) / len(vals), 3)  # mid-rank percentile
    return {"groups": doc["groups"], "features": feats, "ledgers": led, "decisions": dec}
