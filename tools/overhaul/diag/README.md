# D8 Mystery Egg chooser-return blocker diagnostics (temporary)

Remove this directory, `include/mystery_egg_diag.h`, the `MYSTERY_EGG_DIAG*` call sites
and the two `gMysteryEggDiag*` globals in `src/debug.c` once the fault is fixed and verified.

## Trace build (no behaviour change)

    make configure ROM_REVISION=1 && make debug ROM_REVISION=1

Run in melonDS / no$gba with debug output visible. Expected log sequence on a healthy run:

    MEDIAG MEDIAG_A_CHOOSER_INIT
    MEDIAG MEDIAG_A_CHOOSER_FINISH pos=N
    MEDIAG MEDIAG_A_CHOOSER_FADED
    MEDIAG MEDIAG_A_CHOOSER_EXIT_BEGIN
    MEDIAG MEDIAG_A_CHOOSER_EXIT_END
    MEDIAG MEDIAG_B_SAVE_BEGIN eggPosition=N
    MEDIAG MEDIAG_B_SAVE_END species=S
    MEDIAG MEDIAG_C_RETURN_TO_FIELD
    MEDIAG MEDIAG_D_FADE_IN_START type=.. frames=..
    MEDIAG MEDIAG_D_FADE_IN_DONE
    MEDIAG MEDIAG_E_GIVE_BEGIN species=S metLoc=.. partyCount=0
    MEDIAG MEDIAG_E_GIVE_EGG_BUILT
    MEDIAG MEDIAG_E_GIVE_END added=1
    MEDIAG MEDIAG_F_MESSAGE messageID=..
    MEDIAG MEDIAG_G_HATCH_BEGIN / MEDIAG_G_HATCH_END

The last line printed is the failing stage. `gMysteryEggDiagStage` holds the same id for debugger watch.

## iPhone-friendly diagnostic ROMs (primary path)

Workflow `.github/workflows/diag-mystery-egg-roms.yml` (push to this branch) applies one patch
per variant and uploads Rev 1 ROMs as artifacts. Temporary: never merge to main.

- `mystery-diag-A-vanilla-award` (`diag-A-vanilla-award.patch`): chooser + weighted draw kept;
  egg give/hatch bypassed; vanilla `GetPlayerStarterSpecies` + `GivePokemon Lv5`.
  Black screen => chooser exit / field restoration. Visible Route 201 => fault is downstream.
- `mystery-diag-B-egg-no-hatch` (`diag-B-egg-no-hatch.patch`): `GiveMysteryStarterEgg` runs, shows
  "DIAG: EGG CREATED", no hatch, then the vanilla starter is also given so the Route 201 sequence continues.
  A works + B black => egg construction. B works => `HatchMysteryStarterEgg` / hatch app.
