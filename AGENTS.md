# Codex Planning Instructions — Pokémon Platinum Overhaul

## Official role split

For all future unfinished overhaul phases:

- **Codex `/plan` owns design planning.** It investigates the repo, studies relevant source and prior Emerald work, proposes the subsystem design, resolves sequencing/dependency questions, and produces an implementation-ready plan.
- **User approves or rejects the plan.** User approval is required before a design becomes locked authority.
- **Claude Code owns implementation.** Claude implements approved/locked Codex plans, performs source investigation needed for implementation, validates/builds/tests the result, and reports implementation blockers. Claude does not redesign approved systems.

This is the default project workflow:

> **Codex `/plan` → user approval → canonical plan/spec → Claude Code implementation → validation/status update**

Do not hand future design ownership to Claude Code. Do not begin implementation of a genuinely unfinished subsystem until Codex has planned it and the user has approved the direction.

## Mandatory read order before planning

Before proposing a design plan, inspect:

1. `docs/overhaul/MASTER_PLAN.md`
2. `docs/overhaul/STATUS.md`
3. `docs/overhaul/MASTER_SPEC.md`
4. `docs/overhaul/RECOVERY_INDEX.md`
5. `docs/overhaul/EMERALD_PORT_PLAN.md`
6. the relevant subsystem spec/manifests under `docs/overhaul/`
7. current `main` source for the subsystem being planned

When planning touches an already implemented subsystem, inspect current source/commit history before assuming it is unfinished.

## Locked work must not be redesigned

Unless the user explicitly asks to reopen it, treat the following as existing authority rather than new design work:

- Pass A/B species identity work
- Pass C1 existing-move rebalance
- Pass C2 TM/HM design already canonicalized
- Pass C2.5 created moves
- Pass C3 learnsets/species compatibility
- locked Pass A evolution design

Historical chats/proposals are not authority when canonical repo documentation exists.

If repo documents disagree, identify the contradiction instead of silently choosing one.

## Planning target

Use `/plan` for genuinely unfinished design areas, especially:

- #001–#493 world/encounter availability architecture
- trainer overhaul
- Emerald → Platinum EXP/economy port
- Poké Ball rebalance port
- breeding-system port
- Legendary/Mythical event restoration
- Battle Frontier/postgame
- final integration/QA design

Evolution is not a blank design phase: its rules were locked in Pass A. Codex planning there should focus on manifest recovery, source mapping, item-access dependencies, implementation sequencing, and verification—not redesigning evolution methods from scratch.

## Emerald reuse rule

For systems already solved in Emerald, `/plan` must begin with the Emerald design and implementation rather than inventing a fresh Platinum system.

Classify each feature as:

- `DIRECT PORT`
- `ADAPT`
- `PLATINUM-SPECIFIC`
- `DEFER`

Then specify exactly what behavior carries over and what Platinum-specific changes are necessary.

## Required plan structure

A design plan should contain, at minimum:

1. **Goal and scope**
2. **Existing locked authority** — what must not be changed
3. **Current Platinum source reality** — relevant files/systems/engine behavior
4. **Emerald precedent** — when applicable
5. **Design decisions to make** — only genuinely unresolved decisions
6. **Recommended design** with rationale
7. **Alternatives considered** and why they are weaker
8. **Dependencies and sequencing**
9. **Data/manifests/specs that must be produced**
10. **Implementation handoff for Claude** — concrete source/data targets, not vague prose
11. **Validation/acceptance criteria**
12. **Open questions requiring user approval**
13. **Repo documentation updates required after approval**

Prefer concrete tables and machine-readable deliverables where the subsystem is data-heavy.

## Plan status lifecycle

Use these states:

- `DRAFT PLAN` — Codex proposal, not authority
- `APPROVED PLAN` — user approved direction
- `LOCKED SPEC` — canonical repo authority; Claude may implement
- `IMPLEMENTING`
- `IMPLEMENTED`
- `VERIFIED`

A `/plan` result is not automatically locked merely because it is thorough.

## Handoff rule

Before Claude begins implementing a newly designed subsystem, the approved Codex plan must exist in the repository as a canonical spec/manifest with explicit acceptance criteria.

Claude should be able to implement from the repository alone without needing the planning conversation.

## Anti-regression rules

- Do not re-plan work merely because its old chat is unavailable if repo authority already exists.
- Do not infer missing locked values from general Pokémon knowledge.
- Do not replace a Generation IV-specific decision with a modern-generation convention unless explicitly approved.
- Do not broaden scope during planning just because a nearby system could also be improved.
- Preserve the overhaul's single-save, low-grind, Gen-IV-first identity.
