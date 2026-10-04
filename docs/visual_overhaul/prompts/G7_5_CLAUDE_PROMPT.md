# Claude Code Prompt — G7.5

Work on exactly one complete numbered section: **G7.5 — Global Window / Typography-Adjacent Polish** in `pokeplatinum-legacy`.

Start from current `main`.

Before implementation, read:
- `docs/visual_overhaul/G7_CLAUDE_EXECUTION_PROTOCOL.md`
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_DESIGN.md`
- only the **G7.5** section of `docs/visual_overhaul/G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md`
- `docs/visual_overhaul/G7_CLAUDE_HANDOFF.md`
- `docs/visual_overhaul/G7_2B_MESSAGE_FRAMES.md` as the immediately relevant prior implementation record

Treat those documents as canonical authority.

## Scope

Complete **all of G7.5** in this session.

Do **not** continue to G7.6 after G7.5 is complete.

Use/create branch:

`visual/g7-modern-ds-remaster`

If the branch already exists, verify it is clean and based on current `main` before changing anything.

## Token / time discipline

Use targeted searches first:
- `rg`
- `git grep`
- `find`
- narrow `sed -n`, `head`, or `tail`

Do not:
- recursively dump large directories;
- read huge unrelated source files in full;
- repeatedly reread canonical docs;
- narrate routine shell commands;
- perform broad repo archaeology after ownership is established.

Spend context on implementation and validation.

## G7.5 objective

Bring the remaining high-frequency global window/message chrome into the G7 Modern DS Remaster language without turning this section into a font-engine or text-renderer rewrite.

The target remains:
- modern DS remaster;
- premium on iPhone DS emulators;
- native 256×192 readability;
- strong contrast and hierarchy;
- preserved Pokémon/DS pixel-art language;
- no gameplay/input changes.

## Ownership audit first

Before editing, trace and document:
- which `res/graphics/windows/` assets are globally shared;
- which message frames are player-selectable;
- which assets are used by field dialogs, battle dialogs, menus, signs, prompts, egg hatch, and other high-frequency contexts;
- which palette entries are shared across frames;
- which assets are already generator-owned;
- whether any candidate change would affect decorative Frames 6–20.

Primary surfaces:
- `res/graphics/windows/`
- `tools/visual_overhaul/generate_ui_foundation.py`
- `tools/visual_overhaul/generate_message_frames.py`

Read source/window loading code only as needed to establish ownership and shared-resource behavior.

## Required implementation work

### 1. Standard field/system frames

Audit:
- `standard_field.png`
- `standard_system.png`

Modernize only where needed for consistency with G7.1–G7.4.

Goals:
- deep navy/charcoal structure;
- cool light panel surfaces;
- cleaner highlight/shadow hierarchy;
- no muddy beige/olive leftovers;
- readable at native DS resolution.

Preserve dimensions, tile contract, and message/window geometry.

### 2. Message-frame family

Audit `message_box_00` through `message_box_19`.

Existing G7.2B already modernized the plain high-frequency Frames 1–5.

Do not blindly recolor all 20 frames.

Rules:
- preserve decorative/player-choice Frames 6–20 unless there is a concrete G7 inconsistency that can be fixed safely;
- if a decorative frame is intentionally themed, preserve its identity;
- only normalize shared outline/highlight language where doing so does not erase its theme;
- do not change text field fill unless the font/window palette relationship is fully traced and safe.

### 3. Scroll cursor

Audit `scroll_cursor.png` and its existing generator ownership.

Goals:
- readable over every relevant frame;
- consistent with the G7 focus language;
- retain existing animation/frame count and timing;
- no change to printer behavior.

### 4. Wait dial

Audit `wait_dial.png`.

Goals:
- consistent G7 visual language;
- clear at native resolution;
- preserve frame count, sprite contract, and timing.

### 5. Typography-adjacent consistency

Audit high-frequency text/window presentation for obvious legacy mismatch.

Allowed:
- frame/panel palette improvements;
- cursor/wait indicator cleanup;
- spacing or frame-art changes that preserve geometry/contracts.

Do not:
- replace the core font;
- change font encoding;
- shrink text for aesthetics;
- change message speed;
- change line capacity;
- rewrite the text renderer;
- alter text-printer timing.

If the font pipeline is easy to trace, document findings only unless a change is clearly low-risk and materially necessary.

### 6. Per-context frame variants

Only implement a battle-only/field-only frame distinction if the existing resource contract makes it simple and safe.

If it requires invasive C changes or duplicated palette plumbing, defer it and document why.

## Implementation policy

Prefer, in order:
1. existing generator changes;
2. deterministic palette/resource changes;
3. limited asset art changes;
4. C changes only if necessary and low-risk.

For generator-owned assets:
- edit the generator;
- regenerate;
- rerun the generator;
- verify the second run produces no diff.

If a deterministic new transformation is needed, add a focused generator rather than a large generic framework.

Do not:
- modify gameplay;
- modify save structures;
- perform unrelated cleanup;
- reopen G7.1–G7.4 without a concrete regression;
- expand into G7.6 field-atmosphere work.

## Validation

During implementation, use only targeted previews/validators.

After **all G7.5 work is complete**:

1. rerun every touched generator and confirm no diff;
2. run all relevant visual/window validators;
3. add a focused G7.5 validator if current validators do not objectively protect the changed contracts;
4. run `python3 tools/overhaul/validate_overhaul.py --no-write` if shared integration/resource plumbing or C code changed;
5. build US Rev 0 once;
6. if Rev 0 succeeds, build US Rev 1 once;
7. fix localized failures and rerun only the failed check/build before final evidence.

Do not repeatedly build both revisions after cosmetic edits.

## Runtime boundary

Do not create:
- DeSmuME automation;
- headless gameplay harnesses;
- runtime bots;
- long-running emulator QA systems.

Runtime visual approval belongs to the owner.

A quick static preview/export is acceptable if it takes minutes.

## Documentation

Create/update:

`docs/visual_overhaul/G7_5_GLOBAL_WINDOWS.md`

Keep it concise. Include:
- ownership/resources traced;
- exact files changed;
- visual changes;
- functionality preserved;
- validators;
- Rev 0 / Rev 1 results;
- deferred invasive ideas;
- owner runtime checklist.

## Owner runtime checklist

Cover both portrait stacked and landscape side-by-side iPhone emulator layouts.

Check:
- ordinary field dialog;
- sign/text box;
- Yes/No prompt;
- battle message window;
- party/bag/summary help pane if it uses shared frames;
- egg hatch or another special text context;
- Frames 1–5;
- at least a few decorative Frames 6–20 to ensure no collateral damage;
- scroll cursor;
- wait dial;
- long wrapped messages.

Verify:
- no seams;
- no clipped borders;
- text remains readable;
- no palette clash;
- scroll/wait indicators remain visible;
- message timing and input behavior are unchanged.

## Commit / finish rules

Use one or a few coherent G7.5 commits. Avoid micro-commits.

Before finishing:
- `git status` clean;
- no temporary QA files;
- generated outputs match generators;
- no unrelated files staged.

## Stop rule

Once **all of G7.5** is implemented, validated, built, committed, and documented:

**STOP.**

Do not begin G7.6.

Return only:
- G7.5 completion status;
- commit SHA(s);
- validator results;
- Rev 0 result;
- Rev 1 result;
- deferred items;
- owner runtime checks;
- PR readiness.
