# IO-FOL-SHEETS — six-sheet pilot preparation

This package reduces implementation discovery for the HGSS overworld Pokémon graphics *library*, not the following-Pokémon mechanic. No Platinum field code has been modified.

## Verified repository evidence

- Canonical ranking: `docs/visual_overhaul/selection/CROSS_GEN_IMPLEMENTATION_PLAN.md`, IO-FOL-SHEETS is rank 2, Wave 3; first slice is a non-follower library.
- Decoded source catalog: `docs/visual_overhaul/selection/mining/evidence/hgss_follower_sheets.json` reports 572 eligible donor NSBTX sheets, 538 at 32-pixel texture width and 34 at 64, each eight textures/frames and two palettes with a shiny difference.
- Evidence decoder exists: `tools/visual_overhaul/selection/evidence_hgss_followers.py`; it calls `nsbmd_preview.parse_bmd`, `parse_tex0` and `decode_tex` to extract RGBA frames from HGSS NSBTX. The raw donor location is `<hgss-root>/files/data/mmodel/mmodel`.
- Six evidence-backed source filenames are explicitly pinned in `io_fol_sheets_pilot_manifest.json` (three 32px and three 64px). They are identifiers, **not verified species mappings**.

## What is not yet established

- HGSS donor raw NSBTX files are not proven to exist in this Platinum repository; the decoder requires a separate HGSS checkout. Catalog/renders do not substitute for the donor binary.
- No source-backed species/form ↔ donor filename mapping is provided in this preparation package. Never equate numeric donor filenames with National Dex numbers.
- The intended Platinum map-object graphics provider, its runtime NARC/VRAM budget and direction/animation semantics have not yet been verified. Do not wire these into encounters, events or following-Pokémon behavior during the library phase.
- Format conversion to Platinum-native graphics is not yet proven; RGBA previews are not themselves loadable DS graphics resources.

## Suggested minimal next implementation slice

1. Verify the raw donor provenance (pinned source commit and exact files) and decode **only the six manifest files** using existing scripts. Preserve both palettes and all eight source frames without inventing direction mappings.
2. Produce a deterministic, indexed intermediate library format under a dedicated data directory with a conversion script and a frozen manifest of output sizes/hashes. Do not write to Platinum's active map-object NARC.
3. Validate source dimensions, transparency, 8 frames × 2 palettes, reproducibility, and exact relationship between the manifest IDs and resulting assets. Include a contact sheet for later artistic review.
4. Investigate a single existing field-object graphics loader and record constraints *only if needed for defining the library format*. Do not implement spawning, pathfinding, follower AI, or change events in this slice.
5. Build both US revisions if build files change; otherwise validate data tooling independently. Keep owner runtime/artistic QA deferred.

Run metadata guard from repo root:

```sh
python3 tools/visual_overhaul/selection/validate_io_fol_sheets_pilot.py
```

## Claude workload boundary

The research inventory, selection and validation guard are prepared. Claude should work **only** on deterministic six-donor conversion after raw NSBTX availability is established, or report that precise artifact blocker. Do not ask Claude to redo global HGSS asset mining, infer species identities or implement following Pokémon. Further integration into Platinum should be a separate bounded change after file formats and loader ownership are confirmed.
