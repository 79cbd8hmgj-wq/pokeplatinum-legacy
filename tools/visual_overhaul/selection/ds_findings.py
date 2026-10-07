"""DS-only opportunity findings (phase ds_only). Evidence: existing catalogs/ledgers/docs plus targeted donor-checkout verification
(read-only, pinned commits below). Nothing here modifies Platinum."""
from __future__ import annotations

import json

import opportunities as opp
from common import *  # noqa: F401,F403

WHO = "claude (DS reassessment; not human-approved)"
HGSS = "9d8b7591f09b65804da2fb2dfd56f320633e0d36"
PMD = "be11cacd78574257bb88116c36dfca8f0839feba"
RNG = "55b4e0cd4598bcbc966f64ad6a10eeab98f813e1"
DP = "5bc4b1a3d8f100f77a4c64e59a0d544a0e29b3ec"


def V(repo, commit, path, fact):
    return {"repo": repo, "commit": commit, "path": path, "fact": fact}


def sc(impact, novelty, feas, reuse, cost, risk, slice_):
    return {"visual_impact": impact, "novelty": novelty, "feasibility": feas, "reuse": reuse, "cost": cost, "risk": risk, "slice": slice_}


def F(fid, subject, cl, donor, target, useful, why, constraints, adaptation, scores, asset_use, evidence, pixel_use, tags, cost, risk, conf, **kw):
    feas = 1 if not scores else 3 if scores["feasibility"] >= 4 else 2 if scores["feasibility"] == 3 else 1
    f = {"finding_id": fid, "subject": subject, "classification": cl, "status": "proposed", "donor": donor, "target": target, "useful": useful, "why": why,
            "constraints": constraints, "adaptation": adaptation, "scores": scores, "asset_use": asset_use, "cost": cost, "risk": risk, "confidence": conf, "feasibility": feas,
            "evidence": evidence, "pixel_use": pixel_use, "tags": tags, "proposed_by": WHO, **kw}
    if scores is None:
        del f["scores"], f["asset_use"]
    return f


ACE = {"scores": sc(2, 2, 4, 2, 2, 3, 4), "asset_use": "components"}


