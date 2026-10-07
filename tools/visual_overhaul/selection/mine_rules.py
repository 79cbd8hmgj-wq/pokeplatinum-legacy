"""Mining pass 2: deterministic signals -> opportunity proposals -> scores. Pure functions of the features in mine_features.py.

Nothing here judges a group by whole-asset replacement alone: every group is asked the eight taxonomy questions through
proposal rules (novel capability/detail, technique, component, enhancement, replacement, reference, reject)."""
from __future__ import annotations

import math

PROMOTE = 3.3          # composite >= PROMOTE -> promoted opportunity record
NEEDS_EVIDENCE = 3.0   # composite >= this but evidence too weak -> needs_evidence queue
WEIGHTS = {"visual_impact": 7, "novelty": 6, "feasibility": 5, "reuse": 4, "library": 3, "evidence": 3, "cost": 3, "risk": 2, "dependency": 2, "slice": 2}
INVERTED = ("cost", "risk", "dependency")
DIMS = tuple(WEIGHTS)

USE_MODE = {"replacement_candidate": "whole_asset", "technique_donor": "technique", "component_donor": "component", "enhancement_candidate": "composite_input",
            "reference_only": "reference", "reject": "none"}

# Platinum-native host systems (paths must exist in the repo; validated)
HOST = {
    "battle_effects": ("battle move animation scripts + particle resources", ["res/moves/brave_bird/anim.s", "res/graphics/battle/particles"]),
    "field_effects": ("field overlay/object animation (field task + overworld animation manager)", ["src/field_move_tasks.c", "src/overworld_anim_manager.c"]),
    "environmental_effects": ("environment palette/texture animation and weather/atmosphere layer", ["src/field_overworld_weather.c", "docs/visual_overhaul/G7_6_OVERWORLD_ATMOSPHERE.md"]),
    "backgrounds": ("battle terrain backgrounds / 2D special-area backdrops", ["res/graphics/battle/terrain"]),
    "location_area": ("area-preview layer beside the map-name popup", ["src/overlay005/map_name_popup.c", "res/graphics/map_popups"]),
    "field_graphics": ("3D field texture/material set (environment art)", ["res/graphics/field_sprites", "docs/visual_overhaul/G4_ENVIRONMENT_RECONSTRUCTION_COMPLETE.md"]),
    "textures": ("3D field/map texture resources (NSBTX materials)", ["docs/visual_overhaul/G4_ENVIRONMENT_RECONSTRUCTION_COMPLETE.md"]),
    "ui_menus_hud": ("Platinum menu/party/dex UI resources", ["res/graphics/party_menu", "res/graphics/pokedex"]),
    "interface_embellishments": ("battle/menu feedback layer (cursor pulses, glows, gauges)", ["res/graphics/battle/interface", "src/battle/healthbox.c"]),
    "transitions_presentation": ("field/title transition and event presentation", ["src/field_transition.c", "res/graphics/title_screen"]),
    "trainer_sprites": ("trainer class sprites", ["res/trainers/classes"]),
    "pokemon_sprites": ("Pokemon battle sprites", ["res/pokemon"]),
    "pokemon_animation": ("Pokemon animation/summary presentation", ["res/pokemon"]),
    "icons": ("Pokemon icons", ["res/pokemon/.shared"]),
    "npc_player_sprites": ("overworld NPC/player sprites", ["res/graphics/field_sprites"]),
    "misc": ("unassigned", ["docs/visual_overhaul"]),
}

IMPACT_TEXT = {1: "negligible", 2: "small, localized", 3: "noticeable in specific scenes", 4: "strong, frequently visible", 5: "transformative"}


def P(cls, comps, why, impact, nov, feas, cost, risk, slice_, techs=(), pixel="derived", mode=None, adapt=None, note=""):
    return {"class": cls, "use_mode": mode or USE_MODE.get(cls, "component"), "components": list(comps), "techniques": list(techs), "why_surfaced": why,
            "base": {"visual_impact": impact, "novelty": nov, "feasibility": feas, "cost": cost, "risk": risk, "slice": slice_}, "pixel_use": pixel, "adaptation": adapt or [], "note": note}


def tier(n: int, cuts=(4, 15, 50, 200)) -> int:
    return 1 + sum(n >= c for c in cuts)


