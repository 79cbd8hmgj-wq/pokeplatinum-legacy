#include "battle/battle_status_overlay.h"

#include <nitro.h>

#include "constants/battle.h"
#include "constants/battle/condition.h"
#include "constants/graphics.h"

#include "battle/battle_display.h"
#include "battle/battle_lib.h"
#include "battle/battle_system.h"

#include "pokemon_sprite.h"
#include "system.h"

// IO-STATUS pilot: confusion indicator.
//
// Three yellow four-point stars orbit above a confused battler's head. Each star is two thin
// quads (a vertical and a horizontal diamond) drawn with texture sampling disabled
// (GX_TEXFMT_NONE), so the shapes use only vertex colours. The overlay therefore owns no OAM
// entry, no texture/atlas texel and no palette bank.
//
// Render-state contract (audited in docs/visual_overhaul/implementation/IO_STATUS_PILOT_IMPLEMENTATION.md,
// enforced by tools/visual_overhaul/io_status/validate_confusion_overlay.py):
//   * Called straight after PokemonSpriteManager_DrawSprites, inside the same frame and before
//     the buffer swap, from the existing SysTask_DrawSprites. No new task.
//   * Every command sits inside one PushMtx/PopMtx(1) pair (the per-star pairs nest inside it), so
//     the matrix stack and current matrix are left as found. The matrix mode is never changed.
//   * Texture image parameter: switched to "none" for the overlay, then re-issued with exactly the
//     arguments PokemonSpriteManager_DrawSprites used for its own pass.
//   * Not written at all: texture palette base, texture matrix, material colours.
//   * Written but write-only in hardware (cannot be read back): polygon attributes and vertex
//     colour. Every consumer that can run afterwards sets them itself before its first polygon:
//     the mon pass sets PolygonAttr and material/vertex colour per quad, the SPL particle drawer sets
//     PolygonAttr and Color per particle, and each mode-0 frame starts with G3X_Reset (which also
//     resets PolygonAttr, TexImageParam, TexPlttBase and the matrix stack).
//   * Nothing is issued unless at least one battler qualifies; the overlay is the last geometry
//     submitted in the frame, so a (hypothetical) polygon/vertex RAM overflow would drop the stars
//     rather than a battler.

#define MAX_OVERLAY_BATTLERS MAX_BATTLERS

// Untextured polygons reuse a polygon ID block that no battler quad (IDs 0..3) uses. The
// overlay is fully opaque so IDs never take part in translucency ordering.
#define OVERLAY_POLYGON_ID_BASE 8

// Orbit: 0x10000 index units = one revolution; 0x0400 per frame is a full turn in 64 frames.
#define ORBIT_STAR_COUNT      3
#define ORBIT_STEP_PER_FRAME  0x0400
#define ORBIT_STAR_SPACING    (0x10000 / ORBIT_STAR_COUNT)
#define ORBIT_RADIUS_X        20
#define ORBIT_RADIUS_Y        5
#define ORBIT_HEAD_MARGIN     8 // pixels the orbit centre sits below the top of the sprite frame
#define STAR_HALF_SIZE_MIN    4
#define STAR_HALF_SIZE_RANGE  3 // half size ranges MIN..MIN+RANGE as the star swings to the front
#define STAR_OUTLINE_GROW     2
#define STAR_DEPTH_FRONT_BIAS 24 // z bias that puts the overlay in front of the battler quad
#define STAR_OUTLINE_Z        (-4 * FX32_ONE)
#define SCREEN_MIN_Y          (STAR_HALF_SIZE_MIN + STAR_HALF_SIZE_RANGE + STAR_OUTLINE_GROW + 1)

// Unit star in 4.12 vertex space; scaled to pixels with G3_Scale.
#define STAR_ARM_LENGTH FX32_ONE
#define STAR_ARM_WIDTH  0x0640

#define COLOR_STAR_FILL    GX_RGB(31, 27, 3)
#define COLOR_STAR_OUTLINE GX_RGB(12, 7, 0)

// 2 diamonds per pass, 2 passes (outline + fill), per star.
#define POLYGONS_PER_STAR (2 * 2)
#define POLYGONS_PER_MON  (POLYGONS_PER_STAR * ORBIT_STAR_COUNT)
#define VERTICES_PER_MON  (POLYGONS_PER_MON * 4)

typedef struct OverlayAnchor {
    s16 x;
    s16 y;
    s16 z;
    u8 battler;
} OverlayAnchor;