def ds_findings(groups, ev):
    pv = sorted(g for g in groups if g.startswith("field_environment_art/hgss/hgss_preview_"))
    out = []
    out.append(F("opp:hgss/map_location_preview", "Area/location preview card (new Sinnoh artwork; HGSS module + layout as the DS reference)", "novel_capability",
        {"game": "hgss", "source_id": "hgss", "cataloged": True, "group_ids": pv, "locator": "HGSS fielddata/graphic/preview_graphic (23 areas x time of day) + src/map_preview_graphic.c (950-line task module) + src/unk_02055BF0.c trigger",
         "verification": [V("pokeheartgold", HGSS, "src/map_preview_graphic.c", "self-contained task-based preview module with per-map index (MapPreviewGraphic_GetIndex) and time-of-day image selection (BeginShowImage/Task_ShowImage)"),
                          V("pokeheartgold", HGSS, "src/unk_02055BF0.c", "shows the preview on map entry via MapPreviewGraphic_BeginShowImage")]},
        {"kind": "none", "host_system": "new area-preview layer shown on map entry beside the existing map-name popup", "refs": ["src/overlay005/map_name_popup.c", "res/graphics/map_popups", "src/map_header.c"]},
        "A location preview card (artwork + name) on entering an area, with time-of-day variants. Platinum exposes only 136x48 name signs.",
        "Committed evidence shows Platinum has no area-preview screen; HGSS proves the full DS-native module (same Gen IV engine lineage) and art layout. Strong identity/presentation gain for every area.",
        ["Platinum has no area-preview code/resources: new UI state and per-location Sinnoh art are required", "HGSS art depicts Johto/Kanto: layout/composition reference only, never pixels", "256x192 DS BG and palette/VRAM budget; must not collide with the map-name popup"],
        ["author Sinnoh preview art per location tier (vertical slice: 2-3 locations first)", "adapt the HGSS module structure to Platinum field task/popup path (re-implement natively; no code copied verbatim)", "decide time-of-day variants after the slice"],
        sc(4, 5, 4, 4, 3, 2, 5), "techniques",
        {"basis": "catalog_evidence", "summary": "ledger field_environment_art: 23 HGSS preview groups are reference_only/no_native_target (missing_in_native); composed previews committed; HGSS source module verified in the donor checkout.",
         "refs": ["docs/visual_overhaul/selection/ledgers/field_environment_art.json", "docs/visual_overhaul/selection/evidence/field_environment_art.json", "docs/visual_overhaul/selection/review/environment_previews/previews_contact_sheet.png", "docs/visual_overhaul/selection/SELECTION_CHECKPOINT.md"],
         "bound_digest": opp.bound_digest(pv, groups, ev)},
        "none", ["UI_element", "layout", "environmental_motif"], "high", "medium", "medium", covers_pools=["field_environment_art/hgss"]))

    out.append(F("opp:hgss/follower_pokemon", "Following-Pokemon overworld presence (HGSS follower sprite sheets + FollowMon system)", "novel_capability",
        {"game": "hgss", "source_id": "hgss", "cataloged": False, "locator": "HGSS files/data/mmodel/mmodel/*.NSBTX: 572 pokemon_follower_2pal sheets (catalog_extensions README: scanned, excluded from the NPC/player catalog scope) + src/follow_mon.c (2019 lines) + src/save_follow_mon.c",
         "verification": [V("pokeheartgold", HGSS, "include/follow_mon.h", "FollowMon API: InitMapObject/ChangeMon/GetSpriteID(species,form,gender)/SetObjectParams/IsActive/IsVisible/GetPermission"),
                          V("pokeheartgold", HGSS, "src/follow_mon.c", "2019-line field module; with save_follow_mon.c (38 lines) holds the follower state"),
                          V("pokeheartgold", HGSS, "files/data/mmodel/mmodel", "863 NSBTX sheets total; the 572 follower sheets are the 2-palette Pokemon sheets counted by the catalog extension")]},
        {"kind": "none", "host_system": "overworld follower object (Pokemon walking behind the player) using the map-object system", "refs": ["src/map_object.c", "src/map_object_move.c"]},
        "A party Pokemon visibly follows the player in the field, with per-species/form/gender/shiny sheets.",
        "The single largest presentation novelty available in the DS set: Platinum has no follower at all (no follower code in map_object.c), and HGSS shares Platinum's Gen IV map-object lineage so both art format and system design are DS-native.",
        ["engine feature as much as art: follower object, party sync, collision/permission rules, save flag, script/cutscene hiding", "572 sheets are whole assets (no Platinum equivalent); size/permission tables per species", "map-object sprite/OAM budget with an extra object; Platinum overworld lighting/shadow interaction"],
        ["port the follower design natively (task/map-object integration), sheets via the existing field-sprite NSBTX path", "start with a handful of species to prove sprite sizing and object limits", "decide hide rules for cutscenes/surf/bike"],
        sc(5, 5, 2, 5, 5, 4, 2), "mixed",
        {"basis": "donor_checkout_verification", "summary": "Follower system and 572 follower sheets verified in the HGSS checkout; the sheet count is already recorded in the committed catalog-extension README.",
         "refs": ["docs/visual_overhaul/catalog_extensions/README.md"]},
        "donor_pixels", ["pose", "animation_frame"], "high", "high", "medium"))

    out.append(F("opp:pmd_sky/battler_status_indicators", "Temporary status indicators above battlers (PMD Sky status-icon model)", "novel_detail",
        {"game": "pmd_sky", "source_id": "pmd_sky", "cataloged": False, "locator": "PMD Sky per-entity status icon mask (UpdateStatusIconFlags) + SYSTEM/manpu_ma.{sma,smd}, SYSTEM/manpu_su.sma and EFFECT/effect.bin (not cataloged / not decoded: icon art container not yet identified)",
         "verification": [V("pmd-sky", PMD, "src/overlay_29_022E3F20.c", "UpdateStatusIconFlags builds a 64-bit icon mask per entity from sleep/burn/freeze/cringe/bide/reflect/curse... status classes (logic verified)"),
                          V("pmd-sky", PMD, "files/SYSTEM/manpu_ma.smd", "present (33 KB) with manpu_ma.sma/manpu_su.sma; contents not decoded, role unverified (name only)")]},
        {"kind": "none", "host_system": "battle: temporary indicator layer above battler sprites (alongside the healthbox status icon)", "refs": ["src/battle/healthbox.c"]},
        "Short-lived status indicators over the battler that show status applied/active, driven by a status-icon mask.",
        "Adds at-a-glance feedback on the battler; Platinum only shows status in the healthbox. The mask-per-status design maps onto Platinum battle status events.",
        ["icon art location not yet identified/cataloged in PMD Sky (catalog has no assets matching status/manpu); may need redraw", "OAM budget during battle; must not collide with healthbox/HP bar/move animations", "icons must read at DS battle scale"],
        ["implement as a Platinum-native OAM layer fed by battle status events", "locate/decode the PMD icon art (targeted catalog extension) or redraw in Platinum palette"],
        sc(3, 4, 3, 4, 3, 3, 4), "mixed",
        {"basis": "donor_checkout_verification", "summary": "Status-icon logic verified in pmd-sky; icon art container unverified (manpu/effect.bin uncataloged), so confidence is capped at medium.", "refs": ["docs/visual_overhaul/DONOR_ASSET_CATALOG.json"]},
        "derived", ["UI_element", "animation_frame"], "medium", "medium", "medium"))

    out.append(F("opp:ranger2/effect_primitives", "Ranger 2 2D effect primitives (fire/tornado/lightning/glow)", "component_donor",
        {"game": "ranger2", "source_id": "ranger2", "cataloged": True, "group_ids": [],
         "locator": "res/prebuilt/data/effect/e###_LZ.bin (200 animated cell bundles), target/ and targetOBJ/ (436 more); standard Nitro NCER/NANR/NCGR/NCLR",
         "verification": [V("pokeranger2", RNG, "res/prebuilt/data/effect/e010_LZ.bin", "rendered with the repo renderer: 57 cells, multi-phase fireball launch/impact/embers"),
                          V("pokeranger2", RNG, "res/prebuilt/data/effect/e100_LZ.bin", "rendered: 18 cells of lightning bolts/arcs"),
                          V("pokeranger2", RNG, "res/prebuilt/data/effect/e030_LZ.bin", "rendered: 3-cell tornado")]},
        {"kind": "system", "subsystem": "battle_effects_particles", "system": "battle move particle/2D effect resources", "refs": ["res/graphics/battle/particles", "res/moves/brave_bird/anim.s"]},
        "Shaded, DS-era effect primitives (fireball, tornado, electric arcs, glow rings) usable as component shapes for specific Platinum move effects.",
        "Same Nitro cell/animation packaging as Platinum 2D effects and visibly richer than generic shapes; component use lets individual moves gain identity without replacing whole animations.",
        ["Ranger art style/scale must be matched to Platinum battle effects per move", "16-colour palette budget and Platinum particle/OAM formats", "per-move use only; no wholesale effect replacement"],
        ["recolour/redraw selected primitives into Platinum particle resources (derived/recolored pixels)", "tie each primitive to one move anim.s"],
        sc(4, 3, 3, 5, 3, 3, 4), "components",
        {"basis": "donor_checkout_verification", "summary": "Targeted render sample committed (ranger2_effect_ui_sample.png): shaded multi-frame effects in Nitro formats. Visual comparison only; no per-move target chosen yet.",
         "refs": ["docs/visual_overhaul/selection/opportunities/evidence/ranger2_effect_ui_sample.png"]},
        "recolored_donor", ["particle_shape", "animation_frame", "material_treatment"], "medium", "medium", "medium", covers_pools=["battle_effects_particles/ranger2"]))

    out.append(F("opp:ranger2/effect_sequencing", "Ranger 2 multi-phase effect sequencing (launch/impact/embers)", "technique_donor",
        {"game": "ranger2", "source_id": "ranger2", "cataloged": True, "group_ids": [], "locator": "effect/e010 (57-cell fireball with launch, impact, scatter phases) and e100 (bolt/arc/impact phases) NANR sequences",
         "verification": [V("pokeranger2", RNG, "res/prebuilt/data/effect/e010_LZ.bin", "57 cells span launch, travel, impact burst and ember scatter")]},
        {"kind": "system", "subsystem": "battle_effects_particles", "system": "battle move animation scripts", "refs": ["res/moves/brave_bird/anim.s"]},
        "Phase structure and frame pacing of effect animations (spawn -> travel -> impact -> residue) expressed in Platinum anim scripts.",
        "Technique only via Platinum's native script/particle system; the same approach already used for G5 staging, no donor pixels.",
        ["Platinum move scripts (res/moves/*/anim.s) are the only implementation path", "must keep existing particle resources and sound timing"],
        ["translate phase/timing structure to anim.s commands; no donor assets"],
        sc(3, 2, 4, 4, 2, 2, 4), "techniques",
        {"basis": "donor_checkout_verification", "summary": "Phase structure visible in the committed render sample (e010/e100).", "refs": ["docs/visual_overhaul/selection/opportunities/evidence/ranger2_effect_ui_sample.png"]},
        "none", ["animation_timing"], "low", "low", "medium"))

    ref = lambda fid, subj, game, src, loc, host, useful, why, cons, adapt, refs, summ, verif=None, pools=(): F(fid, subj, "reference_only",
        {"game": game, "source_id": src, "cataloged": True, "locator": loc, **({"verification": verif} if verif else {})},
        {"kind": "none", "host_system": host}, useful, why, cons, adapt, None, "none",
        {"basis": "repo_document", "summary": summ, "refs": refs}, "none", ["layout"], "low", "low", "medium", covers_pools=list(pools))
    out += [
        ref("opp:hgss/ui_dex_party_reference", "HGSS Pokedex/party-list UI graphics", "hgss", "hgss", "files/graphic/zukan_gra (123 members), files/graphic/plist_gra (27 members)", "Platinum Pokedex/party menus (already remastered natively in G7)",
            "Design reference for dex/party layout and animation.", "Targeted evidence closure composed the HGSS party-list screens (plist_gra: Pokeball-motif backdrop + slot-tab panels) and the Pokedex screens (zukan_gra: SEARCH/OPEN/QUIT/CRY/DETAILS/SIZE/FORMS/BACK button strips, red header + grid panels, cry dial). Each has a Platinum counterpart already rebuilt natively in G7; no element adds a capability Platinum lacks, so the family is confirmed reference-only.",
            ["HGSS layouts target different screen structure", "G7 owns the current look"], ["compare layouts before any reuse; promote to component_donor only with a concrete element"],
            ["docs/visual_overhaul/selection/ledgers/party_summary_ui.json", "docs/visual_overhaul/selection/ledgers/pokedex_ui.json", "docs/visual_overhaul/G7_COMPLETE_SUMMARY.md", "docs/visual_overhaul/selection/mining/evidence/hgss_zukan_screens.png", "docs/visual_overhaul/selection/mining/evidence/hgss_camera_plist.png", "docs/visual_overhaul/selection/mining/evidence/hgss_ui_targeted.json"], "Targeted renders of 4 party and ~40 Pokedex tilemap screens (partial NSCR/NCGR pairing, some screens blank); G7 already shipped native UI. Verdict: reference_only confirmed."),
        ref("opp:hgss/camera_viewfinder", "HGSS photo-camera viewfinder frame", "hgss", "hgss", "files/graphic/camera_viewfinder", "none (Platinum has no photo feature)",
            "Viewfinder frame art for an HGSS-only photo feature.", "Used only by src/field_take_photo.c, a gameplay feature Platinum lacks; no visual-overhaul target.",
            ["requires a photo mini-feature"], ["none planned"], ["docs/visual_overhaul/selection/ledgers/menu_ui_frames.json"], "menu_ui_frames ledger needs_evidence; donor use verified as a standalone feature.",
            [V("pokeheartgold", HGSS, "src/field_take_photo.c", "only consumer of graphic/camera_viewfinder")]),
        ref("opp:hgss/npc_trainer_variety_pool", "HGSS-only NPC/trainer sprites (111 field sheets, 68 trainer classes)", "hgss", "hgss", "field_npc_player_sprites (111 HGSS-only) + trainer_battle_sprites (68 classes without Platinum counterpart)", "none (no Platinum target)",
            "Additional character sprites usable if new NPC/trainer variants are ever added.", "Whole sprites with no Platinum counterpart; slot names do not prove subject identity (subject_unverified), so they stay a reference pool.",
            ["subject unverified", "no overhaul requirement for new classes yet"], ["verify subject identity per sprite before any use"],
            ["docs/visual_overhaul/catalog_extensions/README.md", "docs/visual_overhaul/selection/ledgers/field_npc_player_sprites.json"], "catalog_extensions README: 111 HGSS-only sprites, 68 classes without Platinum counterpart.", pools=["field_npc_player_sprites/hgss", "trainer_battle_sprites/hgss"]),
        ref("opp:diamond/control_reference", "Diamond as Platinum control/reference", "diamond", "diamond", "dp trainer back/otherpoke/icon sets", "Platinum (same engine lineage)",
            "Control for what Platinum changed/removed vs Diamond; never a preferred donor.", "Diamond differs from Platinum only where Platinum is the later revision (489 battle sprites differ, Snover/Rotom icons); control class can never be selected.",
            ["control class: comparison only"], ["use only to detect Platinum revisions/unused content"], ["docs/visual_overhaul/selection/SELECTION_CHECKPOINT.md", "docs/visual_overhaul/selection/ledgers/pokemon_battle_sprites.json"], "Selection rules: donor class control is never selectable."),
        ref("opp:pmd_sky/environment_and_title_backgrounds", "PMD Sky dungeon/ground backgrounds and title BACK art", "pmd_sky", "pmd_sky", "MAP_BG/DUNGEON bgp (1482 map backgrounds), BACK/*.bgp (25 static)", "Platinum special-area presentation",
            "Palette and environmental-motif ideas for special areas.", "2D tilemap dungeon art does not map onto Platinum's 3D field/battle backgrounds; useful only as colour/motif reference.",
            ["2D tilesets vs 3D maps"], ["reference palettes only"], ["docs/visual_overhaul/PMD_SKY_VISUAL_ASSET_INVENTORY.md", "docs/visual_overhaul/selection/ledgers/title_and_presentation.json"], "Ledgers: technique/reference class; inventory lists 1514 map/background resources.", pools=["field_environment_art/pmd_sky", "title_and_presentation/pmd_sky"]),
        ref("opp:pmd_sky/ground_overlay_sprites", "PMD Sky GROUND animated sprites (523 groups)", "pmd_sky", "pmd_sky", "files/GROUND/*.wan (555 files)", "Platinum field overlays",
            "Possible animated overlay/object frames.", "WAN containers have no committed renderer, so no visual evidence exists yet; keep as reference until decoded.",
            ["no WAN decoder/renders in repo"], ["promote to component_donor after a targeted decode of a small sample"], ["docs/visual_overhaul/selection/ledgers/field_effects_overlays.json"], "Ledger field_effects_overlays: 523 technique-class groups, unmeasured.", pools=["field_effects_overlays/pmd_sky"]),
        ref("opp:ranger2/ui_and_story_backgrounds", "Ranger 2 interface, menu, event and ending art", "ranger2", "ranger2", "interface/menu/event/ending/title bundles (e.g. i000 gauge, i005/i010 glow rings, 158 tiled backgrounds)", "Platinum UI/title presentation",
            "Gauge/glow/cursor shapes and story-background composition ideas.", "Capture-styler specific UI and illustrations in Ranger style; Platinum UI is owned by G7, so no concrete element is proposed.",
            ["Ranger-specific gameplay UI", "style mismatch with G7 UI"], ["revisit for individual glow/gauge primitives"], ["docs/visual_overhaul/RANGER_VISUAL_BUNDLE_CLASSIFICATION.md", "docs/visual_overhaul/selection/opportunities/evidence/ranger2_effect_ui_sample.png"], "Bundle classification + sample render: i005/i010 glow rings, i000 gauges.", pools=["menu_ui_frames/ranger2", "title_and_presentation/ranger2", "battle_backgrounds_hud/ranger2"]),
        ref("opp:ranger2/pokemon_sprite_frames", "Ranger 2 Pokemon field sprite frames (35k frames, 282 species)", "ranger2", "ranger2", "res/prebuilt/data/poke/p###_##_LZ.bin", "Platinum Pokemon presentation",
            "Pose/animation reference for field-scale Pokemon.", "Field-scale frames (75.8% fit within 40x40) do not match Platinum's 160x80 battle contract; HGSS already supplies field follower sheets for every species.",
            ["scale/contract mismatch with battle sprites"], ["reference only"], ["docs/visual_overhaul/RANGER_RENDER_COMPATIBILITY.md", "docs/visual_overhaul/RANGER_SPRITE_PIPELINE_CHECKPOINT.md"], "Render compatibility census: 75.81% fits_small, 22.80% fits.", pools=["pokemon_animation_reference/ranger2", "no_platinum_target/ranger2"]),
    ]
    out.append(F("opp:hgss_diamond/icons_identical", "HGSS/Diamond Pokemon icons are pixel-identical to Platinum", "reject",
        {"game": "hgss", "source_id": "hgss", "cataloged": True, "locator": "poketool/icongra icons (HGSS and Diamond) for 494 base species"},
        {"kind": "none"}, "None: indexed art and palettes are identical.", "Swapping icons yields no visual payoff (G3 icon ruling: direct but reject).",
        ["no visual difference"], ["keep Platinum icons"], None, "none",
        {"basis": "repo_document", "summary": "G3 audit icon ruling plus ledger pokemon_icons: 1071 native_keep.", "refs": ["docs/visual_overhaul/G3_CHARACTER_POKEMON_DONOR_AUDIT.md", "docs/visual_overhaul/selection/ledgers/pokemon_icons.json"]}, "none", ["pose"], "low", "low", "high"))

    # ---- evidence closure (C/D): HGSS 3D field resources and follower sheets, uncataloged until a targeted extension exists
    cen = json.loads((SEL / "mining/evidence/hgss_3d_census.json").read_text())
    fol = json.loads((SEL / "mining/evidence/hgss_follower_sheets.json").read_text())
    E3 = "docs/visual_overhaul/selection/mining/evidence/"
    bf, br, mt = cen["bm_field"], cen["bm_room"], cen["hgss_map_textures"]
    out.append(F("opp:hgss/field_building_model_library", "HGSS building/prop model library (340 outdoor + 222 interior BMD0 models)", "component_donor",
        {"game": "hgss", "source_id": "hgss", "cataloged": False,
         "locator": "HGSS files/fielddata/build_model/bm_field.narc (340 BMD0), bm_room.narc (222 BMD0) + bm_*_matshp.dat; uncataloged (the catalog has no model groups)",
         "verification": [V("pokeheartgold", HGSS, "files/fielddata/build_model/bm_field.narc", f"340 BMD0 outdoor buildings/props decoded with the committed NSBMD previewer ({bf['tris_total']} triangles; {bf['with_any_novel_texture']} models carry a texture absent from Platinum)"),
                          V("pokeheartgold", HGSS, "files/fielddata/build_model/bm_room.narc", f"222 BMD0 interiors decoded ({br['tris_total']} triangles); {br['all_textures_identical_to_platinum']} reuse only textures Platinum already has, {br['with_any_novel_texture']} bring novel textures")]},
        {"kind": "system", "subsystem": "field_environment_art", "system": "field prop/building models (NSBMD props + texture sets)", "refs": ["res/field/props/models", "res/field/props/texture_sets"]},
        "Pokemon Centers/Marts/gyms, Japanese-style town houses, pagoda/tower, fountains, bridges, gates, fences, signs, lamps, doors, market stalls and interiors as DS-native models + textures.",
        f"Same Gen IV BMD0/NSBMD format family as Platinum's {cen['platinum']['prop_models']} prop models, so geometry and textures can be reused as components (kit-bash new Sinnoh props/buildings, texture detail) rather than imported wholesale. {bf['with_any_novel_texture']}/{bf['models']} outdoor models bring textures Platinum lacks.",
        ["Johto/Kanto architecture: use as parts/kit-bash and texture detail, not as drop-in Sinnoh buildings", "building placement, material/shape tables (matshp) and area texture sets must be rebuilt per Platinum area", "texture palette/format budgets per area; preview shows model parts without node transforms (some multi-node models are approximate)"],
        ["target extension: catalog bm_field/bm_room as ~560 model groups + per-model texture hashes", "convert BMD0 -> NSBMD props through the Platinum prop-model path; regrade textures with the G4 environment pipeline", "start with 5-10 props that Sinnoh lacks (fountain, signposts, lamps, bridges)"],
        sc(4, 3, 2, 5, 4, 3, 3), "components",
        {"basis": "donor_checkout_verification", "summary": f"Decoded and rendered all 562 BMD0 models and their textures (committed sheets); Platinum comparison by exact texture hash against {cen['platinum']['textures_decoded']} Platinum textures.",
         "refs": [E3 + "hgss_bm_field_models.png", E3 + "hgss_bm_room_models.png", E3 + "hgss_3d_census.json"]},
        "recolored_donor", ["texture_region", "material_treatment", "environmental_motif", "silhouette"], "high", "medium", "medium"))

    out.append(F("opp:hgss/map_texture_set_library", "HGSS map texture sets (106 BTX0 sets, ~1.8k novel unique textures)", "component_donor",
        {"game": "hgss", "source_id": "hgss", "cataloged": False,
         "locator": "HGSS files/a/0/4/4 (NARC of 106 BTX0 map texture sets, 3659 textures); uncataloged (the catalog has no texture/model groups for HGSS)",
         "verification": [V("pokeheartgold", HGSS, "files/a/0/4/4", f"{mt['sets']} BTX0 sets, {mt['textures']} textures, {mt['unique_exact']} unique; {mt['novel_unique']} ({mt['novel_pct']}%) have no exact match among Platinum's {cen['platinum']['unique_exact']} unique textures; {mt['near_match_only']} are near matches (variants)")]},
        {"kind": "system", "subsystem": "field_environment_art", "system": "area map texture sets (NSBTX)", "refs": ["res/field/maps/texture_sets", "docs/visual_overhaul/G4_ENVIRONMENT_RECONSTRUCTION_COMPLETE.md"]},
        "Terrain/cliff/path/water/cave/ice/gym-floor/foliage/roof textures as a DS-native region library (tall trees, autumn foliage, tile and brick, cave walls, ice, shop interiors).",
        "Identical DS 3D texture format (TEX0 4/16/256-colour + compressed) to Platinum's map texture sets, so regions convert trivially; the novel majority gives fresh detail for the existing G4 environment-grade pipeline.",
        ["Johto palettes must be re-graded to the Sinnoh area look (G4 pipeline)", "per-area texture set size/VRAM limits", "palette pairing is by name; some compressed textures need per-set verification"],
        ["catalog the 106 sets as texture groups; hash against Platinum to keep only novel/near-match regions", "feed selected regions to the G4 recolor tools for one vertical-slice area"],
        sc(4, 3, 3, 5, 3, 3, 4), "components",
        {"basis": "donor_checkout_verification", "summary": f"Decoded all 106 sets; exact-hash comparison with Platinum prop/map texture sets and embedded model textures; novel-texture contact sheet committed.",
         "refs": [E3 + "hgss_map_textures_novel.png", E3 + "hgss_3d_census.json"]},
        "recolored_donor", ["texture_region", "material_treatment", "environmental_motif"], "medium", "medium", "medium"))

    out.append(F("opp:hgss/follower_sheet_library", "HGSS overworld Pokemon sheet library (572 species/form sheets; usable without the follower system)", "novel_detail",
        {"game": "hgss", "source_id": "hgss", "cataloged": False,
         "locator": "HGSS files/data/mmodel/mmodel/*.NSBTX: 572 two-palette Pokemon sheets (538 at 32x32, 34 at 64x64), 8 frames each; uncataloged (excluded from the NPC/player catalog scope)",
         "verification": [V("pokeheartgold", HGSS, "files/data/mmodel/mmodel", f"decoded {fol['sheets']} sheets: {fol['frames_per_sheet']} distinct frames each (~{fol['mean_distinct_frames']}/8 distinct), normal + shiny palette, 4bpp 32x32 matching Platinum's field-sprite contract")]},
        {"kind": "none", "host_system": "overworld Pokemon presence outside any follower mechanic: event/cutscene sprites, special encounters, roaming/standing Pokemon NPCs", "refs": ["res/graphics/field_sprites/pokemon", "src/map_object.c"]},
        "A full-species overworld sprite set (down/up/left/right pairs + shiny palette) for events, cutscenes, special encounters and decorative field Pokemon.",
        f"Platinum ships {len(__import__('os').listdir(ROOT / 'res/graphics/field_sprites/pokemon'))} overworld Pokemon sheets; HGSS adds {fol['sheets']} drop-in sheets in the same NSBTX/4bpp path. The system (following) stays deferred; the sheets alone enable cutscene/event/special-encounter Pokemon.",
        ["whole-asset sheets: art is HGSS pixels (Platinum field-sprite palette/shading must match)", "needs per-species mapping + object OAM budget; no follower logic implied", "34 large sheets are 64x64"],
        ["pilot 3-5 species in one event/cutscene through the existing field-sprite path", "later extension: catalog the 572 sheets as groups"],
        sc(4, 5, 3, 4, 2, 2, 3), "whole_assets",
        {"basis": "donor_checkout_verification", "summary": f"Decoded all {fol['sheets']} sheets and rendered a 28-species sample (normal + shiny).",
         "refs": [E3 + "hgss_follower_sheets.png", E3 + "hgss_follower_sheets.json"]},
        "donor_pixels", ["pose", "animation_frame"], "low", "low", "high"))

    out.append(ref("opp:hgss/land_data_terrain", "HGSS land-data terrain models (676 maps, per-map NSBMD)", "hgss", "hgss", "files/a/0/6/5 (676 land-data blobs: permissions + props + terrain NSBMD + BDHC)", "none (terrain is map-specific)",
        "Terrain geometry of Johto/Kanto maps.", f"Decoded {cen['hgss_land_data']['terrain_models_decoded']} terrain models (median {cen['hgss_land_data']['tris_median']} triangles): flat chunked ground specific to Johto layouts; the value is in the texture/building libraries, not the terrain meshes.",
        ["Johto-specific map layouts", "Platinum map matrices/permissions differ"], ["none planned; reconsider only for relief technique"],
        [E3 + "hgss_3d_census.json"], "land-data decode census (676 maps).",
        [V("pokeheartgold", HGSS, "files/a/0/6/5", "676-file land-data NARC; terrain NSBMD at offset 0x10+perm+props")]))
    return out


def augment_existing(f):
    """Scores/asset_use for explicit findings produced by the earlier migration that remain active (HGSS trainer enhancement)."""
    if f["classification"] == "enhancement_candidate":
        f["scores"], f["asset_use"] = ACE["scores"], ACE["asset_use"]
        f["feasibility"] = 3
    return f
