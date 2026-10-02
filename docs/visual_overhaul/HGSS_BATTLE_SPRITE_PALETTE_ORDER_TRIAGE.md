# HGSS Battle Sprite Palette-Order Triage

This pass examines the 41 geometry-close species that failed exact RGB palette matching.
It does **not** modify Platinum palettes and does **not** promote anything to runtime-safe by itself.

For each changed view, it solves a minimum-cost one-to-one assignment between the
HGSS donor's used palette colors and Platinum's non-transparent palette indices.
If the optimum is still the identity mapping, the evidence supports that HGSS and
Platinum kept the same palette-index semantics and only changed the actual colors.

## Summary

- Palette-mismatch species input: **41**
- Views checked: **77**
- Identity-order candidate species: **30**
- Reorder-suspected species: **11**

## Identity-order candidates

- SPECIES_BELLOSSOM
- SPECIES_CLEFFA
- SPECIES_CORSOLA
- SPECIES_DROWZEE
- SPECIES_ENTEI
- SPECIES_FLAAFFY
- SPECIES_FORRETRESS
- SPECIES_GRIMER
- SPECIES_JYNX
- SPECIES_KANGASKHAN
- SPECIES_LANTURN
- SPECIES_MACHOKE
- SPECIES_MAGBY
- SPECIES_MAGNEMITE
- SPECIES_MAGNETON
- SPECIES_MEW
- SPECIES_NATU
- SPECIES_NOCTOWL
- SPECIES_PHANPY
- SPECIES_PINECO
- SPECIES_POLITOED
- SPECIES_QUAGSIRE
- SPECIES_SHELLDER
- SPECIES_SKIPLOOM
- SPECIES_SPINARAK
- SPECIES_SQUIRTLE
- SPECIES_TOGEPI
- SPECIES_UMBREON
- SPECIES_URSARING
- SPECIES_WOOPER

## Reorder-suspected species

- SPECIES_EXEGGCUTE
- SPECIES_FERALIGATR
- SPECIES_GRANBULL
- SPECIES_IGGLYBUFF
- SPECIES_NIDORINA
- SPECIES_PORYGON2
- SPECIES_SLOWKING
- SPECIES_SNORLAX
- SPECIES_SUNFLORA
- SPECIES_TEDDIURSA
- SPECIES_TOGETIC

## Rule

Identity-order candidates may be tested later with Platinum's retained normal/shiny
palettes because no index permutation is indicated. Reorder-suspected species remain
on the explicit conversion path. Neither category bypasses runtime animation validation.
