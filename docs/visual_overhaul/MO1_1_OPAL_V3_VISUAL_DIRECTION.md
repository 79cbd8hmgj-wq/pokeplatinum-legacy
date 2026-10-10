# MO1-1 Opal Bag V3 visual direction (prototype, not implemented)

## Design decision
V2 is the preferred stylistic basis: original Opal identity, not retail Platinum and not neon/terminal UI. V3 refines V2's same 256×192 screen arrangement. The user approved V2's direction, **not** every V3 pixel or screen ownership.

## Prototype contract
- Keep nine visible item rows, quantities, prominent selection state and a three-line-capable description region.
- Keep a six-button example pocket grid, but **do not mistake it for the source's 1/4/7/8 pocket variants**.
- Retain stylus dial affordance in the example; hitboxes are illustrative, not verified against current input regions.
- Keep existing action eligibility and item behavior untouched. The prototype's button legend must be cross-checked against actual mappings.
- Current game renders main-engine item list/description and sub-engine pocket dial; do not treat screen relocation as a simple graphical change.

## V3 style tokens
- Framing: mineral slate/violet (`#34354A`, `#3F3B52`).
- Primary surfaces: fogged porcelain and pearl (`#FAF6F4`, `#F0E9EC`).
- Selection: muted amethyst (`#D8CBDC`, edge `#865D82`).
- Secondary accents: opal blue-green `#8EA5A5`; antique gold `#C4A87B`.
- Text: deep violet/ink `#292D40`; avoid low-contrast pale text.
- Form: layered corners, short highlight strokes, restrained faceted emblem; **no circuitry, neon, hologram styling, or blanket return to vanilla Platinum**.

## Implementation boundaries
The supplied editable Python prototype creates two independent 256×192 PNGs and a 3× composite. These are **visual mockups**, not converted NCGR/NSCR/NCLR game graphics, not a tested ROM, and not evidence of touch target viability. Real tile/palette budgeting, item icon placement, string metrics, dynamic rendering and special modes remain to be proved.

## Next engineering gate
1. Measure font wrapping and item list line heights on hardware/emulator.
2. Audit all multi-pocket touch areas, dial behaviors and special Bag modes.
3. Translate the approved color/material tokens to legal palettes and tilesets.
4. Implement in an isolated graphics + windows branch, build both revisions, collect side-by-side in-game screenshots.
5. Add action ribbon only after reusing existing eligibility/dispatch and passing interaction tests.
