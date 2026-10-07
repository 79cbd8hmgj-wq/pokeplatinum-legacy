#!/usr/bin/env python3
"""One-shot, deterministic migration of already-produced donor findings into opportunities/findings.json.

Uses only existing repo evidence. Findings whose evidence artifacts are not in this repo are written with
evidence.basis = prior_session_unrecorded (capped low confidence / feasibility 1, flagged needs_donor_verification);
nothing about those donors beyond what was already reported is invented. Re-running overwrites the file.
"""
from __future__ import annotations

from common import *  # noqa: F401,F403
import opportunities as opp
import outcomes

U = "prior_session_unrecorded"
WHO = "claude (migration of prior findings; not human-approved)"
UNREC = "Finding reported in an earlier session; its evidence artifacts are not committed here and the donor game is not a cataloged source. Treat as a lead until re-verified against the donor checkout."


def F(fid, subject, cl, donor, target, useful, why, constraints, adaptation, cost, risk, conf, feas, evidence, pixel_use, tags, **kw):
    return {"finding_id": fid, "subject": subject, "classification": cl, "status": "proposed", "donor": donor, "target": target, "useful": useful, "why": why,
            "constraints": constraints, "adaptation": adaptation, "cost": cost, "risk": risk, "confidence": conf, "feasibility": feas, "evidence": evidence,
            "pixel_use": pixel_use, "tags": tags, "proposed_by": WHO, **kw}


def unrec(summary, refs=()):
    return {"basis": U, "summary": f"{summary} {UNREC}", "refs": list(refs)}


from ds_findings import augment_existing, ds_findings  # noqa: E402


