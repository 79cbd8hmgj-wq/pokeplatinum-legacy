# Pokémon Opal — B2–B8 preimplementation design contract

**Purpose:** pre-resolve design, asset sourcing, sequencing, and validation decisions so Claude Code can spend tokens on source implementation. **Status:** design/handoff, **not** a claim that B2–B8 are implemented. Continue within PR #110. Do not touch PR #109 or change battle mechanics. Owner performs runtime acceptance later.

## Verified donor integration baseline

The B1 donor pipeline is operational. Use the verified paths and provenance; do not redo the donor catalog or invent sprite IDs.

| Installed graphic | Source | Frames | OBJ tiles | Colors | Provenance |
|---|---|---:|---:|---:|---|
| `ranger_fire_bloom` | Ranger 2 `effect/e010_LZ.bin`, `e010_a01` cells | 8 | 236 | 7 | `b1_installed_donors/ranger_fire_bloom.provenance.json` |
| `ranger_ice_bloom` | Ranger 2 `effect/e009_LZ.bin`, `e009_a01` cells | 8 | 236 | 7 | `b1_installed_donors/ranger_ice_bloom.provenance.json` |
| `ranger_rock_burst` | Ranger 2 `effect/e002_LZ.bin`, `e002_a01` cells | 9 | 219 | 6 | `b1_installed_donors/ranger_rock_burst.provenance.json` |

Installed resource roots: `res/graphics/battle/moves/`; corresponding recipes: `tools/visual_overhaul/b1_recipes/`. Existing converter sequence: `export_b1_ranger_effect_cells.py` -> `build_b1_donor_battle_sprite.py` -> `install_b1_donor_battle_sprite.py` -> native Nitro resource pipeline. Source render function `SPRITE_FUNC_OFFSET_AND_ANIMATE`. **Existing B1 per-sprite limit:** at most 256 OBJ tiles and 15 opaque colors; this is *not* proof of total battle OAM/VRAM headroom.

Authoritative databases: `DONOR_ASSET_CATALOG.json` (64,841 catalog records), recovered `DONOR_CURATION_HANDOFF.md`, ranked `selection/IMPLEMENTATION_QUEUE.json`, `selection/OPPORTUNITY_POOL.json`. Creative modes from `POKEMON_OPAL_ASSET_DIRECTION.md`: preserve, replace, enhance, composite, animate, create, discard. Consult only relevant records. Do not recatalog the entire donor pool.

## B2 — Donor effect selection gates

The following **ten slots are design targets, not verified graphics**. Resolve exact catalog IDs, source packages, decoded cells/frames, hashes, palettes, conversion cost, and target before integration. Do not treat a filename or ranking as visual validation.

| Slot | Preferred source search | Example moves / reuse family |
|---|---|---|
| Electrical arcs/glow | Ranger 2, PMD Sky, HGSS | Thunderbolt, Discharge, Charge Beam |
| Spectral smoke/rings | Ranger 2, PMD Sky | Shadow Ball, Dark Pulse |
| Water crest/spray | Ranger 2, PMD Sky, HGSS | Surf, Hydro Pump, Water Pulse |
| Wind trails | Ranger 2, PMD Sky | Gust, Air Slash |
| Leaves/petals | Ranger 2, PMD Sky, HGSS | Leaf Storm, Razor Leaf |
| Metallic shards/specular | Ranger 2, HGSS | Flash Cannon, Iron Tail |
| Fighting impact streaks | Ranger 2, HGSS | Close Combat, Brick Break |
| Dragon energy wave | Ranger 2, PMD Sky | Dragon Pulse, Dragon Claw |
| Psychic aura/distortion | PMD Sky, Ranger 2 | Psychic, Psybeam |
| Weather ambience | HGSS, Ranger 2, PMD Sky | Rain Dance, Hail, Sunny Day |

First integration examples: **Thunderbolt** (charge/lighting/electric arcs), **Shadow Ball** (spectral travel/impact/afterglow), **Surf** (large-area layer/multiple targets). Use the established B1 import path unless the visual requires extending it. Preserve both elemental colors and Opal's pearl/mineral-violet/gold UI identity.

## Reusable cinematic archetypes (design templates, not completed implementations)

