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
4. Read the design document and only the implementation-plan section relevant to the current batch, expanding context only when necessary.
5. Audit exact resource/code ownership for the current target using targeted search.
6. Preserve all gameplay and input semantics.
7. Prefer deterministic generator-backed assets.
8. Validate and build once at the end of the current batch.
9. Commit/document the current batch.
10. **Stop after the current batch. Do not automatically continue into the next numbered batch.**

## Current target

PR #50 merged G7.1A, G7.1B, G7.2A and G7.2B. G7.3 was audited and intentionally deferred for runtime-sensitive additions.

**Current implementation target: G7.4A — Party + Summary modernization.**

Execute only G7.4A in the next session. Do not continue to G7.4B after completion.

Party goals:
- stronger selected member card;
- clearer HP/status hierarchy;
- preserve member-ball/icon/touch semantics;
- preserve cell/OAM geometry unless a demonstrable requirement forces a layout change.

Summary goals:
- modernize tab hierarchy;
- strengthen page section separation;
- prioritize move/stat data;
- preserve every page, including contest/ribbon content;
- strengthen move-selection focus.

Use the existing generators first:
- `tools/visual_overhaul/generate_party_menu_ui.py`
- `tools/visual_overhaul/generate_summary_ui.py`

## Validation

At minimum after the first batch:
- relevant visual validators;
- generator rerun produces no diff;
- core master validator if integration touches shared code/resource plumbing;
- US Rev 0 build;
- US Rev 1 build.

Commit the first batch separately and record what changed before moving to G7.1B.
