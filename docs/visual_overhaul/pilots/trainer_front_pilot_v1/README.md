# Trainer front sprite pilot v1 (HGSS, six human-approved classes)

Branch `claude/trainer-sprite-pilot`. Scope: **only** the front sprite of youngster, lass, bug_catcher, twins, beauty, swimmer_female.
Approval source: `selection/review/decisions/trainer_battle_sprites.json` (human visual review) -> selection ledger `preferred/human_approved`.
Not touched: Ace Trainers, Arcade Star, Young Couple, all back sprites, every other class, engine code, palettes of other resources.

## What changed (18 files, 3 per class under `res/trainers/classes/<class>/`)
`front.png` (80x80, 8-bit palette PNG like the originals), `front_scan.png` (160x80, 4-bit) and `front_scan.png.key`.
`front_cell.json` / `front_anim.json` are unchanged: rebuilt NCER/NANR are byte-identical to the HGSS members.

## Provenance and proof
* Source: `pret/pokeheartgold@9d8b7591f09b65804da2fb2dfd56f320633e0d36`, NARC `files/a/0/5/8`, members `5k..5k+4` (k = HGSS class index; ids/hashes in `PILOT_MANIFEST.json`).
* Assets derived with the repo's own `tools/nitrogfx`, then rebuilt with the exact `res/trainers/classes/meson.build` arguments: NCGR, NCER, NANR and scan NCGR are **byte-identical** to the HGSS members; NCLR identical in its 16-colour row 0 (the HGSS NCLRs carry unused data in other palette rows; the sprites only use row 0). `apply` refuses to write on any mismatch.
* Palette/transparency/dimensions: index 0 transparent, indices <= 15, 80x80 front / 160x80 scan, enforced by `verify`.
* Archive ordering: `ARCHIVE_CHECK.json` — `trfgra.narc` rebuilt from the pre-pilot and pilot trees with nitrogfx+nitroarc: 525 members, identical member order, **exactly 18 members changed** (NCGR, NCLR, scan NCGR of the six classes), NCER/NANR unchanged.
* No unrelated changes: `verify` fails if any file under `res/ src/ include/` outside the 18 allow-listed paths differs from the base commit.

## Reversibility
Each class is its own commit (`git revert <commit>`), or `python3 tools/visual_overhaul/trainer_front_pilot.py revert --class <class>` (restores `originals/<class>/`, guarded by hashes). `verify` reports each class as `original` / `pilot`.

## Commands
```
python3 tools/visual_overhaul/trainer_front_pilot.py verify [--narc <built trfgra.narc>]
python3 tools/visual_overhaul/trainer_front_pilot.py apply --hgss-root <pokeheartgold> [--class C] [--dry-run]
python3 tools/visual_overhaul/trainer_pilot_archive_check.py --base <pre-pilot commit>
python3 tools/visual_overhaul/build_trainer_pilot_targets.py
```
CI: `.github/workflows/build-trainer-pilot.yml` builds both US revisions on this branch and verifies the built `trfgra.narc` against the HGSS member hashes.

## Minimum runtime checks (Delta / hardware), per class — see `RUNTIME_TARGETS.md` for trainers to fight
1. Enemy front sprite appears with correct colours (no palette swap/garbage, background transparent).
2. Slide-in/intro: no clipping at the sprite edges, no flicker.
3. Placement: feet on the ground line like the original (cell/OAM layout is identical to the original; the artwork bounding box differs slightly — see `selection/review/trainer_sprites/REVIEW_MANIFEST.json` geometry per class).
4. Sprite remains stable when the battle ends (fade-out) and in double battles where the class appears (twins, swimmer_female).
5. Compare against `compare/<class>.png`.
Only if all six pass: widen rollout. If any fails: revert that class only.
