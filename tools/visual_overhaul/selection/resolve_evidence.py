#!/usr/bin/env python3
"""Evidence closure: turn committed evidence (mining/evidence/*.json + renders) into mining/EVIDENCE_RESOLUTIONS.json.

Deterministic and donor-free: reads only the committed evidence JSON files and CANDIDATE_GROUPS.json. mine_pool.py applies the
resolutions to the existing opportunity records (it updates records, never duplicates them): evidence quality is raised to the measured
level, scores are adjusted from the evidence, and a group that the evidence shows to be weak is closed as reference_only.

  usage: resolve_evidence.py
"""
from __future__ import annotations

from common import *  # noqa: F401,F403

MINING = SEL / "mining"
EVID = MINING / "evidence"
OUT = MINING / "EVIDENCE_RESOLUTIONS.json"
WHO = "claude (evidence closure from decoded donor samples; not human-approved)"
R = "docs/visual_overhaul/selection/mining/evidence/"


def ref(*names):
    for n in names:
        assert (EVID / n).is_file(), n
    return [R + n for n in names]


def fam(source_id, domain, family, verdict, note, refs, **kw):
    return {"source_id": source_id, "domain": domain, "family": family, "verdict": verdict, "note": note, "evidence_refs": refs, "decided_by": WHO, **kw}


