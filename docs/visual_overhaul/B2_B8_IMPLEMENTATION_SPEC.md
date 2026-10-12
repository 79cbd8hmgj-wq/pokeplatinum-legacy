# Pokémon Opal — B2–B8 implementation support packet

**Status:** implementation *specification*, not a claim that B2–B8 are implemented.  
**PR:** #110 · `feat/b1-opal-cinematic-battle-foundation`  
**Input:** `B2_B8_IMPLEMENTATION_MANIFEST.json` (machine-readable; same folder).  
**Owner split:** ChatGPT supplies asset priorities, cinematic recipes and source-aware constraints; Claude Code implements and builds; the owner does emulator/visual acceptance later.

## Read this, not the entire historical archive

Start with `docs/visual_overhaul/b1_installed_donors/README.md`, `docs/visual_overhaul/B1_OPAL_CINEMATIC_BATTLE_ARCHITECTURE.md`, `docs/visual_overhaul/POKEMON_OPAL_ASSET_DIRECTION.md` and this manifest. Only open additional files if a listed integration issue requires them. The already validated B1 converter/installer is preferred over building fresh exporters.

## Reconciliation with existing B2–B8 preparation

The existing `docs/visual_overhaul/B2_B8_PREIMPLEMENTATION_MANIFEST.json` and `tools/visual_overhaul/validate_b2_b8_handoff.py` remain valid as a **baseline**, with their six generic archetypes. This packet is an **additive implementation expansion** with 11 specialized move groups and concrete phase entrypoints, not a replacement or a second competing design authority. Preserve the existing validator; avoid repeating its work.

**Important legacy classification caveat:** `docs/visual_overhaul/selection/ledgers/battle_effects_particles.json` still labels Ranger effect groups `ranger_effect/e000` onwards as `reference_only` / `not_portable`. Those older selection-policy labels do *not* mean their graphics cannot be converted: the later B1 pipeline demonstrably imported e002, e009 and e010 as native Platinum battle sprite assets. Treat new e-series packages as **candidate unverified** until their exact frame/format/conversion has been proved, not as automatically rejected or automatically compatible.

## Ready now: verified donor imports

| Installed sprite | Ranger 2 package | Frames | OBJ tiles | Palette | Source authority |
|---|---|---:|---:|---:|---|
| Fire Bloom | `effect/e010_LZ.bin` | 8 | 236 | 7 colors | `b1_installed_donors/ranger_fire_bloom.provenance.json` |
| Ice Bloom | `effect/e009_LZ.bin` | 8 | 236 | 7 colors | `b1_installed_donors/ranger_ice_bloom.provenance.json` |
| Rock Burst | `effect/e002_LZ.bin` | 9 | 219 | 6 colors | `b1_installed_donors/ranger_rock_burst.provenance.json` |

Existing technical method: export Nitro cells, assemble PNG + cell/animation JSON, install into move graphics NARCs, append resource order indices, use `SPRITE_FUNC_OFFSET_AND_ANIMATE` via existing script system, and free the sprite manager before unloading effects. Do not take 256 tiles as a blanket declaration of free graphics memory during battles.

## Next donor families (candidates only)

| Ranked | Donor family | Use in implementation | Required evidence before integration |
|---:|---|---|---|
| 6/7 | Ranger 2 `ranger_effect/e` | New electricity, spectral, water impact sprite components and timing technique | Exact package, rendered cell/frame hashes, format and overlap check |
| 22 | Ranger 2 `ranger_target/t` | Impact/charge rings and target-adjacent ornamentation | Source cell and transparency; never modify targeting logic |
| 10/13 | Ranger 2 `ranger_event/event` | Transition motifs for boss/legendary presentation | Check actual encounter visual hook and state cleanup |
| 18/19 | PMD Sky `pmd_mapbg_d/v` | Atmosphere and motion sequencing ideas, possibly converted components | Confirm actual render, format and whether a compatible BG/OBJ target exists |
| 5/9 | Ranger 2 `ranger_interface/i` | UI micro-detail and focus motion | Audit G7 HUD ownership and VRAM slots before use |

