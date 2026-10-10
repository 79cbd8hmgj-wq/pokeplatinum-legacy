# B1 — Ranger 2 battle-effect vertical slice (source-grounded)

**State:** candidate mapping and reusable in-ROM sequencing; donor graphic import still pending. Do not call this a finished asset transplant.

## Verified source evidence

`docs/visual_overhaul/selection/opportunities/evidence/README.md` identifies the targeted contact-sheet `ranger2_effect_ui_sample.png`, rendered from `pokeranger2` @ `55b4e0cd` using `tools/visual_overhaul/render_ranger_pokemon_package.py`. Sampled resources: `effect/e000,e010,e030,e060,e100,e150`, `interface/i000,i005,i010,i020`, `target/t001_00,t010_00`. The evidence documents shaded multi-stage Nitro NCGR/NCLR/NCER/NANR visual assets (fireball launch/impact/embers, tornado, lightning, glow rings). **The source does not establish a one-to-one mapping from each sampled package to each listed visual element.** Check the individual render frames before selection.

The queue already ranks Ranger's `ranger_effect/e` technique donor as #6 and component donor as #7 for battle move scripts/particle resources. The donor database must remain authoritative.

## First targets and integration requirements

| Platinum host | Donor visual goal | Current implemented fallback | Needed installed source |
| --- | --- | --- | --- |
| `res/moves/flamethrower/anim.s` | charge / flame stream / ember trail / bloom | native extra defender-anchored pulse | curated e-series NCGR/NCLR/NCER/NANR extracted and repackaged for compatible sprite/particle renderer |
| `res/moves/thunderbolt/anim.s` | branching lightning / graded impact glow | native extra defender-anchored arc | separately verified Ranger arc frames, safe animation assembly |
| `res/moves/shadow_ball/anim.s` | opalescent rim on spectral charge, staged finish | native second spectral pulse | original Opal composite with Ranger glow candidate; preserve Ghost-purple attack identity |
| `res/moves/ice_beam/anim.s` | crystalline beam / sparkling freeze dispersion | native second impact | ranked donor format-compatible sprites or newly authored Opal texture |
| Battle HUD | separate status/selection motion, restrained mineral-violet/pearl/gold | existing G7/AV1 interfaces | palette-owner verified sprite sheets and NANR, not contact-sheet PNG |

## Implementation gates, not runtime blockers

1. Resolve candidate `asset_id` and curation overlay status to exact original Ranger path. Reject unresolved `decode_issue` entries.
2. Extract a specific package's **actual** NCGR/NCLR/NCER/NANR members; verify frame dimensions, color depth, palette count and animation sequences. No cropped contact sheet as game art.
3. Compare compatible rendering routes: (a) existing battle OAM sprite manager, (b) import to SPL `.spa` only if binary authoring tool is proven, (c) original Opal redraw into native resources. Every selection requires a live animation-script reference and resource manifest.
4. Install one staged visual slice and build both revisions; then expand. User owns runtime QA after implementation.
5. Never overwrite an existing AV1 donor-enhanced animation unconditionally or introduce battle mechanic edits.

## Source status and honesty

The added B1 impact pulses are source-level functioning effects, not donor artwork. This document records concrete integration targets and source requirements rather than presenting contact sheets as shipped sprites.
