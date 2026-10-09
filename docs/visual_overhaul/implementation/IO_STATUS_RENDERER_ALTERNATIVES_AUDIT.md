# IO-STATUS — rendering alternatives, source-level recovery (2026-10-09)

Baseline: main 14a23d2e7e8e94aaf4d1f0cffb6e5512895dd498. **Architecture investigation; NOT an implemented status overlay or a claim that graphics capacity is available.** Read alongside IO_STATUS_COMPOSITE_PREFLIGHT.md. This is a narrow source investigation, not donor rediscovery.

## Finding: Gate C is specific to an additional 2D-OAM implementation, not necessarily to the visual concept

The existing battlers do not use main OBJ/OAM sprites for their principal images. `src/pokemon_sprite.c` implements `PokemonSpriteManager_DrawSprites` by binding a shared 3D texture and palette (`G3_TexImageParam`, `G3_TexPlttBase`) and issuing `NNS_G2dDrawSpriteFast` quads. The battler loop already handles active/hide/hide2, animation transform and shadow draws. The normal draw uses centres and current x/y offsets. Therefore rendering additional 3D quads at the existing Pokémon draw site is a **credible alternate host**.

A status glyph as a 3D textured quad does **not** consume a main OBJ sprite, OBJ palette or OBJ tile slot. This can eliminate the original OAM/OBJ Gate-C prerequisite, **provided** we establish texture/palette capacity and renderer state safety. It would be incorrect to claim the entire capacity problem solved by merely switching APIs.

## Concrete implementation recommendation

Prefer a **3D-overlay pilot within/next to `PokemonSpriteManager_DrawSprites`** over extra ManagedSprite allocations, subject to the proof gates below. Use Platinum-native procedural glyphs (confusion/infatuation) and no imported donor pixels. Prefer a verified unused section of the **already-allocated battler texture atlas** and an existing owned palette only if they can be proved uncontested; otherwise explicitly allocate a bounded independent 3D texture and palette with ownership and no-op fallback.

Do not overwrite unused-looking atlas texels without proving they are unused across all four Pokémon, both animation frames, shadow resources and upload paths. Do not borrow battler palette colours if the resulting glyph would vary by Pokémon or obscure shinies. Do not assume successful OAM resource measurements imply free 3D texture memory.

## Evidence from source

- `src/pokemon_sprite.c`: `MON_SPRITE_CHAR_BUF_TILES_W/H = 32/32`, char buffer `32 * 32 * TILE_SIZE_4BPP` (32 KiB). Texture coordinates are recorded for four battlers and two frames; shadow char offset is `MAN_SHADOW_CHAR_OFFSET = 0x5050` and additional sprite data use non-obvious layouts, including the special fourth battler offsets. This is **not sufficient** to declare a safe rectangular free region without a write-range audit.
- `PokemonSpriteManager_DrawSprites`: `G3_TexImageParam`, per-mon `G3_TexPlttBase`, transforms, alpha, `NNS_G2dDrawSpriteFast`, then shadow quads. Overlay quads must not break existing polygon ID/alpha, depth ordering, matrix stack or shadow rendering; state must be restored.
- The preflight already identifies authoritative volatile reads via `BattleMon_Get(... BATTLEMON_VOLATILE_STATUS ...)`, hide flags, the render-mode exclusions, battle-context lifetime and cleanup.
- The NDS toolkit archive available to the project contains inspection tooling, but there is no playable Platinum ROM artifact or running emulator in this audit. Its existence alone cannot establish texture-allocation peaks.

## Revised technical gates for 3D path (before code that draws overlays)

1. **Ownership:** identify the precise draw call site in the battle render flow and its battle-context access. Do not store freed `BattleContext` pointers in a persistent renderer. Prefer a narrow, copied status mask per battler refreshed at a controlled battle-system boundary.
2. **Atlas audit:** inspect every write to `charRawData`, all four Pokémon frame rectangles, shadow texture rectangles, and every `BufferPokemonSpriteCharData` upload. Produce a machine-checkable occupied-tile bitmap proving a glyph area stays unused in singles, doubles, animations and switching. If no safe atlas space exists, do not modify the shared atlas.
3. **Palette proof:** identify an owned 3D palette bank, its refresh/animation behavior and available indices. No palette borrowing that corrupts battler/shadow rendering.
4. **3D command safety:** count additional polygons, verify rendering order and depth/alpha under transitions, and check 3D FIFO workload/geometry constraints; fail closed when renderer is unavailable.
5. **Assets (Gate D):** generate simple two-frame confusion/infatuation glyphs, palette matched to Platinum, with exact dimensions, deterministic build recipe and NARC/atlas source provenance. No new OBJ allocations.
6. **Validation:** source-level compile for both ROM revisions, deterministic asset and atlas-overlap validator, memory ownership checks, and CI. Owner's final emulator visual/runtime testing remains deferred until after implementation.

## Comparison

| Candidate | Solves original OBJ Gate C? | New proof needed | Assessment |
|---|---|---|---|
| New ManagedSprite/OAM | No | Peak main OBJ OAM/palette/char headroom and no-op alloc | Keep as fallback only |
| 3D textured quad with proven atlas slack | Yes, for OBJ usage | Atlas writes/collisions, palette ownership, draw state | **Preferred investigation** |
| Separate 3D texture/palette | Yes, for OBJ usage | 3D VRAM ownership, uploads, teardown and geometry | Second 3D option |
| Existing BG or healthbox window | Not directly | BG ownership, z-order, follow/scroll timing | Lower priority; invasive |

## Decision

The previous Gate C should no longer be treated as a project-wide blocker demanding OBJ measurements if the pilot chooses a non-OBJ renderer. **No current evidence proves either a free atlas region or a free 3D palette slot.** Until the gates above pass, implementation remains source-blocked for this alternative. The immediately actionable next engineering task is a source-derived atlas/write-range audit plus glyph generation, not another generic OAM-capacity report. Final runtime/art acceptance is owner-deferred; static memory-corruption risks cannot be waived.
