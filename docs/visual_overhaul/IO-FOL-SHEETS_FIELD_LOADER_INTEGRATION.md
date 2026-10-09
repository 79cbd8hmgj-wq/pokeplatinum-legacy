# IO-FOL-SHEETS — Platinum field-loader integration investigation

Status: **investigation, not in-game implementation**. Traced against `pokeplatinum-legacy` main source on 2026-10-09. Associated with PR #93 (full 572-sheet export workflow). Do not close IO-FOL-SHEETS or claim follower rendering works until build and emulator gates pass.

## Existing PR scope and evidence

PR #93 adds donor coverage verification and a complete HGSS follower-sheet export workflow. Its description explicitly states that donor binaries and field-loader integration remain outstanding. The reported source catalog is 572 NSBTX sheets; the published exporter generates 9,152 normal/shiny RGBA frames, with hash manifests and validation gates. **Exported PNG files are not directly consumable as map-object rendering resources.**

## Verified source call chain

- `src/map_object.c`: `MapObject_SetGraphicsID` stores an object's graphics ID. `MapObject_GetEffectiveGraphicsID` returns its effective ID, applying the Berry Patch substitution where applicable. `MapObjectTask_Draw` invokes `MapObject_Draw` if drawing is initialized. This file is not itself the underlying graphics resource loader.
- `src/overlay005/ov5_021ECC20.c`: `ov5_021ECC20` calls `ov5_021ECE40` to initialize the field graphics subsystem.
- `src/overlay005/ov5_021ECE40.c`: `ov5_021ECE40` calls `ov5_021EDDAC`, `ov5_021EE320`, `ov5_021ED224`, `ov5_021ED0A4`, and `ov5_021ED4E4`. These initialize field-object resources.
- `ov5_021ED224` creates two `ResourceHeap` pools (`0x1000 * capacity` and `0x80 * capacity`) and a `TextureResourceManager`. **Do not treat these size formulas as confirmed spare runtime capacity.**
- `ov5_021ED2E8` checks `ResourceHeap_HasItem`, resolves the resource ID against an `UnkStruct_ov5_021ED2D0` mapping table, obtains `MapObjectMan_GetNARC(...)`, and calls `ResourceHeap_LoadMemberFromNARC` for the mapped member.
- `ov5_021ED334` checks texture IDs and mapping entries before invoking `ov5_021EDF3C`. The registration tables and resource format need further inspection.
- `ov5_021ECEB4` dispatches a requested graphics resource through different paths. `ov5_021ECF04` calls it with `MapObject_GetGraphicsID`.
- `ov5_021ECF1C` obtains `BillboardResources` and creates a drawable billboard via `ov5_021EDDDC`.
- `ov5_021ECF70` calls `Billboard_Delete` and conditionally releases a resource; `ov5_021ECFA4` also handles Berry Patch IDs on cleanup.

These observations make the **existing ID -> archive member -> texture/resource manager -> billboard lifecycle** the preferred integration seam. No replacement rendering pipeline is justified yet.

## Source files to inspect next (bounded investigation)

1. `src/overlay005/ov5_021ECE40.c`: fully trace `ov5_021EDF3C`, `ov5_021ED110`, `ov5_021ED184`, `ov5_021ED82C`, and related registration/refcount paths.
2. `src/overlay005/const_ov5_021FB484.c` and `src/overlay005/const_ov5_021FC9B4.c` (or their actual defining paths): establish ID-to-NARC-member mapping, sentinel rules, and whether tables can be extended.
3. `src/overlay005/ov5_021ECA70.c` and `src/overlay005/ov5_021ECE40.c`: verify billboard frame, direction, and update lifecycle.
4. `generated/object_events_gfx.h`, associated resource generation, and archive build definitions: determine safe namespace/range for HGSS graphics without changing existing object IDs.
5. The PR #93 exporter and mapping artifacts: explicitly reconcile 566 named species/form mappings + six generic slots; document how each maps to Platinum species/form IDs, especially gender and alternate forms.

## Implementation design and safety gates (NOT YET APPLIED)

