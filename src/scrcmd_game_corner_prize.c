#include "scrcmd_game_corner_prize.h"

#include <nitro.h>
#include <string.h>

#include "generated/items.h"

#include "field_script_context.h"
#include "inlines.h"

typedef struct GameCornerPrize {
    u16 item;
    u16 price;
} GameCornerPrize;

BOOL ScrCmd_GetGameCornerPrizeData(ScriptContext *ctx)
{
    u16 index = ScriptContext_GetVar(ctx);
    u16 *item = ScriptContext_GetVarPointer(ctx);
    u16 *price = ScriptContext_GetVarPointer(ctx);

    static const GameCornerPrize sGameCornerPrizeData[] = {
        { ITEM_SILK_SCARF, 1000 },
        { ITEM_WIDE_LENS, 1000 },
        { ITEM_ZOOM_LENS, 1000 },
        { ITEM_METRONOME, 1000 },
        { ITEM_TM90, 1000 },
        { ITEM_TM58, 1000 },
        { ITEM_TM75, 2000 },
        { ITEM_TM32, 2000 },
        { ITEM_TM44, 2500 },
        { ITEM_TM89, 3000 },
        { ITEM_TM10, 3000 },
        { ITEM_TM27, 3000 },
        { ITEM_TM21, 4000 },
        { ITEM_TM35, 4000 },
        { ITEM_TM24, 4000 },
        { ITEM_TM13, 4000 },
        { ITEM_TM29, 4000 },
        { ITEM_TM74, 5000 },
        { ITEM_TM68, 6000 }
    };

    *item = sGameCornerPrizeData[index].item;
    *price = sGameCornerPrizeData[index].price;

    return FALSE;
}
