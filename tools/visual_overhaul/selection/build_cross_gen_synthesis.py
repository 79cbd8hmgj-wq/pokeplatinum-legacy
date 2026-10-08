#!/usr/bin/env python3
"""B7 cross-generation synthesis: DS ranked queue + frozen GBA/GBC pool -> one ranked implementation plan.

Reads (never rewrites): IMPLEMENTATION_QUEUE.json, OPPORTUNITY_POOL.json, opportunities/findings.json (DS), OPPORTUNITY_CLASSES.json,
gba_gbc/GBA_GBC_OPPORTUNITY_POOL.json, gba_gbc/GBA_GBC_NEEDS_EVIDENCE.json.
Writes: CROSS_GEN_OPPORTUNITY_RANKING.json, CROSS_GEN_IMPLEMENTATION_PLAN.md. Planning only; no Platinum source/asset is touched.

Method
* Unit of ranking = an implementation opportunity (IO): one concept on one Platinum host. Every DS queue item (94) and every GBA/GBC
  record (19) is accounted for exactly once (ranked member, corroboration, gated/deferred, or reference_only/reject). Provenance is kept per member.
* Score = canonical 7-weight mean from OPPORTUNITY_CLASSES.json (visual impact 7, novelty 6, feasibility 5, reuse 4, cost 3, risk 2, slice 1;
  cost/risk inverted). Anchor rule: if a reviewed explicit DS finding exists for the concept, its scores are the IO's scores; otherwise the
  strongest mined library (mean of its top-5 records per dimension, no library-size bonus). Corroborating GBA/GBC evidence changes confidence and
  evidence breadth, never the score.
* A mined library whose pool is covered by an explicit reference_only/reject finding is gated out of the ranking unless a later reviewed decision
  (cross-donor slice plan S2/S3) selected a narrower technique use; the nuance is stated on the IO.
"""
from __future__ import annotations

import collections
import json

from common import *  # noqa: F401,F403
import opportunities as opp
import validate_gba_gbc_pool as V

OUT_JSON = SEL / "CROSS_GEN_OPPORTUNITY_RANKING.json"
OUT_MD = SEL / "CROSS_GEN_IMPLEMENTATION_PLAN.md"
BASELINE = "81168942"  # main after PR #76

# ---------------------------------------------------------------- assignment of every DS queue item to an IO / gated cluster
EXPLICIT = {
    "opp:hgss/map_location_preview": "IO-PREVIEW", "opp:hgss/follower_sheet_library": "IO-FOL-SHEETS", "opp:hgss/follower_pokemon": "IO-FOL-MECH",
    "opp:hgss/map_texture_set_library": "IO-TEX-HGSS", "opp:ranger2/effect_primitives": "IO-FX-PRIM", "opp:ranger2/effect_sequencing": "IO-FX-SEQ",
    "opp:pmd_sky/battler_status_indicators": "IO-STATUS", "opp:hgss/field_building_model_library": "IO-MODELS",
    "opp:trainer/tc_ace_trainer_female/enhancement": "IO-TRN-COMP", "opp:trainer/tc_ace_trainer_male/enhancement": "IO-TRN-COMP",
}


def assign(i: dict) -> str:
    if i["kind"] == "explicit":
        return EXPLICIT[i["finding_id"]]
    s, d, c = i["source_id"], i["subsystem"], i["opportunity_class"]
    if s == "hgss":
        if d == "trainer_sprites":
            return {"novel_detail": "GX-TRN-NOVEL", "replacement_candidate": "IO-TRN-REPL"}.get(c, "IO-TRN-COMP")
        if d == "overworld_pokemon":
            return "IO-FOL-SHEETS"
        if d == "npc_player_sprites":
            return "GX-NPC-NOVEL" if c == "novel_detail" else "IO-NPC-COMP"
        if d == "models":
            return "IO-MODELS"
        if d == "textures":
            return "IO-TEX-HGSS"
        if d == "pokemon_sprites":
            return "IO-PKM-REPL" if c == "replacement_candidate" else "IO-PKM-COMP"
        if d == "icons":
            return "GX-ICONS-EXTRA"
        if d == "location_area":
            return "IO-PREVIEW"
    if s == "ranger2":
        if d in ("interface_embellishments", "ui_menus_hud", "backgrounds"):
            return "GX-RANGER-UI"
        if d == "battle_effects":
            return "IO-FX-PRIM" if c == "component_donor" else "IO-FX-SEQ"
        if d == "transitions_presentation":
            return "IO-CARD"
        if d in ("field_graphics", "textures"):
            return "IO-TEX-RANGER"
        if d == "pokemon_animation":
            return "GX-RANGER-POKE"
    if s == "pmd_sky":
        if d == "environmental_effects":
            return "IO-PAL-CYCLE"
        if d == "backgrounds":
            return "GX-PMD-BG-ART"
        if d == "field_effects":
            return "GX-PMD-GROUND"
        if d == "transitions_presentation":
            return "IO-CARD"
    raise KeyError(f"unassigned queue item: {i['rank']} {i['title']}")


