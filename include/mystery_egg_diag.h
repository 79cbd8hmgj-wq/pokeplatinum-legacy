#ifndef POKEPLATINUM_MYSTERY_EGG_DIAG_H
#define POKEPLATINUM_MYSTERY_EGG_DIAG_H

// TEMPORARY D8 blocker diagnostics; remove once the fault is fixed and verified.
// Active only with LOGGING_ENABLED (`make debug`). Each checkpoint stores its id
// in gMysteryEggDiagStage (watchable from a debugger) and logs to the emulator.

#include "debug.h"

enum MysteryEggDiagStage {
    MEDIAG_NONE = 0,
    MEDIAG_A_CHOOSER_INIT = 1, // chooser overlay started
    MEDIAG_A_CHOOSER_LOOP, // chooser main loop entered
    MEDIAG_A_CHOOSER_FINISH, // selection confirmed, fade-out starting
    MEDIAG_A_CHOOSER_FADED, // fade-out done, Main returned TRUE
    MEDIAG_A_CHOOSER_EXIT_BEGIN, // ChooseStarter_Exit entered
    MEDIAG_A_CHOOSER_EXIT_END, // ChooseStarter_Exit teardown complete
    MEDIAG_B_SAVE_BEGIN, // SaveChosenStarter entered
    MEDIAG_B_SAVE_END, // species drawn + persisted
    MEDIAG_C_RETURN_TO_FIELD, // ReturnToField command executed
    MEDIAG_D_FADE_IN_START, // FadeScreen (in) command executed
    MEDIAG_D_FADE_IN_DONE, // fade-in wait satisfied
    MEDIAG_E_GIVE_BEGIN, // GiveMysteryStarterEgg entered
    MEDIAG_E_GIVE_EGG_BUILT, // egg Pokemon constructed
    MEDIAG_E_GIVE_END, // egg added to party
    MEDIAG_F_MESSAGE, // Message command executed
    MEDIAG_G_HATCH_BEGIN, // HatchMysteryStarterEgg entered
    MEDIAG_G_HATCH_END, // hatch task queued
};

#ifdef LOGGING_ENABLED
extern volatile u32 gMysteryEggDiagStage;
extern volatile u32 gMysteryEggDiagActive;
#define MYSTERY_EGG_DIAG(stage)                 \
    do {                                        \
        gMysteryEggDiagStage = (stage);         \
        EmulatorLog("MEDIAG " #stage);          \
    } while (0)
#define MYSTERY_EGG_DIAG_V(stage, fmt, ...)                      \
    do {                                                         \
        gMysteryEggDiagStage = (stage);                          \
        EmulatorLog("MEDIAG " #stage " " fmt, __VA_ARGS__);      \
    } while (0)
#else
#define MYSTERY_EGG_DIAG(stage)                ((void)0)
#define MYSTERY_EGG_DIAG_V(stage, fmt, ...)    ((void)0)
#endif

#endif // POKEPLATINUM_MYSTERY_EGG_DIAG_H