def proposals(g: dict, f: dict) -> list[dict]:
    """All plausible opportunity proposals for one group, from structural/ledger signals only."""
    dom, src, rel, role, reason = f["domain"], g["source_id"], f["native_relation"], f["ledger_role"], f["ledger_reason"]
    out: list[dict] = []
    animated = f["has_nanr"] or f["frames_total"] > 1 or f["cells_total"] > 1
    rich = f["cells_total"] >= 12 or f["frames_total"] >= 12
    if src == "diamond":  # control/reference by policy: never a promoted opportunity without a justified exception
        return [P("reference_only", [], f"Diamond control group ({rel}); comparison only", 1, 1, 1, 1, 1, 1)]
    if rel in ("identical", "content_match_native") or reason == "identical_to_native":
        return [P("reject", [], "identical to the Platinum asset (no visual difference)", 1, 1, 1, 1, 1, 1)]
    if f["companion_only"] and dom not in ("pokemon_sprites", "icons") and not f["has_animated_tiles"]:
        return [P("reject", [], "companion/metadata-only members; no independent visual content", 1, 1, 1, 1, 1, 1)]
    if dom == "trainer_sprites":
        multi = f["cell_count"] > 1
        if rel == "missing_in_native":
            out.append(P("component_donor", ["clothing_detail", "accessory", "pose", "silhouette", "shading"], "HGSS trainer class with no Platinum counterpart: outfit/pose/accessory parts for new or reworked classes", 3, 4, 3, 2, 3, 2,
                         adapt=["identify the Platinum class that would host the part", "redraw parts on the Platinum 80x80 single-cell contract"]))
        elif role == "preferred":
            out.append(P("replacement_candidate", [], "human-approved HGSS trainer set preferred over Platinum", 3, 1, 4, 3, 3, 4, pixel="donor_pixels", adapt=["runtime QA of the converted set"]))
        elif rel in ("art_diff_geometry_close", "art_diff_geometry_review", "art_diff_minor"):
            out.append(P("enhancement_candidate", ["shading", "clothing_detail", "pose"], "HGSS art differs from Platinum: detail/shading parts can enhance the Platinum sprite while keeping Sinnoh identity", 3, 2, 4, 2, 3, 4,
                         adapt=["derive shading/detail onto the Platinum silhouette", "stay within the Platinum 16-colour row"]))
            out.append(P("component_donor", ["pose", "silhouette", "accessory"], "same group as parts library (pose/accessory) independent of the whole-asset verdict", 2, 2, 4, 2, 3, 3))
        elif rel == "palette_only":
            out.append(P("component_donor", ["palette"], "HGSS palette treatment of the same art", 2, 2, 4, 1, 2, 3, pixel="recolored_donor"))
        if multi and rel not in ("identical",):
            out.append(P("novel_detail", ["animation_frame"], f"HGSS set carries {f['cell_count']} animation cells (Platinum trainer fronts are single-cell): extra presentation frames", 3, 4, 2, 3, 3, 2,
                         mode="component", adapt=["confirm Platinum trainer animation host", "frame set needs human visual review"]))
    elif dom == "pokemon_sprites":
        if role == "preferred":
            out.append(P("replacement_candidate", [], "art revision judged eligible and best donor", 3, 1, 4, 3, 3, 4, pixel="donor_pixels", adapt=["port art-diff views only", "runtime QA gate"]))
        if rel == "palette_only":
            out.append(P("component_donor", ["palette"], "HGSS palette treatment differs from Platinum on identical art", 2, 2, 4, 1, 2, 3, pixel="recolored_donor"))
        elif rel in ("art_diff_geometry_close", "art_diff_geometry_review"):
            out.append(P("enhancement_candidate", ["pose", "shading", "silhouette"], "revised HGSS art: pose/shading parts can improve the Platinum sprite", 3, 2, 3 if rel.endswith("close") else 2, 3, 3, 3))
            out.append(P("component_donor", ["pose", "shading"], "revised pose/shading as parts library", 3, 2, 3 if rel.endswith("close") else 2, 3, 3, 3))
        elif rel == "missing_in_native" or f["needs_evidence"]:
            out.append(P("novel_detail", ["pose"], "HGSS-only presentation form (egg/shadow/other) with no Platinum counterpart", 2, 4, 2, 3, 3, 2, mode="whole_asset", pixel="donor_pixels"))
    elif dom == "icons":
        if rel == "missing_in_native":
            out.append(P("novel_detail", ["UI_element"], "HGSS-only form icon with no Platinum counterpart", 2, 4, 3, 2, 2, 2, mode="whole_asset", pixel="donor_pixels"))
    elif dom == "npc_player_sprites":
        if src == "hgss":
            if rel == "missing_in_native":
                out.append(P("novel_detail", ["clothing_detail", "pose", "accessory"], f"HGSS-only field sheet ({f['frames_ok'] or 16} frames) with no Platinum counterpart: extra NPC variety", 2, 4, 3, 2, 3, 2, mode="whole_asset", pixel="donor_pixels",
                             adapt=["slot-name alignment is not subject identity: verify subject", "NSBTX 32x32 4bpp matches the Platinum field-sprite contract"]))
            elif rel == "art_diff_minor":
                out.append(P("enhancement_candidate", ["shading"], "minor art revision of an existing Platinum NPC sheet", 2, 2, 4, 2, 2, 3))
            elif rel == "subject_unverified":
                out.append(P("component_donor", ["clothing_detail", "pose"], "sheet differs from the slot's Platinum sprite, subject unverified", 2, 3, 3, 2, 3, 2))
        else:
            out.append(P("reference_only", [], "Ranger NPC package: different game scale/art language", 1, 2, 1, 4, 3, 1))
    elif dom == "location_area":
        out.append(P("novel_capability", ["layout", "environmental_motif", "palette"], "HGSS area preview art with no Platinum equivalent (missing_in_native); module + layout reference for an area-preview layer", 4, 5, 3, 3, 2, 4,
                     techs=["event_presentation"], pixel="none", mode="technique", adapt=["new Sinnoh art per location", "native preview layer in the map-popup path"]))
        if f["tod"]:
            out.append(P("technique_donor", [], "time-of-day variant set (palette/art variants per period)", 3, 3, 4, 2, 2, 4, techs=["palette_variants", "state_driven_visuals"], pixel="none"))
    elif dom == "backgrounds":
        if src == "pmd_sky":
            out.append(P("component_donor", ["environmental_motif", "palette", "texture_region"], f"PMD composed {f['bg_w']}x{f['bg_h']} 2D background: environmental motifs and palette ramps", 3, 3, 2, 3, 3, 3,
                         adapt=["2D dungeon art -> Platinum 256x192 BG or texture motif", "redraw to the DS palette budget"]))
        else:
            out.append(P("component_donor", ["environmental_motif", "palette"], "Ranger capture-area backdrop: terrain motif/palette set for battle backdrops", 3, 3, 3, 3, 3, 3, adapt=["Ranger package decode required per use", "redraw to Platinum terrain background format"]))
    elif dom == "environmental_effects":
        if src == "pmd_sky":
            out.append(P("technique_donor", [], "background with animated-tile (BPA) companion: tile/palette animation on a static background", 3, 4, 3, 2, 2, 3,
                         techs=["environmental_animation", "palette_cycling", "background_movement"], pixel="none", adapt=["express as Platinum texture/palette animation (NSBTA/NSBTP) or weather layer"]))
            out.append(P("component_donor", ["environmental_motif", "animation_frame"], "animated environment tiles as motif frames", 3, 3, 2, 3, 3, 3))
        else:
            out.append(P("component_donor", ["particle_shape", "environmental_motif", "animation_frame"], "Ranger field effect resource", 3, 3, 2, 3, 3, 2))
    elif dom == "field_graphics":
        out.append(P("component_donor", ["environmental_motif", "texture_region"], f"Ranger composed {f['map_w']}x{f['map_h']} field map ({f['quad_layers']} layers): environmental motif/tile library", 3, 3, 2, 3, 3, 2,
                     adapt=["Ranger tile art is 2D: motif reference/redraw for Platinum 3D textures"]))
        if f["quad_layers"] >= 8:
            out.append(P("technique_donor", [], f"layered composition ({f['quad_layers']} quad layers, {f['map_w']}x{f['map_h']})", 2, 3, 3, 3, 2, 2, techs=["object_layering", "background_movement"], pixel="none"))
    elif dom == "textures":
        out.append(P("component_donor", ["texture_region", "material_treatment"], f"Ranger 3D texture payload ({f['tex_chips']} decoded chips, 8bpp 256-colour)", 3, 3, 3, 3, 3, 3,
                     adapt=["256-colour DS 3D texture format is supported; recolour/retile to the Platinum material set"], pixel="recolored_donor"))
    elif dom == "field_effects":
        if f["anim_groups"] >= 3 or rich:
            out.append(P("component_donor", ["animation_frame", "particle_shape"], f"PMD animated sprite ({f['frames_ok']}/{f['frames_total']} frames, {f['anim_groups']} animation groups)", 3, 3, 2, 3, 3, 3))
            out.append(P("technique_donor", [], f"multi-state animation structure ({f['anim_groups']} groups)", 3, 3, 3, 2, 2, 3, techs=["animation_sequencing", "state_driven_visuals"], pixel="none"))
        elif f["frames_total"] > 1:
            out.append(P("component_donor", ["animation_frame"], f"PMD animated sprite ({f['frames_ok']} frames)", 2, 2, 2, 3, 3, 2))
    elif dom == "battle_effects":
        eff = g["unit"].startswith("ranger_effect")
        out.append(P("component_donor", ["particle_shape", "animation_frame", "material_treatment"] if eff else ["UI_element", "animation_frame"],
                     f"Ranger {'effect' if eff else 'target/marker'} bundle ({f['cells_ok']}/{f['cells_total']} nonblank cells, standard Nitro NCER/NANR)", 4 if eff and rich else 3, 3, 3, 3, 3, 4 if eff else 3,
                     adapt=["recolour/redraw into Platinum particle resources", "bind to one move script"]))
        if rich and eff:
            out.append(P("technique_donor", [], f"multi-phase effect animation ({f['cells_total']} cells): launch/travel/impact/residue phases", 3, 2, 4, 2, 2, 4, techs=["effect_staging", "animation_sequencing", "frame_timing"], pixel="none"))
        if not eff:
            out.append(P("novel_detail", ["UI_element"], "target/marker feedback sprite family", 2, 4, 2, 3, 3, 2, mode="component"))
    elif dom == "interface_embellishments":
        out.append(P("novel_detail", ["UI_element", "particle_shape", "animation_frame"], f"Ranger interface feedback primitive ({f['cells_ok']} cells): glow rings/gauges/pulses", 3, 4, 3, 2, 2, 4, mode="component",
                     techs=["state_driven_visuals"], adapt=["redraw as Platinum OAM feedback layer", "drive from existing menu/battle events"]))
        if f["cells_total"] >= 4:
            out.append(P("technique_donor", [], "multi-cell growth/pulse state set", 3, 3, 4, 2, 2, 4, techs=["state_driven_visuals", "ui_entrance_exit"], pixel="none"))
    elif dom == "ui_menus_hud":
        if src == "hgss":
            out.append(P("component_donor", ["UI_element", "layout"], "HGSS UI graphic family (not visually compared with Platinum)", 2, 2, 3, 3, 3, 2))
        elif src == "pmd_sky":
            out.append(P("component_donor", ["UI_element"], "PMD frame/font graphic", 2, 2, 2, 3, 3, 2))
        else:
            out.append(P("component_donor", ["UI_element", "layout"], f"Ranger menu/HUD package ({f['cells_ok'] or f['n_members']} members, Nitro cell format)", 2, 3, 3, 3, 3, 2))
    elif dom == "transitions_presentation":
        out.append(P("technique_donor", [], "event/ending/title presentation package: staged background + cell composition", 3, 4, 3, 3, 3, 3,
                     techs=["event_presentation", "transition_choreography"], pixel="none", adapt=["express through Platinum field/title transition path"]))
        if src == "pmd_sky":
            out.append(P("component_donor", ["environmental_motif", "palette"], "PMD title/story background", 3, 3, 2, 3, 3, 3))
        if (src == "pmd_sky" and f["bg_w"]) or (src == "ranger2" and any(x in g["unit"] for x in ("ranger_event", "ranger_ending")) and f["has_tilemap"]):
            out.append(P("novel_capability", ["layout", "environmental_motif"], "full-screen still-scene art (event/ending/story card): a presentation screen type Platinum does not expose", 4, 5, 2, 4, 3, 2,
                         techs=["event_presentation"], pixel="none", mode="technique", adapt=["author Sinnoh scene art; reuse only the staging/layout idea", "new native presentation state"]))
    elif dom == "pokemon_animation":
        if g["unit"].startswith("ranger_pokeOBJ"):
            out.append(P("reference_only", [], "Ranger Pokemon object cell bundle with no Platinum target", 1, 2, 1, 4, 3, 1))
        elif f["family"] == "ranger_poke_w" and f["n_members"] >= 4:
            out.append(P("novel_detail", ["animation_frame", "pose"], f"Ranger walk-cycle set ({f['n_members']} frames, <=40x40) matches the 32x32 field-sprite contract: overworld Pokemon presence frames", 3, 4, 2, 3, 3, 2, mode="component",
                         adapt=["semantic pose/orientation not yet approved", "needs an overworld Pokemon host in Platinum"]))
        elif f["frames_total"] == 0 and f["n_members"] >= 8:
            out.append(P("technique_donor", [], f"Ranger Pokemon animation set ({f['n_members']} frames): multi-frame sequencing", 2, 2, 2, 3, 3, 2, techs=["animation_sequencing", "frame_timing"], pixel="none"))
    if not out:
        out.append(P("reference_only", [], "no actionable signal beyond reference", 1, 1, 1, 1, 1, 1))
    return out


