"""Mining rules for the hgss_field_3d extension (field/building models, map texture sets, follower sheets).

Pure functions of the measured source_metadata already committed in the extension catalog (donor-free). `aggregate` builds the per-group
feature block `f["x3d"]`; `proposals` emits opportunity proposals in the same shape as mine_rules.P(). Whole-asset replacement is never
proposed here: replacement_candidate is created only from a ledger-preferred group (rules.py), which these subsystems cannot reach
(structural conversion / contract mismatch)."""
from __future__ import annotations

import collections

SUBSYSTEM_DOMAIN = {"field_building_models": "models", "field_texture_sets": "textures", "overworld_pokemon_sheets": "overworld_pokemon"}
LEGENDARY = {144, 145, 146, 150, 151, 243, 244, 245, 249, 250, 251, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493}

COMPONENT_OF_CAT = {
    "roof": ["architectural_detail", "roof"], "wall": ["wall_material"], "window": ["window"], "door": ["door"], "gate": ["door", "architectural_detail"], "signage": ["signage"],
    "light": ["lighting_prop"], "machine": ["machinery"], "furniture": ["furniture"], "foliage": ["foliage"], "water": ["water_surface"], "stairs": ["stairs"], "fence": ["fence"],
    "gym": ["architectural_detail"], "floor": ["floor_material"], "rock_cliff": ["terrain_material"], "tower": ["architectural_detail"], "bridge": ["architectural_detail"],
    "snow_ice": ["snow_ice"], "road_path": ["terrain_material"], "sky_cloud": ["overlay_decal"], "shadow": [],
}
TEX_THEME = {"foliage": "foliage_ground", "water": "water", "rock_cliff": "rock_cliff", "snow_ice": "snow_ice", "road_path": "road_path", "floor": "floor_interior", "wall": "wall_architecture",
             "roof": "wall_architecture", "window": "wall_architecture", "door": "wall_architecture", "gate": "wall_architecture", "gym": "wall_architecture", "stairs": "wall_architecture",
             "fence": "wall_architecture", "furniture": "floor_interior", "machine": "floor_interior", "signage": "overlay_signage", "light": "overlay_signage", "sky_cloud": "overlay_signage",
             "shadow": "overlay_signage", "bridge": "wall_architecture", "tower": "wall_architecture"}


def comps_of(cats: dict) -> list[str]:
    out: list[str] = []
    for c in cats:
        for t in COMPONENT_OF_CAT.get(c, []):
            if t not in out:
                out.append(t)
    return out


def model_theme(m: dict, room: bool) -> str:
    cats = {k: v for k, v in m["categories"].items() if k != "shadow"}
    geo = m["geometry_class"]
    main = next(iter(cats), None)
    if geo == "empty":
        return "empty"
    if geo == "flat_surface":
        return "ground_surface"
    if geo == "panel":
        return "door_window_panel" if main in ("door", "window", "gate", None) else "sign_panel"
    if main == "water":
        return "water_feature"
    if main == "foliage":
        return "foliage_prop"
    if main == "signage":
        return "sign_info_board"
    if main == "light":
        return "lighting_prop"
    if main == "machine":
        return "machinery_terminal"
    if main == "furniture":
        return "furniture_interior"
    if main in ("stairs", "bridge"):
        return "stairs_bridge"
    if main == "gym":
        return "gym_structure"
    if geo in ("medium_structure", "large_structure"):
        return "interior_room_shell" if room else "building_exterior"
    return "small_prop_misc" if geo == "small_prop" else "structure_misc"


def tex_set_theme(set_cats: dict, uses: collections.Counter, n: int) -> str:
    cats = {k: v for k, v in set_cats.items()}
    if not cats:
        return "mixed"
    score = collections.Counter()
    for c, v in cats.items():
        score[TEX_THEME.get(c, "mixed")] += v
    theme, top = score.most_common(1)[0]
    return theme if top >= 0.3 * max(1, sum(score.values())) else "mixed"


