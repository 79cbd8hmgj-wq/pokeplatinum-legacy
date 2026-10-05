# DDA-1J — Ranger Render Visual QA

## Why this checkpoint exists

The full structural census proved that the generalized renderer can decode and
compose all 296 real Ranger Pokémon/form packages without package-level failure.

That does **not** by itself prove that every composed PNG is visually correct.

A direct visual review of the generated Pikachu output from the full-corpus
artifact exposed a presentation problem: several NCER cells appear as narrow,
striped/sliced fragments rather than a clearly recognizable complete Pokémon
sprite.

Example inspected output:

- species #025, variant 00
- groups `a01`, `a02`, `p01`, `s`, `t`, `w`
- individual `s/cell_000.png` is only a small fragment-like render rather than
  a convincing complete Pikachu frame

## Interpretation

This means the current state must be split into two separate conclusions:

### Verified

- LZ10 decompression works across the real Ranger Pokémon corpus.
- NARC extraction and member-name recovery work.
- NCLR/NCBR/NCER resource pairing generalizes.
- All 296 real packages can be processed.
- The current NCER parser can enumerate 35,806 cells.

### Not yet verified

- The current 2D OBJ VRAM tile mapping reconstructs every cell correctly.
- The default `--vram-stride-tiles 32` is globally correct.
- The 2,875 geometry shortlist entries are visually valid complete sprite poses.

Therefore **pose selection is paused** until render correctness is validated.

## Diagnostic now running

A dedicated CI diagnostic has been added:

`.github/workflows/ranger-vram-diagnostic.yml`

It renders the five shape-diverse fixtures:

- #006 Charizard
- #025 Pikachu
- #094 Gengar
- #167 Spinarak
- #445 Garchomp

at candidate 2D OBJ strides:

- 8 tiles
- 16 tiles
- 32 tiles
- 64 tiles

It also extracts Pikachu and generates raw NCBR/Nitro tile-grid previews.

## Decision gate

The next step is to compare:

1. raw NCBR tile sheets;
2. NCER cell renders at each candidate VRAM stride;
3. whether one mapping produces coherent complete Pokémon frames across the five
   heterogeneous fixtures.

Do not use the geometry candidate shortlist for Platinum integration until this
visual reconstruction gate passes.

If no fixed stride is correct across the sample, the renderer must derive the OBJ
mapping mode/stride from Nitro/Ranger metadata instead of using a global constant.
