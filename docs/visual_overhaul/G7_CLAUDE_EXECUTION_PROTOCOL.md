# G7 — Claude Code Execution Protocol

Status: **OPERATIONAL AUTHORITY FOR CLAUDE SESSIONS**

This file governs *how* Claude Code should execute the already-approved G7 design and implementation plan.

Design authority remains:
- `G7_MODERN_DS_REMASTER_DESIGN.md`

Implementation authority remains:
- `G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md`

This protocol exists to reduce token waste, avoid runaway sessions, keep phases bounded, and produce merge-ready work quickly.

## 1. Session scope rule

**One implementation batch per Claude session.**

A batch may contain tightly coupled subparts already grouped by the implementation plan, for example:
- G7.4A = Party + Summary
- G7.4B = Bag + Start + Shop

Do not automatically continue into the next numbered batch after the current batch is complete.

At the end of the batch:
1. validate;
2. build;
3. commit;
4. write/update the batch report;
5. stop and return a concise status summary.

This replaces the earlier open-ended "continue through the plan" behavior.

## 2. Context / token discipline

Do not spend context re-reading the entire repository.

At session start, read only:
1. this execution protocol;
2. the G7 design document;
3. the relevant section of the G7 implementation plan for the current batch;
4. the latest implementation report for the immediately preceding batch if relevant;
5. the exact source/assets/generators touched by the current batch.

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
Target: **10–15 minutes**
- identify ownership;
- identify shared-resource risk;
- identify existing generator/validator;
- decide lowest-risk implementation path.

If ownership is still unclear after targeted search, spend at most one additional focused investigation pass before reporting a blocker.

### Implementation
Target: **20–40 minutes**
- make the smallest coherent change that satisfies the batch;
- prefer palette/asset/generator changes over C changes where the design can be achieved safely;
- avoid optional enhancements that expand the batch.

### Validation
Target: **15–25 minutes**
Run only the validation required to prove the batch.

Do not spend an hour building experimental runtime harnesses.

## 4. Build strategy

Avoid redundant builds.

During implementation:
- use generator/validator checks;
- use targeted compile/resource checks if available.

At the **end of the batch only**:
1. run relevant G7 visual validators;
2. rerun all touched generators and confirm no diff;
3. run `python3 tools/overhaul/validate_overhaul.py --no-write` if shared integration/code/resource plumbing changed or if the batch plan requires it;
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

For the current batch:

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

Each batch report should be concise and contain:
- ownership trace;
- exact files changed;
- what changed visually;
- functionality preserved;
- validation/build results;
- deferred items;
- owner runtime checklist.

Prefer tables and short bullets over long prose.

## 10. Commit policy

One coherent commit per subpart where useful, but avoid micro-commits.

Examples:
- G7.4A Party
- G7.4A Summary

or one G7.4A commit if the changes are tightly coupled and easy to review.

Before finishing:
- `git status` must be clean;
- generated artifacts must match generators;
- temporary QA files/harnesses must not remain;
- no unrelated files should be staged.

## 11. Stop conditions

Stop the session after the current batch is complete.

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

Merged on `main` through PR #50:
- G7.1A command menu — implemented
- G7.1B move selection — implemented
- G7.2A healthboxes — implemented
- G7.2B message frames — implemented
- G7.3 encounter intensity hierarchy — audited; risky runtime-sensitive additions intentionally deferred

**Next implementation batch: G7.4A — Party + Summary.**
