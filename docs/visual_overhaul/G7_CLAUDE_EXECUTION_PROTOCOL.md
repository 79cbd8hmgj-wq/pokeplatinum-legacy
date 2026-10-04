# G7 — Claude Code Execution Protocol

Status: **OPERATIONAL AUTHORITY FOR CLAUDE SESSIONS**

This file governs *how* Claude Code should execute the already-approved G7 design and implementation plan.

Design authority remains:
- `G7_MODERN_DS_REMASTER_DESIGN.md`

Implementation authority remains:
- `G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md`

This protocol exists to reduce token waste, avoid runaway sessions, keep phases bounded, and produce merge-ready work quickly.

## 1. Session scope rule

**One complete numbered G7 section per Claude session.**

Examples:
- G7.4 means complete **all of G7.4A + G7.4B** in one session.
- G7.5 means complete the whole global-window / typography-adjacent section.
- G7.6 means complete the whole overworld-atmosphere section.

Subparts inside a numbered section are implementation checkpoints, **not separate Claude sessions**.

Do not automatically continue into the next numbered section after the current section is complete.

At the end of the section:
1. run the section's complete validation set once;
2. build Rev 0 and Rev 1 once;
3. commit coherent subparts as needed;
4. write/update the section report;
5. stop and return a concise status summary.

This replaces both the earlier open-ended "continue through the plan" behavior and the overly narrow one-subpart-per-session rule.

## 2. Context / token discipline

Do not spend context re-reading the entire repository.

At session start, read only:
1. this execution protocol;
2. the G7 design document;
3. the relevant section of the G7 implementation plan for the current section;
4. the latest implementation report for the immediately preceding batch if relevant;
5. the exact source/assets/generators touched by the current section.

Use targeted search first:
- `rg`
- `git grep`
- `find`
- narrow `sed -n` / `head` / `tail`

Avoid:
- recursively dumping large directories;
- reading large unrelated source files in full;
- repeatedly reopening the same files;
- narrating every shell command;
- broad repo archaeology after ownership is already established.

If a large source file is relevant, search for symbols first and read only the surrounding ranges.

## 3. Time discipline

Target execution pattern:

### Discovery
Target: **10–20 minutes for the entire numbered section**
- identify ownership for all subparts before deep implementation;
- identify shared-resource risk;
- identify existing generators/validators;
- decide the lowest-risk path for each subpart.

If ownership for one subpart is still unclear after targeted search, isolate that subpart rather than re-auditing the whole repository.

### Implementation
Target: **30–70 minutes for the entire numbered section**
- complete every required subpart in the numbered section;
- prefer palette/asset/generator changes over C changes where the design can be achieved safely;
- finish one subpart before moving to the next;
- avoid optional enhancements that expand beyond the numbered section.

### Validation
Target: **15–30 minutes**
Run the complete section validation once after all subparts are implemented.

Do not run full dual-revision builds between subparts unless a specific failure requires it.

Do not spend an hour building experimental runtime harnesses.

## 4. Build strategy

Avoid redundant builds.

During implementation:
- use generator/validator checks;
- use targeted compile/resource checks if available.

At the **end of the section only**:
1. run relevant G7 visual validators;
2. rerun all touched generators and confirm no diff;
3. run `python3 tools/overhaul/validate_overhaul.py --no-write` if shared integration/code/resource plumbing changed or if the section plan requires it;
4. build US Rev 0;
5. build US Rev 1.

Do not repeatedly rebuild both revisions after every small edit unless a failed build requires a correction.

If a build fails:
- diagnose the first actionable error;
- fix it;
- rerun only the failed build first;
- once clean, run the other revision for final evidence.

## 5. Runtime boundary

The owner handles runtime visual approval on iPhone DS emulators.

Claude must **not** spend substantial session time creating headless emulator harnesses, automated gameplay bots, temporary runtime patches, or DeSmuME automation unless the user explicitly asks for runtime automation.

For G7 visual work, Claude's runtime responsibility is:
- prepare a concise owner checklist;
- identify exactly what screenshots/states should be checked;
- leave runtime-only subjective decisions to the owner.

A small one-off local preview/export is acceptable if it takes minutes, not an open-ended emulator debugging session.

## 6. Decision policy

The approved design already answers ordinary aesthetic questions.

Claude should decide routine details autonomously using this order:

1. preserve functionality;
2. satisfy G7 design;
3. prefer the lowest-risk native Platinum path;
4. preserve existing Pass G work;
5. prefer deterministic generator-backed edits;
6. preserve resource contracts;
7. defer optional invasive ideas.

Do not ask the user to choose between minor palette values, border thicknesses, or equivalent implementation details unless the choice changes the approved design direction.

## 7. Scope-control rules

For the current section:

**Required work gets implemented.**
**Optional work gets implemented only if it is low-risk and naturally falls out of the required work.**
**Anything invasive gets documented for later.**

Do not:
- fix unrelated gameplay issues;
- redesign another menu because it is nearby;
- refactor large systems for cleanliness;
- add new renderers when an existing system can satisfy the requirement;
- reopen already-accepted G7 batches without a concrete defect.

## 8. Generator ownership

If an asset is generator-owned:
- edit the generator, not just the generated file;
- regenerate output;
- rerun the generator;
- verify the second run produces no diff.

If an asset is not yet generator-owned and the transformation is deterministic:
- add a focused generator;
- do not build a giant generic framework unless multiple current assets need it.

## 9. Documentation budget

Do not write hundreds of lines of narrative for every batch.

Each section report should be concise and contain:
- ownership trace;
- exact files changed;
- what changed visually;
- functionality preserved;
- validation/build results;
- deferred items;
- owner runtime checklist.

Prefer tables and short bullets over long prose.

## 10. Commit policy

Use one coherent commit per major subpart where useful, but avoid micro-commits.

For example, a G7.4 session may reasonably produce:
- G7.4A Party + Summary
- G7.4B Bag + Start + Shop
- G7.4 documentation/validation update

or fewer commits if the changes are tightly coupled and easy to review.

Do not stop the session after G7.4A; complete G7.4B before final validation and handoff.

Before finishing:
- `git status` must be clean;
- generated artifacts must match generators;
- temporary QA files/harnesses must not remain;
- no unrelated files should be staged.

## 11. Stop conditions

Stop the session only after the **entire current numbered G7 section** is complete.

Stop early only if:
- ownership cannot be established safely;
- a required design goal would require gameplay/save-format changes;
- shared palette/resource effects cannot be isolated safely;
- the only path is opaque binary patching without a verified contract;
- build failure remains non-local after one focused diagnosis/fix pass.

When stopping for a blocker, report:
- exact blocker;
- files/symbols involved;
- what was tried;
- safest next option.

## 12. Final response format

Keep the final Claude response short.

Report:
- batch completed;
- commits;
- validators;
- Rev 0 / Rev 1 build result;
- deferred items;
- exact owner runtime checks;
- PR readiness.

Do not include a long replay of the work log.

## Current G7 checkpoint

Merged on `main`:
- G7.1A command menu — implemented
- G7.1B move selection — implemented
- G7.2A healthboxes — implemented
- G7.2B message frames — implemented
- G7.3 encounter intensity hierarchy — audited; risky runtime-sensitive additions intentionally deferred
- G7.4 core menus — implemented and merged via PR #53:
  - Party
  - Pokémon Summary
  - Bag
  - Start Menu
  - Shop / secondary UI

**Next implementation section: G7.5 — Global Window / Typography-Adjacent Polish.**

