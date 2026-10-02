#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ns/container.h"
#include "palette.h"

enum Mode { MODE_SPEAR, MODE_LAKES };

static const char *sSpear[] = {
    "colum_a_pl", "colum_b_pl", "colum_c_pl",
    "dun08_chip_a_pl", "dun08_chip_b_pl", "dun08_chip_d_pl",
    "dun08_chip_e_pl", "dun08_chip_g_pl",
};

static const char *sLakes[] = {
    "beachp", "blueglayp", "ckado", "enccriff", "fenter", "grass",
    "hage", "lgreen", "lgreenp", "nectgrass", "nhana", "nsandp",
    "rhana", "sandset", "shana", "tshadow", "lake", "lakep.1_pl",
};

static bool NameEquals(const struct ResourceName *name, const char *target)
{
    char buffer[RES_NAME_LENGTH + 1] = {0};
    memcpy(buffer, name->asChars, RES_NAME_LENGTH);
    return strcmp(buffer, target) == 0;
}

static bool InList(const struct ResourceName *name, const char **list, size_t n)
{
    for (size_t i = 0; i < n; i++) if (NameEquals(name, list[i])) return true;
    return false;
}

static uint16_t Clamp31(int v)
{
    if (v < 0) return 0;
    if (v > 31) return 31;
    return (uint16_t)v;
}

static struct NDSColor GradeSpear(struct NDSColor c)
{
    /* Ancient Spear Pillar stone: reduce the yellow cast without flattening ramp depth. */
    if (c.r >= c.g && c.g >= c.b && c.g >= 10 && c.r >= c.b + 4) {
        uint16_t avg = (c.r + c.g + c.b) / 3;
        c.r = Clamp31((2 * c.r + avg) / 3);
        c.g = Clamp31((2 * c.g + avg) / 3);
        c.b = Clamp31((c.b + 2 * avg) / 3 + 1);
    }
    return c;
}

static bool IsBrightGreen(struct NDSColor c)
{
    return c.g >= 18 && c.g >= c.r + 4 && c.g >= c.b + 2;
}

static struct NDSColor GradeLakes(struct NDSColor c, bool water)
{
    if (water) {
        if (c.b >= 22 && c.g >= 14 && c.b >= c.r + 6) {
            c.r = Clamp31((c.r * 88 + 50) / 100);
            c.g = Clamp31((c.g * 92 + 50) / 100);
            c.b = Clamp31((c.b * 96 + 50) / 100);
        }
        return c;
    }

    if (IsBrightGreen(c)) {
        uint16_t avg = (c.r + 2 * c.g + c.b) / 4;
        c.r = Clamp31(((3 * c.r + avg) / 4) * 88 / 100);
        c.g = Clamp31(((3 * c.g + avg) / 4) * 88 / 100);
        c.b = Clamp31(((3 * c.b + avg) / 4) * 88 / 100);
    }
    return c;
}

int main(int argc, char **argv)
{
    if (argc != 4) {
        fprintf(stderr, "usage: %s spear|lakes INPUT.nsbtx OUTPUT.nsbtx\n", argv[0]);
        return 2;
    }

    enum Mode mode;
    if (!strcmp(argv[1], "spear")) mode = MODE_SPEAR;
    else if (!strcmp(argv[1], "lakes")) mode = MODE_LAKES;
    else { fprintf(stderr, "unknown mode\n"); return 2; }

    FILE *input = fopen(argv[2], "rb");
    if (!input) { perror("open input"); return 3; }
    struct NSContainer container = {0};
    int result = NSContainer_ReadFromFile(&container, input);
    fclose(input);
    if (result != 0) { NSContainer_Free(&container); return result; }
    if (container.type.raw != containerMagics[CONTAINER_BTX0].raw || container.chunkCount < 1) {
        NSContainer_Free(&container);
        return 4;
    }

    struct NSChunkTex *chunk = container.chunks[0].texChunk;
    int palettesChanged = 0, colorsChanged = 0;
    for (int i = 0; i < chunk->palettes.n; i++) {
        struct Palette *pal = &VecGet(chunk->palettes, i);
        bool target = mode == MODE_SPEAR
            ? InList(&pal->name, sSpear, sizeof(sSpear) / sizeof(sSpear[0]))
            : InList(&pal->name, sLakes, sizeof(sLakes) / sizeof(sLakes[0]));
        if (!target) continue;

        bool water = NameEquals(&pal->name, "lake") || NameEquals(&pal->name, "lakep.1_pl");
        int local = 0;
        for (int j = 0; j < pal->numColors; j++) {
            struct NDSColor before = pal->data[j];
            struct NDSColor after = mode == MODE_SPEAR ? GradeSpear(before) : GradeLakes(before, water);
            if (before.r != after.r || before.g != after.g || before.b != after.b) {
                pal->data[j] = after;
                local++; colorsChanged++;
            }
        }
        if (local) { palettesChanged++; printf("%.*s: %d\n", RES_NAME_LENGTH, pal->name.asChars, local); }
    }

    FILE *output = fopen(argv[3], "wb");
    if (!output) { perror("open output"); NSContainer_Free(&container); return 5; }
    result = NSContainer_WriteToFile(&container, output);
    fclose(output);
    NSContainer_Free(&container);
    if (result != 0) return result;

    printf("%s: %d palettes / %d colors changed\n", argv[1], palettesChanged, colorsChanged);
    if (mode == MODE_SPEAR && palettesChanged < 5) return 6;
    if (mode == MODE_LAKES && palettesChanged < 8) return 6;
    return 0;
}