def aggregate(subsystem: str, unit: str, metas: list[dict], assets: list[dict]) -> dict:
    if subsystem == "field_building_models":
        m = metas[0]
        room = "bm_room" in unit
        theme = model_theme(m, room)
        return {"kind": "model", "meta": m, "room": room, "family": f"hgss_{'bm_room' if room else 'bm_field'}_{theme}", "theme": theme}
    if subsystem == "field_texture_sets":
        uses = collections.Counter(m["texture_use"] for m in metas)
        cats = collections.Counter()
        for m in metas:
            for c in m["categories"]:
                cats[c] += 1
        theme = tex_set_theme(dict(cats), uses, len(metas))
        sizes = collections.Counter(f"{m['w']}x{m['h']}" for m in metas)
        novel_cats = collections.Counter()
        for m in metas:
            if m["texture_use"] in ("directly_reusable", "convertible", "component_region", "enhancement_input"):
                for c in m["categories"]:
                    novel_cats[c] += 1
        return {"kind": "texture_set", "n": len(metas), "uses": dict(sorted(uses.items())), "categories": dict(cats.most_common()), "novel_categories": dict(novel_cats.most_common()), "theme": theme,
                "family": f"hgss_texset_{theme}", "formats": dict(sorted(collections.Counter(m["texture_format"] for m in metas).items())), "sizes": dict(sizes.most_common(4)),
                "platinum_near": sum(bool(m["platinum_near_match"]) for m in metas), "bytes": sum(a.get("opaque_pixels") or 0 for a in assets)}
    m = metas[0]
    if m["slot_placeholder"]:
        fam = "hgss_follower_slot"
    elif m["species_dex"] in LEGENDARY:
        fam = "hgss_follower_legendary"
    elif m["frame_dims"] and m["frame_dims"][0][0] > 32:
        fam = "hgss_follower_large"
    elif m["form"]:
        fam = "hgss_follower_form"
    else:
        fam = "hgss_follower_species"
    return {"kind": "follower", "meta": m, "family": fam, "theme": fam}


