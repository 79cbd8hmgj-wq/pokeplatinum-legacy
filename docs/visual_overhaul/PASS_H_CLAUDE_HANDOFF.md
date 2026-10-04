# Pass H — Claude Code Handoff

Use this prompt after the Pass H design/implementation-plan PR is merged to `main`.

## Prompt

You are implementing Pass H of my Pokémon Platinum overhaul in:

`79cbd8hmgj-wq/pokeplatinum-legacy`

Start from the latest `main`. Do not use the historical `visual-overhaul-g2a` branch as your base.

First read these files in full and treat them as authority:

1. `docs/visual_overhaul/PASS_H_MODERN_DS_REMASTER_DESIGN.md`
2. `docs/visual_overhaul/PASS_H_IMPLEMENTATION_PLAN.md`
3. `docs/visual_overhaul/PASS_G_VISUAL_OVERHAUL.md`
4. `docs/visual_overhaul/G5_BATTLE_PRESENTATION_COMPLETE.md`
5. `docs/visual_overhaul/G6_SHOWCASE_INTEGRATION_COMPLETE.md`
6. `docs/overhaul/STATUS.md`

The design target is a **Modern DS Remaster**: a more modern, premium, immersive, and intense Pokémon presentation designed to look excellent when this real DS ROM is played through an iPhone DS emulator. It is explicitly allowed to stray from authentic 2009 Platinum presentation. Do not turn it into fake iOS UI and do not depend on emulator shaders, texture packs, skins, or post-processing.

Pass G is the baseline. Preserve and extend its existing UI generators, battle-terrain work, battle staging, environment lighting/fog/camera work, and G6 showcase routing. Do not restart from retail assets.

### Your first implementation batch

Create a new branch from current `main`, preferably:

`visual/pass-h-h1-battle-ui`

Then execute the first batch in `PASS_H_IMPLEMENTATION_PLAN.md`:

- complete the H0 battle UI ownership audit;
- complete the H0 top-screen battle ownership audit;
- identify the exact resource/code owners for the lower-screen Fight/Bag/Run/Pokémon command deck, neutral background, move cards, move type/PP presentation, selection states, and touch hitboxes;
- create the shared Pass H style-token module;
- modernize the normal/doubles/Safari healthbox family;
- modernize the battle message frame if its ownership is confirmed;
- redesign the lower-screen command deck if resource ownership and touch geometry are confirmed;
- redesign the move-selection deck into modern action cards if its resource ownership is confirmed;
- preserve or correctly update touch geometry whenever visible geometry changes;
- add a deterministic Pass H battle UI validator and machine-readable manifest;
- run all relevant visual validators;
- run the main overhaul static validation;
- build US Rev 0 and US Rev 1;
- write the H1 implementation report;
- commit and push the work and open a PR.

Required deliverables are listed in section 15 of `PASS_H_IMPLEMENTATION_PLAN.md`.

### Working rules

Do actual implementation work rather than returning another plan.

Use source/resource audits before changing unknown binary resources. Do not guess archive members.

Prefer deterministic generators. Existing generators should be extended rather than creating overlapping scripts that own the same assets.

Keep resource contracts intact unless the audit proves a source-level layout expansion is safe.

Do not change Pokémon balance, mechanics, encounters, story progression, save format, or the completed C1/C2/C2.5/C3/D1-D8 overhaul systems.

Do not weaken the new design just to preserve retail Platinum authenticity. When a desired effect is technically impractical, reproduce the intended visual result through the nearest safe Platinum-native technique and document the deviation.

Do not stop for routine implementation choices. Continue with the design authority unless you hit a real blocker such as unknown resource ownership, unsafe touch geometry, opaque archive ownership, resource-limit failure, or a choice that genuinely requires rendered runtime evidence.

The user will handle subjective runtime/Delta-style emulator testing. Do not claim runtime visual verification from builds/static checks alone.

When the first batch is complete, report:
- exact files changed;
- exact UI systems implemented;
- validator results;
- Rev 0/Rev 1 build results;
- any source limitations;
- the small runtime screenshot checklist the user should test next.

Proceed now.
