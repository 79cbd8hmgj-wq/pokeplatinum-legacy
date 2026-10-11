#include "battle_anim/opal_cinematic.h"

#include <nitro.h>

#include "constants/battle/battle_anim.h"

#include "battle_anim/battle_anim_helpers.h"
#include "battle_anim/battle_anim_system.h"
#include "battle_anim/battle_anim_util.h"

#include "bg_window.h"
#include "heap.h"
#include "sprite.h"
#include "sprite_system.h"
#include "sys_task_manager.h"

// -------------------------------------------------------------------
// Opal FX sprite
//
// One sprite function for every Opal sheet (res/graphics/battle/moves/opal_*.png).
//  - static mode: one burst per resolved anchor battler (anchor mask may name several, e.g. NOT_ATTACKER)
//  - travel mode: one sprite per resolved destination battler, flying from the first anchor battler
// Targets are resolved by BattleAnimUtil_GetBattlerSprites, i.e. the exact same battler set that
// Func_Shake / Func_FadeBattlerSprite use, so effects never appear on battlers the engine did not
// resolve (fainted / absent slots resolve to nothing).
// Every instance has a hard lifetime cap, so the owning anim task can never wait indefinitely.
// -------------------------------------------------------------------
#define OPAL_FX_MAX_INSTANCES 4
#define OPAL_FX_MAX_LIFETIME  180 // frames; hard cap when the script passes 0 or a looping animation never ends
#define OPAL_FX_TRAIL_COUNT   3 // lead + two afterimages
#define OPAL_FX_TRAIL_LAG     3 // frames between trail instances

typedef struct OpalFxInstance {
    ManagedSprite *sprite;
    s16 startX;
    s16 startY;
    s16 endX;
    s16 endY;
    s16 lag; // frames this instance trails the lead
    u8 scaleMul; // percent of the base scale
} OpalFxInstance;

typedef struct OpalFxContext {
    BattleAnimSystem *battleAnimSys;
    SpriteManager *spriteMan;
    OpalFxInstance instances[OPAL_FX_MAX_INSTANCES];
    int count;
    int elapsed;
    int duration;
    int arc;
    int scale; // percent
    int flags;
    int maxLag;
    BOOL travel;
} OpalFxContext;

static void BattleAnimTask_OpalFx(SysTask *task, void *param);
static void OpalFx_ApplyScale(OpalFxContext *ctx, OpalFxInstance *inst);

static inline int OpalFx_ClampAxis(int value, int limit)
{
    if (value > limit) {
        return limit;
    }

    if (value < -limit) {
        return -limit;
    }

    return value;
}

void BattleAnimSpriteFunc_OpalFx(BattleAnimSystem *system, SpriteSystem *spriteSys, SpriteManager *spriteMan, ManagedSprite *sprite)
{
    OpalFxContext *ctx = BattleAnimUtil_Alloc(system, sizeof(OpalFxContext));
    ctx->battleAnimSys = system;
    ctx->spriteMan = spriteMan;

    int anchorMask = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_ANCHOR_MASK);
    int destMask = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_DEST_MASK);
    ctx->duration = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_FRAMES);
    int offsetX = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_OFFSET_X);
    int offsetY = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_OFFSET_Y);
    int destOffsetX = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_DEST_OFFSET_X);
    int destOffsetY = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_DEST_OFFSET_Y);
    ctx->arc = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_ARC);
    ctx->scale = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_SCALE);
    int animFlags = BattleAnimSystem_GetScriptVar(system, OPAL_FX_VAR_ANIM_FLAGS);

    if (ctx->scale <= 0) {
        ctx->scale = 100;
    }

    ctx->flags = animFlags & ~0xFF;

    if (ctx->duration <= 0 || ctx->duration > OPAL_FX_MAX_LIFETIME) {
        // Open-ended: lives until its play-once animation ends (hard-capped), so life-relative scaling is meaningless.
        ctx->duration = OPAL_FX_MAX_LIFETIME;
        ctx->flags &= ~(OPAL_FX_FLAG_POP | OPAL_FX_FLAG_SHRINK_OUT);
    }
    ctx->travel = destMask != 0;

#if OPAL_REDUCED_MOTION
    ctx->flags &= ~(OPAL_FX_FLAG_DRIFT_UP | OPAL_FX_FLAG_POP | OPAL_FX_FLAG_SHRINK_OUT);
