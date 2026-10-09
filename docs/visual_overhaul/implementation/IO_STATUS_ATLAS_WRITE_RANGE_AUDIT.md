# IO-STATUS — source-derived atlas occupancy audit (2026-10-09)

Baseline: `main` `0be140e6cd9d46a7a7c3a0a52595ed8f3121c208`. This is **not** a visual implementation or runtime acceptance.

## Results and limits

`src/pokemon_sprite.c` creates a 32×32-tile, 4bpp texture buffer (256×256 px, 32768 bytes). The constructor fills **the entire buffer** with the shadow-image background byte, then places shadow texels in a restricted region; battler texture writes are made on reload/animation. Therefore no strip starts with undefined ownership: a new glyph must be explicitly inserted **after initialization** and before the next `PokemonSpriteManager_UpdateCharAndPltt` upload, and retained across texture refreshes. No new atlas bytes may be silently assumed unused merely because a drawn quad doesn't sample them.

The accompanying source-layout-guarded validator models every possible address written by the battler-copy loops for all four slots and the shadow-copy initialization loop. It conservatively includes both animation frames and ignores visually transparent pixels, because the copy loops overwrite them anyway.

| Byte-writing region | Source behavior |
|---|---|
| Battlers 0–2 | `y * 0x80 + x + i * 0x2800`, `y=0..79`, `x=0..39` |
| Battler 3, first half | `y * 0x80 + x + 0x50`, `y=0..79`, `x=0..19` |
| Battler 3, second half | `y * 0x80 + x + 0x2828`, `y=0..79`, `x=20..39` |
| Shadows | `y * 0x80 + x + 0x5050`, `y=0..79`, `x=0..39` |

These source-defined copy ranges occupy **16000 unique bytes** with no collisions. The **bottom strip** of the 256×256 texture, `y = 240..255`, is not written by any of these loops. Four nonoverlapping 16×16-pixel glyph frame rectangles can fit at `(0,240)`, `(16,240)`, `(32,240)`, `(48,240)` (2 effects × 2 frames). That is **512 total 4bpp bytes** within the *existing* 32 KiB buffer, not an added allocation. The right strip `x = 240..255` also appears free in this model.

**Important qualification:** the shader/3D renderer's palette is the unresolved constraint. Each battler's palette slots are replaced during switches and fades; shadow palettes are also updated. A visually empty-looking 3D palette bank is not automatically available. The model does not prove that other source paths cannot overwrite the glyph regions, nor does it prove that the glyphs draw correctly on-screen. Before implementation, audit all other writes / texture manipulation paths and ensure the atlas uploader includes the glyph area every time.

## Gate C direction

The atlas occupancy result is strong evidence that **no additional OBJ/OAM storage is required** for a 3D-quad glyph pilot, and that texture capacity can be obtained in the existing battler atlas. It does **not** finish the renderer-specific Gate C: palette ownership, draw state, status synchronization, and reupload timing must still be resolved.

## Implementation outline for a subsequent bounded PR

1. Derive or reserve a genuinely owned 3D palette treatment that cannot corrupt battlers or their shadows, and document ownership under fades/switches.
2. Produce deterministic 16×16 glyph image pairs for confusion and infatuation from Platinum-native art; explicitly index two frames for each.
3. Inject texels only after full atlas initialization; keep glyphs intact after each battler refresh. Prove via a source-level/asset test that texture rectangles do not intersect the source copy writes.
4. Render glyph quads in the existing Pokémon manager draw path only for visible active battlers with corresponding volatile status, following their live position. Avoid reading destroyed battle context; honor Gate E exclusions.
5. Add CI static validators, native build for both revisions, and memory/renderer ownership tests. The owner will do final in-game visual acceptance at the end of implementation.

Run locally from the repository root:

```bash
python3 tools/visual_overhaul/io_status/validate_atlas_write_ranges.py
```

The validator **fails closed** if the audited source constants or write-loop syntax change. It is still a focused source-model test, not a proof of all execution paths.
