# Opal DAU2 - multi-source visual curation + SPL emitter research (tooling and evidence only)

Stacked on DAU1 (PR #112, **merged** into `main` at `76bbdbb8` before this work started, so this branch is cut from updated `main`). **No gameplay data, move script, B9 P0 animation, `res/` file, ROM or donor binary is touched, and B9 P1/P2 are not started.** Nothing here is a visual approval; every visual decision is `AWAITING_OWNER_REVIEW`.

## One command each

```sh
python3 tools/visual_overhaul/dau2_curate.py manifest      # verify the pinned B9 v2 manifest and bind the 33 P1/P2 moves to the repository (source-free)
python3 tools/visual_overhaul/dau2_curate.py features      # donor-dependent (~1.5 min): decode every pool, write ASSET_FEATURES.json (numbers only, no pixels)
python3 tools/visual_overhaul/dau2_curate.py labels        # donor-dependent: HGSS cell-bank container labels (+ local labelling worksheets in build/dau2/hgss_labeling)
python3 tools/visual_overhaul/dau2_curate.py matrix        # source-free: per-move candidate matrix, owner review queue, gallery index
python3 tools/visual_overhaul/dau2_curate.py recipes       # source-free: validate + cost the 33 provisional animation recipes -> DESIGN_SHORTLIST.md
python3 tools/visual_overhaul/dau2_curate.py sheets        # donor-dependent (~1.5 min): boards + contact sheets into build/dau2 (LOCAL, git-ignored) + ASSET_INDEX.json
python3 tools/visual_overhaul/dau2_curate.py emitters      # SPL emitter study of every archive + 3 replays + recipes (seconds)
python3 tools/visual_overhaul/dau2_curate.py package       # zip the local previews into build/dau2/ for attaching to a review (local only)
python3 tools/visual_overhaul/dau2_curate.py check         # source-free CI gate over every committed artefact
python3 tools/visual_overhaul/test_dau2.py                 # 43 host tests, no donor bytes
python3 tools/visual_overhaul/test_dau2_sources.py         # corpus tests; Platinum always, Diamond/HGSS skipped *explicitly* when absent
```

## Deliverables

| File | What |
|---|---|
| `source/B9_MOVE_MANIFEST_v2.json` (+ `.sha256`, `P1_P2_MOVE_INDEX.md`) | the **original** B9 v2 manifest, byte-identical, SHA-256 `419c17818fbdabf20bf65b729ef40bd123c09899398c75fdb0258a8c8561be37`; planning input only |
| `B9_P1_P2_BINDING.json` | the 19 P1 + 14 P2 moves resolved to `res/moves/<slug>/anim.s` (+ script hash) and every discrepancy found |
| `ASSET_FEATURES.json` | Platinum-native SPL units + compact shape/hue numbers for every decoded convertible unit (search aid; no pixels) |
| `MOVE_CANDIDATE_MATRIX.{json,md}` | per-move, per-component, cross-source candidates with every field the DAU2 spec lists; evidence basis kept explicit |
| `OWNER_REVIEW_QUEUE.json`, `OWNER_REVIEW_GALLERY.md`, `ASSET_INDEX.json` | the review queue; the index of every local preview cell -> immutable asset id (+ pixel hash of the cell) |
| `model_visual_observations.json` | **advisory** notes a model made by looking at the rendered boards (334 cells); never an approval |
| `EMITTER_COVERAGE.json`, `EMITTER_RESEARCH.md`, `emitter/recipes/*.emitter_recipe.json` | SPL emitter parse of 1,874 archives, coverage table, evidence, limits, three declarative recipes |
| `DESIGN_SHORTLIST.md`, `RECIPES_P1_P2.{md,json}` | **the 33-move design shortlist**: one primary + up to two alternatives per move (launch / travel / impact / timing / provenance / compatibility / static cost). All PROVISIONAL until runtime verified |
| `HGSS_CELL_BANK_LABELS.json`, `hgss_cell_bank_label_overrides.json`, `hgss_cell_bank_model_labels.json` | evidence-tiered labels for the 130 HGSS cell-bank containers; owner override file; advisory model visual categories. Unidentified banks are never auto-selected |
| `GAP_REPORT.md` | concise gap report: counts, exact blockers, decisions still needed from the owner |

Code: `tools/visual_overhaul/dau2/` (`manifest`, `roles`, `assets`, `features`, `candidates`, `native_scripts`, `hgss_labels`, `recipes_data`, `recipes`, `recipes_report`, `sheets`, `report`, `spl_emitter`, `spl_sim`, `emitter_study`, `emitter_preview`, `emitter_report`, `cli`, `cli2`) + `dau2_curate.py`. DAU1 code is reused unchanged (`dau1/` is not modified).

## Evidence discipline (what the labels mean)

* `named_move_particle` - a Platinum move-particle with its real file name, or a Diamond/HGSS archive whose decoded textures are pixel-identical to the Platinum file at the same list position (`TEXTURE_VERIFIED`; entries that differ stay `UNVERIFIED_INDEX_ALIGNMENT` and get **no** name-based role).
* `named_source` - GBA sprite / Crystal object with a real source name matching the component query.
* `feature_heuristic` - anonymous art (PMD effects, Ranger 2 effect packages, Diamond move-effect cells, unverified SPL entries) ranked by hue/shape. It is a search aid and is searched **only inside effect-labelled containers** (HGSS cell banks carry no label and are not searched). It can never mark anything visually approved.
* Move -> ingredient queries (`roles.py`) are the model's design judgement from each move's B9 template and intent; they are not part of the manifest.
* SPL particle textures are untinted intensity masks - the in-game colour comes from the emitter (see the recipes), so grey/white previews of them are expected.
* Previews contain decoded Nintendo art, so they are **never committed** (`build/` is git-ignored; `check` fails if an image/binary is tracked anywhere under `docs/visual_overhaul/asset_unlock`, which now includes DAU1's former `gallery/*_excerpt.png`: removed from version control, local copies kept). Licence status of all donor art is unverified (`../PROVENANCE.md`).

## Owner decisions applied in this revision

1. Galleries stay local-only. 2. DAU1's committed donor-image excerpts were removed from version control (local copies kept; Git history still holds the old blobs). 3. Recipes combine native Platinum particle emitters with new Opal sprite sequences wherever strongest. 4. No donor game's style is privileged: sources are mixed by quality and cohesion. 5. Double Team, Hypnosis and Swords Dance are custom composites. 6. HGSS cell banks keep being labelled; unidentified containers are excluded from automatic selection.
