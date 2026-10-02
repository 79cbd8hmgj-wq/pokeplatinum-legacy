#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ns/container.h"
#include "palette.h"

static const char *sTargetPalettes[] = {
    "ckado",
    "enccriff",
    "fenter",
    "grass",
    "hage",
    "lgreen",
    "lgreenp",
    "nectgrass",
    "nhana",
    "nsandp",
    "rhana",
    "sandset",
    "shana",
    "tshadow",
};

static bool NameEquals(const struct ResourceName *name, const char *target)
{
    char buffer[RES_NAME_LENGTH + 1] = {0};
    memcpy(buffer, name->asChars, RES_NAME_LENGTH);
    return strcmp(buffer, target) == 0;
}

static bool IsTargetPalette(const struct ResourceName *name)
{
    for (size_t i = 0; i < sizeof(sTargetPalettes) / sizeof(sTargetPalettes[0]); i++) {
        if (NameEquals(name, sTargetPalettes[i])) {
            return true;
        }
    }
    return false;
}

static bool IsForestGreen(struct NDSColor color)
{
    return color.g >= 16 && color.g >= color.r + 3 && color.g >= color.b + 2;
}

static uint16_t Scale86(uint16_t value)
{
    return (value * 86 + 50) / 100;
}

static struct NDSColor GradeGreen(struct NDSColor color)
{
    uint16_t avg = (color.r + 2 * color.g + color.b) / 4;
    uint16_t r = (3 * color.r + avg) / 4;
    uint16_t g = (3 * color.g + avg) / 4;
    uint16_t b = (3 * color.b + avg) / 4;

    color.r = Scale86(r);
    color.g = Scale86(g);
    color.b = Scale86(b);
    return color;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "usage: %s INPUT.nsbtx OUTPUT.nsbtx\n", argv[0]);
        return 2;
    }

    FILE *input = fopen(argv[1], "rb");
    if (input == NULL) {
        perror("open input");
        return 3;
    }

    struct NSContainer container = {0};
    int result = NSContainer_ReadFromFile(&container, input);
    fclose(input);
    if (result != 0) {
        NSContainer_Free(&container);
        return result;
    }

    if (container.type.raw != containerMagics[CONTAINER_BTX0].raw || container.chunkCount < 1) {
        fprintf(stderr, "input is not a valid BTX0 container\n");
        NSContainer_Free(&container);
        return 4;
    }

    struct NSChunkTex *chunk = container.chunks[0].texChunk;
    int palettesChanged = 0;
    int colorsChanged = 0;

    for (int i = 0; i < chunk->palettes.n; i++) {
        struct Palette *palette = &VecGet(chunk->palettes, i);
        if (!IsTargetPalette(&palette->name)) {
            continue;
        }

        int paletteChanges = 0;
        for (int j = 0; j < palette->numColors; j++) {
            struct NDSColor before = palette->data[j];
            if (!IsForestGreen(before)) {
                continue;
            }
            struct NDSColor after = GradeGreen(before);
            if (before.r != after.r || before.g != after.g || before.b != after.b) {
                palette->data[j] = after;
                paletteChanges++;
                colorsChanged++;
            }
        }

        if (paletteChanges > 0) {
            palettesChanged++;
            printf("%.*s: %d color(s) graded\n", RES_NAME_LENGTH, palette->name.asChars, paletteChanges);
        }
    }

    FILE *output = fopen(argv[2], "wb");
    if (output == NULL) {
        perror("open output");
        NSContainer_Free(&container);
        return 5;
    }
    result = NSContainer_WriteToFile(&container, output);
    fclose(output);
    NSContainer_Free(&container);

    if (result != 0) {
        return result;
    }

    printf("G4A Eterna grade: %d palettes, %d colors changed.\n", palettesChanged, colorsChanged);
    if (palettesChanged < 8 || colorsChanged < 20) {
        fprintf(stderr, "unexpectedly small recolor result; refusing silent partial application\n");
        return 6;
    }
    return 0;
}
