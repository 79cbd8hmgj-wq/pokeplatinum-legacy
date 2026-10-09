#ifndef POKEPLATINUM_BATTLE_STATUS_OVERLAY_H
#define POKEPLATINUM_BATTLE_STATUS_OVERLAY_H

#include "struct_decls/battle_system.h"

/**
 * @brief Draw untextured 3D status indicators above battlers (IO-STATUS pilot).
 *
 * Currently draws a ring of orbiting stars above any battler that has the
 * confusion volatile condition.
 *
 * This is a purely cosmetic, read-only pass. It must be called once per frame
 * from the battle's draw task, immediately after PokemonSpriteManager_DrawSprites
 * and before the frame's buffer swap. It keeps no state, allocates nothing, owns no
 * texture/palette/OAM resources, and issues no 3D commands when no battler
 * qualifies.
 *
 * @param battleSys
 */
void BattleStatusOverlay_Draw(BattleSystem *battleSys);

#endif // POKEPLATINUM_BATTLE_STATUS_OVERLAY_H