# ---------------------------------------------------------------- per-IO plan metadata (hand-authored, evidence-cited)
SPIKE_PAL = "spike: confirm OBJ/BG palette slot-7 write path and fade interaction in src/battle/terrain.c"
SPIKE_CARD = "spike: choose BG layer/VRAM bank for a card while the field is locked (fallback: sub screen)"
SPIKE_OAM = "spike: measure battle OAM/palette headroom (GBA_GBC_NEEDS_EVIDENCE defer:platinum/battle_overlay_oam_palette_headroom)"
SPIKE_OBJ = "spike: prove an overworld OBJ palette pipeline for a donor-style Pokemon sheet (unproven per cross-donor plan)"

IO = {
    "IO-PAL-CYCLE": dict(
        title="Battle terrain palette/tile-cycle service (water platform first)", wave=1, bucket="immediate", slice_ref="S2",
        summary="Data-driven per-terrain palette ramp rotation (table + tick) so static battle platforms gain subtle constant motion; the art is re-indexed Platinum-native, no donor pixels.",
        files=["src/battle/terrain.c", "src/unk_0201567C.c", "res/graphics/battle/terrain", "tools/visual_overhaul/generate_battle_terrain.py"],
        depends_on=[], spikes=[SPIKE_PAL], cost="medium", risk="medium-low", pixel_use="none",
        human_review="animated capture at game speed (day/evening/night), subtle-vs-busy, photosensitivity check",
        rollback="remove the tick call + table; revert the re-authored terrain PNG/PAL",
        nuance="Pool field_environment_art/pmd_sky is also covered by reference_only opp:pmd_sky/environment_and_title_backgrounds; that finding rejects the 2D tilemap art/motifs. Palette/tile animation as a technique was selected separately by the cross-donor slice plan (S2, mining/evidence/pmd_mapbg_bpa.json). Art stays excluded.",
        reuse_later="Distortion World/Giratina arenas, cave and ice terrains, league arenas, title/Hall of Fame 2D layers"),
    "IO-TRN-COMP": dict(
        title="HGSS trainer-sprite component enhancement (Ace Trainer M/F pilot, then component library)", wave=3, bucket="immediate", slice_ref="S1",
        summary="Hand-authored shading/detail on the Platinum Ace Trainer front sprites derived from HGSS components (0 donor pixels), proving a component-transfer + review gate reusable for the 73-record hgss_front library.",
        files=["res/trainers/classes/ace_trainer_male/front.png", "res/trainers/classes/ace_trainer_female/front.png", "tools/visual_overhaul/hgss_trainer_sprite_lib.py", "tools/visual_overhaul/apply_platinum_sprite_pixel_patch.py"],
        depends_on=[], spikes=[], cost="low", risk="low", pixel_use="derived",
        human_review="required: final hand-authored sprites (1x/4x, in-battle, M and F); per-component accept/reject",
        rollback="restore the two front.png files",
        nuance="Explicit reviewed findings (the Ace Trainer pair) anchor the score; the 73-record component library and 15 composite inputs are scope expansion after the gate is proven. Canonical score is low (visual impact 2); it is sequenced first-wave for infrastructure and zero risk, not for impact.",
        reuse_later="other hgss_front component records, hgss_back"),
    "IO-CARD": dict(
        title="Still-scene card presentation (Solaceon News Press front page first)", anchor_source="ranger2", wave=2, bucket="immediate", slice_ref="S3",
        summary="A reusable full-screen still card state (masthead, headline, illustration well, tabs) shown over the field script flow; Ranger 2 event bundles supply composition/state-variant structure only.",
        files=["res/field/scripts/scripts_solaceon_town_pokemon_news_press.s", "src/bg_window.c", "src/field_task.c"],
        depends_on=[], spikes=[SPIKE_CARD], cost="medium-high", risk="medium", pixel_use="none",
        human_review="art direction before engineering; then in-engine screenshots on both screens and text fit for all four articles",
        rollback="revert the 2-line script edit; new commands/resources become inert",
        nuance="Pool title_and_presentation/ranger2 is covered by the broad reference_only opp:ranger2/ui_and_story_backgrounds (no concrete element proposed). The later cross-donor slice plan S3 selected the event-card composition technique specifically; art stays excluded. PMD Sky BACK still cards are absorbed as technique corroboration only (S3 rejected them as an art source).",
        reuse_later="story/flashback cards, Team Galactic news, legend lore, Hall-style recaps, area-preview card (IO-PREVIEW)"),
    "IO-STATUS": dict(
        title="Persistent battler status-glyph overlay (volatile and stat conditions)", wave=2, bucket="immediate", slice_ref=None,
        summary="A small animated glyph anchored to each battler while a condition is active, covering conditions Platinum never shows after the animation ends (confusion, infatuation, taunt-type, stat drops, screens). Redrawn Platinum-native.",
        files=["src/battle/healthbox.c", "src/battle/battle_lib.c", "src/battle/battle_display.c", "src/battle_anim/script_funcs_status.c"],
        depends_on=[], spikes=[SPIKE_OAM], cost="medium", risk="medium", pixel_use="none (redraw)",
        human_review="required: glyph set selection (which conditions), double-battle clutter, in-battle capture",
        rollback="remove the overlay task and glyph sheet; healthbox icon path is untouched",
        nuance="Merged record: the DS PMD Sky status-icon model and the GBA PMD Red trace are the same concept. PMD Red supplies traced mask/slot/timing behaviour and the Platinum comparison; the multi-status cycling rule is a conditional sub-technique (a static side-by-side row may beat it on DS screens). OAM headroom is unmeasured (cost/risk only).",
        reuse_later="any other battler-local transient indicator"),
    "IO-PREVIEW": dict(
        title="Area/location preview card on map entry", wave=3, bucket="immediate", slice_ref="S4",
        summary="A preview card (new Sinnoh artwork + name, time-of-day variants) shown beside the existing map-name popup. HGSS supplies the module structure and layout; FireRed corroborates and adds visit-gated hold, skip, per-area style and a second UI consumer.",
        files=["src/overlay005/map_name_popup.c", "res/graphics/map_popups", "src/map_header.c"],
        depends_on=["IO-CARD (soft: shares the still-card host)"], spikes=[], cost="high", risk="medium", pixel_use="none",
        human_review="required: art direction for 2-3 pilot locations before volume art; popup collision check",
        rollback="disable the entry trigger; popup path is unchanged",
        nuance="One record with multi-donor evidence: HGSS (primary) + FireRed map_location_preview (reference_only, subsumed).",
        reuse_later="all areas; dungeon/region-map consumer (FireRed second-consumer detail)"),
    "IO-FX-PRIM": dict(
        title="Ranger 2 effect primitives as per-move particle shapes", wave=4, bucket="later", slice_ref=None,
        summary="Redraw selected Ranger primitives (fire/tornado/lightning/glow) into Platinum particle resources for specific moves.",
        files=["res/moves", "src/particle_system.c", "res/graphics/battle"],
        depends_on=[], spikes=["design step: choose per-move Platinum targets (none chosen yet)"], cost="medium", risk="medium", pixel_use="derived",
        human_review="required per move", rollback="per-move: restore the move's anim.s/spa", nuance="", reuse_later=""),
    "IO-FOL-SHEETS": dict(
        title="HGSS overworld Pokemon sheet library (non-follower use, pilot subset first)", wave=3, bucket="immediate", slice_ref=None,
        summary="572 species/form overworld sheets usable for event/cutscene/roaming Pokemon presence without a follower mechanic.",
        files=["res/graphics/field_sprites", "src/map_object.c"],
        depends_on=[], spikes=[SPIKE_OBJ], cost="medium", risk="medium", pixel_use="donor_pixels (whole assets)",
        human_review="required: species identity and palette fit per sheet", rollback="remove added object sheets", nuance="Absorbs the four mined follower libraries (species, form, large, legendary).", reuse_later="IO-FOL-MECH"),
    "IO-TEX-HGSS": dict(
        title="HGSS map texture-set regions", wave=4, bucket="later", slice_ref=None,
        summary="Region-level reuse of HGSS NSBTX materials on Platinum map texture sets.",
        files=["res/field/area_data", "res/field/props"],
        depends_on=[], spikes=[], cost="medium", risk="medium", pixel_use="derived",
        human_review="required", rollback="restore area texture sets",
        nuance="Already palette-graded in G4/G7.6; a region transplant is a second, riskier pass over the same assets (cross-donor plan).", reuse_later=""),
    "IO-FX-SEQ": dict(
        title="Ranger 2 multi-phase effect sequencing (launch/impact/embers)", wave=4, bucket="later", slice_ref=None,
        summary="Re-express launch/impact/ember phase structure in anim.s sequencing for selected moves.",
        files=["res/moves"], depends_on=[], spikes=[], cost="low", risk="low", pixel_use="none",
        human_review="per move", rollback="restore the move's anim.s",
        nuance="G5 already applied selective impact staging; low novelty (cross-donor plan).", reuse_later=""),
    "IO-FOL-MECH": dict(
        title="Following-Pokemon overworld mechanic", wave=5, bucket="later", slice_ref=None,
        summary="Overworld follower object using the map-object system plus follower sheets. Highest visual impact, lowest feasibility.",
        files=["src/map_object.c", "src/map_object_move.c", "src/player_avatar.c"],
        depends_on=["IO-FOL-SHEETS"], spikes=[SPIKE_OBJ], cost="high", risk="high", pixel_use="donor_pixels (whole assets)",
        human_review="required", rollback="gate behind a flag; remove follower object spawn",
        nuance="Yellow partner reaction table (reference_only) informs friendship-keyed reaction design; Platinum already has friendship reactions in the Poketch Friendship Checker. It is not a second opportunity.", reuse_later=""),
    "IO-MODELS": dict(
        title="HGSS building/prop model library", wave=5, bucket="later", slice_ref=None,
        summary="340 outdoor + 222 interior props as component donors for Platinum field models.",
        files=["res/field/props", "res/field/area_data"], depends_on=[], spikes=["spike: NSBMD prop authoring pipeline does not exist (G7.6 records this)"],
        cost="high", risk="high", pixel_use="derived", human_review="required", rollback="restore prop models",
        nuance="Absorbs 20 mined model libraries for exterior/interior/prop families.", reuse_later=""),
    "IO-PKM-COMP": dict(
        title="HGSS Pokemon battle-sprite components and composites", wave=5, bucket="later", slice_ref=None,
        summary="Component and composite use of HGSS battle sprites on existing Platinum Pokemon sprites.",
        files=["res/pokemon", "src/pokemon_sprite.c"], depends_on=["IO-TRN-COMP (review gate proven first)"], spikes=[],
        cost="high", risk="medium", pixel_use="derived", human_review="required per sprite", rollback="restore sprite files", nuance="", reuse_later=""),
    "IO-TEX-RANGER": dict(
        title="Ranger 2 field texture/material sets", wave=5, bucket="later", slice_ref=None,
        summary="Ranger 2 field texture and material-animation technique/components (905 ntfp groups remain unscoped).",
        files=["res/field/area_data"], depends_on=[], spikes=["scoping: 905 ntfp groups unscoped"], cost="high", risk="medium", pixel_use="derived",
        human_review="required", rollback="restore area texture sets", nuance="Needs NSBTA/3D material authoring; no pipeline (cross-donor plan).", reuse_later=""),
    "IO-NPC-COMP": dict(
        title="HGSS NPC/player model components and enhancements", wave=5, bucket="later", slice_ref=None,
        summary="Small component/enhancement set on existing Platinum NPC sprites.",
        files=["res/graphics/field_sprites"], depends_on=[], spikes=[], cost="low", risk="low", pixel_use="derived",
        human_review="required", rollback="restore sprite files", nuance="", reuse_later=""),
    "IO-PKM-REPL": dict(
        title="HGSS Pokemon battle-sprite whole replacements (26)", wave=6, bucket="later", slice_ref=None,
        summary="Whole-asset replacements ledgered as preferred; gated by runtime QA.", files=["res/pokemon", "src/pokemon_sprite.c"], depends_on=[],
        spikes=["gate: runtime QA before any replacement import"], cost="medium", risk="medium", pixel_use="donor_pixels (whole assets)",
        human_review="required: runtime QA", rollback="restore sprite files", nuance="Replacement is one outcome among eight, not the primary one.", reuse_later=""),
    "IO-TRN-REPL": dict(
        title="HGSS trainer front-sprite whole replacements (6)", wave=6, bucket="later", slice_ref=None,
        summary="Whole-asset trainer replacements ledgered as preferred; gated by runtime QA.", files=["res/trainers/classes"], depends_on=[],
        spikes=["gate: runtime QA before any replacement import"], cost="low", risk="medium", pixel_use="donor_pixels (whole assets)",
        human_review="required: runtime QA", rollback="restore sprite files", nuance="", reuse_later=""),
}