static BOOL CanDrawOverlay(BattleSystem *battleSys);
static BOOL TryGetAnchor(BattleSystem *battleSys, BattleContext *battleCtx, int battler, OverlayAnchor *anchor);
static void DrawConfusionStars(const OverlayAnchor *anchor, u32 phase);
static void DrawStarPass(int x, int y, int z, int halfSize, int zVertex, GXRgb color);

void BattleStatusOverlay_Draw(BattleSystem *battleSys)
{
    if (!CanDrawOverlay(battleSys)) {
        return;
    }

    BattleContext *battleCtx = BattleSystem_GetBattleContext(battleSys);
    if (battleCtx == NULL) {
        return;
    }

    // Gather first so nothing touches the geometry engine in the common (no status) case.
    OverlayAnchor anchors[MAX_OVERLAY_BATTLERS];
    int count = 0;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    if (maxBattlers > MAX_OVERLAY_BATTLERS) {
        maxBattlers = MAX_OVERLAY_BATTLERS;
    }

    for (int battler = 0; battler < maxBattlers; battler++) {
        if (TryGetAnchor(battleSys, battleCtx, battler, &anchors[count])) {
            count++;
        }
    }

    if (count == 0) {
        return;
    }

    PokemonSpriteManager *monSpriteMan = BattleSystem_GetPokemonSpriteManager(battleSys);
    u32 phase = (gSystem.frameCounter * ORBIT_STEP_PER_FRAME) & 0xFFFF;

    NNS_G3dGeFlushBuffer();
    G3_PushMtx();

    if (monSpriteMan->excludeIdentity != TRUE) {
        G3_Identity();
    }

    G3_TexImageParam(GX_TEXFMT_NONE, GX_TEXGEN_NONE, GX_TEXSIZE_S8, GX_TEXSIZE_T8, GX_TEXREPEAT_NONE, GX_TEXFLIP_NONE, GX_TEXPLTTCOLOR0_USE, 0);

    for (int i = 0; i < count; i++) {
        G3_PolygonAttr(GX_LIGHTMASK_NONE, GX_POLYGONMODE_MODULATE, GX_CULL_NONE, OVERLAY_POLYGON_ID_BASE + anchors[i].battler, 31, 0);
        DrawConfusionStars(&anchors[i], phase);
    }

    // Hand the texture unit back exactly as PokemonSpriteManager_DrawSprites configured it.
    G3_TexImageParam(monSpriteMan->imageProxy.attr.fmt, GX_TEXGEN_TEXCOORD, monSpriteMan->imageProxy.attr.sizeS, monSpriteMan->imageProxy.attr.sizeT, GX_TEXREPEAT_NONE, GX_TEXFLIP_NONE, monSpriteMan->imageProxy.attr.plttUse, monSpriteMan->charBaseAddr);
    G3_PopMtx(1);
}

static BOOL CanDrawOverlay(BattleSystem *battleSys)
{
    // Only the normal render mode; mode 3 (sub-menu) hides the overlay, modes 1 and 2 have
    // already released the graphics this pass depends on.
    if (BattleSystem_GetRenderMode(battleSys) != 0) {
        return FALSE;
    }

    // The draw task is created before the battle context exists.
    if (!BattleSystem_IsInitialized(battleSys)) {
        return FALSE;
    }

    if (BattleSystem_GetBattleType(battleSys) & (BATTLE_TYPE_LINK | BATTLE_TYPE_SAFARI | BATTLE_TYPE_PAL_PARK | BATTLE_TYPE_CATCH_TUTORIAL)) {
        return FALSE;
    }

    if (BattleSystem_GetBattleStatusMask(battleSys) & BATTLE_STATUS_RECORDING) {
        return FALSE;
    }

    return TRUE;
}