- Keep all existing Platinum graphics IDs and resources stable; reserve an explicit noncolliding namespace for new followers only after auditing ID width, table limits and serializers.
- Convert all exported HGSS frame pixels/palettes into the native resource format used by the field billboard subsystem; **do not attempt to load RGBA PNGs directly from NARC as existing billboard objects**.
- Generate deterministic HGSS-to-Platinum species/form mapping with collision, missing-ID and unsupported-form checks; generic slots must never masquerade as named Pokémon.
- Register new archive members through the existing resource tables/manager; preserve fallback to vanilla graphics when loading fails or a form is unmapped.
- Audit budgets for archive growth, field heaps, palette/texture memory, active object limits and cleanup/refcounts. Do not preload all 572 assets into VRAM.
- Implement a bounded integration proof with a small representative set of species/forms, then expand to full catalog only after the shared loader path passes. This is a **test gate**, not a scope reduction from the committed 572-sheet library.
- Require successful Platinum builds, emulator demonstrations of directions/movement frames and normal/shiny variants, map transitions, resource release/reload, and regressions for vanilla NPC/map graphics.
- Avoid modifying unrelated Pokémon rebalance/evolution/learnset changes. Do not claim PR #93's successful export/CI proves any runtime graphics behavior.

## Handoff and authoritative location

This document is intentionally stored on the **PR #93 branch**, rather than only in a ChatGPT download or chat. Continue refining it with verified source traces. Claude Code should receive a bounded implementation specification after mapping, resource packing, registration IDs and budget constraints are resolved; any implementation must be validated independently in a build and emulator.

Sources in repository: `src/map_object.c`, `src/overlay005/ov5_021ECC20.c`, `src/overlay005/ov5_021ECE40.c`, `src/overlay005/ov5_021ECA70.c`. PR: https://github.com/79cbd8hmgj-wq/pokeplatinum-legacy/pull/93.


## Follow-up source trace — billboard resource and animation format (2026-10-09)

Verified in `src/overlay005/ov5_021ECE40.c`:
- `ov5_021EDA0C` requests all three resource categories for a graphics ID: mappings `ov5_021EDD2C(id)` and `ov5_021EDD38(id)` plus an ID-specific texture request.
- `ov5_021ED2E8` resolves resource IDs to archive member numbers through table `Unk_ov5_021ED2D0`; an unregistered resource will encounter an assertion, not a graceful automatic fallback. **Any fallback must be explicitly designed and tested.**
- `ov5_021ED110` reuses an existing `BillboardResources` entry or allocates a free `0xffff` slot and initializes it with `ov5_021EDE3C`; returns NULL if the slots are exhausted.
- `ov5_021ED184` marks a matching billboard resource slot `0xffff` (free). `ov5_021ED1C8` considers other map objects before release.
- `ov5_021EDF3C` either queues deferred texture loading or calls `ov5_021EDCF4` and `ov5_021EE0E8` to handle immediately, depending on redraw/budget state.
- `ov5_021ECF1C` calls `ov5_021EDA0C` to ensure resources and `ov5_021ED110` for billboard registration before creating a billboard.

Verified in `src/billboard_gfx_sequence.c`: `BillboardGfxSequence_SetData` reads an initial 32-bit sequence count, followed by `seqCount` 16-bit start-frame positions, `seqCount` 8-bit texture indices, and `seqCount` 8-bit palette indices. `BillboardGfxSequence_GetTexPlttIndexAt` selects the texture/palette index associated with a frame. This is **one part of the native resource format**, not sufficient proof that converted PNGs alone can render.

Verified `generated/object_events_gfx.txt` is a symbolic graphics-ID list, including dummy slots. **Do not treat dummy IDs as safe to replace without tracing their consumers.**

**Path correction:** `include/overlay005/const_ov5_021FB484.h` and `include/overlay005/const_ov5_021FC9B4.h` are declarations of external mapping arrays, not `.c` definitions; the previously suggested `src/overlay005/const_ov5_021FB484.c` and `src/overlay005/const_ov5_021FC9B4.c` do not exist in the inspected tree. Locate the actual definitions before changing any mapping.

Next source-first blocker: find real definitions/build generation of `Unk_ov5_021FB484`, `Unk_ov5_021FB5BC`, `Unk_ov5_021FC9B4` and determine atlas, sequence, texture packaging, ID allocation, and runtime budgets. No build or emulator test has been performed for the new library.
