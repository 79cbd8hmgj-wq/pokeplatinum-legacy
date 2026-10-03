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

## Isolation build (vanilla award path, egg give/hatch bypassed)

    git apply tools/overhaul/diag/mystery_egg_isolation.patch

Keeps the random 13-species draw; restores `GetPlayerStarterSpecies` + `GivePokemon Lv5`.
The D8 validator is expected to fail with this patch applied; never commit it.
