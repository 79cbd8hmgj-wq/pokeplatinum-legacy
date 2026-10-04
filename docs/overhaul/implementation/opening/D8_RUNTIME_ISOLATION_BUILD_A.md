# D8 Mystery Egg runtime isolation — Build A

Status: DIAGNOSTIC ONLY — DO NOT MERGE AS THE FINAL FEATURE.

## Purpose

Blocker C-1 is unchanged across PRs #26, #28, #29, and #30: after confirming the starter choice, both screens remain black while music continues and the field script never visibly resumes.

This build isolates the final remaining non-vanilla code inside the chooser from the already-separated Mystery Starter logic.

## Build A change

Starting point: main at `41e7524ac457b0acbb22c66975083acb4d312984`.

Only `src/choose_starter/choose_starter_app.c` is restored byte-for-byte from the pre-D8 reference commit `6fc1eedfec637041733b5e5d9626a49c7524daa9`.

Therefore the chooser is fully vanilla again:

- Turtwig / Chimchar / Piplup preview sprites
- vanilla species-specific confirmation text
- vanilla Pokémon cries
- vanilla chooser state machine
- vanilla fades
- vanilla SysTask lifetimes
- vanilla teardown
- vanilla output contract

The current D8 logic outside the chooser is intentionally retained:

- `ScrCmd_SaveChosenStarter` still performs exactly one weighted 13-species Mystery Starter draw after chooser completion.
- `VAR_MYSTERY_STARTER_SPECIES` still stores the actual randomized species.
- `VAR_PLAYER_STARTER` still stores the canonical Turtwig/Chimchar/Piplup story/rival branch.
- Route 201 still returns to the field and directly awards the randomized species at Lv. 5.
- Native hatch presentation remains disabled.

The visible vanilla preview species are intentionally meaningless in this diagnostic build. The selected left/center/right position must not influence the random draw.

## Runtime test

Use a fresh launch / normal in-game save path. Do not rely on emulator save states.

1. Reach Route 201 and open the briefcase.
2. Confirm any of the three normal vanilla starter previews.
3. Observe whether the chooser fades out and Route 201 returns to the field.
4. If the field returns, verify that the Pokémon actually awarded can be one of the 13 Mystery Starter species rather than necessarily matching the preview.
5. Repeat at least once with a different chooser position if convenient.

Primary result is binary:

- **PASS-A:** chooser exits and field progression resumes.
- **FAIL-A:** same permanent black-screen hang occurs.

## Interpretation

### If PASS-A

The current post-choice Mystery Starter machinery is viable. The failure is inside the D8 chooser presentation delta eliminated by this build: the Egg-as-Pokémon preview path and/or its associated no-cry / neutral-text modifications.

Next build should reintroduce one chooser presentation change at a time. Recommended order:

1. vanilla chooser + neutral text/no cry, normal starter sprites;
2. vanilla behavior + Egg visual supplied as a non-Pokémon UI/2D sprite;
3. only if needed, isolate `SPECIES_EGG` through the Pokémon sprite manager by itself.

Preferred production architecture if the Egg Pokémon-sprite path is confirmed bad:

`vanilla chooser lifecycle -> Mystery Egg visual overlay -> confirm -> chooser fully exits -> weighted draw -> field-safe reveal/award`.

Do not put the hatch sequence back inside the chooser.

### If FAIL-A

The Egg visuals are innocent. Stop editing chooser presentation.

The next isolation target becomes the boundary immediately after the vanilla chooser:

1. vanilla chooser + vanilla `SaveChosenStarter` / vanilla award (baseline control);
2. vanilla chooser + weighted draw but no persistent Mystery variable;
3. vanilla chooser + weighted draw + variable persistence;
4. current Route 201 award path.

This becomes a strict bisection of post-choice D8 logic instead of speculative repair.

## ROM identity

The GitHub Actions artifact for this branch/PR must be treated as the test identity. Record:

- PR number
- PR head SHA
- workflow run ID
- revision (US rev 0 or 1)
- artifact name
- artifact SHA-256 if available

Do not infer identity from a local ROM filename alone.

## Merge rule

This diagnostic branch is evidence, not the final implementation. Do not merge Build A into main merely because it passes. Use the result to choose the next production fix.