GATED = {
    "GX-ICONS-EXTRA": ("HGSS 'icon_extra' icons (4 auto-mined records)", "gated_evidence_gap", "no Platinum target or host system is named for these auto-mined records (the taxonomy requires a host_system for novel_detail); identify what the icons are before ranking"),
    "GX-TRN-NOVEL": ("HGSS-only trainer classes with no Platinum counterpart", "gated_reference_only", "opp:hgss/npc_trainer_variety_pool (reference_only: no Platinum target)"),
    "GX-NPC-NOVEL": ("HGSS-only NPC models with no Platinum counterpart", "gated_reference_only", "opp:hgss/npc_trainer_variety_pool (reference_only: no Platinum target)"),
    "GX-RANGER-UI": ("Ranger 2 interface pulses/glows, menu parts and capture backgrounds", "gated_reference_only", "opp:ranger2/ui_and_story_backgrounds (reference_only) and G7 owns Platinum UI; reopening G7 needs an owner decision"),
    "GX-RANGER-POKE": ("Ranger 2 Pokemon animation/frames", "gated_reference_only", "opp:ranger2/pokemon_sprite_frames (reference_only: scale mismatch, Platinum Pokemon presentation)"),
    "GX-PMD-BG-ART": ("PMD Sky 2D map-background art", "gated_reference_only", "opp:pmd_sky/environment_and_title_backgrounds (reference_only: 2D tilemap art does not map to Platinum 3D; colour/motif reference only)"),
    "GX-PMD-GROUND": ("PMD Sky GROUND overlay/object animation", "gated_evidence_gap", "opp:pmd_sky/ground_overlay_sprites (reference_only until WAN decoded; no renderer, no visual evidence)"),
}

