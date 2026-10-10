# B1 — NDS Toolkit live battle runtime test protocol

**Purpose:** Capture objective runtime evidence from a real Opal ROM in melonDS via the separate NDS Disassembly Toolkit Phase 7H. **Status: protocol only. No live emulator or Opal ROM was available to the author when written.**

## Required environment

1. Build both US ROM revisions from PR #110 (or the branch under test), recording the exact commit and SHA-256 for each `.nds`.
2. Install the separate `NDS-Disassembly-Toolkit-main` package in Python 3.11+ (for example `python -m pip install -e .` inside its directory). Do not copy its implementation into Opal.
3. Launch a compatible **melonDS with GDB RSP enabled**, disable JIT, load the target revision, and establish the exact save/game state.
4. Use **ARM9 localhost port 3333** and, when relevant, ARM7 port 3334. Do not expose GDB RSP directly to the internet. The toolkit attaches; **it does not launch melonDS or load ROMs**.
5. Note: stock melonDS may accept read/write watchpoint packets without actually producing watchpoint stops; prefer code breakpoints and step traces for proven runtime evidence.

## Baseline and comparison

Use the **same ROM revision, graphics settings and gameplay state** for each capture, with one matching build before the cinematic changes and one candidate build. Record SHA-256, emulator commit/version, toolkit revision, CPU, JIT disabled, save-state identifier and script/action for every artifact.

```bash
# Run with an already started melonDS debugger session.
nds-toolkit runtime probe --cpu arm9
nds-toolkit runtime snapshot --cpu arm9

# At a paused stable battle-idle state:
nds-toolkit runtime trace capture --cpu arm9 --steps 2000 --output idle.ndstrace

# Reopen the same save and stop during an AV1 move animation:
nds-toolkit runtime trace capture --cpu arm9 --steps 2000 --output attack.ndstrace

nds-toolkit runtime trace inspect idle.ndstrace
nds-toolkit runtime trace inspect attack.ndstrace
nds-toolkit runtime diff idle.ndstrace attack.ndstrace
```

These traces do **not** automatically identify a move or prove framebuffer correctness. To capture animation events reliably, use symbol-backed code breakpoints discovered from the built ROM/map or a static `.ndsre` project; never guess an ARM9 address, overlay residency or a function offset.

For known, valid memory regions, augment traces with `--memory ADDRESS:LENGTH` to inspect before/after changes. Record exact base and length and interpret the data conservatively. When using `--project game.ndsre`, correlate functions/symbols and verify matching project fingerprints.

## Required scenarios

| ID | Game state | Runtime/visual assertion |
| --- | --- | --- |
| RT-01 | Battle idle, open command/move panels | No unowned SUB palette changes; stable input and readable G7 panel |
| RT-02 | Ember / Fire Spin | Layered effect begins/ends; background tint clears; no emitter leakage |
| RT-03 | Thunder Shock / Spark | Attacker/defender anchors align; post-impact arcs clear |
| RT-04 | Psybeam / Swift | Multiple emitter sequencing and fade cleanup |
| RT-05 | Animated water/ice/cave/Distortion terrain | S2-D terrain cycling respects scene fade ownership |
| RT-06 | Open/return from Bag or Party in battle | Terrain cycles pause in menus, then resume safely |
| RT-07 | Single vs double, multi-target vs single target | OAM priorities, particle anchors and HUD positions remain correct |
| RT-08 | Miss, immunity, status, faint, switch, cancel | No stuck blend/brightness or orphan particle resources |
| RT-09 | Repeat on US rev0 and US rev1 | No revision-specific corruption/crashes |

**Capture outputs:** `.ndstrace` files, JSON inspection/differentials, game-state notes, top/bottom LCD images/video, measured frame-rate, and clear pass/fail per scenario. `.ndstrace` alone does not measure visual quality or FPS: use emulator capture/profiling separately.

## Interpretation and acceptance

- Source validators and ROM builds are necessary, not runtime proof.
- A successful debugger connection is not proof of a successful animation.
- Never call a stock melonDS watchpoint's lack of hits proof of no memory writes.
- Same-state comparison matters: the toolkit may report ordinary gameplay/state differences if captures start at different instructions.
- A release-ready B1 milestone requires gameplay input tests and frame captures in addition to ARM9/ARM7 trace evidence.
- Do not attach full retail ROMs to PR artifacts. Logs, checksums, traces and screenshots suffice.
