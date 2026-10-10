# B1 — Battle integration risks and enforcement

Source-level inspection completed 2026-10-10 on the independent B1 branch. No cinematic move scripts or gameplay calculations changed in this batch.

| Risk | Verified code evidence | Required B1 action | Current status |
| --- | --- | --- | --- |
| Terrain cycle overwrites battle scene fade | `src/battle/terrain.c` checks render mode, `PaletteData_GetSelectedBuffersMask`, and whether faded==unfaded before modifying MAIN OBJ/BG colors | Do not write the terrain-cycle palette bank from a new effect; reuse animation fade control and verify resume | Static ownership guard added; emulator overlap untested |
| Terrain keeps cycling in bag/party | `SysTask_CycleTerrainPalette` pauses outside battle render mode | Retain guard with B1 HUD/modal changes | Existing source guard added |
| Terrain tasks leak after battle | `Terrain_StopPaletteCycle` stops task and attempts conditional palette restoration | Test battle exit, switch, fade and interruption | Existing source guard added; runtime untested |
| SUB palette conflict with command UI | `battle_subscreen.c` owns `PLTTBUF_SUB_BG` and separate `subscreenPaletteBuf`/move palette buffers | New HUD must use known-free palette slots; do not overwrite G7 command banks blindly | Ownership confirmed; precise free slots not yet measured |
| Particle system leaks in layered AV1 effects | `battle_anim_system.c` implements unload; `battle_particle_util.c` requests VRAM auto-release; AV1 scripts explicitly unload their loaded systems | For every new composite, assert load/unload matching and wait for emitters before release | Static guard added for six AV1 pilots; interruption QA untested |
| Persistent alpha blending/brightness | Animation system exposes `BattleAnimScriptCmd_SetDefaultAlphaBlending`; script-level fades appear in AV1 | New sequences must restore baseline blending/tint, including early/cancel paths | Handler confirmed; reset-path coverage pending |
| Healthbox text/gauge overwritten by visual effects | G7 healthboxes use dynamic OBJ VRAM writes and a shared palette; G7 command UI is layered SUB BG + sprites | Preserve palette indexes and reserved sprite cells; inspect double battle and long names | Existing specs reviewed; actual VRAM budgets not yet inventoried |
| G5/G7/AV1 layering and sequencing conflict | G5 presentation, G7 graphics and AV1 animation changes all merged | Compare pre/post screenshot and per-frame effects in same battle | Requires emulator; cannot certify statically |
| Texture/emitter authoring gap | AV1 confirms existing `.spa` resources and no in-repo SPL texture authoring tool | Build reuse-first effects, investigate tooling before new particle formats | Known limitation |

## Minimum regression scenarios

- Single and double battles, status immunity, attacks that miss, multi-hit and multi-target, weather present, HP low/near faint, faint/switch, move-menu cancel, and return from Bag/Party.
- Representative AV1 moves: Ember, Fire Spin, Thunder Shock, Spark, Psybeam and Swift.
- Animated terrain scenes: water, ice, Distortion World and cave.
- Both US revisions and actual emulator visual capture for fade restoration, input responsiveness, FPS and VRAM conflicts.

## Gate for B1 implementation

Before changing a shared palette, sprite or particle source, identify the owning system, palette slot or emitter ID, fallback when occupied, cleanup path and one reproducible test. The new CI checks preserve already-known relationships but are **not proof** of collision-free rendering or gameplay behavior.
