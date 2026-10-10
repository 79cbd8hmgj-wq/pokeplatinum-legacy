# MO1 — Pokémon Opal Bag Modernization (DS-native, 2026 UX)

Status: **DESIGN SPEC / NOT IMPLEMENTED**. This is an outcome-driven UI overhaul, not another sprite-animation pass.
Scope: Bag interface only, existing Bag modes and save format preserved. Runtime/visual QA belongs exclusively to project owner.

## 1. Observed source baseline (not assumptions)

- `include/applications/bag/defs.h`: `BAG_UI_NUM_VISIBLE_ITEMS = 9`; controller already owns list, item description, pocket names, item action windows, quantity/money/status windows, touch selectors, and saved cursor positions.
- `src/applications/bag/windows.c`: item list sits on main BG2 at (14,0), width 17 tiles; description main BG0 at (0,18), width 32 tiles, 3 text lines. The description is **already present**: do not claim the redesign invents it.
- `src/applications/bag/main.c`: pocket switching via D-pad and touch, remembered pocket position/scroll, contextual use/give/register/trash actions, moving/sorting items, and mode-specific flows already exist.
- `res/graphics/bag/`: editable tilemap, tileset/palette, highlights, buttons, pocket icons, and NANR resources. AV3-A already animated the item/pocket highlights; do not repeat the work.
- `BagApplicationMode` includes normal, give-to-Pokémon, sell, gardening, Poffin single/multiplayer; all require compatibility.

## 2. Success criteria (compared against retail and current Opal)

- On opening Bag, selected item **name, count, description and context** are legible without navigating to a second page.
- Switching pockets remains direct and restores the prior per-pocket selection.
- Common selection-to-action interactions should take fewer button presses/touches than retail, without bypassing destructive confirmations.
- A first-time player can distinguish selected item, available actions, current pocket, and scroll position at a glance.
- No layout depends on stylus precision alone; full D-pad/A/B/L/R parity must be preserved or improved.
- Visible redesign: re-authored panel composition and hierarchy, not merely a palette tweak, fade order, or 1px cursor animation.
- Stable 60fps input responsiveness where feasible and no regression in existing modes. Frame rate is a target, not a verified result.

## 3. Proposed information architecture

**Primary concept: list + contextual inspector.** Preserve the functioning 9-row list and its existing touch scroll behavior while redesigning the surrounding framing. Use the available dual screens as an enhancement rather than requiring moving all content to a new engine.

- Main/top: prominent category and selected-item inspector with name, icon, quantity, description, and relevant item context (e.g., key/registered, TM/HM details where data is available); decorative Bag art should not displace needed information.
- Sub/touch: compact pocket navigation, item list or direct-selection controls, clear action affordances.
- **Important migration gate:** retail list and description currently live on main BG layers. This split-screen concept requires verified BG/window and touch routing changes; it is NOT already implemented or a trivial asset swap. If two-screen relocation is costly, first ship a re-composed layout on current screens that keeps the existing list/description ownership, then migrate only with proved input/render contracts.
- Prefer a clear focus state, legible contrast, and consistent Opal iconography. Original 256×192 per screen; do not reduce touch targets for visual density.

## 4. Interaction design

**Navigation:** D-pad moves selected item; L/R changes accessible pockets immediately; touching pocket selector chooses pocket; B backs out/cancels; A opens relevant action. Retain dial scrolling and remembered scroll/position. Verify L/R mapping in source before changing controls; these are target bindings if not already wired.

**Contextual action ribbon:** show at most 2–3 applicable actions around the selected item (e.g., Use, Give, Register) with clear primary action; do not present invalid verbs. A remains equivalent to the menu for compatibility. The action menu is still available for less-common options (move/sort, item check, toss). No automatic use, giving, selling or trashing; preserve prompts, limitations and item hooks.

**Quantity:** explicitly show item count, and compact quantity control only when in a quantity-selecting mode. Selling, tossing, teaching TMs, key items, berries and registered items have different contracts; cannot share blind shortcuts.

**Transitions:** pocket switch should keep context stable; brief content change animation may be used only when it does not delay input or destabilize text rendering. Do not do another fade-only milestone.

## 5. Visual identity

- Palette: Opal-specific neutral/dark framing with restrained gemstone accents **subject to legibility and DS palette budget**; preserve type/status/icon readability.
- Consistent high-contrast selection row, clear category label, compact metadata grid; large item icon or preview only if existing sprite/icon pipelines can supply it affordably.
- Animated transitions communicate state (pocket changed / action invoked / item selected) and must be nonblocking.
- Preserve pixel-friendly DS typography, no assumed antialiasing/high-resolution fonts.

## 6. Implementation boundaries

Candidate source hosts: `src/applications/bag/main.c`, `windows.c`, `sprites.c`, corresponding `include/applications/bag/` definitions and `res/graphics/bag/` tilemap/tiles/cells/animation assets.

First implementation should be **one coordinated, visible menu redesign PR**, comprising:
1. redesigned panel layout and tile art;
2. clearer selected-item inspector and hierarchy;
3. context-action presentation with existing action handler routing;
4. improved pocket selection feedback without new delay;
5. relevant static validators and builds.

Keep application modes, list contents, item effects, save data, registered item behavior, special inventory cases and input accessibility unchanged unless separately proven and approved. Prefer original DS tile/window/sprite systems. No new generic UI framework or 3D renderer.

## 7. Engineering checks before editing code

- Verify which BG layers are shown on MAIN vs SUB, item icon ownership, and touch rectangles; map all window coordinates and overlaps.
- Measure BG tile/VRAM/OAM/palette budgets against actual existing assets and NARC order; don't assume free memory.
- Inspect `BagApplication_Main` state flow for opening actions, quantities, sorting, selling, berry tags, TMs, Poffin modes and returns from Party screen.
- Identify actual high-frequency button paths and count presses before and after; no hypothetical efficiency claim.
- Retain the original nine-row list or justify any replacement against touch targets, rendering contracts and scrolling performance.

## 8. Acceptance checklist

- Side-by-side real DS screenshots show a substantial improvement in item information hierarchy, selected-item legibility, and action discoverability.
- Normal, give, sell, gardening, and Poffin flows work; pocket count variations (1/4/7/8) and empty-item states remain correct.
- List scroll, item sorting, pocket switch, touch and buttons, selected quantity, registration, TM/HM, key items, berries, and cancellation covered.
- Both US ROM revisions compile and static asset checks pass.
- No gameplay/item metadata changes unless separately approved.
- Emulator, runtime, visual and usability acceptance performed exclusively by project owner.

## 9. Delivery approach

ChatGPT owns design, source mappings, compact source-level patches and PR review. Claude is reserved for a proven multi-file integration blocker. Avoid launching isolated PRs for cursor movement or fade timing. Current AV3 patches are preserved, but MO1 replaces micro-adjustments as the next visual goal.

Next engineering activity: audit exact Bag window/BG routing and action-state hooks, then design/review an integrated **two-screen wireframe** and implement a single substantial Bag redesign.