#endif

    int attacker = BattleAnimSystem_GetAttacker(system);
    int dir = BattleAnimUtil_GetTransformDirectionX(system, attacker);

    BattleAnimSpriteInfo anchors[4];
    int anchorCount = 0;
    BattleAnimUtil_GetBattlerSprites(system, anchorMask, anchors, &anchorCount);

    BattleAnimSpriteInfo dests[4];
    int destCount = 0;
    if (ctx->travel) {
        BattleAnimUtil_GetBattlerSprites(system, destMask, dests, &destCount);
    }

    int total = ctx->travel ? destCount : anchorCount;
    if (ctx->travel && anchorCount == 0) {
        total = 0;
    }

    // A trail (afterimages) is only built for a single resolved destination.
    BOOL trail = ctx->travel && (ctx->flags & OPAL_FX_FLAG_TRAIL) != 0 && destCount == 1;
    if (trail) {
        total = total > 0 ? OPAL_FX_TRAIL_COUNT : 0;
    }

    if (total > OPAL_FX_MAX_INSTANCES) {
        total = OPAL_FX_MAX_INSTANCES;
    }

    SpriteTemplate template = BattleAnimSystem_GetLastSpriteTemplate(system);

    for (int i = 0; i < total; i++) {
        OpalFxInstance *inst = &ctx->instances[i];

        if (i == 0) {
            inst->sprite = sprite;
        } else {
            inst->sprite = SpriteSystem_NewSprite(spriteSys, spriteMan, &template);
        }

        int anchorBattler;
        int destBattler = -1;
        if (ctx->travel) {
            anchorBattler = anchors[0].battler;
            destBattler = dests[trail ? 0 : i].battler;
        } else {
            anchorBattler = anchors[i].battler;
        }

        inst->lag = trail ? i * OPAL_FX_TRAIL_LAG : 0;
        inst->scaleMul = trail ? 100 - 25 * i : 100;

        inst->startX = BattleAnimUtil_GetBattlerPos(system, anchorBattler, BATTLE_ANIM_POSITION_MON_X) + offsetX * dir;
        inst->startY = BattleAnimUtil_GetBattlerPos(system, anchorBattler, BATTLE_ANIM_POSITION_MON_Y) + offsetY;
        if (ctx->travel) {
            inst->endX = BattleAnimUtil_GetBattlerPos(system, destBattler, BATTLE_ANIM_POSITION_MON_X) + destOffsetX * dir;
            inst->endY = BattleAnimUtil_GetBattlerPos(system, destBattler, BATTLE_ANIM_POSITION_MON_Y) + destOffsetY;
        } else {
            inst->endX = inst->startX;
            inst->endY = inst->startY;
        }

        ManagedSprite_SetPositionXY(inst->sprite, inst->startX, inst->startY);
        ManagedSprite_SetAnim(inst->sprite, OPAL_FX_ANIM(animFlags));
        ManagedSprite_SetPriority(inst->sprite, BATTLE_ANIM_HW_SPRITE_PRIORITY);
        ManagedSprite_SetExplicitPriority(inst->sprite, BATTLE_ANIM_HW_SPRITE_EXP_PRIORITY);
        ManagedSprite_SetAffineOverwriteMode(inst->sprite, AFFINE_OVERWRITE_MODE_DOUBLE);
        OpalFx_ApplyScale(ctx, inst);

        if (inst->lag > 0) {
            ManagedSprite_SetDrawFlag(inst->sprite, FALSE);
        }

        if ((ctx->flags & OPAL_FX_FLAG_TRANSLUCENT) != 0 || (trail && i > 0)) {
            ManagedSprite_SetExplicitOamMode(inst->sprite, GX_OAM_MODE_XLU);
        }

        if ((ctx->flags & OPAL_FX_FLAG_MIRROR) != 0 && dir < 0) {
            ManagedSprite_SetFlipMode(inst->sprite, TRUE);
        }
    }

    ctx->count = total;
    ctx->maxLag = trail ? (OPAL_FX_TRAIL_COUNT - 1) * OPAL_FX_TRAIL_LAG : 0;

    if (total == 0) {
        // The engine resolved no battler for this effect: draw nothing and finish on the first tick.
        ManagedSprite_SetDrawFlag(sprite, FALSE);
        ctx->instances[0].sprite = sprite;
        ctx->count = 1;
        ctx->elapsed = ctx->duration;
    }

    BattleAnimSystem_StartAnimTask(system, BattleAnimTask_OpalFx, ctx);
}

