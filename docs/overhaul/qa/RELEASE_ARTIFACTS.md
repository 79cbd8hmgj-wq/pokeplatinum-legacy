# Release Artifacts (D7 Phase 12)

**Status: NO ARTIFACTS PRODUCED.** Nothing here is a release candidate. If a TEST/QA build is ever distributed it must be labelled `TEST/QA BUILD — runtime QA incomplete`.

## Why no patch was generated

Spec s14/s20 require patch artifacts "using the repository's supported patch workflow". An audit of tracked files and workflows found **no supported patch-generation path**
(no xdelta/IPS/BPS/ups tooling, no patch target in `Makefile`/meson, no release workflow; `build.yml` only compiles the ROM and uploads nothing). Inventing one here would be
unsupported tooling and risks distributing derived copyrighted data, so none was created. Tracked as `RELEASE_BLOCKERS.md` **A-6** (owner decision: choose a patch format/tool).
The base ROM is never bundled or committed.

## Record to complete when a patch workflow exists

| Field | Rev 0 | Rev 1 |
|---|---|---|
| Required input ROM | Pokémon Platinum (US) Rev 0 — user-supplied; checksum to be recorded by the owner | Pokémon Platinum (US) Rev 1 — user-supplied; checksum to be recorded by the owner |
| Build output | `pokeplatinum.us.nds` from `make rom ROM_REVISION=0` | `pokeplatinum.us.nds` from `make rom ROM_REVISION=1` |
| Source commit | see `BUILD_MATRIX.md` | see `BUILD_MATRIX.md` |
| Output checksum (SHA-256) | recorded per CI run in `BUILD_MATRIX.md` | recorded per CI run in `BUILD_MATRIX.md` |
| Patch filename | — (not generated) | — (not generated) |
| Patch checksum | — | — |

## Installation instructions (draft — applies once a patch format is chosen)

1. Obtain a legal dump of the matching Platinum (US) revision; do not use a different revision.
2. Apply the revision-matched patch with the tool named in the release notes.
3. Verify the output ROM against the checksum published for that revision.
4. Start a **new game** for the supported experience.

## Known limitations (current)

* Runtime QA incomplete: 0 of 240 runtime-matrix runs executed (`RUNTIME_TEST_MATRIX.md`); no full campaign, no 493 run.
* Progression calibration is model-flagged but unproven (`RELEASE_BLOCKERS.md` B-1).
* Dragon Swipe has no assigned recipient (owner decision pending).

## Save-compatibility statement

Fresh saves are the supported target. The overhaul does not appear to change the save structure (flags were taken from unused slots; see `SAVE_COMPATIBILITY_REPORT.md`),
but **runtime import/reload has not been tested**, so no compatibility is promised yet. Overhaul saves must not be loaded back into vanilla Platinum.
