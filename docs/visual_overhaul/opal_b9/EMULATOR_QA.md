# Opal B9 P0 — emulator / hardware QA sheet (owner action)

**Nothing in this PR has been run in an emulator or on hardware by the author.** Source validators, host tests and ROM builds are the only
verification performed. Track three states per move, separately: **source-passed** (done, below) · **emulator-tested** · **visual-approved**.
Record ROM revision + SHA256, scenario, PASS/FAIL, video/screenshot, observed fault.

Build: `make skrew && make configure ROM_REVISION=<0|1> && make rom ROM_REVISION=<0|1>` or download the `pokeplatinum-us-rev{0,1}-<sha>` artifacts of this PR's `build` workflow.
Low-flash / reduced-motion: compile-time `OPAL_LOW_FLASH` / `OPAL_REDUCED_MOTION` in `include/constants/battle/battle_anim.h` (B9 adds no new flashing cue except one white sprite flash via the existing `OpalReactLight`).

## Per-move status

| Move | source-passed | emulator-tested | visual-approved | Specific things to look at |
|---|---|---|---|---|
| Tackle | ✅ | ☐ | ☐ | dust at the user's feet, hit flash on contact, nothing left on screen after the return |
| Scratch | ✅ | ☐ | ☐ | three arcs read as claw lines (not a slash); both directions visible; no extra waiting |
| Pound | ✅ | ☐ | ☐ | ring is soft, camera punch is small; ring palette (gold) fits |
| Quick Attack | ✅ | ☐ | ☐ | streak/afterimages don't fight the native dash; dust placement |
| Bite | ✅ | ☐ | ☐ | **do the donor jaws double the native `bite_spa` jaws?** If so drop native emitters 3/4 (or the donor jaws) — one-line change |
| Ember | ✅ | ☐ | ☐ | volley vs. native core vs. Ranger bloom; must not read like Fire Blast |
| Water Gun | ✅ | ☐ | ☐ | stream continuity, splash on the native impact frame; friendly-fire branch (double: hit your own partner) |
| Bubble | ✅ | ☐ | ☐ | bubbles arrive together with the native pop; doubles: pops on both foes |
| Vine Whip | ✅ | ☐ | ☐ | lash direction/offset on both sides of the field; second flick timing |
| Razor Leaf | ✅ | ☐ | ☐ | **fan arrival vs. native leaf flight and native impact (frame 75)**; leaf count readable, not cluttered |
| ThunderShock | ✅ | ☐ | ☐ | arcs read as branching sparks, clearly smaller than Thunderbolt; backdrop restored |
| Powder Snow | ✅ | ☐ | ☐ | swirl tint (ice palette), flecks, glints after each flash; backdrop restored |
| Gust | ✅ | ☐ | ☐ | streak lanes vs. native gale; leaf debris |
| Peck | ✅ | ☐ | ☐ | thrust streak is subtle; new light recoil is acceptable |
| Rock Throw | ✅ | ☐ | ☐ | boulder lands on the native impact; grit puff size; camera punch not excessive |
| Confusion | ✅ | ☐ | ☐ | rings visible over the native BG switch + sprite warp; no palette bleed afterwards |
| Growl | ✅ | ☐ | ☐ | rings/arcs sync with both cries; doubles: arc to each foe |
| Leer | ✅ | ☐ | ☐ | glint position on the user's eye, on both user sides; target glint |
| Tail Whip | ✅ | ☐ | ☐ | crescent sits behind the user (both facings); star pop on every foe in doubles |

## Scenario matrix (run each for every move unless noted)

| ID | Setup | Expected |
|---|---|---|
| B9-SINGLE | singles, player as attacker, then opponent as attacker | cues mirror correctly (ox/dox are mirrored per side, oy is not) |
| B9-DOUBLE | doubles, all four alive; target each foe in turn; then the partner (Water Gun, Tackle…) | cue only on the resolved target(s); Growl / Leer / Tail Whip on both foes |
| B9-MISS | miss, Protect, type immunity (Ghost vs Tackle/Scratch/Pound/Quick Attack), Substitute | **no** hit cue — animation not played on miss/immune/Protect; with Substitute the cue is expected on the substitute sprite (B2–B8 report; verify) |
| B9-STATFAIL | Growl on a −6 Attack foe; Leer/Tail Whip on a −6 Defense foe; Clear Body | no animation at all, only the "won't go lower" text |
| B9-STATUS-ORDER | Growl / Leer / Tail Whip success | move animation, then the native stat-fall arrow animation, then text — order and length as vanilla |
| B9-REPEAT | use each move 10× in a row, then a different move | no accumulating tint, offset, OAM/palette corruption; compare turn length with vanilla/PR #110 build |
| B9-WEATHER | rain / sun / sand / hail | none of the P0 scripts add a weather cue (spec P0 has none); native weather unaffected |
| B9-FAINT | KO with the move, switch-in | clean faint, no residual sprite |
| B9-CONTEST | contest appeal with Tackle, Scratch, Pound, Quick Attack, Bite, Ember, Vine Whip, Razor Leaf, Thunder Shock, Powder Snow, Gust, Peck, Rock Throw, Confusion, Growl, Tail Whip | **unverified** — only Water Gun / Bubble / Leer have contest branches and those are native; the other scripts have no contest branch so the new cues run in contests (positions come from `BattleAnimUtil_GetBattlerPos`). Report any misplaced sprite |
| B9-OPTIONS | Battle Scene = Off | animation skipped (vanilla path), no cue |
| B9-A11Y | build with `OPAL_LOW_FLASH 1` and `OPAL_REDUCED_MOTION 1` | pop/shrink/drift disabled; camera cues absent; no new bright pulses |
| B9-PERF | repeated Bite / Water Gun / Razor Leaf (highest sprite counts) in doubles | no slowdown; static upper bounds are in `IMPLEMENTATION_REPORT.md`, **no frame-time measurement exists** |
