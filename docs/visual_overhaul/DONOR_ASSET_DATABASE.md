# Donor Asset Database

## Project rule

No Platinum sprite replacement work should begin while donor-source collection is
still in progress.

The visual-overhaul phase is now an **asset collection and cataloging phase**.

The goal is to build one source-agnostic database of recoverable, reviewable visual
assets from every donor game/source before deciding which assets should replace any
Platinum graphics.

## Database purpose

The catalog answers:

- what source the asset came from;
- which Pokémon/species/form/variant it belongs to;
- what resource/group/frame produced it;
- whether it rendered successfully;
- its native and occupied geometry;
- whether the render has been visually validated;
- whether it appears usable for any Platinum target;
- what kind of target it may be useful for;
- whether it is preferred, alternate, rejected, or still unreviewed;
- provenance back to the original donor file.

The database must preserve **all useful alternatives**. It is not a one-winner
selection table.

## Asset review states

Every asset uses one of these review states:

- `unreviewed` — extracted/rendered but not visually inspected;
- `valid_render` — visually confirmed to be reconstructed correctly;
- `usable` — valid render with at least one plausible Platinum use;
- `alternate` — usable but not currently a preferred candidate;
- `reject` — unusable for the visual-overhaul goals;
- `decode_issue` — source exists but the current decoder/render is not trustworthy.

No asset is marked `usable` merely because its dimensions fit 80x80.

## Target tags

An asset may have zero or more target tags, for example:

- `battle_front`
- `battle_back`
- `battle_animation_frame`
- `party_icon`
- `summary_icon`
- `overworld`
- `portrait`
- `trainer`
- `effect`
- `ui`
- `other`

These tags describe possible use. They do not cause any Platinum replacement.

## Source independence

Each donor source gets its own importer/normalizer. Source-specific fields remain
available under `source_metadata`, while common fields are normalized into the
catalog schema.

This allows Ranger, HGSS, other DS games, prototypes, demos, debug builds, or later
sources to coexist in one catalog without forcing them into the same file format.

## Ranger status

Ranger is the first populated donor source.

Current verified structural result:

- 296 real Pokémon/form packages process successfully;
- 35,806 NCER cells are recoverable;
- 282 species are represented.

However the Ranger cell renderer is still under visual reconstruction validation.
Until that gate is closed, Ranger frame entries should remain `unreviewed` or
`decode_issue`, not automatically promoted to `usable`.

## Workflow

1. collect donor source;
2. extract/decode assets;
3. normalize entries into the catalog;
4. visually validate reconstruction;
5. tag plausible uses;
6. preserve alternates;
7. continue collecting other sources;
8. only after source collection is mature, compare candidates across sources;
9. only then design a Platinum replacement/import ledger.

## Hard boundary

The donor asset catalog is informational and curation-oriented.

It must not write to Platinum sprite resources, generate replacement ledgers, or
silently choose one donor over another.
