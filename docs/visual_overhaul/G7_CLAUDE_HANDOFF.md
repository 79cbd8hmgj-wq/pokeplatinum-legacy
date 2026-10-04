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

PR #50 merged G7.1A, G7.1B, G7.2A and G7.2B. G7.3 was audited and intentionally deferred for runtime-sensitive additions. PR #53 merged the complete G7.4 core-menu section.

**Current implementation section: G7.5 — Global Window / Typography-Adjacent Polish.**

Complete all of G7.5 in one Claude session.

Goals:
- audit the full message-box/window frame family before changing shared resources;
- modernize standard field/system frames where needed for G7 consistency;
- modernize scroll cursor and wait dial where needed;
- remove remaining high-frequency beige/olive or mismatched legacy chrome;
- keep text readability and printer behavior unchanged;
- preserve message speed, line capacity, encoding, and font behavior;
- do not replace the core font unless the font pipeline is first proven safe and the benefit clearly justifies it;
- use per-context frame variants only if the current resource contract supports them cleanly and without invasive source work.

Primary source surfaces:
- `res/graphics/windows/`
- `tools/visual_overhaul/generate_ui_foundation.py`
- `tools/visual_overhaul/generate_message_frames.py`
- existing window/message-box load paths only where ownership must be traced

Implementation principle:
- first determine which assets are global vs player-selectable decorative frames;
- preserve decorative Frames 6–20 unless a concrete high-frequency inconsistency requires action;
- prefer generator-backed palette/art updates over C changes;
- do not turn G7.5 into a font-engine or text-renderer rewrite.

Do not continue to G7.6 in the same session.

## Validation

At the end of the full G7.5 section:
- relevant window/frame/UI validators;
- rerun every touched generator and confirm no diff;
- core master validator if shared integration/resource plumbing is changed;
- US Rev 0 build;
- US Rev 1 build;
- concise G7.5 implementation report;
- clean git status.

Then stop before G7.6.
