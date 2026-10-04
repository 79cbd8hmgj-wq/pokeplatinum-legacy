# G7 — Claude Code Handoff

Use this file together with:
- `docs/visual_overhaul/G7_CLAUDE_EXECUTION_PROTOCOL.md` — operational/session rules
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_DESIGN.md` — design authority
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md` — implementation authority

## Execution mandate

Implement G7 as an escalation of the existing Pass G visual overhaul. Do not redesign from memory and do not restart from retail Platinum assets.

The user has already approved the G7 direction:
- modern DS remaster;
- designed for DS emulation on iPhone;
- dual-screen/touch semantics preserved;
- more immersive and intense;
- willing to stray from retail Platinum authenticity;
- runtime visual approval will be handled by the user.

## Required workflow

1. Start from current `main`.
2. Create/use `visual/g7-modern-ds-remaster`.
3. Read `G7_CLAUDE_EXECUTION_PROTOCOL.md` first and obey its bounded-session rules.
4. Read the design document and only the implementation-plan section relevant to the current numbered section, expanding context only when necessary.
5. Audit exact resource/code ownership for all subparts of the current section using targeted search.
6. Preserve all gameplay and input semantics.
7. Prefer deterministic generator-backed assets.
8. Complete all subparts in the current numbered section before final validation.
9. Validate and build once at the end of the numbered section.
10. Commit/document the section, then **stop before the next numbered G7 section**.

## Current target

PR #50 merged G7.1A, G7.1B, G7.2A and G7.2B. G7.3 was audited and intentionally deferred for runtime-sensitive additions.

**Current implementation section: G7.4 — Core Menu Modernization.**

Complete **all of G7.4 in one Claude session**:

### G7.4A — Party + Summary
Party:
- stronger selected member card;
- clearer HP/status hierarchy;
- preserve member-ball/icon/touch semantics;
- preserve cell/OAM geometry unless a demonstrable requirement forces a layout change.

Summary:
- modernize tab hierarchy;
- strengthen page section separation;
- prioritize move/stat data;
- preserve every page, including contest/ribbon content;
- strengthen move-selection focus.

Use first:
- `tools/visual_overhaul/generate_party_menu_ui.py`
- `tools/visual_overhaul/generate_summary_ui.py`

### G7.4B — Bag + Start + Shop
Bag:
- cleaner pocket identity;
- stronger item focus;
- clearer quantity/value hierarchy;
- preserve pocket switching and touch behavior.

Start menu:
- stronger icon/focus hierarchy;
- more deliberate panel composition;
- preserve menu topology and input semantics.

Shop / secondary UI:
- bring shop chrome into the same G7 language;
- preserve default vs Frontier shop identity;
- avoid unnecessary layout changes.

Use first:
- `tools/visual_overhaul/generate_bag_ui.py`
- `tools/visual_overhaul/generate_start_menu_ui.py`
- `tools/visual_overhaul/generate_shop_ui.py`
- `tools/visual_overhaul/generate_ui_foundation.py` only where shared chrome requires it.

Finish G7.4A, then continue directly into G7.4B **without running full Rev 0/Rev 1 builds between them**. Run final validation/builds only after all of G7.4 is complete.

Do not continue to G7.5 in the same session.

## Validation

At the end of the full G7.4 section:
- relevant visual validators for Party, Summary, Bag, Start, Shop, and shared chrome;
- rerun every touched generator and confirm no diff;
- core master validator if integration touches shared code/resource plumbing;
- US Rev 0 build;
- US Rev 1 build;
- concise G7.4 implementation report;
- clean git status.

Then stop before G7.5.
