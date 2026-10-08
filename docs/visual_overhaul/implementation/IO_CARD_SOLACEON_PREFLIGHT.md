# IO-CARD — Solaceon News Press implementation preflight

Status: **design/source preflight; no implementation or asset changes**.
Synthesis: `docs/visual_overhaul/selection/CROSS_GEN_IMPLEMENTATION_PLAN.md`, `CROSS_DONOR_IMPLEMENTATION_PLAN.md` (S3).
Goal: add a reusable Platinum-native still-card presentation capability, piloted at the Solaceon Pokémon News Press PC.

## Asset philosophy / recipe

Use donor assets as **ingredients** when justified, including composited art, layered effects, retiming, recoloring and structural reuse—not just whole replacements. The original S3 deliberately selected **Ranger 2 Almia Times event-card composition/state-variant technique**, *not* Ranger pixels. This first slice retains that specific decision; expanding to other donor assets requires an identified source component and review, not a speculative import.

- Platinum: native fonts/window pipeline, item icons, navy/teal framing, field-script progression.
- Ranger 2: masthead / headline rule / illustration well / multi-column layout / page-state variants as structural reference.
- PMD Sky: optional composition reference only; do not force its title-screen art into the page.
- Concrete four-article imagery: Platinum-native Dusk, Heal, Quick and Dive Ball icon resources (asset paths require verification before implementation).
- Composite result: Platinum-native 256×192 newspaper page with masthead, headline, illustration region, tabs and article text; do not overwrite original field or interface resources.
- Prepare an extension seam for later Sinnoh area-preview cards (`IO-PREVIEW`), but do not implement previews in this slice.

## Verified host and interaction semantics

Exact existing script:
`res/field/scripts/scripts_solaceon_town_pokemon_news_press.s`

Existing `SolaceonTownPokemonNewsPress_PC`:
1. `PlaySE SEQ_SE_CONFIRM`, `LockAll`.
2. `Message ..._TopStory`, `Message ..._ReadWhichArticle`.
3. `InitGlobalTextMenu 1, 1, 0, VAR_RESULT`; `AddMenuEntry` 0 Dusk, 1 Heal, 2 Quick, 3 Dive, 4 Exit; `ShowMenu`.
4. Copies `VAR_RESULT` into `VAR_0x8008`; dispatches 0..3 to article branches; Exit to `..._PCEnd`.
5. Each article currently runs `Message ..._Article<Ball>`, `WaitButton`, `CloseMessage`, `ReleaseAll`, `End`.
6. Exit runs `CloseMessage`, `ReleaseAll`, `End`.

Do not change which four articles are available, the index-to-article mapping, or `ReleaseAll` semantics. Do not touch reward/assignment dialogue in the same file.

`src/bg_window.c` is a general BG/window API, not an event/card controller.
`src/field_task.c` has `FieldTask_InitCall` and `FieldTask_RunApplication` for field-task state/child applications. **These are candidates, not a validated card hook**. Verify the existing field script command-dispatch/overlay application conventions before choosing one. Avoid blindly editing this general-purpose infrastructure.

## Bounded engineering questions Claude must settle

1. What field-script command implementation and command-table registration point is appropriate for `ShowStillCard` and a matching close/resume action? Can one self-contained command pause and resume the script safely?
2. What existing overlay or field UI task can host a full-screen card without fighting overworld BG layers/VRAM? Prefer a sub-screen or child application if it is safer; preserve return-to-field state.
3. How are the five inputs (four article choices + Exit) and existing localized article text rendered using Platinum's native text renderer without duplicating literal English strings?
4. Which on-disk Platinum item icon assets are the correct Dusk/Heal/Quick/Dive sources, and what is their palette/format conversion path?
5. What is the precise ownership/teardown contract for card graphics, input, palettes, and suspended field controls when exiting or choosing any article?

Answer these in the implementation PR documentation, with exact symbol references. If a bounded question reveals a real blocker, stop; do not create a new UI framework by guesswork.

## Implementation requirements

- Ship **one reusable card renderer/state**, not a one-off image replacement; card descriptor can select headline, article and illustration.
- Deliver the Solaceon PC pilot and four tab/article states.
- Preserve menu choices and existing article content; retain a fall-back/reversible script integration.
- Use a real Platinum-native card art set and font pipeline, avoiding a permanent placeholder mockup.
- Favor **simple composite layers**: background/ornament layer + item illustration + dynamic text/tabs. Optional subdued shimmer only if it can share existing machinery without new dependencies.
- No donor pixels from Ranger 2/PMD Sky for this selected S3 slice.
- Do not invent an image-generation prerequisite or expand scope to IO-PREVIEW.
- No changes to other towns' scripts or other visual-overhaul opportunities.

## Acceptance and evidence

Source/build/format verification in CI; manual runtime review explicitly **deferred**, not falsely marked passed.
Capture/describe card entry, cancel/Exit, each of four article selections, text overflow/localization, field unlock, successive interactions, graphics cleanup. Human art direction and runtime visual acceptance remain pending until manually reviewed.

## Claude read budget (priority order)

1. THIS FILE (contract)
2. exact Solaceon script above
3. relevant script command registration + an existing field child-application pattern discovered via **targeted search**
4. relevant resource/asset pipeline for icons and background tiles

Do not reread donor catalogs, ranked DS pool, every graphics API, or all previous planning documents.
Deliver source changes + reproducible art assets/scripts; build/validate; commit/push/open PR; stop.

## Known, intentionally unresolved

- Exact field card hosting path / BG layer/VRAM bank.
- Script-command dispatch details.
- Item icon conversion resources and layout.
- In-engine appearance, input/lifetime/VRAM safety (manual QA).

No claim of a compiled prototype or emulator validation is made in this preflight.
