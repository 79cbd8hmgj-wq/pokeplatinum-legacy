# HGSS -> Platinum Battle Sprite Palette Contract Audit

This is the second G3 battle-sprite safety gate. It runs only on the species
whose changed HGSS views already passed the conservative frame-geometry triage.

Platinum's existing normal and shiny palette files remain authoritative.
The build packs sprite pixel indices separately from those palettes, so donor
art must preserve Platinum's index/color contract rather than merely look correct
inside the donor PNG.

## Summary

- Geometry-close species input: **69**
- Art-diff views checked: **130**
- Direct-index-safe views: **53**
- Exact-normal-remap views: **0**
- Palette-mismatch views: **77**
- Fully direct-index-safe species: **28**
- Species requiring only exact normal-color remap: **0**
- Species with unresolved palette mismatch: **41**

## Import policy

- **direct-index-safe**: eligible for the next small runtime pilot.
- **exact-normal-remap**: do not auto-import yet. Normal-color remapping is
  possible, but the same index remap would also affect Platinum's shiny palette;
  that semantic relationship must be reviewed first.
- **palette-mismatch**: manual conversion/rejection path only.

## Direct-index-safe species

- SPECIES_ABRA
- SPECIES_CLEFABLE
- SPECIES_CLEFAIRY
- SPECIES_DIGLETT
- SPECIES_DITTO
- SPECIES_DUGTRIO
- SPECIES_ELECTRODE
- SPECIES_GLOOM
- SPECIES_GROWLITHE
- SPECIES_HORSEA
- SPECIES_HYPNO
- SPECIES_JIGGLYPUFF
- SPECIES_LAPRAS
- SPECIES_LARVITAR
- SPECIES_MAGMAR
- SPECIES_METAPOD
- SPECIES_NIDORINO
- SPECIES_OMANYTE
- SPECIES_OMASTAR
- SPECIES_PERSIAN
- SPECIES_PSYDUCK
- SPECIES_PUPITAR
- SPECIES_SANDSLASH
- SPECIES_TENTACOOL
- SPECIES_TYRANITAR
- SPECIES_VENUSAUR
- SPECIES_VOLTORB
- SPECIES_WEEPINBELL

## Exact-normal-remap species

- None

## Palette-mismatch species

- SPECIES_BELLOSSOM
- SPECIES_CLEFFA
- SPECIES_CORSOLA
- SPECIES_DROWZEE
- SPECIES_ENTEI
- SPECIES_EXEGGCUTE
- SPECIES_FERALIGATR
- SPECIES_FLAAFFY
- SPECIES_FORRETRESS
- SPECIES_GRANBULL
- SPECIES_GRIMER
- SPECIES_IGGLYBUFF
- SPECIES_JYNX
- SPECIES_KANGASKHAN
- SPECIES_LANTURN
- SPECIES_MACHOKE
- SPECIES_MAGBY
- SPECIES_MAGNEMITE
- SPECIES_MAGNETON
- SPECIES_MEW
- SPECIES_NATU
- SPECIES_NIDORINA
- SPECIES_NOCTOWL
- SPECIES_PHANPY
- SPECIES_PINECO
- SPECIES_POLITOED
- SPECIES_PORYGON2
- SPECIES_QUAGSIRE
- SPECIES_SHELLDER
- SPECIES_SKIPLOOM
- SPECIES_SLOWKING
- SPECIES_SNORLAX
- SPECIES_SPINARAK
- SPECIES_SQUIRTLE
- SPECIES_SUNFLORA
- SPECIES_TEDDIURSA
- SPECIES_TOGEPI
- SPECIES_TOGETIC
- SPECIES_UMBREON
- SPECIES_URSARING
- SPECIES_WOOPER
