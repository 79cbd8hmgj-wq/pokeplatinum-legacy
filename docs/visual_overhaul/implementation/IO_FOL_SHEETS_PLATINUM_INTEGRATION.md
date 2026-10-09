# IO-FOL-SHEETS — Platinum native integration handoff

> **SUPERSEDED AS AN ACTIVE WORK ITEM (2026-10-09):** Pokémon Opal uses Platinum as a foundation and other games as curated donor sources. This earlier document assumed all 572 HGSS follower sheets must be embedded in the ROM. That assumption is no longer valid. PR #93's exporter/catalog is a completed **donor preparation capability**, not an order to import 572 runtime follower graphics. Treat the steps below only as an **optional technical reference** if a chosen Opal feature actually needs specific follower frames in-game. See `docs/visual_overhaul/POKEMON_OPAL_ASSET_DIRECTION.md`. Do not commission this full-library integration in Claude Code.



This is an **implementation plan for the entire library, not a pilot**. Existing PR #93 has the 572-entry HGSS identity inventory and a passing GitHub Action that exports the 9,152 frames as an artifact. It does **not** yet integrate the graphics into the ROM.

## Source-backed Platinum integration route

- `res/graphics/field_sprites/meson.build` is the native field-sprite packaging pipeline. `field_sprites_nsbtxs` is populated through `nitrobtx_exe pack` custom targets, then packaged into `field_sprites.narc` (around lines 724–745).
- At lines 526–542, the existing 32px texture pipeline invokes `nitrobtx pack --texture ... --name ... --spritesheet --frame-height 32 --extract-palette`.
- This source demonstrates a **native converter and NARC packaging path**, but it does not establish multi-palette 8-frame compatibility automatically. Test the exact normal/alternate palette and 32px/64px layouts before copying command forms.
- `src/overlay005/sprite_resource_manager.c` handles a different sprite resource API. `src/overlay005/map_prop.c` is a field **3D prop model** renderer, not a confirmed Pokémon field character loader. Do not route the sheets to either based merely on filenames.
- `include/constants/species.h` delegates to generated `generated/species.h`, so mapping must resolve actual generated species values rather than assume HGSS model IDs == Platinum species IDs.
- `include/constants/map_object.h` defines directions NORTH 0, SOUTH 1, WEST 2, EAST 3; this alone does **not** establish which of HGSS's eight texture frames correspond to those directions.

## HGSS identity mapping

`docs/visual_overhaul/implementation/io_fol_sheets_hgss_identity.json` identifies 572 sources via pinned HeartGold `include/constants/mmodel.h`. Models 201–206 are **six generic follower slots**. Models 297–862 carry **566 named species/form constants**. These symbolic identities may map to Platinum's species and form symbols after a version-specific validation pass. Never infer direct numeric equality. Preserve all 572 resources even when a model is a generic slot.

## Claude implementation boundary — finish section in a cohesive build

1. Use the complete export artifact (no small subset), validate all files/hashes, and pin deterministic source/tool hashes. Do not add the bulky generated RGBA assets into Git history unless the repository's existing resource policy supports it; choose reproducible on-build generation or a pinned complete library archive.
2. Derive species/form IDs from HGSS symbols and Platinum's generated constants, including explicit exceptional forms and all six generic models. Emit a testable mapping manifest. No silently unmapped named models.
3. Reuse the existing native field-sprite NSBTX/NARC pipeline where compatible; if a separate library archive is necessary for VRAM/ROM budget or lookup constraints, document and implement its deterministic packing and table indexing.
4. Connect the library to the **actual field-character graphics loader**, verifying its life-cycle, render/animation semantics, map-object IDs and texture/palette budgets. Do not add following AI, pathfinding or follow-player behavior (separate advanced feature).
5. Prove all 572 are accessible by a stable resource ID/API and both palette variants/eight directional-animation source frames are preserved. Verify mapping of frames before assigning directional semantics.
6. Rebuild US Rev 0 and Rev 1, check archive/member indices, ROM size, VRAM/heap transfer bounds, and add full-coverage validators. Owner runtime/art QA is deferred, **not implementation**.

The library is not complete until step 6 passes. Stay on this section through intermediate commits and PRs. Do not send Claude a pilot request or mark this done based only on the export workflow.
