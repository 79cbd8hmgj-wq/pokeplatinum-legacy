# G7.3 — Battle Intensity Hierarchy: Audit (and G7.7 encounter matrix)

Status: **audit complete; no source change shipped in this batch (see §4)**

Parent: `G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md` (G7.3, and the matrix
deliverable of G7.7). Starting commit: `e2184b59` (G7.2B). Builds on
`G5_BATTLE_PRESENTATION_COMPLETE.md`; nothing from G5 is revisited.

## 1. The tier system already exists in source

The plan's "identify the existing battle-type/trainer/event flags available at
transition time" step finds that Platinum already classifies every encounter in
`src/enc_effects.c` (`EncEffects_GetEffectPair`), choosing one **cut-in effect**
(the overworld→battle transition, code-driven in
`src/overlay005/encounter_effect*.c`) and one **BGM** per encounter:

| G7 tier | Encounter class | `ENCEFF_*` pair | Cut-in | BGM |
|---|---|---|---|---|
| 0 | Ordinary wild | `NORMAL_WILD` | local (grass / water / cave × lower / higher level) | wild |
| 0 | Wild double | `DOUBLE_WILD` | `CUTIN_DOUBLE` | wild |
| 1 | Ordinary trainer | `NORMAL_TRAINER` | local trainer variants (same 6) | trainer |
| 1 | Double / link / Frontier | `DOUBLE_BATTLE`, `LINK_BATTLE`, `FRONTIER` | `CUTIN_DOUBLE`, `CUTIN_FRONTIER` | trainer |
| 2 | Gym Leader (×8) | `LEADER_<name>` | **eight unique** cut-ins (one per leader) | gym leader |
| 2 | Volkner double | `DOUBLE_LEADER` | `CUTIN_DOUBLE` | gym leader |
| 2 | Galactic Grunt | `GALACTIC_GRUNT` | `CUTIN_GALACTIC_GRUNT` | grunt |
| 2 | Galactic Commander | `GALACTIC_CMDR` | `CUTIN_GALACTIC_BOSS` | commander |
| 2 | Cyrus | `GALACTIC_CYRUS` | `CUTIN_GALACTIC_BOSS` | Cyrus |
| 2 | Rival | `RIVAL` | **local (no unique cut-in)** | rival |
| 2 | Frontier Brain | `FRONTIER_BRAIN` | `CUTIN_FRONTIER` | brain |
| 3 | Elite Four (×4) | `ELITE_FOUR_<name>` | **four unique** cut-ins | elite four |
| 3 | Champion Cynthia | `CHAMPION_CYNTHIA` | unique cut-in | champion |
| 3 | Legendary / mythical | `SHAYMIN`, `DIALGA_PALKIA`, `UXIE_AZELF`, `MESPRIT`*, `ARCEUS`, `MINOR_LEGENDARIES`, `CRESSELIA`*, `KANTO_BIRDS`*, `GIRATINA`, `REGI_TRIO` | `CUTIN_LEGENDARY` / `CUTIN_MYTHICAL` (* = local) | per species |

Arenas: G5 already gives Elite Four / Champion / Giratina / Distortion / indoor
arenas their own palettes (`generate_battle_terrain.py`); gym fights use the
shared indoor arena resources.

## 2. Findings against the plan's acceptance list

| Plan item | Finding |
|---|---|
| four presentation tiers | already structurally present (table above); tiers 0/1 restrained, 2/3 carry unique cut-ins and BGM |
| prefer palette / transition / background / staging differentiation | the differentiation exists as per-class cut-in + BGM + (E4/Champion/Giratina) arena palettes |
| do not globally increase shake | respected; G5's `Func_ShakeBg` impact layer is per-move and untouched |
| critical / super-effective / KO hooks | see §3 |
| no change to battle results, no persistent offsets, no grade leaks | nothing shipped, so nothing can leak |

## 3. Shared presentation hooks located

* **Critical hit** — `res/battle/scripts/subscripts/subscript_critical_hit.s`,
  `_000`, runs once per critical hit and prints `ACriticalHit` before
  `WaitButtonABTime 30`. A bounded accent could be inserted *before*
  `PrintMessage` via `PlayBattleAnimation` with a new short common animation
  (flash + base-arena nudge). It touches the battle-script layer and needs a
  newly authored common animation; it cannot be exercised here.
* **Super-effective / not-very-effective** — only a *sound* hook exists in the
  controller (`BattleController_EmitPlayMoveHitSoundEffect`,
  `effectiveness` 0/1/2); the visual message path is spread across move-effect
  subscripts, so there is no single clean visual hook.
* **KO** — `subscript_faint_mon.s` / `subscript_replace_fainted.s` own the faint
  animation and fade timing; changing them risks turn timing and replay/link
  parity.

## 4. Decision: audit only

The plan says to add presentation only "if it can be isolated from damage
calculation", to document otherwise, and never to alter turn timing or script
branching. The one hook that is clean (critical hit) still requires authoring a
new common battle animation whose rendering cannot be verified in this
environment, and every other candidate crosses script/timing or link-parity
code. Shipping blind would violate the plan's risk rules for little gain, so
G7.3 ships **no source or asset change**. The existing G5 work plus the already
tiered encounter system satisfy the tier hierarchy structurally.

Recommended follow-ups (each independently testable by the owner):

1. **Rival cut-in** — give `ENCEFF_RIVAL` its own entry in `sEncEffectsTable`
   (today it falls back to the local grass/water/cave effect, the only tier-2
   encounter without one). Needs a chosen donor effect or a new effect in
   `encounter_effect*.c`.
2. **Critical-hit accent** in `subscript_critical_hit.s` using a new, short
   common animation (≤ 8 frames, no BG offset left behind).
3. **Gym arena identity** via new per-gym background slots (shared indoor
   resources currently cause collateral recolors if edited in place).

## 5. G7.7 encounter matrix (deliverable skeleton)

The table in §1 is the matrix the plan asks for in G7.7: class → tier →
transition → arena → special treatment. Today's special treatments:
per-leader / per-E4 / Champion cut-ins, Galactic Boss cut-in, legendary /
mythical cut-ins, E4 / Champion / Giratina / Distortion arena palettes (G5).
Open gaps: Rival cut-in, gym arena identity, per-legend arena emphasis.

## 6. Owner runtime review (optional)

If desired, spot-check one encounter per row of §1 in both emulator
orientations to confirm tier perception; report only concrete defects.