def proposals(mkP, g: dict, f: dict) -> list[dict]:
    x = f["x3d"]
    out: list[dict] = []
    rel = f["native_relation"]
    if x["kind"] == "model":
        m = x["meta"]
        geo, tris, cats = m["geometry_class"], m["tris"], {k: v for k, v in m["categories"].items() if k != "shadow"}
        ntex = max(1, m["texture_count"])
        novel_frac = (m["tex_novel"] + 0.5 * m["tex_near_platinum"]) / ntex if m["texture_count"] else 0.0
        comps = comps_of(cats)
        has_pt = rel == "art_diff_geometry_review"
        cp = m.get("platinum_counterpart") or {}
        if geo == "empty" or tris == 0:
            return [mkP("reference_only", [], "model has no renderable geometry", 1, 1, 1, 1, 1, 1)]
        if m.get("duplicate_of"):  # same mesh (tris, per-shape tris, extents) as an earlier model: a texture/palette variant, counted once under its first model
            return [mkP("reference_only", [], f"geometry variant of {m['duplicate_of']} ({m['geometry_variants']} models share this mesh)", 1, 1, 1, 1, 1, 1)]
        impact = {"large_structure": 4, "medium_structure": 3, "small_prop": 3, "panel": 2, "flat_surface": 2}.get(geo, 2)
        if tris >= 300:
            impact = min(5, impact + 1)
        if tris >= 24 and (novel_frac > 0 or has_pt or comps):
            c = ["geometry_motif"] + comps + (["texture_region"] if m["tex_novel"] else [])
            out.append(mkP("component_donor", c[:6], f"HGSS {x['theme'].replace('_', ' ')} model ({geo}, {tris} tris, {m['texture_count']} textures, {m['tex_novel']} without Platinum match): geometry/material parts for kit-bashed Sinnoh props and buildings",
                           impact, 4 if novel_frac >= 0.8 else 3 if novel_frac >= 0.5 else 2, 3, 4 if geo == "large_structure" else 3, 3, 2, pixel="recolored_donor",
                           adapt=["extract roof/wall/window/door/prop parts rather than whole buildings", "rebuild placement/matshp and texture set per Platinum area", "regrade textures with the G4 pipeline"]))
        if rel == "missing_in_native" and geo in ("small_prop", "panel", "medium_structure") and novel_frac >= 0.5 and comps:
            out.append(mkP("novel_detail", comps[:4] + ["geometry_motif"], f"prop/structure type with no Platinum counterpart ({', '.join(list(cats)[:3])}): a new field detail rather than a replacement",
                           4 if (geo == "medium_structure" and tris >= 150) else 3, 4, 2, 3, 3, 3, mode="whole_asset", pixel="recolored_donor",
                           adapt=["author a Sinnoh-styled variant or regrade textures", "add through the prop model set + area data path"]))
        if has_pt and tris >= 1.15 * (cp.get("tris") or 0) and (cp.get("tris") or 0) > 0:
            out.append(mkP("enhancement_candidate", ["geometry_motif", "shading"] + comps[:2], f"Platinum counterpart {cp.get('file', '').rsplit('/', 1)[-1]} shares {int(100 * (cp.get('overlap_exact') or 0))}% of its textures; HGSS has {tris} tris vs {cp.get('tris')}: richer geometry as a composite input",
                           3, 2, 3, 3, 3, 3, pixel="derived", adapt=["lift the extra geometry detail onto the Platinum prop", "keep Platinum textures/identity"]))
        if geo == "flat_surface" and ({"water", "foliage", "snow_ice"} & set(cats)):
            out.append(mkP("technique_donor", [], f"flat ground-overlay surface ({', '.join(list(cats)[:2])}): decal/overlay surface technique for water edges, snow or foliage patches",
                           2, 3, 3, 2, 2, 3, techs=["ground_overlay_surface", "environmental_overlay"], pixel="none", adapt=["express as Platinum prop/decal geometry; no donor pixels"]))
        if not out:
            out.append(mkP("reference_only", [], "no actionable component/novelty signal beyond reference", 1, 1, 1, 1, 1, 1))
        return out
    if x["kind"] == "texture_set":
        u = x["uses"]
        reuse_n = u.get("directly_reusable", 0) + u.get("convertible", 0)
        region_n = u.get("component_region", 0)
        enh_n = u.get("enhancement_input", 0)
        cats = x["novel_categories"] or x["categories"]
        comps = ["texture_region", "material_treatment"] + comps_of(cats)[:3]
        if reuse_n + region_n >= 4:
            big = reuse_n + region_n >= 30
            out.append(mkP("component_donor", comps, f"{reuse_n} directly reusable/convertible textures and {region_n} component regions ({x['theme'].replace('_', ' ')} set; {x['n']} textures): material/texture-region library for the G4 environment pipeline",
                           4 if big else 3, 3 if (reuse_n + region_n) >= 0.5 * x["n"] else 2, 3, 2, 3, 4, pixel="recolored_donor",
                           adapt=["select regions by hash against Platinum sets", "regrade palettes to the Sinnoh area look", "rebuild the area texture set"]))
        if enh_n >= 2:
            out.append(mkP("enhancement_candidate", ["texture_region", "shading", "palette"], f"{enh_n} textures are near variants of Platinum textures: shading/detail inputs for existing materials",
                           3, 2, 3, 2, 2, 3, pixel="derived", adapt=["blend detail into the Platinum texture, keep its identity"]))
        sig = sum(v for c, v in x["novel_categories"].items() if c in ("signage", "light", "sky_cloud", "gym", "machine"))
        if sig >= 4:
            out.append(mkP("novel_detail", ["signage", "overlay_decal", "texture_region"], f"{sig} novel signage/overlay/decorative textures: decorative motifs and environmental overlays Platinum's sets lack",
                           3, 4, 3, 2, 2, 3, mode="component", pixel="recolored_donor", adapt=["recolor and place as prop or overlay decals"]))
        if x["theme"] in ("water", "snow_ice") and x["n"] >= 6:
            out.append(mkP("technique_donor", [], f"{x['theme'].replace('_', ' ')} texture set ({x['n']} textures): material treatment/palette ramp technique", 3, 3, 3, 2, 2, 3,
                           techs=["material_treatment", "palette_variants"], pixel="none", adapt=["re-express ramps through Platinum NSBTA/palette animation; no donor pixels"]))
        if not out:
            out.append(mkP("reference_only", [], "set offers fewer than four reusable regions or is identical to Platinum", 1, 1, 1, 1, 1, 1))
        return out
    # follower sheets
    m = x["meta"]
    fam = x["family"]
    if m["slot_placeholder"]:
        return [mkP("reference_only", [], "party-slot runtime placeholder sheet (texture swapped at run time); no species art", 1, 1, 1, 1, 1, 1)]
    leg = fam == "hgss_follower_legendary"
    peq = bool(m["platinum_equivalents"])
    if not peq:
        out.append(mkP("novel_detail", ["pose", "animation_frame"], ("legendary/mythical " if leg else "") + f"overworld Pokemon sheet (8 frames, normal+shiny) with no Platinum equivalent: event/cutscene/special-encounter Pokemon without any follower system",
                       4 if leg else 3, 5, 2, 3, 2, 4 if leg else 3, mode="whole_asset", pixel="donor_pixels", dims={"reuse": 4, "library": 3},
                       adapt=["register as a field sprite on the existing NSBTX path", "pilot in one scripted event", "match Platinum field-sprite shading"]))
    else:
        out.append(mkP("enhancement_candidate", ["pose", "animation_frame", "shading"], f"Platinum already has {len(m['platinum_equivalents'])} sheet(s) for this species ({m['platinum_frame_counts']} frames vs HGSS {m['frames']}): alternate poses/movement frames as composite inputs, not a drop-in",
                       2, 2, 2, 3, 3, 2, pixel="derived", adapt=["use HGSS frames only as reference/composite input for Platinum frames", "frame-count contract differs (not a replacement)"]))
        out.append(mkP("component_donor", ["pose", "animation_frame"], "alternate pose/direction frames for the same species", 2, 2, 2, 3, 3, 2, pixel="recolored_donor"))
    return out
