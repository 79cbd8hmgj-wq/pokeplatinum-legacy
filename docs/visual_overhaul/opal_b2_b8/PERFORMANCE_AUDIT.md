# Opal B2–B8 quality / performance audit

**Scope honesty:** these are *static* audits (symbolic execution of every script path + build outputs). **No frame-time, VBlank-DMA, VRAM-headroom or hardware measurement
was performed.** The numeric limits below are conservative policy caps derived from the battle engine's own configuration; they are enforced in CI, they are not proof of smoothness.

## Hardware envelope read from source

| Resource | Engine configuration | Source |
|---|---|---|
| Main OBJ character VRAM | `GX_VRAM_OBJ_64_E` = 64 KiB (2048 tiles), 1D mapping 64K | `src/battle/battle_main.c` (`GXBanks`, `sTransferTemplate`) |
| Main OAM entries | 128 (32 affine) | `sOamTemplate` |
| Sprite resource capacities | 96 char / 32 palette / 64 cell / 64 anim | `sCapacities` |
| Opal sprite managers | each owns one OBJ palette + its char data; max 4 ids per script | `BATTLE_ANIM_SCRIPT_MAX_SPRITE_MANAGERS` |

## Enforced policy (tools/visual_overhaul/opal_cue_trace.py, runs on every path of every Opal script)

| Limit | Value | Rationale |
|---|---|---|
| concurrent sprite managers | ≤ 2 | ≤ 2 extra OBJ palettes next to healthboxes/battlers |
| concurrent Opal OBJ char tiles | ≤ 400 (12.5 KiB = 19 % of the bank) | B1 rule: do not treat 256 tiles as free headroom; B1's largest was 236 |
| concurrent Opal OAM entries | ≤ 40 of 128 | leaves ≥ 88 for healthboxes, battlers, terrain, vanilla effect sprites |
| per-sheet char data | ≤ 192 tiles (6 KiB) | `validate_opal_assets.py` |
| FX sprite lifetime | ≤ 180 frames, hard-capped in C (no indefinite wait) | `OPAL_FX_MAX_LIFETIME` |
| camera cue | ≤ 90 frames, one owner at a time, exact restore (host-proven) | `opal_cinematic_math.h` + `test_opal_cinematic_math.c` |
| base-BG fades | never overlap in time; start alpha = current alpha; end alpha 0 | validator |
| particle systems / sprite managers | none live at `End`; managers freed before `UnloadParticleSystem` | validator |

Per-script peaks: `BUDGET_TABLES.md` (generated). Worst cases: Surf 9 live FX sprites / 12 OAM entries; SolarBeam release 22 OAM entries and 368 tiles
(two concurrent sheets); Fire Blast 384 tiles because it overlaps the B1 ranger bloom (236 tiles) with the 148-tile fire sheet.

## Code / data footprint

* `opal_cinematic.c`: ≈ 2.1 KiB of ARM code, 4 bytes of BSS (`arm-none-eabi-size` on the CodeWarrior object).
* Graphics archive and script archive deltas versus the B1 head: see `BUDGET_TABLES.md` ("Archive sizes").
* The ROM image is padded to 128 MiB in both revisions; the added content is far below the padding granularity.

## Cohesion review (B8-01)

* One vocabulary: all cues are `Opal*` macros; palettes come from one 4-step ramp family (gold, steel, ghost, water, fire, ice, psychic, earth, solar, opal-pearl).
* Opal identity (pearl / mineral-violet / gold) is used for framing cues (blocked guard, legendary arrivals, generic cues); elemental moves keep their element colours.
* Timing: charge ≤ 14 frames before the native release; camera ease 6 frames; pulses ≤ 10 frames; no added wait on native emitters except Shadow Ball / Thunderbolt charge phases that replace the native dim (same length ± 2 frames).
* Duplicates removed: Fire Blast overlay on top of the ranger bloom; weather accent no longer reloads the 184-tile ring sheet (51-tile dedicated sheet).
* Not unified automatically: B1/AV1 scripts for other moves (Flamethrower, Ember, …) keep their B1 look; extending the vocabulary to them is mechanical (see `move_template_map.json` for the pattern).

## Not measured (owner / follow-up)

1. Frame pacing in doubles + weather + spread (target: no dropped frames versus the B1 head).
2. Real OBJ VRAM / palette headroom with four healthboxes, trainer sprites and terrain sprites resident.
3. VBlank DMA cost of palette fades when two fades run in different scripts' tails.
4. Contest rendering of the sprite cues (camera cue is disabled there by design).
