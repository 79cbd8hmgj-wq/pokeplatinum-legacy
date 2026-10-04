#include "overlay011/move_palettes.h"

#include "constants/graphics.h"
#include "generated/pokemon_types.h"

ALIGN_4 static const u16 sMovePaletteNormal[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(29, 28, 30),
    RGB(23, 21, 26),
    RGB(18, 15, 23),
    RGB(15, 12, 20),
    RGB(12, 9, 17),
    RGB(9, 7, 13),
    RGB(6, 5, 9),
    RGB(25, 24, 27),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteFighting[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 27, 25),
    RGB(31, 23, 17),
    RGB(30, 16, 6),
    RGB(28, 12, 0),
    RGB(23, 10, 0),
    RGB(18, 7, 0),
    RGB(13, 5, 0),
    RGB(31, 26, 22),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteFlying[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(25, 27, 30),
    RGB(17, 22, 31),
    RGB(6, 15, 30),
    RGB(0, 10, 28),
    RGB(0, 8, 23),
    RGB(0, 7, 18),
    RGB(0, 5, 13),
    RGB(22, 25, 31),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePalettePoison[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(29, 25, 30),
    RGB(28, 17, 31),
    RGB(25, 6, 30),
    RGB(22, 0, 28),
    RGB(18, 0, 23),
    RGB(14, 0, 18),
    RGB(10, 0, 13),
    RGB(29, 22, 31),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteGround[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 28, 25),
    RGB(29, 24, 16),
    RGB(26, 17, 5),
    RGB(24, 14, 0),
    RGB(20, 11, 0),
    RGB(15, 9, 0),
    RGB(11, 6, 0),
    RGB(31, 27, 21),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteRock[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 29, 27),
    RGB(22, 19, 16),
    RGB(19, 15, 9),
    RGB(16, 12, 6),
    RGB(13, 10, 4),
    RGB(10, 7, 3),
    RGB(7, 5, 2),
    RGB(23, 21, 19),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteBug[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 29, 25),
    RGB(28, 25, 15),
    RGB(24, 21, 5),
    RGB(22, 18, 0),
    RGB(18, 15, 0),
    RGB(14, 12, 0),
    RGB(10, 8, 0),
    RGB(29, 27, 20),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteGhost[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 28, 30),
    RGB(20, 15, 18),
    RGB(16, 10, 15),
    RGB(14, 7, 12),
    RGB(11, 5, 10),
    RGB(9, 4, 8),
    RGB(6, 3, 5),
    RGB(21, 18, 20),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteSteel[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 30, 30),
    RGB(24, 24, 24),
    RGB(21, 21, 21),
    RGB(18, 18, 19),
    RGB(14, 14, 16),
    RGB(11, 11, 12),
    RGB(8, 8, 9),
    RGB(25, 25, 26),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteMystery[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 28, 29),
    RGB(24, 19, 22),
    RGB(20, 14, 18),
    RGB(18, 11, 15),
    RGB(15, 8, 12),
    RGB(12, 6, 9),
    RGB(8, 4, 7),
    RGB(25, 22, 24),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteFire[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 25, 25),
    RGB(31, 18, 18),
    RGB(30, 9, 8),
    RGB(28, 3, 2),
    RGB(23, 1, 1),
    RGB(18, 1, 0),
    RGB(13, 0, 0),
    RGB(31, 23, 22),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteWater[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(25, 29, 30),
    RGB(16, 25, 29),
    RGB(5, 20, 26),
    RGB(0, 16, 24),
    RGB(0, 13, 20),
    RGB(0, 10, 15),
    RGB(0, 8, 11),
    RGB(21, 28, 31),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteGrass[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(26, 30, 25),
    RGB(19, 28, 15),
    RGB(10, 24, 5),
    RGB(6, 22, 0),
    RGB(5, 18, 0),
    RGB(4, 14, 0),
    RGB(3, 10, 0),
    RGB(23, 29, 20),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteElectric[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 30, 25),
    RGB(31, 29, 17),
    RGB(29, 26, 6),
    RGB(26, 23, 0),
    RGB(21, 19, 0),
    RGB(17, 15, 0),
    RGB(12, 11, 0),
    RGB(31, 30, 22),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePalettePsychic[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 26, 29),
    RGB(31, 20, 27),
    RGB(31, 12, 23),
    RGB(29, 7, 20),
    RGB(24, 5, 16),
    RGB(19, 3, 13),
    RGB(13, 2, 9),
    RGB(31, 24, 28),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteIce[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(27, 29, 30),
    RGB(22, 28, 31),
    RGB(15, 24, 30),
    RGB(10, 21, 28),
    RGB(7, 17, 23),
    RGB(5, 13, 18),
    RGB(4, 9, 13),
    RGB(25, 29, 31),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteDragon[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(27, 27, 30),
    RGB(22, 22, 31),
    RGB(14, 13, 28),
    RGB(10, 9, 25),
    RGB(7, 7, 21),
    RGB(5, 5, 16),
    RGB(4, 3, 12),
    RGB(25, 25, 31),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteDark[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 29, 29),
    RGB(18, 16, 16),
    RGB(15, 13, 13),
    RGB(12, 10, 10),
    RGB(10, 8, 8),
    RGB(8, 6, 6),
    RGB(6, 4, 4),
    RGB(19, 18, 18),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 sMovePaletteNone[] = {
    RGB(13, 14, 29),
    RGB(31, 31, 31),
    RGB(30, 30, 30),
    RGB(15, 15, 16),
    RGB(11, 11, 12),
    RGB(9, 9, 10),
    RGB(7, 7, 8),
    RGB(5, 5, 6),
    RGB(4, 4, 5),
    RGB(16, 16, 17),
    RGB(1, 3, 7),
    RGB(0, 0, 0),
    RGB(12, 12, 12),
    RGB(17, 21, 26),
    RGB(29, 30, 31),
    RGB(0, 0, 0)
};

ALIGN_4 static const u16 Unk_ov11_0221FBAC[] = {
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
    RGB(19, 1, 0),
};

ALIGN_4 static const u16 *const sMovePaletteTable[] = {
    sMovePaletteNormal,
    sMovePaletteFighting,
    sMovePaletteFlying,
    sMovePalettePoison,
    sMovePaletteGround,
    sMovePaletteRock,
    sMovePaletteBug,
    sMovePaletteGhost,
    sMovePaletteSteel,
    sMovePaletteMystery,
    sMovePaletteFire,
    sMovePaletteWater,
    sMovePaletteGrass,
    sMovePaletteElectric,
    sMovePalettePsychic,
    sMovePaletteIce,
    sMovePaletteDragon,
    sMovePaletteDark
};

void include_unk_ov11_0221FBAC();

void include_unk_ov11_0221FBAC()
{
    Unk_ov11_0221FBAC[0];
}

const u16 *GetMoveTypePalette(int moveType)
{
    const u16 *paletteSourceAdr;

    if (moveType != -1) {
        paletteSourceAdr = sMovePaletteTable[moveType];
    } else {
        paletteSourceAdr = sMovePaletteNone;
    }

    return paletteSourceAdr;
}

void LoadMoveSelectPltt(PaletteData *paletteSys, enum PokemonType moveType, int unused, enum PaletteBufferID bufferID, int paletteDest)
{
    const u16 *paletteSource = GetMoveTypePalette(moveType);
    PaletteData_LoadBuffer(paletteSys, paletteSource, bufferID, PLTT_DEST(paletteDest), PALETTE_SIZE_BYTES);
}