static void OpalFx_ApplyScale(OpalFxContext *ctx, OpalFxInstance *inst)
{
    int pct = ctx->scale * inst->scaleMul / 100;
    int local = ctx->elapsed - inst->lag;

    if ((ctx->flags & OPAL_FX_FLAG_POP) != 0 && local < ctx->duration / 3) {
        pct = pct * (40 + 60 * local / (ctx->duration / 3 + 1)) / 100;
    } else if ((ctx->flags & OPAL_FX_FLAG_SHRINK_OUT) != 0 && local > ctx->duration * 2 / 3) {
        int remaining = ctx->duration - local;
        if (remaining < 0) {
            remaining = 0;
        }

        pct = pct * (40 + 60 * remaining / (ctx->duration / 3 + 1)) / 100;
    }

    if (pct < 1) {
        pct = 1;
    }

    f32 scale = (f32)pct / 100.0f;
    ManagedSprite_SetAffineScale(inst->sprite, scale, scale);
}

static void BattleAnimTask_OpalFx(SysTask *task, void *param)
{
    OpalFxContext *ctx = param;

    ctx->elapsed++;
    BOOL finished = ctx->elapsed >= ctx->duration + ctx->maxLag;

    for (int i = 0; i < ctx->count; i++) {
        OpalFxInstance *inst = &ctx->instances[i];
        int local = ctx->elapsed - inst->lag; // lifetime of this instance
        int x = inst->startX;
        int y = inst->startY;

        if (local < 1) {
            continue; // trail instance that has not launched yet stays hidden
        }

        if (inst->lag > 0 && local == 1) {
            ManagedSprite_SetDrawFlag(inst->sprite, TRUE);
        }

        if (ctx->travel) {
            int t = local;
            int d = ctx->duration;
            if (t > d) {
                t = d;
            }

            x = inst->startX + (inst->endX - inst->startX) * t / d;
            y = inst->startY + (inst->endY - inst->startY) * t / d;
            y -= ctx->arc * 4 * t * (d - t) / (d * d);
        }

        if ((ctx->flags & OPAL_FX_FLAG_DRIFT_UP) != 0) {
            y -= local / 3;
        }

        ManagedSprite_SetPositionXY(inst->sprite, x, y);
        OpalFx_ApplyScale(ctx, inst);
        ManagedSprite_TickFrame(inst->sprite);

        if ((ctx->flags & OPAL_FX_FLAG_HOLD_LAST) == 0 && !ManagedSprite_IsAnimated(inst->sprite)) {
            // Play-once sequence has ended: hide it.
            ManagedSprite_SetDrawFlag(inst->sprite, FALSE);
        }

        if (ctx->travel && local >= ctx->duration) {
            ManagedSprite_SetDrawFlag(inst->sprite, FALSE);
        }
    }

    if (!ctx->travel && ctx->duration == OPAL_FX_MAX_LIFETIME) {
        // duration 0 means "until every play-once animation has ended"
        BOOL anyVisible = FALSE;
        for (int i = 0; i < ctx->count; i++) {
            if (ManagedSprite_GetDrawFlag(ctx->instances[i].sprite)) {
                anyVisible = TRUE;
            }
        }

        if (!anyVisible) {
            finished = TRUE;
        }
    }

    if (finished) {
        for (int i = 0; i < ctx->count; i++) {
            Sprite_DeleteAndFreeResources(ctx->instances[i].sprite);
        }

        BattleAnimSystem_EndAnimTask(ctx->battleAnimSys, task);
        Heap_Free(ctx);
        return;
    }

    SpriteSystem_DrawSprites(ctx->spriteMan);
}

// -------------------------------------------------------------------
// Opal camera cue
//
// DS-native "camera": the battle backdrop (BATTLE_BG_BASE) is scrolled by a few pixels while battler
// sprites, healthboxes, text and the touch screen stay put, which reads as a small parallax pan.
//  - PAN:   ease to (dx, dy), hold, ease back
//  - PUNCH: one decaying shake, amplitude (dx, dy)
// The base background offset is snapshotted at cue start and written back exactly when the cue ends.
// Only one cue may own the camera at a time; a second request while one is active is ignored
// (first-come priority), so snapshots can never stack. BattleAnimScript_End also resets the base and
// effect background offsets to 0, which is the final backstop for any aborted animation.
// -------------------------------------------------------------------
#define OPAL_CAM_VAR_MODE 0
#define OPAL_CAM_VAR_DX   1
#define OPAL_CAM_VAR_DY   2
#define OPAL_CAM_VAR_IN   3
#define OPAL_CAM_VAR_HOLD 4
#define OPAL_CAM_VAR_OUT  5

typedef struct OpalCameraContext {
    BattleAnimSystem *battleAnimSys;
    BgConfig *bgConfig;
    int mode;
    int dx;
    int dy;
    int inFrames;
    int holdFrames;
    int outFrames;
    int frame;
    int baseX;
    int baseY;
} OpalCameraContext;

static BOOL sOpalCameraActive = FALSE;

