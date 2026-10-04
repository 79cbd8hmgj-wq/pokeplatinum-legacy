// G7.6 overworld atmosphere palette grader.
//
// Applies a data-driven list of colour-grade rules to named palettes of a
// BTX0 texture set. Texel indices, dimensions and resource names are never
// touched. The rule file is authored by generate_g76_atmosphere.py, which is
// the authority for every number used here.
//
// usage: recolor_g76_atmosphere RULES.txt INPUT.nsbtx OUTPUT.nsbtx
//
// Rule line (whitespace separated key=value, '#' comments):
//   names=a,b,c|*     palettes the rule applies to ('*' = every palette)
//   skip=x,y          palettes excluded from a '*' rule
//   lmin lmax smin smax hmin hmax   colour mask (luma/sat 0..1, hue degrees;
//                     hmin>hmax = wrapped band that also admits greys)
//   sat con lum       chroma scale, contrast around luma 0.5, luma gain
//   mulr mulg mulb    per-channel gain after the luma stage
//   shr shg shb       additive offset weighted by (1-luma)^2  (shadows)
//   hir hig hib       additive offset weighted by luma^2       (highlights)
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ns/container.h"
#include "palette.h"

#define MAX_RULES 128
#define NAME_LIST 1024

struct Rule {
    char names[NAME_LIST];
    char skip[NAME_LIST];
    double lmin, lmax, smin, smax, hmin, hmax;
    double sat, con, lum;
    double mul[3], sh[3], hi[3];
    int colors;
};

static struct Rule sRules[MAX_RULES];
static int sRuleCount;

static bool ListHas(const char *list, const char *name)
{
    if (list[0] == '\0') {
        return false;
    }
    char buffer[NAME_LIST];
    strncpy(buffer, list, NAME_LIST - 1);
    buffer[NAME_LIST - 1] = '\0';
    for (char *tok = strtok(buffer, ","); tok != NULL; tok = strtok(NULL, ",")) {
        if (strcmp(tok, name) == 0) {
            return true;
        }
    }
    return false;
}

static bool RuleTargets(const struct Rule *rule, const char *name)
{
    if (strcmp(rule->names, "*") == 0) {
        return !ListHas(rule->skip, name);
    }
    return ListHas(rule->names, name);
}

static int ParseRules(const char *path)
{
    FILE *f = fopen(path, "r");
    if (f == NULL) {
        perror("open rules");
        return -1;
    }
    char line[4096];
    while (fgets(line, sizeof(line), f) != NULL) {
        if (line[0] == '#' || line[0] == '\n') {
            continue;
        }
        if (sRuleCount >= MAX_RULES) {
            fprintf(stderr, "too many rules\n");
            fclose(f);
            return -1;
        }
        struct Rule *r = &sRules[sRuleCount];
        r->lmin = 0;
        r->lmax = 1;
        r->smin = 0;
        r->smax = 1;
        r->hmin = 0;
        r->hmax = 360;
        r->sat = 1;
        r->con = 1;
        r->lum = 1;
        for (int i = 0; i < 3; i++) {
            r->mul[i] = 1;
            r->sh[i] = 0;
            r->hi[i] = 0;
        }
        for (char *tok = strtok(line, " \t\r\n"); tok != NULL; tok = strtok(NULL, " \t\r\n")) {
            char *eq = strchr(tok, '=');
            if (eq == NULL) {
                fprintf(stderr, "bad token %s\n", tok);
                fclose(f);
                return -1;
            }
            *eq = '\0';
            const char *k = tok;
            const char *v = eq + 1;
            if (strcmp(k, "names") == 0) {
                strncpy(r->names, v, NAME_LIST - 1);
            } else if (strcmp(k, "skip") == 0) {
                strncpy(r->skip, v, NAME_LIST - 1);
            } else if (strcmp(k, "lmin") == 0) {
                r->lmin = atof(v);
            } else if (strcmp(k, "lmax") == 0) {
                r->lmax = atof(v);
            } else if (strcmp(k, "smin") == 0) {
                r->smin = atof(v);
            } else if (strcmp(k, "smax") == 0) {
                r->smax = atof(v);
            } else if (strcmp(k, "hmin") == 0) {
                r->hmin = atof(v);
            } else if (strcmp(k, "hmax") == 0) {
                r->hmax = atof(v);
            } else if (strcmp(k, "sat") == 0) {
                r->sat = atof(v);
            } else if (strcmp(k, "con") == 0) {
                r->con = atof(v);
            } else if (strcmp(k, "lum") == 0) {
                r->lum = atof(v);
            } else if (strcmp(k, "mulr") == 0) {
                r->mul[0] = atof(v);
            } else if (strcmp(k, "mulg") == 0) {
                r->mul[1] = atof(v);
            } else if (strcmp(k, "mulb") == 0) {
                r->mul[2] = atof(v);
            } else if (strcmp(k, "shr") == 0) {
                r->sh[0] = atof(v);
            } else if (strcmp(k, "shg") == 0) {
                r->sh[1] = atof(v);
            } else if (strcmp(k, "shb") == 0) {
                r->sh[2] = atof(v);
            } else if (strcmp(k, "hir") == 0) {
                r->hi[0] = atof(v);
            } else if (strcmp(k, "hig") == 0) {
                r->hi[1] = atof(v);
            } else if (strcmp(k, "hib") == 0) {
                r->hi[2] = atof(v);
            } else {
                fprintf(stderr, "unknown key %s\n", k);
                fclose(f);
                return -1;
            }
        }
        if (r->names[0] == '\0') {
            fprintf(stderr, "rule without names\n");
            fclose(f);
            return -1;
        }
        sRuleCount++;
    }
    fclose(f);
    return 0;
}