static BOOL TryGetAnchor(BattleSystem *battleSys, BattleContext *battleCtx, int battler, OverlayAnchor *anchor)
{
    BattlerData *battlerData = BattleSystem_GetBattlerData(battleSys, battler);
    if (battlerData == NULL) {
        return FALSE;
    }

    // Read-only battle state. Fainted battlers keep stale volatile bits until switch-out.
    if (BattleMon_Get(battleCtx, battler, BATTLEMON_CUR_HP, NULL) == 0) {
        return FALSE;
    }

    if ((BattleMon_Get(battleCtx, battler, BATTLEMON_VOLATILE_STATUS, NULL) & VOLATILE_CONDITION_CONFUSION) == 0) {
        return FALSE;
    }

    // The sprite pointer is re-read every frame and never cached: deleted sprites only clear
    // their pool slot's active flag and BattlerData is not NULLed.
    PokemonSprite *monSprite = BattlerData_GetPokemonSprite(battlerData);
    if (monSprite == NULL || !PokemonSprite_IsActive(monSprite)) {
        return FALSE;
    }

    if (PokemonSprite_GetAttribute(monSprite, MON_SPRITE_HIDE)
        || PokemonSprite_GetAttribute(monSprite, MON_SPRITE_HIDE_2)
        || PokemonSprite_GetAttribute(monSprite, MON_SPRITE_PARTIAL_DRAW)
        || PokemonSprite_GetAttribute(monSprite, MON_SPRITE_ALPHA) == 0) {
        return FALSE;
    }

    int scaleY = PokemonSprite_GetAttribute(monSprite, MON_SPRITE_SCALE_Y);
    if (PokemonSprite_GetAttribute(monSprite, MON_SPRITE_SCALE_X) <= 0 || scaleY <= 0) {
        return FALSE;
    }

    // Same centre the battler quad is drawn around (see PokemonSpriteManager_DrawSprites).
    int frameHeight = (MON_SPRITE_FRAME_HEIGHT * scaleY) >> MON_AFFINE_SHIFT;
    int x = PokemonSprite_GetAttribute(monSprite, MON_SPRITE_X_CENTER) + PokemonSprite_GetAttribute(monSprite, MON_SPRITE_X_OFFSET);
    int y = PokemonSprite_GetAttribute(monSprite, MON_SPRITE_Y_CENTER) + PokemonSprite_GetAttribute(monSprite, MON_SPRITE_Y_OFFSET) - PokemonSprite_GetAttribute(monSprite, MON_SPRITE_SHADOW_HEIGHT);
    int z = PokemonSprite_GetAttribute(monSprite, MON_SPRITE_Z_CENTER) + PokemonSprite_GetAttribute(monSprite, MON_SPRITE_Z_OFFSET);

    y += ORBIT_HEAD_MARGIN - frameHeight / 2;

    if (y < SCREEN_MIN_Y) {
        y = SCREEN_MIN_Y;
    }

    anchor->x = x;
    anchor->y = y;
    anchor->z = z;
    anchor->battler = battler;
    return TRUE;
}

static void DrawConfusionStars(const OverlayAnchor *anchor, u32 phase)
{
    for (int i = 0; i < ORBIT_STAR_COUNT; i++) {
        int angle = (phase + i * ORBIT_STAR_SPACING) & 0xFFFF;
        int sinVal = FX_SinIdx(angle);
        int cosVal = FX_CosIdx(angle);

        int x = anchor->x + ((ORBIT_RADIUS_X * cosVal) >> FX32_SHIFT);
        int y = anchor->y + ((ORBIT_RADIUS_Y * sinVal) >> FX32_SHIFT);
        // sinVal > 0 swings the star to the front: larger and nearer.
        int halfSize = STAR_HALF_SIZE_MIN + (((sinVal + FX32_ONE) * STAR_HALF_SIZE_RANGE) >> (FX32_SHIFT + 1));
        int z = anchor->z + STAR_DEPTH_FRONT_BIAS + (sinVal >> 8);

        DrawStarPass(x, y, z, halfSize + STAR_OUTLINE_GROW, STAR_OUTLINE_Z, COLOR_STAR_OUTLINE);
        DrawStarPass(x, y, z, halfSize, 0, COLOR_STAR_FILL);
    }
}

static void DrawStarPass(int x, int y, int z, int halfSize, int zVertex, GXRgb color)
{
    G3_PushMtx();
    G3_Translate(x << FX32_SHIFT, y << FX32_SHIFT, z << FX32_SHIFT);
    G3_Scale(halfSize << FX32_SHIFT, halfSize << FX32_SHIFT, FX32_ONE);
    G3_Color(color);
    G3_Begin(GX_BEGIN_QUADS);

    // Vertical diamond.
    G3_Vtx(0, -STAR_ARM_LENGTH, zVertex);
    G3_Vtx(STAR_ARM_WIDTH, 0, zVertex);
    G3_Vtx(0, STAR_ARM_LENGTH, zVertex);
    G3_Vtx(-STAR_ARM_WIDTH, 0, zVertex);

    // Horizontal diamond.
    G3_Vtx(-STAR_ARM_LENGTH, 0, zVertex);
    G3_Vtx(0, STAR_ARM_WIDTH, zVertex);
    G3_Vtx(STAR_ARM_LENGTH, 0, zVertex);
    G3_Vtx(0, -STAR_ARM_WIDTH, zVertex);

    G3_End();
    G3_PopMtx(1);
}