void OpalCinematic_ResetState(void)
{
    sOpalCameraActive = FALSE;
}

// Smoothstep on 0..256
static inline int OpalCamera_Ease(int num, int den)
{
    if (den <= 0 || num >= den) {
        return 256;
    }

    int t = num * 256 / den;
    return t * t * (768 - 2 * t) / (256 * 256);
}

static void OpalCamera_Apply(OpalCameraContext *ctx, int offsetX, int offsetY)
{
    Bg_SetOffset(ctx->bgConfig, BATTLE_BG_BASE, BG_OFFSET_UPDATE_SET_X, ctx->baseX + offsetX);
    Bg_SetOffset(ctx->bgConfig, BATTLE_BG_BASE, BG_OFFSET_UPDATE_SET_Y, ctx->baseY + offsetY);
}

static void BattleAnimTask_OpalCamera(SysTask *task, void *param)
{
    OpalCameraContext *ctx = param;
    int total = ctx->inFrames + ctx->holdFrames + ctx->outFrames;

    if (ctx->frame >= total) {
        OpalCamera_Apply(ctx, 0, 0); // exact restore of the snapshot
        sOpalCameraActive = FALSE;
        BattleAnimSystem_EndAnimTask(ctx->battleAnimSys, task);
        Heap_Free(ctx);
        return;
    }

    int weight; // 0..256
    if (ctx->mode == OPAL_CAM_MODE_PUNCH) {
        int remaining = total - ctx->frame;
        int sign = (ctx->frame & 1) ? -1 : 1;
        weight = sign * 256 * remaining / total;
    } else if (ctx->frame < ctx->inFrames) {
        weight = OpalCamera_Ease(ctx->frame + 1, ctx->inFrames);
    } else if (ctx->frame < ctx->inFrames + ctx->holdFrames) {
        weight = 256;
    } else {
        weight = 256 - OpalCamera_Ease(ctx->frame - ctx->inFrames - ctx->holdFrames + 1, ctx->outFrames);
    }

    OpalCamera_Apply(ctx, ctx->dx * weight / 256, ctx->dy * weight / 256);
    ctx->frame++;
}

void BattleAnimScriptFunc_OpalCamera(BattleAnimSystem *system)
{
#if OPAL_REDUCED_MOTION
    return;
#else
    if (sOpalCameraActive) {
        return;
    }

    OpalCameraContext *ctx = BattleAnimUtil_Alloc(system, sizeof(OpalCameraContext));
    ctx->battleAnimSys = system;
    ctx->bgConfig = BattleAnimSystem_GetBgConfig(system);
    ctx->mode = BattleAnimSystem_GetScriptVar(system, OPAL_CAM_VAR_MODE);

    int attacker = BattleAnimSystem_GetAttacker(system);
    int dir = BattleAnimUtil_GetTransformDirectionX(system, attacker);

    ctx->dx = OpalFx_ClampAxis(BattleAnimSystem_GetScriptVar(system, OPAL_CAM_VAR_DX) * dir, OPAL_CAM_MAX_DX);
    ctx->dy = OpalFx_ClampAxis(BattleAnimSystem_GetScriptVar(system, OPAL_CAM_VAR_DY), OPAL_CAM_MAX_DY);
    ctx->inFrames = BattleAnimSystem_GetScriptVar(system, OPAL_CAM_VAR_IN);
    ctx->holdFrames = BattleAnimSystem_GetScriptVar(system, OPAL_CAM_VAR_HOLD);
    ctx->outFrames = BattleAnimSystem_GetScriptVar(system, OPAL_CAM_VAR_OUT);

    if (ctx->inFrames < 1) {
        ctx->inFrames = 1;
    }

    if (ctx->holdFrames < 0) {
        ctx->holdFrames = 0;
    }

    if (ctx->outFrames < 1) {
        ctx->outFrames = 1;
    }

    // Hard cap: a cue can never hold the camera longer than 90 frames.
    while (ctx->inFrames + ctx->holdFrames + ctx->outFrames > 90) {
        if (ctx->holdFrames > 0) {
            ctx->holdFrames--;
        } else if (ctx->inFrames > 1) {
            ctx->inFrames--;
        } else {
            ctx->outFrames--;
        }
    }

    ctx->baseX = Bg_GetXOffset(ctx->bgConfig, BATTLE_BG_BASE);
    ctx->baseY = Bg_GetYOffset(ctx->bgConfig, BATTLE_BG_BASE);
    sOpalCameraActive = TRUE;

    BattleAnimSystem_StartAnimTask(system, BattleAnimTask_OpalCamera, ctx);
#endif
}