1. **Projectile:** Shadow Ball / Energy Ball / Water Pulse — charge -> travel -> impact -> decay.
2. **Beam:** Thunderbolt / Ice Beam / Flash Cannon — windup -> release -> sustained effect -> restore.
3. **Explosion:** Fire Blast / Sludge Bomb — warning -> burst -> fragment echo -> settle.
4. **Area surge:** Surf / Blizzard / Earthquake — environmental cue -> surge -> multi-target hit visual -> restore.
5. **Melee:** Close Combat / Iron Tail — attack anticipation -> contact -> recoil -> reset.
6. **Multihit:** Rock Blast / Bullet Seed — anticipation -> repeat hit -> accent final hit -> restore.
7. **Weather:** Rain Dance / Sunny Day / Hail — transition -> ambient effect -> handoff to existing weather -> cleanup.
8. **Status:** Will-O-Wisp / Thunder Wave — tell -> visual application -> signature accent -> restore.
9. **Psychic/distortion:** Psychic / Dark Pulse — concentration -> distortion -> defender reaction -> restore.
10. **Ground:** Earth Power / Stone Edge — ground cue -> eruption -> debris -> settle.
11. **Natural force:** Razor Leaf / Leaf Storm — flourish -> launch -> impact -> decay.
12. **Entry:** Legendary/boss introductions — anticipation -> reveal -> unique accent -> enter battle.

**Timing design (not measured DS performance):** prioritize responsive normal moves; allow more elaborate powerful moves. Use concrete frames only after adapting existing animation command/task timing. Avoid adding cinematic wait time to gameplay mechanics.

## B3–B8 source implementation contracts

| Phase | Actual implementation required | Acceptance gate |
|---|---|---|
| B3 camera | Reusable safe BG scroll, framing/zoom simulation or battler offset/shake; restoration in singles, doubles and cancel paths | no HUD/hitbox displacement or stale offsets |
| B4 atmosphere | Elemental fades, pulses, weather lighting that respect existing terrain and palette tasks | balanced fades/restore and no G7/S2-D palette takeover |
| B5 reactions | Visual anticipation, recoil, recovery, faint embellishment only after game decision | no battle outcome/damage/status/faint logic changes |
| B6 sequencing | Reusable charge/release/impact/aftermath beats, consistent SFX/particle/sprite teardown | no leaked sprite manager or pending tasks |
| B7 encounters | Legendary and major encounter visual intros at already-existing intro hooks | original story/events, teams and encounter mechanics untouched |
| B8 cohesion | Complete UI/effect consistency, resource budget, battle mode QA, both ROM builds and artifact upload | source checks pass; owner runtime acceptance remains pending |

## Hard engineering guardrails

- No changes to move strength, accuracy, PP, targeting, type chart, status mechanics, AI, abilities, stats or encounters.
- Native `src/battle_anim/` and `res/moves/*/anim.s` are primary implementation surfaces; respect G7 healthbox OBJ and touch SUB BG resource ownership, plus S2-D palette cycling and fades.
- A candidate's dimension fit does not prove palette compatibility or sufficient simultaneous OBJ VRAM/OAM; verify doubles and multi-target paths in code.
- Maintain `WaitForAllEmitters`, `UnloadParticleSystem`, `FreeSpriteManager`, BG restoration and audio cleanup as appropriate in every branch.
- For every **new installed donor** record exact source game, source file/member, decoded cell hashes, palette/tiles, recipe, created resources, move assignments and ownership/cleanup rules. Don't mark planned effects installed.
- Existing graphics conversion tools and CI should be reused; extend only for an actual incompatibility.
- Build US rev0/rev1 at coherent milestones and verify downloadable ROM artifacts; no live emulator check as a source-development blocker.
- Source QA cases: singles, doubles, Contest, friendly-fire/multi-target, weather + terrain cycling, faint transition, repeated animations, and both ROM revisions.
- Do not create an additional planning/audit phase. Claude's role is to implement and validate, then briefly report source files, verified ROM builds, installed assets and deferred runtime checks.

**This document does not supersede gameplay rules, merged G7/AV1/S2-D source contracts, or actual compiler/format evidence.**
