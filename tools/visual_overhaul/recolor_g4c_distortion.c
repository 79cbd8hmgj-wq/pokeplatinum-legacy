#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ns/container.h"
#include "palette.h"

static const char *sTargets[] = {
    "criff", "criffP2", "s_land", "s_land2", "s_land3",
    "s_land_att", "s_land_jump_pl", "s_landp", "tree_sbt01",
};

static bool NameEquals(const struct ResourceName *name, const char *target)
{
    char buffer[RES_NAME_LENGTH + 1] = {0};
    memcpy(buffer, name->asChars, RES_NAME_LENGTH);
    return strcmp(buffer, target) == 0;
}

static bool IsTarget(const struct ResourceName *name)
{
    for (size_t i = 0; i < sizeof(sTargets) / sizeof(sTargets[0]); i++) {
        if (NameEquals(name, sTargets[i])) return true;
    }
    return false;
}

static uint16_t Scale90(uint16_t v)
{
    return (v * 90 + 50) / 100;
}

static struct NDSColor Grade(struct NDSColor c)
{
    bool electricBlue = c.b >= 24 && c.b >= c.r + 10 && c.b >= c.g + 8;
    bool hotMagenta = c.r >= 24 && c.b >= 22 && c.g <= 4;

    if (electricBlue) {
        if (c.r < 31) c.r += 1;
        if (c.g < 31) c.g += 1;
        c.b = Scale90(c.b);
    } else if (hotMagenta) {
        c.r = Scale90(c.r);
        c.b = Scale90(c.b);
        c.g = c.g < 2 ? c.g + 2 : c.g;
    }
    return c;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "usage: %s INPUT.nsbtx OUTPUT.nsbtx\n", argv[0]);
        return 2;
    }

    FILE *input = fopen(argv[1], "rb");
    if (!input) {
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
        if (!IsTarget(&palette->name)) continue;

        int local = 0;
        for (int j = 0; j < palette->numColors; j++) {
            struct NDSColor before = palette->data[j];
            struct NDSColor after = Grade(before);
            if (before.r != after.r || before.g != after.g || before.b != after.b) {
                palette->data[j] = after;
                local++;
                colorsChanged++;
            }
        }
        if (local) {
            palettesChanged++;
            printf("%.*s: %d color(s) graded\n", RES_NAME_LENGTH, palette->name.asChars, local);
        }
    }

    FILE *output = fopen(argv[2], "wb");
    if (!output) {
        perror("open output");
        NSContainer_Free(&container);
        return 5;
    }
    result = NSContainer_WriteToFile(&container, output);
    fclose(output);
    NSContainer_Free(&container);
    if (result != 0) return result;

    printf("G4C Distortion grade: %d palettes, %d colors changed.\n", palettesChanged, colorsChanged);
    if (palettesChanged < 6 || colorsChanged < 10) {
        fprintf(stderr, "unexpectedly small Distortion recolor result\n");
        return 6;
    }
    return 0;
}