static double Clamp01(double v)
{
    return v < 0 ? 0 : (v > 1 ? 1 : v);
}

static bool RuleMatchesColor(const struct Rule *r, double rr, double gg, double bb)
{
    double luma = 0.30 * rr + 0.59 * gg + 0.11 * bb;
    double mx = fmax(rr, fmax(gg, bb));
    double mn = fmin(rr, fmin(gg, bb));
    double sat = mx > 0 ? (mx - mn) / mx : 0;
    double hue = 0;
    if (mx > mn) {
        double d = mx - mn;
        if (mx == rr) {
            hue = fmod((gg - bb) / d, 6.0);
        } else if (mx == gg) {
            hue = (bb - rr) / d + 2.0;
        } else {
            hue = (rr - gg) / d + 4.0;
        }
        hue *= 60.0;
        if (hue < 0) {
            hue += 360.0;
        }
    }
    if (luma < r->lmin || luma > r->lmax || sat < r->smin || sat > r->smax) {
        return false;
    }
    if (r->hmin != 0 || r->hmax != 360) {
        if (r->hmin <= r->hmax) {
            // Inclusive band: greys have no meaningful hue and never match.
            return sat >= 0.04 && hue >= r->hmin && hue <= r->hmax;
        }
        // Wrapped band (hmin > hmax) is an exclusion of the hmax..hmin gap;
        // greys are outside the gap and therefore match.
        return sat < 0.04 || hue >= r->hmin || hue <= r->hmax;
    }
    return true;
}

static struct NDSColor ApplyRule(const struct Rule *r, struct NDSColor color)
{
    double c[3] = { color.r / 31.0, color.g / 31.0, color.b / 31.0 };
    double luma = 0.30 * c[0] + 0.59 * c[1] + 0.11 * c[2];

    for (int i = 0; i < 3; i++) {
        c[i] = luma + (c[i] - luma) * r->sat;
    }
    double newLuma = Clamp01(0.5 + (luma - 0.5) * r->con) * r->lum;
    for (int i = 0; i < 3; i++) {
        c[i] = luma > 0.001 ? c[i] * (newLuma / luma) : c[i] + newLuma;
        c[i] *= r->mul[i];
    }
    double shadowW = (1.0 - newLuma) * (1.0 - newLuma);
    double highW = newLuma * newLuma;
    for (int i = 0; i < 3; i++) {
        c[i] += r->sh[i] * shadowW + r->hi[i] * highW;
        c[i] = Clamp01(c[i]);
    }
    color.r = (uint16_t)(c[0] * 31.0 + 0.5);
    color.g = (uint16_t)(c[1] * 31.0 + 0.5);
    color.b = (uint16_t)(c[2] * 31.0 + 0.5);
    return color;
}

int main(int argc, char **argv)
{
    if (argc != 4) {
        fprintf(stderr, "usage: %s RULES.txt INPUT.nsbtx OUTPUT.nsbtx\n", argv[0]);
        return 2;
    }
    if (ParseRules(argv[1]) != 0) {
        return 2;
    }

    FILE *input = fopen(argv[2], "rb");
    if (input == NULL) {
        perror("open input");
        return 3;
    }
    struct NSContainer container = { 0 };
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
        char name[RES_NAME_LENGTH + 1] = { 0 };
        memcpy(name, palette->name.asChars, RES_NAME_LENGTH);

        int paletteChanges = 0;
        for (int j = 0; j < palette->numColors; j++) {
            struct NDSColor before = palette->data[j];
            // Never touch magenta key colours.
            if (before.r >= 28 && before.b >= 28 && before.g <= 3) {
                continue;
            }
            struct NDSColor after = before;
            for (int k = 0; k < sRuleCount; k++) {
                struct Rule *r = &sRules[k];
                if (!RuleTargets(r, name)) {
                    continue;
                }
                if (!RuleMatchesColor(r, after.r / 31.0, after.g / 31.0, after.b / 31.0)) {
                    continue;
                }
                after = ApplyRule(r, after);
                r->colors++;
            }
            if (before.r != after.r || before.g != after.g || before.b != after.b) {
                palette->data[j] = after;
                paletteChanges++;
                colorsChanged++;
            }
        }
        if (paletteChanges > 0) {
            palettesChanged++;
            printf("%s: %d\n", name, paletteChanges);
        }
    }

    FILE *output = fopen(argv[3], "wb");
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
    printf("TOTAL palettes=%d colors=%d\n", palettesChanged, colorsChanged);
    return 0;
}