# GBA/GBC records that attach to an IO (everything else is reference_only/reject/deferred)
GBA_ATTACH = {
    "opp:pmd_red/battler_status_overlays": ("IO-STATUS", "corroborates_and_strengthens"),
    "opp:pmd_red/battler_status_overlays/multi_status_cycling": ("IO-STATUS", "conditional_sub_technique"),
    "opp:firered/map_location_preview": ("IO-PREVIEW", "corroborates"),
    "opp:firered/animated_palette_sequences": ("IO-PAL-CYCLE", "corroborates_timing_shape_only"),
    "opp:yellow/pikachu_presentation/partner_reaction_table": ("IO-FOL-MECH", "informs_design_only"),
}

DS_SOURCES = {"hgss": "HGSS", "pmd_sky": "PMD Sky", "ranger2": "Ranger 2"}


def level(x: float) -> str:
    return "high" if x >= 3.5 else "medium" if x >= 2.5 else "low"


def main() -> int:
    classes = jload(SEL / "OPPORTUNITY_CLASSES.json")
    W = classes["ranking"]["weights"]
    pool = jload(SEL / "OPPORTUNITY_POOL.json")
    queue = jload(SEL / "IMPLEMENTATION_QUEUE.json")
    findings = {f["finding_id"]: f for f in opp.load_findings()["findings"]}
    gba = jload(V.POOL)
    ne = jload(V.NE)
    errs = V.validate()
    assert not errs, errs

    by_lib = collections.defaultdict(list)
    for r in pool["records"]:
        if r["origin"] == "mined":
            by_lib[f"lib:{r['source_id']}/{r['domain']}/{r['family']}/{r['classification']}/{r['use_mode']}"].append(r)

    def scores_of(item: dict) -> dict:
        if item["kind"] == "explicit":
            s = findings[item["finding_id"]]["scores"]
            return {k: float(s[k]) for k in opp.SCORE_KEYS}
        rs = sorted(by_lib[item["library_id"]], key=lambda r: -r["composite"])[:5]
        return {k: sum(r["dims"][k] for r in rs) / len(rs) for k in opp.SCORE_KEYS}

    def canon(s: dict) -> float:
        tot = sum(W[k] * ((6 - s[k]) if k in opp.INVERTED else s[k]) for k in opp.SCORE_KEYS)
        return round(tot / sum(W.values()), 3)

    groups = collections.defaultdict(list)
    for it in queue["ranked"]:
        it = dict(it)
        it["cluster"] = assign(it)
        it["canonical_score"] = canon(scores_of(it))
        it["scores"] = {k: round(v, 2) for k, v in scores_of(it).items()}
        groups[it["cluster"]].append(it)
    assert sum(len(v) for v in groups.values()) == len(queue["ranked"]) == 94

    # ------------------------------------------------------------ ranked IOs
    ios = []
    for io_id, meta in IO.items():
        members = groups[io_id]
        assert members, io_id
        explicit = [m for m in members if m["kind"] == "explicit"]
        pool_ = [m for m in members if m["source_id"] == meta["anchor_source"]] if meta.get("anchor_source") else members
        explicit = [m for m in pool_ if m["kind"] == "explicit"]
        anchor = max(explicit or pool_, key=lambda m: m["canonical_score"])
        cls = anchor["opportunity_class"]
        if io_id == "IO-TRN-COMP":
            cls = "enhancement_candidate"
        elif io_id == "IO-CARD":
            cls = "novel_capability"
        elif io_id == "IO-PKM-COMP":
            cls = "component_donor"
        donors: dict[str, dict] = {}
        for m in members:
            d = donors.setdefault(m["source_id"], {"source_id": m["source_id"], "generation": "DS", "role": "primary" if m["source_id"] == anchor["source_id"] else "supporting", "items": []})
            d["items"].append({"kind": m["kind"], "id": m.get("finding_id") or m["library_id"], "ds_queue_rank": m["rank"], "ds_queue_score": m["rank_score"], "canonical_score": m["canonical_score"], "records": m["records"]})
        corro = []
        for fid, (target, role) in GBA_ATTACH.items():
            if target == io_id:
                r = next(x for x in gba["records"] if x["finding_id"] == fid)
                corro.append({"id": fid, "generation": "GBA/GBC", "donor": r["donor"]["source_id"], "classification": r["classification"], "role": role,
                              "pinned_commit": r["donor"]["commit"], "affects_score": False})
        s = anchor["scores"]
        ios.append({
            "io_id": io_id, "title": meta["title"], "class": cls, "bucket": meta["bucket"], "wave": meta["wave"], "slice_ref": meta["slice_ref"],
            "canonical_score": anchor["canonical_score"], "scores": s, "score_anchor": {"id": anchor.get("finding_id") or anchor["library_id"], "kind": anchor["kind"], "ds_queue_rank": anchor["rank"]},
            "best_ds_queue_rank": min(m["rank"] for m in members), "ds_queue_items": len(members), "ds_records": sum(m["records"] for m in members),
            "donors": list(donors.values()), "donor_count": len(donors), "corroboration": corro,
            "evidence_donor_count": len(donors | {c["donor"]: 1 for c in corro}),
            "summary": meta["summary"], "platinum_files": meta["files"], "depends_on": meta["depends_on"], "spikes_or_gates": meta["spikes"],
            "cost": meta["cost"], "risk": meta["risk"], "pixel_use": meta["pixel_use"], "human_review": meta["human_review"], "rollback": meta["rollback"],
            "confidence": findings[anchor["finding_id"]]["confidence"] if anchor["kind"] == "explicit" else "medium (mined library, auto-scored; no human review of the score)",
            "score_basis": "reviewed explicit DS finding" if anchor["kind"] == "explicit" else "mined library (top-5 record mean)",
            "reference_only_overlap_note": meta["nuance"], "reuse_later": meta["reuse_later"],
        })
    # rank by canonical score; tie-break: more donors, class tier, best DS rank
    tier = {k: v["tier"] for k, v in classes["classes"].items()}
    ios.sort(key=lambda x: (-x["canonical_score"], -x["evidence_donor_count"], tier[x["class"]], x["best_ds_queue_rank"]))
    for n, x in enumerate(ios, 1):
        x["rank"] = n
    # execution order: wave, then rank
    for n, x in enumerate(sorted(ios, key=lambda x: (x["wave"], x["rank"])), 1):
        x["execution_order"] = n

    # ------------------------------------------------------------ gated / deferred
    gated = []
    for gid, (title, kind, why) in GATED.items():
        ms = groups[gid]
        gated.append({"gate_id": gid, "title": title, "status": kind, "excluded_from_ranking": True, "reason": why,
                      "donors": sorted({m["source_id"] for m in ms}), "ds_queue_items": [{"ds_queue_rank": m["rank"], "id": m.get("finding_id") or m["library_id"], "ds_queue_score": m["rank_score"], "records": m["records"]} for m in ms],
                      "ds_records": sum(m["records"] for m in ms)})
    assert sum(len(g["ds_queue_items"]) for g in gated) + sum(x["ds_queue_items"] for x in ios) == 94

    # ------------------------------------------------------------ reference_only / reject register (donor identity kept; never ranked)
    ref = []
    for r in gba["records"]:
        if r["classification"] in ("reference_only", "reject"):
            ref.append({"id": r["finding_id"], "generation": "GBA/GBC", "donor": r["donor"]["source_id"], "classification": r["classification"], "subject": r["subject"],
                        "merge": r.get("merge"), "why": r["why"]})
    for f in findings.values():
        if f["classification"] in ("reference_only", "reject"):
            ref.append({"id": f["finding_id"], "generation": "DS", "donor": f["donor"].get("source_id"), "classification": f["classification"], "subject": f["subject"], "merge": None, "why": f["why"]})
    ref.sort(key=lambda r: (r["generation"], r["donor"] or "", r["id"]))

    # ------------------------------------------------------------ duplicates / subsumption
    def n_items(gid):
        return len(groups[gid])

    dups = [
        {"id": "D1", "kept": "IO-PREVIEW", "absorbed": ["opp:firered/map_location_preview", "lib hgss_preview (23 areas) -> explicit opp:hgss/map_location_preview"],
         "decision": "One area-preview opportunity. FireRed was already subsumed by the HGSS concept (B2); it stays reference_only and is attached as corroboration (visit-gated hold 120 vs 40 frames, B skips, per-area style, second UI consumer). The mined HGSS preview library is the same 23 areas as the explicit finding."},
        {"id": "D2", "kept": "IO-STATUS", "absorbed": ["opp:pmd_red/battler_status_overlays", "opp:pmd_red/battler_status_overlays/multi_status_cycling"],
         "decision": "PMD Red and PMD Sky are the same concept (battler-local, mask-driven status indicator). One record: the DS finding stays the anchor, PMD Red strengthens it with traced behaviour and the Platinum comparison; the cycling rule is a conditional sub-technique. No duplicate inserted."},
        {"id": "D3", "kept": "IO-PAL-CYCLE", "absorbed": ["opp:firered/animated_palette_sequences", f"{n_items('IO-PAL-CYCLE')} PMD Sky mapbg technique libraries"],
         "decision": "FireRed palette sequences are reference_only (Platinum has native hosts); they only corroborate timing shape for the PMD Sky technique. Six mined libraries become one palette-cycle service."},
        {"id": "D4", "kept": "IO-FOL-SHEETS", "absorbed": [f"{n_items('IO-FOL-SHEETS') - 1} mined overworld_pokemon libraries (species, form, large, legendary)"],
         "decision": "The explicit 572-sheet library finding subsumes the four mined follower-sheet libraries. The follower mechanic stays a separate, dependent opportunity (IO-FOL-MECH)."},
        {"id": "D5", "kept": "IO-FOL-MECH", "absorbed": ["opp:yellow/pikachu_presentation/partner_reaction_table"],
         "decision": "Yellow's happiness x mood reaction table informs reaction design only (reference_only); Platinum already has friendship reactions in the Poketch Friendship Checker."},
        {"id": "D6", "kept": "IO-CARD", "absorbed": [f"{sum(1 for m in groups['IO-CARD'] if m['source_id']=='pmd_sky')} PMD Sky pmd_back_s still-card libraries"],
         "decision": "Same host (field/title transition and event presentation) and same technique; PMD art is excluded (style mismatch, S3), so they corroborate the Ranger-derived composition rather than compete."},
        {"id": "D7", "kept": "IO-TRN-COMP", "absorbed": ["opp:trainer/tc_ace_trainer_{male,female}/enhancement", "uc:trainer_battle_sprites/tc_ace_trainer_*/{01,02}", f"{n_items('IO-TRN-COMP') - 2} hgss_front/hgss_back component and composite libraries"],
         "decision": "One enhancement path: the reviewed Ace Trainer pair is the pilot; library members are scope expansion."},
        {"id": "D8", "kept": "IO-MODELS / IO-TEX-HGSS", "absorbed": [f"{n_items('IO-MODELS')} model items", f"{n_items('IO-TEX-HGSS')} texture-set items"],
         "decision": "Per-family mined libraries collapse into the two explicit library findings; they are not independent implementation units."},
        {"id": "D9", "kept": "(excluded)", "absorbed": ["Emerald field_action_choreography", "Emerald/FireRed environment & interactive-object effects", "Crystal move sequencing and battle transitions", "Yellow starter entrance/exit and transitions"],
         "decision": "Platinum already supersedes these (HM cut-in with Fly path, fldeff.narc families, 31 encounter effects, per-move anim.s). Kept reference_only, excluded from ranking."},
    ]

    # ------------------------------------------------------------ evidence gaps (all non-blocking)
    gaps = [
        {"id": "ne:crystal/angels_motif_vs_platinum", "donor": "crystal", "status": "deferred_non_blocking", "affects": "none ranked", "note": "Closure (B4.5) skipped by project decision. Provisional reference_only; excluded from ranking. If reopened: one five-move key-frame sheet; novel_detail if Platinum lacks a recurring figure."},
        {"id": "defer:ruby/semantic_delta", "donor": "ruby", "status": "skipped_by_project_decision", "affects": "none ranked", "note": "B5 not run. Emerald closed with 0 promoted records, so no ranked item depends on Ruby."},
        {"id": "defer:platinum/battle_overlay_oam_palette_headroom", "donor": "pmd_red", "status": "deferred_non_blocking", "affects": "IO-STATUS cost/risk", "note": "Becomes the first step of the IO-STATUS spike."},
        {"id": "gap:ds/pmd_wan_decoder", "donor": "pmd_sky", "status": "open_non_blocking", "affects": "GX-PMD-GROUND", "note": "No GROUND .wan renderer; the pool stays gated."},
        {"id": "gap:ds/pmd_manpu_effect_bin", "donor": "pmd_sky", "status": "open_non_blocking", "affects": "IO-STATUS (donor art only)", "note": "manpu_*/effect.bin uncataloged; moot because the glyphs are redrawn Platinum-native (PMD Red already shows the art shape)."},
        {"id": "gap:ds/hgss_field_models", "donor": "hgss", "status": "open_non_blocking", "affects": "IO-MODELS, IO-TEX-HGSS", "note": "Largest unexamined DS area: map building models not present as discrete files in the decomp checkout."},
        {"id": "gap:ds/ranger_ntfp_scope", "donor": "ranger2", "status": "open_non_blocking", "affects": "IO-TEX-RANGER", "note": "905 field ntfp groups unscoped."},
        {"id": "gap:ds/ranger_per_move_targets", "donor": "ranger2", "status": "open_non_blocking", "affects": "IO-FX-PRIM", "note": "Per-move Platinum targets not chosen."},
    ]

    first = next(x for x in ios if x["io_id"] == "IO-PAL-CYCLE")
    out = {
        "schema_version": 1, "status": "synthesis_proposal_not_human_approved", "phase": "cross_generation_final_synthesis", "baseline_commit": BASELINE,
        "platinum_assets_modified": False,
        "inputs": {p: file_sha256(SEL / p) for p in ["OPPORTUNITY_CLASSES.json", "IMPLEMENTATION_QUEUE.json", "OPPORTUNITY_POOL.json", "opportunities/findings.json", "gba_gbc/GBA_GBC_OPPORTUNITY_POOL.json", "gba_gbc/GBA_GBC_NEEDS_EVIDENCE.json"]},
        "method": {"weights": W, "inverted": list(opp.INVERTED), "anchor_rule": "reviewed explicit DS finding scores if present, else strongest mined library (mean of top-5 records per dimension, no size bonus)",
                   "corroboration_rule": "GBA/GBC evidence raises confidence/evidence breadth only; it never changes a score",
                   "note": "The DS IMPLEMENTATION_QUEUE.json score is a 10-dimension composite with a library-size bonus; this ranking uses only the 7 canonical weights, so DS queue ranks differ and are kept as ds_queue_rank for traceability."},
        "counts": {
            "ds_queue_items": 94, "gba_gbc_records": len(gba["records"]), "ranked_implementation_opportunities": len(ios),
            "ranked_immediate": sum(1 for x in ios if x["bucket"] == "immediate"), "ranked_later": sum(1 for x in ios if x["bucket"] == "later"),
            "gated_excluded_clusters": len(gated), "gated_excluded_ds_queue_items": sum(len(g["ds_queue_items"]) for g in gated),
            "reference_only_or_reject_findings": len(ref), "gba_gbc_by_class": V.counts(),
            "gba_gbc_new_ranked_opportunities": 0, "gba_gbc_strengthened_ranked_opportunities": len({v[0] for v in GBA_ATTACH.values()}),
            "multi_donor_ranked_opportunities": sum(1 for x in ios if x["evidence_donor_count"] > 1),
        },
        "ranked": ios, "gated_excluded": gated, "reference_only_register": ref, "duplicates_subsumed": dups, "evidence_gaps": gaps,
        "first_slice": {"io_id": first["io_id"], "slice_ref": first["slice_ref"]},
    }
    jdump(OUT_JSON, out)
    write_md(out)
    print(f"ranked IOs: {len(ios)} (immediate {out['counts']['ranked_immediate']}, later {out['counts']['ranked_later']}); gated clusters {len(gated)}; ref/reject {len(ref)}")
    return 0


def write_md(o: dict) -> None:
    import cross_gen_md
    OUT_MD.write_text(cross_gen_md.render(o))


if __name__ == "__main__":
    raise SystemExit(main())