**Important:** Family rank means promising opportunity, not compatible graphics. No nonexistent package or named lightning asset is claimed here. Recovered curation overlays override legacy baseline status.

## No-token bulk animation inventory

Instead of individually reading 492 animation directories, first generate a compact machine-readable inventory (only the mapped moves by default):

```bash
python3 tools/visual_overhaul/audit_b2_b8_move_scripts.py --only-mapped --output /tmp/opal_b2_b8_moves.json
```

Run without `--only-mapped` if widening scope beyond the mapped effects. The resulting operation counts and flags are **heuristic triage only**, not control-flow proof. Read and adjust individual branching scripts only when flagged or actively implementing them. The scanner does not edit game resources.

## B2: primary vertical slices

**Thunderbolt — electrical charge and discharge:** attacker-localized anticipation; controlled scene dim; release effect; defender-linked branches and brief light flashes; residual sparks; complete tint and emitter reset. Consult existing `res/moves/thunderbolt/anim.s`, native SHAKE/FADE functions and ranked Ranger effect cells. Preserve the move's existing logic and sounds unless sequencing improves sound sync.

**Shadow Ball — spectral propulsion and residue:** spiral charge + darkened field; existing travel/impact anchor; one short delayed energy ring; fade-in normal battlefield. Consult `res/moves/shadow_ball/anim.s`. Do not add new unverified SPA emitter IDs.

**Surf — large-area wave:** water crest and side/friendly-fire branching, area sweep with multiple battler anchors, foam/residue effect, and scene reset. Consult `res/moves/surf/anim.s`; doubles and targets are critical. Preserve native sprite-manager resource ordering.

After proving these, use the manifest's archetype mapping for the remaining verified `res/moves/<move>/anim.s` directories rather than duplicating source audits.

## B3–B8: concrete cross-phase contracts

| Phase | Required deliverable | Preserve / defer |
|---|---|---|
| B3 Camera | Reusable, bounded shake / BG scroll / short focus staging, with restore | No moving healthbox OBJ and no unverified scale/zoom API; runtime camera smoothness owner-tested |
| B4 Atmosphere | Scene-local palette fades, light pulses, weather overlays with teardown | Respect `src/battle/terrain.c` S2-D cycling ownership; no gameplay weather edits |
| B5 Reactions | Animation-script-only anticipation, hit recoil and recover where possible; faint hooks only after source proof | Restore battler position/visibility, partner and Substitute safety |
| B6 Sequencing | Consistent `anticipate → charge → release → impact → aftermath → reset` grammar, with bespoke exceptions | Keep move timing responsive; do not homogenize all moves |
| B7 Encounters | Verify actual Opal intro triggers, then introduce reusable signature/boss motif | No event scripting or battle outcome modifications |
| B8 Cohesion | Unified Opal pearl/mineral-violet/gold framing (NOT element recolors), optimized graphics/cleanup | Existing G7 HUD and AV1 effects remain authoritative |

## Test-and-release policy

Enforce static source-only guardrails and dual-revision builds on meaningful code batches; verify published build artifacts. Do **not** gate on the optional melonDS debugger test or claim emulator correctness. Deferred runtime acceptance matrix in manifest covers single/double, friendly fire, Contest, weather and palette cycles, interruptions, and special encounters. Record issues instead of silently assuming they pass.

## Work minimization for Claude

1. Load this file and manifest, then relevant source only; do not read all 64k records.
2. Build donor batches around a **specific installed host**, not a huge asset-category survey.
3. Reuse existing Ranger exporter/installer, B1 validators and known sprite function.
4. Implement and validate B2 vertical slices, then shared helpers before scaling to B3–B8.
5. Keep one concise checkpoint when context is nearing limit; don't create extra roadmaps.
6. Don't ask approval between phases; report only actual blockers and exact build results.

## Not evidence of completion

All timelines, camera behaviors, atmospheric treatments and B3–B8 packets are design targets. They require source implementation. Donor candidate families require exact source/format selection before any claim of installation.