def evidence_quality(g: dict, f: dict) -> int:
    rel = f["native_relation"]
    if g["subsystem"] == "pokemon_animation_reference":  # catalog quality note: semantic pose suitability not yet approved
        return 2
    if f["decode_issues"] and f["decode_issues"] >= f["n_members"]:
        return 1
    if g["subsystem"] == "field_npc_player_sprites":  # slot-name alignment is not subject identity
        return 3 if rel != "subject_unverified" else 2
    if g["source_id"] == "hgss" and rel not in (None, "unmeasured", "subject_unverified"):
        return 4
    if rel in ("subject_unverified", "unmeasured") and g["source_id"] == "hgss":
        return 2
    if f["frames_total"] or f["cells_total"] or f["map_w"] or f["bg_w"] or f["tex_chips"] or f["geom"]:
        return 3
    return 2


def score(g: dict, f: dict, p: dict) -> dict:
    b, cls = p["base"], p["class"]
    n = f["family_size"]
    lib = tier(n)
    if len(p["components"]) >= 3:
        lib = min(5, lib + (1 if n >= 4 else 0))
    reuse = min(5, max(1, tier(n, (3, 10, 40, 150)) + (1 if len(p["components"]) + len(p["techniques"]) >= 3 else 0) - (2 if cls == "replacement_candidate" else 0)))
    ev = evidence_quality(g, f)
    conv = {"none": 1, "trivial": 2, "structural": 3, "not_portable": 5}[g["conversion_requirement"]]
    dep = 1 if cls in ("technique_donor",) or p["pixel_use"] == "none" else (conv if cls in ("replacement_candidate",) else min(conv, 4))
    imp = b["visual_impact"]
    if cls not in ("replacement_candidate",) and f["family_size"] >= 8:  # differentiate inside large families by richness percentile
        imp = min(5, imp + (1 if f["rich_pct"] >= 0.85 else -1 if f["rich_pct"] < 0.3 else 0))
        imp = max(1, imp)
    dims = {"visual_impact": imp, "novelty": b["novelty"] if f["has_native_target"] is False or cls != "replacement_candidate" else 1, "feasibility": b["feasibility"], "reuse": reuse, "library": lib, "evidence": ev,
            "cost": b["cost"], "risk": b["risk"], "dependency": dep, "slice": min(5, b["slice"] + (1 if f["n_members"] <= 3 and ev >= 3 else 0))}
    if cls == "replacement_candidate":
        dims["novelty"], dims["library"] = 1, min(dims["library"], 2)
    return dims


def composite(dims: dict) -> float:
    tot = sum(WEIGHTS[k] * ((6 - dims[k]) if k in INVERTED else dims[k]) for k in DIMS)
    return round(tot / sum(WEIGHTS.values()), 3)


def confidence(ev: int, cls: str) -> str:
    return "high" if ev >= 5 else "medium" if ev >= 4 or (ev == 3 and cls not in ("novel_capability",)) else "low"


def cost_label(c: int) -> str:
    return "low" if c <= 2 else "medium" if c == 3 else "high"
