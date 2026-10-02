#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ns/container.h"
#include "palette.h"

static const char *sTargets[] = {
    "criff", "criffP2", "s_land", "s_land2", "s_land3", "s_land4",
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

static uint16_t Clamp31(int v)
{
    if (v < 0) return 0;
    if (v > 31) return 31;
    return (uint16_t)v;
}

static struct NDSColor Grade(struct NDSColor c)
{
    /* Soften harsh primary-blue glow into a richer indigo-violet. */
    if (c.b >= 20 && c.b >= c.r + 8 && c.b >= c.g + 6) {
        c.r = Clamp31(c.r + 2);
        c.g = Clamp31(c.g + 1);
        c.b = Clamp31(c.b - 1);
        return c;
    }

    /* Keep the alien magenta, but pull it off full digital saturation. */
    if (c.r >= 24 && c.b >= 20 && c.g <= 4) {
        c.r = Clamp31((c.r * 90 + 50) / 100);
        c.g = Clamp31(c.g + 2);
        c.b = Clamp31((c.b * 92 + 50) / 100);
        return c;
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
    if (!input) { perror("open input"); return 3; }

    struct NSContainer container = {0};
    int result = NSContainer_ReadFromFile(&container, input);
    fclose(input);
    if (result != 0) { NSContainer_Free(&container); return result; }
    if (container.type.raw != containerMagics[CONTAINER_BTX0].raw || container.chunkCount < 1) {
        fprintf(stderr, "input is not BTX0\n");
        NSContainer_Free(&container);
        return 4;
    }

    struct NSChunkTex *chunk = container.chunks[0].texChunk;
    int palettesChanged = 0, colorsChanged = 0;
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
    if (!output) { perror("open output"); NSContainer_Free(&container); return 5; }
    result = NSContainer_WriteToFile(&container, output);
    fclose(output);
    NSContainer_Free(&container);

    printf("G4C grade: %d palettes, %d colors changed.\n", palettesChanged, colorsChanged);
    if (result != 0) return result;
    if (palettesChanged < 3 || colorsChanged < 5) return 6;
    return 0;
}