def main() -> int:
    groups = {g["group_id"]: g for g in jload(GROUPS_JSON)["groups"]}
    ev = {p.stem: jload(p) for p in (SEL / "evidence").glob("*.json")}
    out = []

    out.append(F("opp:firered/map_location_preview", "Area/location preview card (novel Sinnoh artwork)", "novel_capability",
        {"game": "firered (design reference, not cataloged) + hgss (cataloged area previews)", "source_id": "hgss", "cataloged": True,
         "group_ids": sorted(g for g in groups if g.startswith("field_environment_art/hgss/hgss_preview_")),
         "locator": "HGSS fielddata/graphic/preview_graphic (23 area groups, 76 time-of-day variants); FireRed map/location preview behaviour is the design reference (unrecorded)"},
        {"kind": "none", "host_system": "new area-preview screen shown on map entry, beside the existing map-name popup",
         "refs": ["res/graphics/map_popups", "src/map_header.c"]},
        "A location preview card (artwork + name) shown on entering an area; Platinum currently exposes only 136x48 name signs.",
        "Committed evidence shows Platinum has no area-preview screen (native_relation missing_in_native) while the HGSS previews prove the layout and time-of-day variant structure on the DS. Adds area identity and presentation Platinum lacks.",
        ["no Platinum area-preview code or resources exist (new UI state + art required)", "HGSS preview art depicts Johto/Kanto: use only as layout/composition reference; Sinnoh artwork must be newly authored", "256x192 DS background budget and Platinum palette/VRAM bank limits"],
        ["author Sinnoh-specific preview art per location tier (start with a vertical slice of 2-3 locations)", "implement the card as a Platinum-native BG/OAM layer triggered from the existing map-header popup path", "decide time-of-day variants after the slice"],
        "high", "medium", "medium", 2,
        {"basis": "catalog_evidence", "summary": "ledger field_environment_art: 23 HGSS preview groups are reference_only/no_native_target (missing_in_native); composed previews in review/environment_previews. FireRed-specific provenance is not recorded.",
         "refs": ["docs/visual_overhaul/selection/ledgers/field_environment_art.json", "docs/visual_overhaul/selection/evidence/field_environment_art.json", "docs/visual_overhaul/selection/review/environment_previews/previews_contact_sheet.png", "docs/visual_overhaul/selection/SELECTION_CHECKPOINT.md"],
         "bound_digest": opp.bound_digest(sorted(g for g in groups if g.startswith("field_environment_art/hgss/hgss_preview_")), groups, ev)},
        "none", ["UI_element", "layout", "environmental_motif"]))

    out.append(F("opp:firered/interactive_object_states", "Interactive-object visual states", "novel_detail",
        {"game": "firered", "source_id": "firered", "cataloged": False, "locator": "FireRed interactive overworld objects (state sprites); exact assets not recorded"},
        {"kind": "none", "host_system": "overworld interactive objects (extra visual states, no new object type)", "refs": ["src/map_object.c"]},
        "Distinct visual states for interactive objects (e.g. before/after interaction) as presentation feedback.",
        "Adds feedback about object state without replacing any object system.",
        ["Platinum map objects use fixed OAM sprite sheets; extra states cost sprite resources", "must not change object logic or script flags"],
        ["map each reported state to an existing/added Platinum object frame", "author Sinnoh-styled frames; donor used as state-design reference"],
        "medium", "medium", "low", 1, unrec("Interactive-object visual states."), "derived", ["animation_frame", "UI_element"], needs_donor_verification=True))

    out.append(F("opp:pmd_red/battler_status_overlays", "Temporary status indicators above battlers", "novel_detail",
        {"game": "pmd_red (not cataloged)", "source_id": "pmd_red", "cataloged": False, "locator": "PMD Red status overlay indicators above Pokemon; exact assets not recorded"},
        {"kind": "none", "host_system": "battle: temporary indicator layer above battler sprites (alongside the healthbox status icon)", "refs": ["src/battle/healthbox.c"]},
        "Short-lived status indicators above battlers (PMD-style) that show status application/clearing at the battler.",
        "Adds at-a-glance status feedback on the battler itself; Platinum shows status only in the healthbox.",
        ["DS OAM/sprite budget during battle", "must not collide with healthbox, HP bar or move animations", "indicator art must read at 2x DS battle scale"],
        ["implement as a Platinum-native OAM layer driven by status-change battle events", "redraw indicators in Platinum palette; PMD used as concept/timing reference"],
        "medium", "medium", "low", 1,
        unrec("PMD Red status overlays. A path search of the cataloged pmd_sky assets for 'status'/'condition' found 0 assets (DONOR_ASSET_CATALOG.json), so no in-repo donor asset supports this yet.", ["docs/visual_overhaul/DONOR_ASSET_CATALOG.json"]),
        "derived", ["UI_element", "animation_frame"], needs_donor_verification=True))

    out.append(F("opp:emerald/field_action_choreography", "Field-action choreography", "technique_donor",
        {"game": "emerald (not cataloged)", "source_id": "emerald", "cataloged": False, "locator": "Emerald field-action (field move) sequences: timing/ordering of player, object and effect steps; exact files not recorded"},
        {"kind": "system", "subsystem": "field_effects_overlays", "system": "field move task sequences", "refs": ["src/field_move_tasks.c"]},
        "Step ordering and timing of field-action sequences (player pose, effect, object reaction, release).",
        "Technique only; re-implemented natively in Platinum field tasks. Precedent: G5 applied the Emerald battle-layer separation natively via Func_ShakeBg without donor assets.",
        ["Platinum field task/state-machine structure differs from the GBA task model", "must preserve script/flag behaviour of the field moves"],
        ["re-express timings as Platinum field task states", "no donor assets or code imported"],
        "medium", "low", "low", 1,
        unrec("Emerald field-action choreography.", ["docs/visual_overhaul/G5_DONOR_TECHNIQUE_AUDIT.md"]), "none", ["animation_timing"], needs_donor_verification=True))

    out.append(F("opp:firered/animated_palette_sequences", "Animated environmental palette sequences", "technique_donor",
        {"game": "firered (not cataloged)", "source_id": "firered", "cataloged": False, "locator": "FireRed animated environment palette cycling/sequencing; exact tables not recorded"},
        {"kind": "system", "subsystem": "field_environment_art", "system": "environment palette/lighting animation", "refs": ["docs/visual_overhaul/G7_6_OVERWORLD_ATMOSPHERE.md", "src/field_overworld_weather.c"]},
        "Palette sequencing (cycle timing/order) that animates water, foliage, lights without new tiles.",
        "Technique only, built on Platinum's existing palette/atmosphere pipeline; cheap animation gain without new art.",
        ["Platinum 3D map textures use NSBTP/palette resources, not GBA palette-cycle tables", "must coexist with the G7.6 atmosphere/lighting system"],
        ["re-express cycles as Platinum palette animation resources/tasks", "no donor pixels; sequence design only"],
        "medium", "medium", "low", 1, unrec("FireRed animated environmental palette sequences.", ["docs/visual_overhaul/G7_6_OVERWORLD_ATMOSPHERE.md"]), "none", ["palette", "animation_timing", "environmental_motif"], needs_donor_verification=True))

    out.append(F("opp:emerald/environment_effect_primitives", "Environmental effect primitives", "component_donor",
        {"game": "emerald (not cataloged)", "source_id": "emerald", "cataloged": False, "locator": "Emerald field/environment effect primitives (particle shapes/frames); exact assets not recorded"},
        {"kind": "system", "subsystem": "field_effects_overlays", "system": "field overlay/effect primitives", "refs": ["src/field_overworld_weather.c", "src/overworld_anim_manager.c"]},
        "Small reusable effect primitives (particle shapes, short frame sets) for environmental effects.",
        "Primitive shapes can be redrawn in Platinum palette for field overlays without importing a whole effect.",
        ["GBA 4bpp tiles must be redrawn/converted for DS formats", "primitives must match Platinum field overlay scale and palette budget"],
        ["redraw primitives against the Platinum palette (derived pixel use)", "assemble through Platinum effect/overlay systems"],
        "medium", "medium", "low", 1, unrec("Emerald environmental effect primitives."), "derived", ["particle_shape", "animation_frame", "environmental_motif"], needs_donor_verification=True))

    out.append(F("opp:crystal/battle_anim_artwork", "Unusual battle-animation artwork", "component_donor",
        {"game": "crystal (not cataloged)", "source_id": "crystal", "cataloged": False, "locator": "Crystal battle animation art distinct from later games; exact assets not recorded"},
        {"kind": "system", "subsystem": "battle_effects_particles", "system": "battle move particle resources", "refs": ["res/graphics/battle/particles"]},
        "Distinctive effect artwork pieces from Crystal move animations usable as component shapes.",
        "Selective historical effect shapes can add identity to specific moves where the Platinum art is generic.",
        ["GBC 2bpp/1-bit art needs redraw for DS particle formats", "per-move use only; no wholesale replacement"],
        ["redraw selected shapes into Platinum particle resources", "tie each shape to one move script"],
        "medium", "medium", "low", 1, unrec("Crystal unusual battle-animation artwork."), "derived", ["particle_shape", "animation_frame"], needs_donor_verification=True))

    out.append(F("opp:crystal/battle_anim_choreography", "Unusual battle-animation choreography", "technique_donor",
        {"game": "crystal (not cataloged)", "source_id": "crystal", "cataloged": False, "locator": "Crystal battle animation sequencing for unusual moves; exact scripts not recorded"},
        {"kind": "system", "subsystem": "battle_effects_particles", "system": "battle move animation scripts", "refs": ["res/moves/brave_bird/anim.s"]},
        "Sequencing/timing of unusual move animations expressed through Platinum anim scripts.",
        "Technique only via Platinum's native script/particle system; same approach already used for G5 staging.",
        ["Platinum move scripts (res/moves/*/anim.s) are the only implementation path", "must keep existing particle resources"],
        ["translate sequencing to anim.s commands; no donor assets"],
        "low", "low", "low", 1, unrec("Crystal unusual battle-animation choreography.", ["docs/visual_overhaul/G5_DONOR_TECHNIQUE_AUDIT.md"]), "none", ["animation_timing"], needs_donor_verification=True))

    out.append(F("opp:yellow/pikachu_presentation", "Pikachu-specific presentation assets", "component_donor",
        {"game": "yellow (not cataloged)", "source_id": "yellow", "cataloged": False, "locator": "Yellow Pikachu-specific animation/presentation resources (named in PASS_G_VISUAL_OVERHAUL.md and CROSS_GAME_DONOR_MATRIX.md)"},
        {"kind": "system", "subsystem": "pokemon_battle_sprites", "system": "Pikachu presentation", "refs": ["res/pokemon/pikachu"]},
        "Pikachu-specific animation frames/expressions as components for Pikachu presentation.",
        "Documented as available donor material; matrix rates it low priority/ideas-only, so it is a component lead rather than a replacement.",
        ["GB-era art must be redrawn; Platinum Pikachu sprite contract unchanged", "specific usable frames are not enumerated in the repo"],
        ["enumerate candidate frames from the Yellow checkout, then redraw selected frames as derived art"],
        "medium", "medium", "low", 1,
        {"basis": U, "summary": "Yellow's Pikachu-specific animation resources are named in repo docs but no specific assets/frames are recorded. " + UNREC, "refs": ["docs/visual_overhaul/PASS_G_VISUAL_OVERHAUL.md", "docs/visual_overhaul/CROSS_GAME_DONOR_MATRIX.md"]},
        "derived", ["animation_frame", "pose"], needs_donor_verification=True))

    # trainer enhancement aggregates over the existing proposed component_donor records
    use = outcomes.load_use_files().get("trainer_battle_sprites", {})
    for tid in ("tc_ace_trainer_male", "tc_ace_trainer_female"):
        recs = [r for r in use["records"] if r["target"]["target_id"] == f"trainer_battle_sprites/{tid}" and r["outcome"] == "component_donor"]
        gids = sorted({r["source"]["group_id"] for r in recs})
        nr = recs[0]["target"]["native_ref"]
        out.append(F(f"opp:trainer/{tid}/enhancement", f"{tid.replace('tc_', '').replace('_', ' ')}: Platinum sprite enhanced with HGSS shading/detail", "enhancement_candidate",
            {"game": "hgss", "source_id": "hgss", "cataloged": True, "group_ids": gids, "locator": "HGSS trainer front sets (catalog_extensions/hgss_trainer_sprites)"},
            {"kind": "asset", "subsystem": "trainer_battle_sprites", "target_id": f"trainer_battle_sprites/{tid}", "native_ref": nr, "refs": [nr["path"]]},
            "Jacket fold/zip shading, gloves, hair highlight banding and collar/seam detail from the HGSS sprite, painted onto the Platinum silhouette.",
            "Whole HGSS asset stays keep_platinum (owner verdict) but the components add depth while preserving Sinnoh identity.",
            sorted({c for r in recs for c in r["constraints"]}), sorted({a for r in recs for a in r["adaptation"]}),
            "medium", "medium", "medium", 2,
            {"basis": "catalog_evidence", "summary": "Aggregates the proposed component_donor records; render comparison images committed.", "refs": sorted({p for r in recs for p in r["evidence"]["refs"]}),
             "bound_digest": opp.bound_digest(gids, groups, ev)},
            "derived", sorted({t for r in recs for t in r["tags"]}), links={"use_records": sorted(r["record_id"] for r in recs)}))

    scope = jload(SEL / "PHASE_SCOPE.json")
    deferred = [f for f in out if f["donor"]["source_id"] not in scope["ds_sources"] or opp.names_deferred_game(f, scope)]
    active = [f for f in out if f not in deferred]
    for f in deferred:
        f["phase"] = "deferred_gba_gbc"
    jdump(opp.DEFERRED_JSON, {"schema_version": 1, "phase": "deferred_gba_gbc", "description": "GBA/GBC donor findings preserved verbatim for the next phase. NOT loaded by the register, queue or ranking. Do not edit to make them active; re-derive with DS or GBA/GBC checkouts when that phase starts.",
                              "superseded_by": {"opp:firered/map_location_preview": "opp:hgss/map_location_preview"}, "findings": sorted(deferred, key=lambda f: f["finding_id"])})
    active = [augment_existing(f) for f in active]
    active += ds_findings(groups, ev)
    jdump(opp.FINDINGS_JSON, {"schema_version": 2, "description": "Active (DS-only) opportunity findings; see PHASE_SCOPE.json and OPPORTUNITY_CLASSES.json. Replacement/reject-by-review findings are derived from ledgers/component reviews, not written here.", "findings": active})
    print(f"wrote {len(active)} active, {len(deferred)} deferred findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