def build(groups: dict) -> dict:
    mapbg = jload(EVID / "pmd_mapbg_bpa.json")
    tiled = jload(EVID / "ranger_tiled_bundles.json")["bundles"]
    fams, gres = [], {}

    # ---- A. PMD Sky MAP_BG animated tiles (BPA) + palette animation
    rows = {r["stem"]: r for r in mapbg["rows"]}
    tier_count = {"rich": 0, "moderate": 0, "trivial": 0}
    for gid, g in groups.items():
        if g["source_id"] != "pmd_sky" or not g["unit"].startswith("pmd_mapbg_") or not g["sample_paths"][0].endswith(".bpa"):
            continue
        name = g["unit"][len("pmd_mapbg_"):]
        stem, digit = name[:-1], int(name[-1])
        r = rows.get(stem)
        if r is None:
            continue
        own_frames = r["bpa_frames"][digit - 1] if 1 <= digit <= 8 else 0
        if r["animated_px_pct"] >= 5 or (r["palette_animation"] and own_frames >= 6):
            tier = "rich"
        elif r["animated_px_pct"] >= 0.8 and own_frames >= 3:
            tier = "moderate"
        else:
            tier = "trivial"
        tier_count[tier] += 1
        base = {"measured": {"stem": stem, "own_bpa_frames": own_frames, "composed_frames": r["frames"], "animated_px_pct": r["animated_px_pct"], "palette_animation": r["palette_animation"], "tier": tier}}
        if tier == "rich":
            gres[gid] = {**base, "verdict": "confirm", "dims": {"technique_donor": {"visual_impact": 4, "novelty": 4, "feasibility": 3}},
                         "note": f"decoded with SkyTemple: {r['animated_px_pct']}% of the composed background animates over {own_frames} BPA frames" + (" plus palette animation" if r["palette_animation"] else "") + "; tile/palette animation on a static scene (water, fire, glow, waves, light grade)"}
        elif tier == "moderate":
            gres[gid] = {**base, "verdict": "confirm", "dims": {"technique_donor": {"visual_impact": 3, "novelty": 3, "feasibility": 3}},
                         "note": f"decoded with SkyTemple: {r['animated_px_pct']}% of the background animates over {own_frames} BPA frames; localized ambient motion"}
        else:
            gres[gid] = {**base, "verdict": "reference_only",
                         "note": f"decoded with SkyTemple: only {r['animated_px_pct']}% of the background animates ({own_frames} BPA frames): too little motion to justify a technique record"}
    fams.append(fam("pmd_sky", "environmental_effects", "pmd_mapbg_*", "confirm",
                    "family-level: BPA animated-tile companions decoded for all 72 backgrounds (72/72, 0 errors); per-group tier in group_resolutions. Technique only (2D tile/palette animation re-expressed as Platinum NSBTA/NSBTP or weather-layer motion); no donor pixels.",
                    ref("pmd_mapbg_bpa.json", "pmd_mapbg_bpa_d17p33a.png", "pmd_mapbg_bpa_h01p99d.png", "pmd_mapbg_bpa_v01p07b.png", "pmd_mapbg_bpa_p10p01a.png", "pmd_mapbg_bpa_s01p02a.png", "pmd_mapbg_bpa_t00p02.png", "pmd_mapbg_bpa_g01p01c.png"),
                    evidence_floor=4, match="pmd_mapbg_"))
    fams.append(fam("pmd_sky", "field_effects", "pmd_ground_p", "confirm",
                    "p09p01a1.wan decoded (12 frames, 64x64, 1 animation group): a glowing arch/portal rise-and-pulse. Reusable as an effect-sequencing technique (portal/gateway reveal); no donor pixels.",
                    ref("misc_representatives.png", "misc_representatives.json"), evidence_floor=4, match_group="field_effects_overlays/pmd_sky/pmd_ground_p09p01a1"))

    # ---- B. Ranger 2 tiled bundles (event / ending / title)
    sub_count = {}
    for gid, g in groups.items():
        if g["source_id"] != "ranger2":
            continue
        u = g["unit"]
        if u.startswith("ranger_event") or u.startswith("ranger_ending") or u.startswith("ranger_title"):
            key = g["group_id"].rsplit("/", 1)[-1] + "_LZ.bin"
            b = tiled.get(key)
            if not b or not b.get("screens"):
                continue
            s = b["screens"][0]
            if u.startswith("ranger_event"):
                if s["green_pct"] >= 30:
                    sub = "mission_ui"
                elif s["paper_pct"] >= 8 and s["nonzero_pct"] < 100 or s["paper_pct"] >= 30:
                    sub = "newspaper"
                else:
                    sub = "scene"
            elif u.startswith("ranger_ending"):
                sub = "ending_vignette"
            else:
                sub = "title_layer"
            sub_count[sub] = sub_count.get(sub, 0) + 1
            m = {"subtype": sub, "screens": len(b["screens"]), "nonzero_pct": s["nonzero_pct"], "paper_pct": s["paper_pct"], "green_pct": s["green_pct"]}
            if sub == "newspaper":
                d = {"technique_donor": {"visual_impact": 4, "novelty": 4, "feasibility": 3}, "novel_capability": {"visual_impact": 4, "novelty": 5, "feasibility": 2}}
                note = "rendered: full-screen newspaper/story card (masthead, columns, photo panels): an editorial presentation type Platinum lacks; layout/typography technique only"
            elif sub == "mission_ui":
                d = {"technique_donor": {"visual_impact": 3, "novelty": 3, "feasibility": 3}, "novel_capability": {"visual_impact": 3, "novelty": 3, "feasibility": 2}}
                note = "rendered: mission-board / briefing / map-select screen layout (panels, tabs, list rows): layout and entrance technique reference"
            elif sub == "scene":
                d = {"technique_donor": {"visual_impact": 3, "novelty": 3, "feasibility": 3}, "novel_capability": {"visual_impact": 4, "novelty": 4, "feasibility": 2}}
                note = "rendered: full-screen establishing/panorama still (tower, locale, interior): still-scene presentation type; staging/composition reference, Sinnoh art must be authored"
            elif sub == "ending_vignette":
                d = {"technique_donor": {"visual_impact": 3, "novelty": 3, "feasibility": 3}, "novel_capability": {"visual_impact": 3, "novelty": 4, "feasibility": 2}}
                note = "rendered: letterboxed ending vignette (cast gathered in a locale): credits/epilogue still composition reference"
            else:
                d = {"technique_donor": {"visual_impact": 4, "novelty": 3, "feasibility": 3}, "novel_capability": {"visual_impact": 3, "novelty": 3, "feasibility": 3}}
                note = "rendered: separable title BG layer (sky/cloud/mountain/moon bands, publisher splash): layered title parallax and day/night staging technique"
            gres[gid] = {"verdict": "confirm", "dims": d, "note": note, "measured": m}
            if u.startswith("ranger_title"):
                gres[gid]["techniques"] = ["event_presentation", "layered_backgrounds"]
    fams.append(fam("ranger2", "transitions_presentation", "ranger_event/event", "confirm",
                    "family-level: all 76 event bundles render with the minimal NCGR+NCLR+NSCR preview (Ranger tilemap path); sub-typed by measured paper/green coverage (newspaper cards, mission UI, scenes).",
                    ref("ranger_tiled_event.png", "ranger_tiled_bundles.json"), evidence_floor=4, techniques=["event_presentation", "screen_composition"]))
    fams.append(fam("ranger2", "transitions_presentation", "ranger_ending/edu", "confirm",
                    "family-level: all 31 ending bundles render as letterboxed vignette stills.", ref("ranger_tiled_ending.png", "ranger_tiled_bundles.json"), evidence_floor=4, techniques=["event_presentation", "screen_composition"]))
    fams.append(fam("ranger2", "transitions_presentation", "ranger_title/title", "confirm",
                    "family-level: title bundles render as separable layer bands (sky, clouds, mountains, moon, splashes).", ref("ranger_tiled_title.png", "ranger_tiled_bundles.json"), evidence_floor=4))
    fams.append(fam("ranger2", "ui_menus_hud", "ranger_menu/um", "confirm",
                    "family-level: 37 menu tilemap bundles render (frames, banners, list rows, panels, mission board); 432-member library with cell sets and 158 full-screen bitmaps still undecoded. Component library for window/panel construction ideas, not a drop-in.",
                    ref("ranger_tiled_menu.png", "ranger_tiled_bundles.json"), evidence_floor=4,
                    dims={"component_donor": {"visual_impact": 3, "novelty": 3, "feasibility": 3}}))
    # Ranger interface: i024/i059 are tiny bitmap/tilemap frames; i072_* are 3D effect textures
    for gid, g in groups.items():
        if g["source_id"] == "ranger2" and g["unit"].startswith("ranger_interface"):
            if g["unit"].endswith(("i024", "i059")):
                gres[gid] = {"verdict": "reference_only", "note": "decoded: i024 is a palette + raster bitmap strip and i059 a 1-screen tilemap frame: no animated interface primitive (unlike the NCER/NANR interface families)"}
            else:
                gres[gid] = {"verdict": "confirm", "dims": {"novel_detail": {"visual_impact": 3, "novelty": 3, "feasibility": 3}},
                             "note": "decoded A3I5/A5I3 3D texture (light beam / glow burst / streak): reusable effect texture primitive"}
    fams.append(fam("ranger2", "interface_embellishments", "ranger_interface/i", "confirm",
                    "family-level: i072_00/01/02 decode as effect textures (32x32 beam, 16x16 glow, 8x16 streak); i024/i059 close as reference.", ref("misc_representatives.png", "misc_representatives.json"), evidence_floor=4))

    # ---- B2. Ranger Pokemon pose sets
    poke = jload(EVID / "ranger_poke_sets.json")
    for suffix, verdict, note, d in (
            ("w", "reference_only", "rendered 295 walk-cycle sets (4-91 cells, ~40px field-scale); coherent but superseded by the HGSS follower sheets (572 sheets, 32x32 4bpp, Platinum field-sprite contract) as the overworld-Pokemon donor", None),
            ("a", "confirm", "rendered 596 attack/ability sets (3-157 cells): multi-pose body animation with attached effect props (e.g. pendulum swing); choreography technique for multi-pose Pokemon presentation, no donor pixels", {"technique_donor": {"visual_impact": 3, "novelty": 3, "feasibility": 2}}),
            ("s", "reference_only", "rendered 296 sets: pose semantics unverified and overlapping with the walk/attack sets; no distinct technique", None),
            ("t", "reference_only", "rendered 272 sets: pose semantics unverified (aura/effect states) and overlapping with the attack sets; no distinct technique", None)):
        kw = {"dims": d} if d else {}
        fams.append(fam("ranger2", "pokemon_animation", f"ranger_poke_{suffix}", verdict, note, ref("ranger_poke_sets.png", "ranger_poke_sets.json"), evidence_floor=4, **kw))

    # ---- C/D. HGSS tails
    for n in (22, 54, 69, 70):
        gid = f"field_npc_player_sprites/hgss/hgss_mmodel_{n:08d}"
        if gid in groups:
            gres[gid] = {"verdict": "confirm", "note": "decoded NSBTX: unique NPC character sheet with 4-direction walk frames (16-32 32x32 frames, 1 palette): NPC variety component", "evidence_refs": ref("misc_representatives.png")}
    for gid in ("pokemon_battle_sprites/hgss/form_egg", "pokemon_battle_sprites/hgss/form_shadow"):
        if gid in groups:
            gres[gid] = {"verdict": "reference_only", "note": "viewed: tiny egg / faint shadow sprite on the 160x80 sheet; Platinum already carries both and nothing here adds detail", "evidence_refs": ref("misc_representatives.png")}
    scope = jload(MINING / "EVIDENCE_CLOSURE_SCOPE.json")
    gres = {k: v for k, v in gres.items() if k in set(scope["group_ids"])}
    sub_count = {}
    for v in gres.values():
        st = (v.get("measured") or {}).get("subtype")
        if st:
            sub_count[st] = sub_count.get(st, 0) + 1
    return {"schema_version": 1, "decided_by": WHO, "scope_groups": scope["group_ids"], "scope_sha256": file_sha256(MINING / "EVIDENCE_CLOSURE_SCOPE.json"), "family_resolutions": fams, "group_resolutions": dict(sorted(gres.items())),
            "tier_counts": {"pmd_bpa": tier_count, "ranger_event_subtypes": dict(sorted(sub_count.items()))},
            "inputs": {n: file_sha256(EVID / n) for n in ("pmd_mapbg_bpa.json", "ranger_tiled_bundles.json", "ranger_poke_sets.json", "misc_representatives.json")}}


def main() -> int:
    groups = {g["group_id"]: g for g in jload(GROUPS_JSON)["groups"]}
    doc = build(groups)
    jdump(OUT, doc)
    print(f"resolutions: {len(doc['family_resolutions'])} family, {len(doc['group_resolutions'])} group; {doc['tier_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
