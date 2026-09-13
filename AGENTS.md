# Codex Planning Instructions — Pokémon Platinum Overhaul

## Role split

Use **Codex `/plan` as the primary design-planning agent** for future overhaul phases.

- **Codex `/plan`**: investigate the repository, recover relevant existing authority, compare Emerald/Platinum systems when applicable, and draft new design plans.
- **User**: approves/rejects major design decisions and determines when a plan becomes locked authority.
- **Claude Code**: implements only approved/locked plans and canonical manifests; it must not redesign them during implementation.
- **ChatGPT project coordination**: reviews/reconciles planning output against existing locked authority, maintains canonical status/spec organization, and catches contradictions or accidental redesigns.

Do not use Claude Code as the default design-planning agent when `/plan` can do the planning first.

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

Use `/plan` primarily for genuinely unfinished design areas, including:

- #001–#493 world/encounter availability architecture
- trainer overhaul
- Emerald → Platinum EXP/economy port
- Poké Ball rebalance port
- breeding-system port
- Legendary/Mythical event restoration
- Battle Frontier/postgame
- final integration/QA design

Evolution is not a blank design phase: its rules were locked in Pass A. Planning there should focus on **manifest recovery, source mapping, item-access dependencies, implementation sequencing, and verification**, not redesigning evolution methods from scratch.

## Emerald reuse rule

For systems already solved in Emerald, `/plan` must begin with the Emerald implementation/design rather than inventing a fresh Platinum system.

Classify each feature as:

- `DIRECT PORT`
- `ADAPT`
- `PLATINUM-SPECIFIC`
- `DEFER`

Then explain exactly what behavior carries over and what Platinum-specific changes are necessary.

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
- `APPROVED PLAN` — user approved direction, ready to canonicalize
- `LOCKED SPEC` — repo canonical authority, safe for Claude implementation
- `IMPLEMENTING`
- `IMPLEMENTED`
- `VERIFIED`

A `/plan` result is **not automatically locked** merely because it is thorough.

## Handoff rule

Before Claude begins implementing a newly designed subsystem, the approved plan must be converted into a canonical repo spec/manifest with explicit acceptance criteria.

Claude should be able to implement from the repository alone without needing the planning chat.

## Anti-regression rules

- Do not re-plan work merely because its old chat is unavailable if repo authority already exists.
- Do not infer missing locked values from general Pokémon knowledge.
- Do not replace a Generation IV-specific decision with a modern-generation convention unless explicitly approved.
- Do not broaden scope during planning just because a nearby system could also be improved.
- Preserve the overhaul's single-save, low-grind, Gen-IV-first identity.
