#ifndef POKEPLATINUM_BATTLE_ANIM_OPAL_CINEMATIC_H
#define POKEPLATINUM_BATTLE_ANIM_OPAL_CINEMATIC_H

#include "battle_anim/battle_anim_system.h"

#include "sprite_system.h"

// Opal B2-B8 presentation layer. Visual only: nothing here reads or writes battle state beyond the
// attacker/defender/battler positions that the animation system already exposes to move scripts.

void BattleAnimSpriteFunc_OpalFx(BattleAnimSystem *system, SpriteSystem *spriteSys, SpriteManager *spriteMan, ManagedSprite *sprite);
void BattleAnimScriptFunc_OpalCamera(BattleAnimSystem *system);
void OpalCinematic_ResetState(void);

#endif // POKEPLATINUM_BATTLE_ANIM_OPAL_CINEMATIC_H
