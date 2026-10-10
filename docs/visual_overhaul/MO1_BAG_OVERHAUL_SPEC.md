# MO1 — Pokémon Opal Bag UX / Visual Overhaul

Status: DESIGN SPEC / implementation pending. Scope: a substantially improved DS-native Bag, not cosmetic cursor/fade tweaks. Core item rules and Bag special modes preserved.

## Verified current source baseline
- `src/applications/bag/main.c`: list menu cursor and print callbacks, pocket changes by D-pad and touch, dial scrolling, per-pocket cursor restoration, Select-based item moving, context-sensitive action creation, normal and special Bag modes (sell, give, gardening, Poffin).
- `src/applications/bag/windows.c`: `BagUI_PrintItemDescription` already presents descriptions on selection; `BagUI_PrintTMHMMoveStats` already handles specialized TM/HM information; action menus are dynamically created by `BagUI_ShowItemActionsMenu`.
- `src/applications/bag/sprites.c`: pocket focus, item highlight, Bag sprite/selection animations.
- `res/graphics/bag/`: editable sheets, palettes, tilemaps, sprite animations and cell data.
- AV3-A menu highlight motion and AV3-C entrance fade are minor baselines, not objectives to repeat.

## User-facing goals and acceptance criteria

1. **Find:** the selected item, amount, and category are identifiable at a glance without extra button presses. Preserve text readability on 256×192 screens.
2. **Understand:** the item description remains available; TM/HM details receive an explicit move-information state without hiding key controls.
3. **Act:** available primary actions are exposed clearly without circumventing retail eligibility decisions or modes. No prohibited action may be accessible.
4. **Navigate:** pocket switching and item movement remain D-pad + touch usable. Preserve and improve cursor/pocket persistence, cancel behavior, wrap and empty-list states.
5. **Present:** replace generic panel hierarchy, iconography and context indicators with one coherent Opal art language; use motion to explain changes, not as decoration.
6. **Measure:** capture actual baseline and redesigned input counts for Use, Give, Register, switch pocket, scroll, sort, and inspect TM/HM; show before/after screen captures by the owner in emulator. No unverified performance claims.

## Proposed information architecture (requires layout feasibility check)

**Main screen**: strong item identity (icon/name/count), item category, concise description with readable wrapping, one context detail card (TM/HM type/PP/category; otherwise item-dependent details), and clear mode/status.

**Touch screen**: primary browse/act surface: persistent pockets affordance, item list with clear selected row, contextual action strip on normal-mode valid item selection, and non-overlapping cancel/back path. Prefer large touch targets and button parity. Exact top/sub arrangement must follow the existing Bag rendering/input bindings; don't blindly exchange screens.

**Action strip**: compute available actions from the SAME existing item-action decision tree as `MakeItemActionsMenu`, never recreate permissibility rules from item names. Default suggested action only when legal in current mode. Destructive commands (Trash) remain confirmation-gated.

**Modes**: normal, sell, item-use prompt, give-to-mon, gardening, multiplayer/Poffin, list sorting, item quantity and message dialogs have explicit presentation and regression criteria. Do not flatten these states into normal-mode shortcuts.

## Implementation architecture

### Phase MO1-1: full layout + panel composition
- Map the actual BG layer/window and sprite placement for each DS screen; verify VRAM/window/OAM/palette budgets and touch hitboxes before approving coordinates.
- Implement coherent new Bag panels and icons within existing `res/graphics/bag/` pipeline. Optimize legibility at real DS resolution and preserve font metrics.
- Display contextual item data without redraw flicker using existing cursor callback and update scheduling.
- Build normal, TM/HM, empty pocket, and long-name screenshots for owner review.

### Phase MO1-2: interaction efficiency
- Reuse `MakeItemActionsMenu` eligibility and dispatch. Present a quick action strip and preserve full context menu fallback.
- Keep shoulder/D-pad/touch parity; avoid adding input conflicts with wheel, sorting and quantity dialogs.
- Count button presses for common tasks, aim for meaningful reduction rather than mere animations.

### Phase MO1-3: presentation and integration
- Cohesive focus transitions, pocket/category changes, action confirmation and cancellation feedback. Animations short and interruptible; no unnecessary input lockouts.
- Test mode/state matrix, long strings, localization, empty inventory, disabled actions, touch edges, repeated pocket switch, and fast selection changes.

## Guardrails
No bag capacity changes, item effects, move or Pokémon-system changes, inventory corruption risk, new gameplay functionality, or overengineering. DS hardware is the platform ceiling; GBA-era design conventions are not a requirement.

## Workflow and ownership
ChatGPT: research, inspect code, design, compare donor assets, write specs and manageable patches, review CI. Claude Code: only difficult implementation tasks identified after exact source mapping. GitHub Actions: rev0/rev1 builds. Owner: actual ROM launch, visual/runtime checks and acceptance.

A successful MO1 is recognizably redesigned and measurably more convenient. A cursor wobble or fade-order change is NOT a completed MO1.
