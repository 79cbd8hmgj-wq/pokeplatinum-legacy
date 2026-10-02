# Pass G3 — Character & Pokemon Graphics Donor Audit

## Scope

This checkpoint evaluates HeartGold/SoulSilver as the first donor for Pokemon presentation before any broad sprite replacement.

The rule remains the Pass G donor rule: use the strongest result that is technically efficient on Platinum's DS resource contracts. Do not replace an asset merely because HGSS is later.

## Pokemon icon audit

Platinum exposes species icons as:

`res/pokemon/<species>/icon.png`

with the shared icon palette/cell/animation resources under:

`res/pokemon/.shared/`

HGSS exposes the equivalent icon archive source under:

`files/poketool/icongra/poke_icon/`

Both use 32x64 indexed PNG source images and Nitro NCGR/NCLR/NCER/NANR packing.

Representative decoded comparisons were made for:

- Bulbasaur
- Pikachu
- Mewtwo
- Arceus

For all four samples, the indexed icon pixel data and palette are the same between Platinum and HGSS. The source PNG containers differ in metadata/chunk details, but the rendered icon art does not.

### Icon ruling

**Classification: DIRECT but REJECT as a wholesale donor swap.**

There is no visual payoff in replacing Platinum icons with byte-different containers that render the same art. Keep Platinum icons unless a specific form/species exception is discovered later.

## Battle sprite resource compatibility

Platinum battle sprites are source-backed under:

`res/pokemon/<species>/male_front.png`
`res/pokemon/<species>/male_back.png`
`res/pokemon/<species>/female_front.png`
`res/pokemon/<species>/female_back.png`

Platinum's `make_pl_pokegra.py` converts those sources into `pl_pokegra.narc` and stores normal/shiny palettes separately.

HGSS exposes the same conceptual four-way sprite structure under:

`files/poketool/pokegra/pokegra/<national-dex-id>/...`

The sampled Platinum and HGSS battle images are all **160x80 indexed PNGs**, so the basic source dimensions are directly compatible.

HGSS likewise builds its sprite NCGRs from the four gender/front/back source images and derives the normal palette from the male front image and shiny palette from the male back image.

### Representative front-sprite audit

| Species | Platinum vs HGSS | Finding |
|---|---|---|
| Bulbasaur | different | HGSS has revised front poses; same sampled palette |
| Pikachu | different | HGSS has revised front poses and small palette differences |
| Chikorita | different | HGSS has substantially revised front poses and palette |
| Mewtwo | different | HGSS has a substantially more dynamic front pose |
| Sceptile | same art | No useful front-sprite donor gain in the sample |
| Lucario | same art | No useful front-sprite donor gain in the sample |

### Representative back-sprite audit

- **Mewtwo:** sampled Platinum/HGSS back art is the same.
- **Sceptile:** sampled geometry/art is effectively the same; HGSS's source PNG intentionally carries the shiny palette because HGSS derives the shiny NCLR from the male-back PNG.

That palette behavior is important: a raw PNG preview of an HGSS back sprite can appear shiny even though the indexed pixels are intended to render through the separately built normal palette at runtime.

## G3 battle-sprite ruling

**Classification: SELECTIVE DIRECT/CONVERTIBLE.**

HGSS is valuable for selected revised front sprites, especially where it materially improves an older Pokemon's pose/presentation. It is **not** a justified whole-dex replacement:

- some front sprites are revised;
- others are identical;
- sampled back sprites show little or no art gain;
- palette ownership differs between the source trees;
- sprite-specific `.key` data should travel with an imported HGSS image when it differs;
- Platinum's existing sprite animation/data contract should be preserved unless runtime testing proves a specific donor pose needs animation retuning.

## First guarded pilot

Use a very small pilot before scaling the donor pass:

1. **Mewtwo front sprite**
   - clear pose improvement in HGSS;
   - same 160x80 source contract;
   - Platinum/HGSS normal palette differs only in palette entry 0 in the audit;
   - HGSS front `.key` differs and must be imported with the sprite.

2. **Bulbasaur front sprite**
   - clear revised front poses;
   - same 160x80 source contract;
   - sampled normal palette matches Platinum;
   - import the matching HGSS front `.key` if it differs.

Do **not** alter back sprites or species palettes in this pilot.

The pilot is intended to answer the remaining runtime question: whether Platinum's existing species animation metadata presents the revised two-frame HGSS fronts cleanly in battle.

If the pilot builds and looks correct in Delta, the next step is a generated donor manifest for other visually improved Gen I-III fronts rather than manually replacing the entire National Dex.
