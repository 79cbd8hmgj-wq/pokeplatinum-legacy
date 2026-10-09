# IO-FOL-SHEETS — Full-library delivery track (572 sheets)

**Scope decision:** the six-sheet pilot is cancelled as a milestone. We remain on this section until the entire 572-sheet library is exported, validated, made usable in Platinum and documented. The unrelated following-Pokémon movement mechanic is a separate advanced feature, not part of this library.

## Source inventory

Frozen source: `docs/visual_overhaul/selection/mining/evidence/hgss_follower_sheets.json`, 572 HGSS NSBTX entries; 538 32×32 and 34 64×64; eight frame textures and two palettes per sheet. This is catalog evidence, not verified species identities or game-compatible output.

## Full-batch exporter (no Claude discovery)

`tools/visual_overhaul/selection/export_hgss_follower_library.py` uses the existing `nsbmd_preview.py` decoder, verifies all 572 input files are present, decodes all 8 frames with both **source-order palette variants** (not yet proven to be normal/shiny in that order), writes **9,152 RGBA PNG files**, and generates a SHA-256 index identifying each original donor filename. It **fails if any of 572 inputs is absent** and rejects nonempty output directories to prevent stale frames from contaminating coverage.

```sh
python3 tools/visual_overhaul/selection/validate_io_fol_sheets_pilot.py
python3 tools/visual_overhaul/selection/export_hgss_follower_library.py \
  --hgss-root /path/to/hgss-extracted --out /path/to/hgss-followers-export
python3 tools/visual_overhaul/selection/validate_io_fol_sheets_pilot.py \
  --export-dir /path/to/hgss-followers-export
```

The export directory must not silently become the field engine's active resource archive. RGBA PNGs are **intermediate assets**; they are not directly loadable as the Platinum field-object sprite system.

## Completion gates (all mandatory before closing IO-FOL-SHEETS)

1. **Donor availability/provenance:** prove full raw 572-file HGSS input set and pin donor SHA or hashes. Current environment has the frozen evidence and preview renders, **not verified raw binary source files**.
2. **Full export:** generate and hash all 9,152 frame/palette PNGs; rerun the converter and compare its index deterministically.
3. **Identity/direction map:** derive authoritative species/form associations from HGSS's named constants/tables rather than numeric filename guesses; preserve source texture ordering pending directional verification.
4. **Platinum format and loader:** select actual field graphics archive/loader, determine palette/VRAM budgets and animation mapping, and provide a library that the game can request by verified identifier. Do not build a follower AI or alter movement systems.
5. **Integration and QA:** finish registration/packaging, automated validation, Rev 0/1 builds if active game resources change. Final emulator/artistic testing is owner-deferred, but all feasible static checks must pass.
6. **Coverage:** confirm no cataloged sheet omitted (572/572) and document any unsupported sizes/forms rather than silently dropping them.

**Current delivery status:** full exporter and coverage validator *authored*, no runtime export yet, no loader integration. This is active incomplete work, not a finished section. No request for Claude implementation should broaden into global research.
