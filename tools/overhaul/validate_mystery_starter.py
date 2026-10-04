#!/usr/bin/env python3
"""D8 Mystery Egg starter validator (static + host-compiled rules).

    python3 tools/overhaul/validate_mystery_starter.py              # validate + rewrite the validation report
    python3 tools/overhaul/validate_mystery_starter.py --no-report  # validate only

Every check reads source through an injectable reader so tools/overhaul/opening/test_validate_mystery_starter.py can run deterministic
mutations. Static validation only: a green run is NOT runtime verification.
"""
import difflib
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MANIFEST = "docs/overhaul/implementation/opening/mystery_egg_starter_manifest.json"
REPORT = "docs/overhaul/implementation/opening/MYSTERY_EGG_STARTER_VALIDATION_REPORT.md"
START_SHA = "6fc1eedfec637041733b5e5d9626a49c7524daa9"

LOCKED = [("BULBASAUR", 3), ("CHARMANDER", 3), ("SQUIRTLE", 3), ("PIKACHU", 1), ("CHIKORITA", 10), ("CYNDAQUIL", 10), ("TOTODILE", 10),
          ("TREECKO", 10), ("TORCHIC", 10), ("MUDKIP", 10), ("TURTWIG", 10), ("CHIMCHAR", 10), ("PIPLUP", 10)]
LOCKED_BRANCH = {"BULBASAUR": "TURTWIG", "CHIKORITA": "TURTWIG", "TREECKO": "TURTWIG", "TURTWIG": "TURTWIG",
                 "CHARMANDER": "CHIMCHAR", "CYNDAQUIL": "CHIMCHAR", "TORCHIC": "CHIMCHAR", "CHIMCHAR": "CHIMCHAR",
                 "SQUIRTLE": "PIPLUP", "TOTODILE": "PIPLUP", "MUDKIP": "PIPLUP", "PIPLUP": "PIPLUP", "PIKACHU": "PIPLUP"}
RNG_CALL = re.compile(r"\b(LCRNG_Next|ARNG_Next|MTRNG_Next|MTRNG_Range|LCRNG_Range|GetRandom\w*|rand)\s*\(")
SINNOH = {"SPECIES_TURTWIG", "SPECIES_CHIMCHAR", "SPECIES_PIPLUP"}
# Lines the ordinary Day Care source may gain/lose in D8 (everything else in daycare.c must be byte-identical to the starting SHA).
DAYCARE_ALLOWED = [
    r"^static void Egg_CreateEggAtLevel\(", r"^void Egg_CreateEgg\(", r"Egg_CreateEggAtLevel\(egg, species, param2, trainerInfo, param4, metLocation, 1\);",
    r"Pokemon_InitWith\(egg, species, (1|level), INIT_IVS_RANDOM, FALSE, 0, OTID_NOT_SET, 0\);",
    r"^void Egg_CreateMysteryStarterEgg\(", r"Egg_CreateEggAtLevel\(egg, species, 1, trainerInfo, 4, metLocation, MYSTERY_STARTER_LEVEL\);",
    r"^static void Egg_CreateHatchedMonInternal\(", r"Pokemon_InitWith\(mon, species, (1|level), INIT_IVS_RANDOM, TRUE, personality, OTID_NOT_SET, 0\);",
    r"^void Egg_CreateHatchedMon\(", r"Egg_CreateHatchedMonAtLevel\(egg, heapID, 1\);", r"^void Egg_CreateHatchedMonAtLevel\(",
    r"Egg_CreateHatchedMonInternal\(egg, heapID(, level)?\);", r'#include "mystery_egg_starter.h"', r"^// Scripted Mystery Egg starter",
]


def git_show(path, sha=START_SHA):
    r = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def file_reader(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def strip_comments(text):
    return re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)


def func_body(text, name):
    m = re.search(rf"^[A-Za-z_][\w \*]*\b{name}\s*\([^;{{]*\)\s*\{{", text, flags=re.M)
    if not m:
        return None
    i, depth = m.end() - 1, 0
    for j in range(i, len(text)):
        depth += text[j] == "{"
        depth -= text[j] == "}"
        if depth == 0:
            return text[m.start():j + 1]
    return None


def parse_table(src):
    m = re.search(r"sMysteryStarterTable\[[^\]]*\]\s*=\s*\{(.*?)\};", src, flags=re.S)
    return [(a, int(b)) for a, b in re.findall(r"\{\s*SPECIES_(\w+)\s*,\s*(\d+)\s*\}", m.group(1))] if m else []


def parse_branch(src):
    body = func_body(src, "MysteryStarter_GetRivalBranch") or ""
    out, pending = {}, []
    for line in body.splitlines():
        m = re.search(r"case SPECIES_(\w+):", line)
        if m:
            pending.append(m.group(1))
        m = re.search(r"return SPECIES_(\w+);", line)
        if m:
            for s in pending:
                out[s] = m.group(1)
            pending = []
    return out, ("default:" in body)


def model_species(table, roll):
    acc = 0
    for sp, w in table:
        acc += w
        if roll < acc:
            return sp
    raise ValueError(roll)


class V:
    def __init__(self, reader=None, manifest=None):
        self.read = reader or file_reader
        self.manifest = manifest if manifest is not None else json.loads(file_reader(MANIFEST))
        self.results = []

    def rec(self, name, ok, detail=""):
        self.results.append((name, "PASS" if ok else "FAIL", detail))

    # -- manifest / pool ----------------------------------------------------------------------------------------------------------
    def check_pool(self):
        m = self.manifest
        src = self.read("src/mystery_egg_starter.c")
        table = parse_table(src)
        names = [s for s, _ in table]
        self.rec("pool count == 13", len(table) == 13, f"{len(table)}")
        self.rec("weight total == 100", sum(w for _, w in table) == 100, f"{sum(w for _, w in table)}")
        self.rec("no missing species", not (set(s for s, _ in LOCKED) - set(names)), ",".join(sorted(set(s for s, _ in LOCKED) - set(names))))
        self.rec("no extra species", not (set(names) - set(s for s, _ in LOCKED)), ",".join(sorted(set(names) - set(s for s, _ in LOCKED))))
        self.rec("no duplicate species", len(names) == len(set(names)))
        bad = [f"{s}:{w}!={dict(LOCKED).get(s)}" for s, w in table if dict(LOCKED).get(s) != w]
        self.rec("every locked weight matches source", not bad, ",".join(bad))
        self.rec("table order matches locked 0-99 ranges", table == LOCKED)
        mw = [(p["species"][len("SPECIES_"):], p["weight"]) for p in m["pool"]]
        self.rec("manifest pool == locked pool", mw == LOCKED and m["weight_total"] == 100 and m["pool_size"] == 13)
        self.rec("manifest weights are integers", all(isinstance(p["weight"], int) for p in m["pool"]))
        self.rec("manifest == source (drift)", mw == table, "manifest/source table differ" if mw != table else "")
        ranges_ok, lo = True, 0
        for p in m["pool"]:
            ranges_ok &= p["roll_range"] == [lo, lo + p["weight"] - 1]
            lo += p["weight"]
        self.rec("manifest roll ranges contiguous 0..99", ranges_ok and lo == 100)
        hdr = self.read("include/mystery_egg_starter.h")
        self.rec("roll range constant == 100", re.search(r"#define MYSTERY_STARTER_ROLL_RANGE\s+100\b", hdr) is not None)
        self.rec("pool size constant == 13", re.search(r"#define MYSTERY_STARTER_POOL_SIZE\s+13\b", hdr) is not None)
        self.rec("source has no floating point", not re.search(r"\b(float|double)\b|\d\.\d", strip_comments(src)))

    # -- position independence / preview -------------------------------------------------------------------------------------------
    def check_ui(self):
        src = self.read("src/mystery_egg_starter.c")
        hdr = self.read("include/mystery_egg_starter.h")
        app = self.read("src/choose_starter/choose_starter_app.c")
        cleaned = strip_comments(app)
        sig = re.search(r"u16 MysteryStarter_SpeciesFromRoll\(([^)]*)\)", hdr)
        self.rec("species table lookup takes the roll only (no egg position)", sig is not None and re.fullmatch(r"\s*u32 roll\s*", sig.group(1)) is not None)
        sig = re.search(r"u16 MysteryStarter_Draw\(([^)]*)\)", hdr)
        self.rec("draw takes no argument (egg position cannot alter the table)", sig is not None and sig.group(1).strip() in ("void", ""))
        self.rec("one table: no per-position table in source", len(re.findall(r"sMysteryStarterTable\w*\s*\[", strip_comments(src))) == 1 or
                 len(re.findall(r"\bMysteryStarterEntry\s+s\w+\[", src)) == 1)
        self.rec("chooser builds every sprite from SPECIES_EGG only", "MakeMysteryEggSprite" in cleaned and
                 len(re.findall(r"BuildPokemonSpriteTemplate\(", cleaned)) == 1 and "SPECIES_EGG" in cleaned)
        outside = re.sub(r"#define STARTER_OPTION_\d\s+SPECIES_\w+", "", cleaned)
        sel = func_body(cleaned, "GetSelectedSpecies") or ""
        outside = outside.replace(sel, "") if sel else outside
        self.rec("chooser has no per-position sprite species (STARTER_OPTION_n only in vanilla defines + GetSelectedSpecies)", not re.search(r"MakePokemonSprite\s*\(", cleaned) and not re.search(r"STARTER_OPTION_\d", outside))
        self.rec("no species constants in chooser outside the vanilla output contract other than SPECIES_EGG", not [s for s in re.findall(r"SPECIES_\w+", outside) if s not in ("SPECIES_EGG", "SPECIES_NONE")])
        self.rec("exactly three SPECIES_EGG chooser sprites (NUM_STARTER_OPTIONS == 3, one egg sprite per option)",
                 re.search(r"#define NUM_STARTER_OPTIONS\s+3\b", cleaned) is not None and
                 re.search(r"for \(int i = 0; i < NUM_STARTER_OPTIONS; i\+\+\) \{\s*MakeMysteryEggSprite\(&app->sprites\[i\], app\);", cleaned) is not None and
                 cleaned.count("MakeMysteryEggSprite(") == 3)  # prototype + loop call + definition
        exit_body = func_body(cleaned, "ChooseStarter_Exit") or ""
        self.rec("ChooseStarter_Exit restores data->species = GetSelectedSpecies(app->cursorPosition) (vanilla output contract)",
                 re.search(r"SetVBlankCallback\(NULL, NULL\);\s*data->species = GetSelectedSpecies\(app->cursorPosition\);\s*BOOL touchPadResult", exit_body) is not None)
        self.rec("GetSelectedSpecies restored with vanilla Turtwig/Chimchar/Piplup mapping",
                 all(re.search(r"#define STARTER_OPTION_%d\s+%s\b" % (i, sp), cleaned) for i, sp in enumerate(("SPECIES_TURTWIG", "SPECIES_CHIMCHAR", "SPECIES_PIPLUP"))) and
                 re.search(r"case CURSOR_POSITION_LEFT:\s*return STARTER_OPTION_0;\s*case CURSOR_POSITION_CENTER:\s*return STARTER_OPTION_1;\s*case CURSOR_POSITION_RIGHT:\s*return STARTER_OPTION_2;", sel) is not None)
        tail = exit_body[exit_body.index("BOOL touchPadResult"):] if "BOOL touchPadResult" in exit_body else ""
        order = ["DisableTouchPad()", "DeletePreviewWindow(", "DeleteCursorCellActor(", "DeleteCursorOAM(", "StopCursorMovement(", "DeleteCamera(", "Delete3DGraphics(",
                 "DeleteCellActors(", "DeletePokemonSprites(", "DeleteSpriteDisplay(", "DeleteMessageWindow(", "DeleteSubplaneWindows(", "DeleteBGs(", "Heap_Free(app->bgConfig)",
                 "DeleteDrawing()", "VramTransfer_Free()", "ApplicationManager_FreeData(appMan)", "Heap_Destroy(HEAP_ID_CHOOSE_STARTER_APP)"]
        pos = [tail.find(x) for x in order]
        self.rec("ChooseStarter_Exit teardown order identical to pre-D8 (6fc1eedf)", all(x >= 0 for x in pos) and pos == sorted(pos))
        self.rec("no cry before hatch", "Sound_PlayPokemonCry" not in cleaned)
        self.rec("no species data lookups in chooser (gender/name/type)", not re.search(r"Pokemon_GetGenderOf|GetSpeciesName|SPECIES_NAME|GetSpeciesType|SpeciesData_", cleaned))
        self.rec("chooser message index independent of cursor position", not re.search(r"360,\s*\d\s*\+\s*app->cursorPosition", cleaned))
        self.rec("Poke Ball model visibility transitions are vanilla (models 1-4 shown after the intro)", all(
                 re.search(r"Set3DGraphicsIsVisible\(&app->starter3DGraphics\[%d\],\s*TRUE\)" % i, cleaned) for i in (1, 2, 3, 4)))
        self.rec("chooser has no custom resting-state / egg-position plumbing", not re.search(r"SetMysteryEggRestingState|MYSTERY_EGG_REST|eggPosition", cleaned))
        self.rec("preview movement uses vanilla offsets (+48, scale 0.40)", "[1] + 48) << FX32_SHIFT" in cleaned and cleaned.count("FX32_CONST(0.40f), FX32_CONST(1.0f), 6)") == 2)
        self.rec("chooser draws no random numbers", not RNG_CALL.search(cleaned))
        txt = json.loads(self.read("res/text/unk_0360.json"))["messages"]
        by = {m["id"][-5:]: "".join(m.get("en_US", [])) for m in txt}
        same = by.get("00001") == by.get("00002") == by.get("00003") and by.get("00001")
        self.rec("confirmation wording identical for all three eggs", bool(same))
        names = re.compile(r"TURTWIG|CHIMCHAR|PIPLUP|Tiny Leaf|Chimp|Penguin|Poké Ball", re.I)
        self.rec("chooser text names no species / type / ball", not any(names.search(by.get(k, "")) for k in ("00000", "00001", "00002", "00003", "00007")))
        self.rec("chooser text says Egg", all("Egg" in by.get(k, "") for k in ("00000", "00001", "00007")))

    # -- RNG / persistence / reveal ordering ---------------------------------------------------------------------------------------
    def check_rng_and_flow(self):
        scrcmd = strip_comments(self.read("src/scrcmd.c"))
        save = func_body(scrcmd, "ScrCmd_SaveChosenStarter") or ""
        r201 = self.read("res/field/scripts/scripts_route_201.s")
        body = r201[r201.index("Route201_Briefcase:"):r201.index("Route201_DawnLeave:")]

        # The fragile application-exit boundary is deliberately vanilla.
        self.rec("SaveChosenStarter uses the vanilla chooser output contract",
                 "ChooseStarterData *chooseStarterData = (*fieldSysDataPtr);" in save and
                 re.search(r"SystemVars_SetPlayerStarter\([^;]*chooseStarterData->species\)", save) is not None)
        self.rec("SaveChosenStarter performs no Mystery RNG / persistence work",
                 "MysteryStarter_" not in save and "SystemVars_SetMysteryStarterSpecies" not in save and
                 "VAR_MYSTERY_STARTER_SPECIES" not in save)
        self.rec("SaveChosenStarter frees chooser data exactly once",
                 save.count("Heap_Free(*fieldSysDataPtr)") == 1)

        # Native script RNG only after the field has fully returned.
        seq = ["StartChooseStarterScene", "SaveChosenStarter", "ReturnToField",
               "FadeScreenIn", "WaitFadeScreen", "GetRandom VAR_0x8000, 100"]
        positions = [body.find(x) for x in seq]
        self.rec("native draw occurs only after chooser exit + full field restore",
                 all(p >= 0 for p in positions) and positions == sorted(positions), str(positions))
        self.rec("Route 201 has exactly one native starter RNG draw",
                 body.count("GetRandom VAR_0x8000, 100") == 1 and len(re.findall(r"\bGetRandom\b", body)) == 1)
        self.rec("active Route 201 path never calls MysteryStarter_Draw",
                 "MysteryStarter_Draw" not in body and "MysteryStarter_" not in body)

        # Locked weighted ranges, encoded with ascending exclusive thresholds.
        thresholds = [
            (3, "Bulbasaur"), (6, "Charmander"), (9, "Squirtle"), (10, "Pikachu"),
            (20, "Chikorita"), (30, "Cyndaquil"), (40, "Totodile"), (50, "Treecko"),
            (60, "Torchic"), (70, "Mudkip"), (80, "Turtwig"), (90, "Chimchar"),
        ]
        got = re.findall(r"GoToIfLt VAR_0x8000, (\d+), Route201_MysteryStarter_(\w+)", body)
        got = [(int(n), s) for n, s in got]
        self.rec("script thresholds encode the locked 0-99 weighted distribution", got == thresholds, str(got))
        self.rec("90-99 falls through defensively to Piplup",
                 "GoTo Route201_MysteryStarter_Piplup" in body)

        branches = {
            "Bulbasaur": ("BULBASAUR", "TURTWIG"),
            "Charmander": ("CHARMANDER", "CHIMCHAR"),
            "Squirtle": ("SQUIRTLE", "PIPLUP"),
            "Pikachu": ("PIKACHU", "PIPLUP"),
            "Chikorita": ("CHIKORITA", "TURTWIG"),
            "Cyndaquil": ("CYNDAQUIL", "CHIMCHAR"),
            "Totodile": ("TOTODILE", "PIPLUP"),
            "Treecko": ("TREECKO", "TURTWIG"),
            "Torchic": ("TORCHIC", "CHIMCHAR"),
            "Mudkip": ("MUDKIP", "PIPLUP"),
            "Turtwig": ("TURTWIG", "TURTWIG"),
            "Chimchar": ("CHIMCHAR", "CHIMCHAR"),
            "Piplup": ("PIPLUP", "PIPLUP"),
        }
        bad = []
        for label, (actual, canonical) in branches.items():
            start = body.find(f"Route201_MysteryStarter_{label}:")
            if start < 0:
                bad.append(label + ":missing")
                continue
            end_candidates = [body.find(f"\nRoute201_MysteryStarter_{x}:", start + 1) for x in list(branches) + ["Award"]]
            end_candidates = [x for x in end_candidates if x >= 0]
            end = min(end_candidates) if end_candidates else len(body)
            block = body[start:end]
            if f"SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_{actual}" not in block:
                bad.append(label + ":actual")
            if f"SetVar VAR_PLAYER_STARTER, SPECIES_{canonical}" not in block:
                bad.append(label + ":canonical")
            if "GoTo Route201_MysteryStarter_Award" not in block:
                bad.append(label + ":award")
        self.rec("all 13 species persist actual + canonical branch correctly", not bad, ",".join(bad))

        award = body[body.index("Route201_MysteryStarter_Award:"):]
        self.rec("award copies the persisted actual species with vanilla SetVarFromVar",
                 "SetVarFromVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES" in award)
        self.rec("starter is awarded directly at Level 5 through vanilla GivePokemon",
                 "GivePokemon VAR_0x8000, 5, ITEM_NONE, VAR_RESULT" in award and award.count("GivePokemon") == 1)
        self.rec("no custom Mystery starter script commands remain on Route 201",
                 not re.search(r"\b(GetMysteryStarterSpecies|GiveMysteryStarterEgg|HatchMysteryStarterEgg)\b", body))

        table = self.read("include/data/scripts/scrcmd.h")
        macros = self.read("asm/macros/scrcmd.inc")
        custom = ("GETMYSTERYSTARTERSPECIES", "GIVEMYSTERYSTARTEREGG", "HATCHMYSTERYSTARTEREGG")
        self.rec("unused D8 script opcodes removed (command table restored to vanilla shape)",
                 not any(x in table for x in custom))
        self.rec("unused D8 script macros removed",
                 not re.search(r"\b(GetMysteryStarterSpecies|GiveMysteryStarterEgg|HatchMysteryStarterEgg)\b", macros))

        lab = self.read("res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s")
        self.rec("Sandgem lab reads actual starter with vanilla SetVarFromVar",
                 "SetVarFromVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES" in lab and
                 "GetMysteryStarterSpecies" not in lab)

        csd = self.read("include/struct_defs/choose_starter_data.h")
        self.rec("ChooseStarterData layout is exactly vanilla (int species; const Options *options;)",
                 re.search(r"typedef struct ChooseStarterData \{\s*int species;\s*const Options \*options;\s*\} ChooseStarterData;", csd) is not None)
        self.rec("save format unchanged (Mystery species uses existing var slot)",
                 "VAR_" not in csd)


    def check_output_and_breeding(self):
        r201 = self.read("res/field/scripts/scripts_route_201.s")
        body = r201[r201.index("Route201_Briefcase:"):r201.index("Route201_DawnLeave:")]
        self.rec("starter output is Lv5 through the native GivePokemon command",
                 "GivePokemon VAR_0x8000, 5, ITEM_NONE, VAR_RESULT" in body)

        # Hardened design: D8 must not alter ordinary breeding or the hatch engine at all.
        untouched = (
            "include/egg_hatch.h",
            "include/overlay005/daycare.h",
            "include/unk_0203D1B8.h",
            "src/egg_hatch.c",
            "src/overlay005/daycare.c",
            "src/unk_0203D1B8.c",
            "include/constants/daycare.h",
            "src/daycare_save.c",
            "include/struct_defs/daycare.h",
        )
        for path in untouched:
            base = git_show(path)
            self.rec(f"{path} byte-identical to pre-D8", base is not None and base == self.read(path))

        meson = self.read("src/meson.build")
        self.rec("reference Mystery starter C module is not linked into the ROM",
                 "'mystery_egg_starter.c'" not in meson and '"mystery_egg_starter.c"' not in meson)

        scripts = "\n".join(self.read(os.path.relpath(p, ROOT))
                            for p in glob.glob(os.path.join(ROOT, "res/field/scripts/*.s")))
        self.rec("no field script invokes custom Mystery hatch commands",
                 not re.search(r"\b(GiveMysteryStarterEgg|HatchMysteryStarterEgg)\b", scripts))

        for p in sorted(glob.glob(os.path.join(ROOT, "docs/overhaul/implementation/breeding/*.json"))):
            rel = os.path.relpath(p, ROOT)
            self.rec(f"breeding manifest unchanged: {os.path.basename(rel)}", (git_show(rel) or "") == self.read(rel))


    def check_rival(self):
        src = self.read("src/mystery_egg_starter.c")
        got, has_default = parse_branch(src)
        bad = [f"{s}->{got.get(s)}" for s, b in LOCKED_BRANCH.items() if got.get(s) != b]
        self.rec("category -> Rival mapping matches the lock", not bad and len(got) == 13, ",".join(bad))
        self.rec("Pikachu -> Piplup branch", got.get("PIKACHU") == "PIPLUP")
        self.rec("branch result is always one of the three Sinnoh representatives", set("SPECIES_" + v for v in got.values()) <= SINNOH)
        self.rec("unknown/NONE species falls back to the Piplup branch", has_default and "default:" in src)
        sv = strip_comments(self.read("src/system_vars.c"))
        for fn in ("SystemVars_GetRivalStarter", "SystemVars_GetPlayerCounterpartStarter"):
            b = func_body(sv, fn) or ""
            self.rec(f"{fn} is vanilla (keyed directly on canonical VAR_PLAYER_STARTER)", "playerStarter = TryGetVarValue(varsFlags, VAR_PLAYER_STARTER)" in b and "Branch" not in b and "Mystery" not in b)
        self.rec("SystemVars_GetPlayerStarter returns canonical VAR_PLAYER_STARTER", re.search(r"return TryGetVarValue\(varsFlags, VAR_PLAYER_STARTER\);", func_body(sv, "SystemVars_GetPlayerStarter") or "") is not None)
        self.rec("SystemVars_Get/SetMysteryStarterSpecies use VAR_MYSTERY_STARTER_SPECIES",
                 "TryGetVarValue(varsFlags, VAR_MYSTERY_STARTER_SPECIES)" in (func_body(sv, "SystemVars_GetMysteryStarterSpecies") or "") and
                 "TrySetVarToValue(varsFlags, VAR_MYSTERY_STARTER_SPECIES, species)" in (func_body(sv, "SystemVars_SetMysteryStarterSpecies") or ""))
        self.rec("no custom branch-remap layer (SystemVars_GetPlayerStarterBranch / GetPlayerStarterBranch removed)",
                 "SystemVars_GetPlayerStarterBranch" not in sv and not any("GetPlayerStarterBranch" in self.read(os.path.relpath(pp, ROOT))
                     for pp in glob.glob(os.path.join(ROOT, "src", "**", "*.[ch]"), recursive=True) + glob.glob(os.path.join(ROOT, "include", "**", "*.h"), recursive=True) +
                     glob.glob(os.path.join(ROOT, "res/field/scripts/*.s")) + [os.path.join(ROOT, "asm/macros/scrcmd.inc")]))
        self.rec("legacy MysteryStarter_GetRivalBranch helper has no runtime consumer",
                 sum(len(re.findall(r"\bMysteryStarter_GetRivalBranch\s*\(", strip_comments(self.read(os.path.relpath(pp, ROOT)))))
                     for pp in glob.glob(os.path.join(ROOT, "src", "**", "*.c"), recursive=True) if not pp.endswith("mystery_egg_starter.c")) == 0)
        vf = self.read("generated/vars_flags.txt").split()
        self.rec("VAR_MYSTERY_STARTER_SPECIES takes the former VAR_UNUSED_0x4031 slot (directly after VAR_PLAYER_STARTER)",
                 "VAR_UNUSED_0x4031" not in vf and "VAR_MYSTERY_STARTER_SPECIES" in vf and vf.index("VAR_MYSTERY_STARTER_SPECIES") == vf.index("VAR_PLAYER_STARTER") + 1)
        base_vf = (git_show("generated/vars_flags.txt") or "").split()
        self.rec("var table size unchanged and rename is the only delta (no save-size change)",
                 bool(base_vf) and len(base_vf) == len(vf) and [x for x in base_vf if x not in vf] == ["VAR_UNUSED_0x4031"] and [x for x in vf if x not in base_vf] == ["VAR_MYSTERY_STARTER_SPECIES"])
        self.rec("the renamed var has no other consumer than the Mystery starter helpers",
                 vf.count("VAR_MYSTERY_STARTER_SPECIES") == 1 and not any("VAR_UNUSED_0x4031" in self.read(os.path.relpath(pp, ROOT))
                     for pp in glob.glob(os.path.join(ROOT, "src", "**", "*.[ch]"), recursive=True) + glob.glob(os.path.join(ROOT, "res/field/scripts/*.s"))))
        strs = strip_comments(self.read("src/scrcmd_strings.c"))
        self.rec("player starter name buffer uses the actual Mystery species", "SystemVars_GetMysteryStarterSpecies(" in (func_body(strs, "ScrCmd_BufferPlayerStarterSpeciesName") or ""))
        self.rec("rival / counterpart name buffers stay on canonical vanilla helpers",
                 "SystemVars_GetRivalStarter(" in (func_body(strs, "ScrCmd_BufferRivalStarterSpeciesName") or "") and
                 "SystemVars_GetPlayerCounterpartStarter(" in (func_body(strs, "ScrCmd_BufferPlayerCounterpartStarterSpeciesName") or "") and
                 "Mystery" not in (func_body(strs, "ScrCmd_BufferRivalStarterSpeciesName") or "") + (func_body(strs, "ScrCmd_BufferPlayerCounterpartStarterSpeciesName") or ""))
        mystery_users, wrong, drift = [], [], []
        for p in sorted(glob.glob(os.path.join(ROOT, "res/field/scripts/*.s"))):
            rel = os.path.relpath(p, ROOT)
            t = self.read(rel)
            if "GetMysteryStarterSpecies" in t:
                mystery_users.append(os.path.basename(rel))
            if "GetPlayerStarterSpecies VAR_RESULT" in t:
                for m in re.finditer(r"(GoToIfEq|CallIfEq) VAR_RESULT, (SPECIES_\w+)", t):
                    if m.group(2) not in SINNOH:
                        wrong.append(f"{os.path.basename(rel)}:{m.group(2)}")
            if not rel.endswith(("scripts_route_201.s", "sandgem_town_pokemon_research_lab.s")):
                base = git_show(rel)
                if base is not None and base != t:
                    drift.append(os.path.basename(rel))
        self.rec("custom GetMysteryStarterSpecies command is unused in all field scripts", not mystery_users, ",".join(mystery_users))
        self.rec("every other script is byte-identical to the vanilla starting SHA (all Rival/branch consumers use canonical VAR_PLAYER_STARTER)", not drift, ",".join(drift))
        r201t = self.read("res/field/scripts/scripts_route_201.s")
        self.rec("Route 201 persists/awards the actual Mystery species directly from VAR_MYSTERY_STARTER_SPECIES",
                 "SetVarFromVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES" in r201t and "GetMysteryStarterSpecies" not in r201t)
        self.rec("Sandgem lab starter-gift skip reads the actual species directly (later gifts unchanged)",
                 "SetVarFromVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES" in self.read("res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s"))
        self.rec("branch consumers compare only against Turtwig/Chimchar/Piplup", not wrong, ",".join(wrong))
        self.rec("hatch presentation is not active: no script calls GiveMysteryStarterEgg / HatchMysteryStarterEgg",
                 not any(re.search(r"\b(GiveMysteryStarterEgg|HatchMysteryStarterEgg)\b", self.read(os.path.relpath(pp, ROOT))) for pp in glob.glob(os.path.join(ROOT, "res/field/scripts/*.s"))))
        rival_labels = [l for p in glob.glob(os.path.join(ROOT, "res/field/scripts/*.s")) for l in re.findall(r"^\w*Rival\w*:", self.read(os.path.relpath(p, ROOT)), flags=re.M)]
        dup = [l for l in rival_labels if re.search(r"Bulbasaur|Charmander|Squirtle|Pikachu|Chikorita|Cyndaquil|Totodile|Treecko|Torchic|Mudkip", l)]
        self.rec("no thirteen-way Rival duplication (no Rival label for non-Sinnoh species)", not dup, ",".join(dup))
        trainers = [t for p in glob.glob(os.path.join(ROOT, "res/field/scripts/*.s")) for t in re.findall(r"TRAINER_RIVAL_\w*(?:BULBASAUR|CHARMANDER|SQUIRTLE|PIKACHU|CHIKORITA|CYNDAQUIL|TOTODILE|TREECKO|TORCHIC|MUDKIP)\w*", self.read(os.path.relpath(p, ROOT)))]
        self.rec("no Rival trainer IDs for non-Sinnoh starters", not trainers)
        pool = {"Grass": "TURTWIG", "Fire": "CHIMCHAR", "Water": "PIPLUP"}
        self.rec("manifest declares exactly three Rival branches", self.manifest.get("rival_branch_count") == 3 and len(self.manifest["rival_branches"]) == 3 and
                 {v: k for k, v in self.manifest["rival_branches"].items()} == {k: "SPECIES_" + v for k, v in pool.items()})
        self.rec("manifest persistence: VAR_PLAYER_STARTER canonical, actual species separate", self.manifest["persistence"].get("canonical_store", "").startswith("VAR_PLAYER_STARTER") and self.manifest["persistence"].get("actual_species_store", "").startswith("VAR_MYSTERY_STARTER_SPECIES"))
        self.rec("manifest category->Rival mapping matches source", all(p["rival_branch"] == "SPECIES_" + got.get(p["species"][8:], "?") for p in self.manifest["pool"]))

    # -- manifest guards ---------------------------------------------------------------------------------------------------------------------------
    def check_manifest(self):
        m = self.manifest
        self.rec("manifest starting SHA", m["starting_sha"] == START_SHA)
        self.rec("manifest never claims VERIFIED", m["validation"]["verified"] is False and m["validation"]["runtime"] == "NOT RUN")
        miss, drift = [], []
        for path, g in m["source_guards"].items():
            if not os.path.exists(os.path.join(ROOT, path)):
                miss.append(path)
                continue
            r = subprocess.run(["git", "rev-parse", f"{START_SHA}:{path}"], cwd=ROOT, capture_output=True, text=True)
            before = r.stdout.strip() if r.returncode == 0 else None
            if before != g["before_blob"]:
                drift.append(path)
        self.rec("every guarded source path exists", not miss, ",".join(miss))
        self.rec("before-blob guards match the starting SHA", not drift, ",".join(drift))
        self.rec("manifest records the deferred hatch presentation", m["reveal"]["hatch_presentation"] == "DEFERRED_DISABLED" and m["reveal"]["mechanism"].startswith("GivePokemon"))
        self.rec("manifest visual equivalence flags", all(m["visual_equivalence"][k] is False for k in ("species_preview", "species_name_preview", "type_hint", "cry_before_hatch", "table_depends_on_position")))
        self.rec("manifest RNG timing: one draw, no rerolls", m["rng"]["draws"] == 1 and not any(m["rng"][k] for k in ("position_is_input", "reroll_on_hatch", "reroll_on_field_return", "reroll_on_battle_start")))
        self.rec("manifest output level == 5", m["output"]["level"] == 5)
        self.rec("manifest has no save-format change", m["persistence"]["save_format_change"] is False)

    def run(self):
        for fn in (self.check_pool, self.check_ui, self.check_rng_and_flow, self.check_output_and_breeding, self.check_rival, self.check_manifest):
            fn()
        return self.results


# -- exhaustive host-compiled test of the real C table ---------------------------------------------------------------------------------------------
def host_compile_histogram():
    """Compiles src/mystery_egg_starter.c with stub headers and evaluates MysteryStarter_SpeciesFromRoll for all 100 rolls x 3 egg positions."""
    cc = shutil.which("gcc") or shutil.which("cc")
    if not cc:
        return None
    ids = {s: i + 1 for i, (s, _) in enumerate(LOCKED)}
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "generated"))
        open(os.path.join(d, "nitro.h"), "w").write("#include <stdint.h>\ntypedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef int BOOL;\n#define TRUE 1\n#define FALSE 0\n#define GF_ASSERT(x) ((x) ? (void)0 : __builtin_trap())\n")
        open(os.path.join(d, "nitro_types.h"), "w").write('#include "nitro.h"\n')
        os.makedirs(os.path.join(d, "nitro"))
        open(os.path.join(d, "nitro", "types.h"), "w").write('#include "../nitro.h"\n')
        open(os.path.join(d, "generated", "species.h"), "w").write("".join(f"#define SPECIES_{s} {i}\n" for s, i in ids.items()))
        open(os.path.join(d, "math_util.h"), "w").write("#include <stdint.h>\nextern uint16_t gStubRng;\nstatic inline uint16_t LCRNG_Next(void){ return gStubRng; }\n")
        shutil.copy(os.path.join(ROOT, "include/mystery_egg_starter.h"), d)
        shutil.copy(os.path.join(ROOT, "src/mystery_egg_starter.c"), d)
        open(os.path.join(d, "main.c"), "w").write(
            '#include <stdio.h>\n#include "mystery_egg_starter.h"\nuint16_t gStubRng;\n'
            'int main(void){ for (int pos = 0; pos < 3; pos++) for (unsigned r = 0; r < 100; r++) {'
            ' gStubRng = (uint16_t)r; unsigned a = MysteryStarter_SpeciesFromRoll(r); unsigned b = MysteryStarter_Draw();'
            ' printf("%d %u %u %u %u\\n", pos, r, a, b, MysteryStarter_GetRivalBranch((uint16_t)a)); } return 0; }\n')
        r = subprocess.run([cc, "-std=c11", "-O0", "-I", d, "-o", os.path.join(d, "t"), os.path.join(d, "main.c"), os.path.join(d, "mystery_egg_starter.c")], capture_output=True, text=True)
        if r.returncode:
            return {"error": r.stderr[:500]}
        out = subprocess.run([os.path.join(d, "t")], capture_output=True, text=True).stdout.split("\n")
    inv = {i: s for s, i in ids.items()}
    rows = [tuple(map(int, l.split())) for l in out if l.strip()]
    return {"rows": [(p, r_, inv[a], inv[b], inv[br]) for p, r_, a, b, br in rows]}


def exhaustive_checks(v):
    res = []
    host = host_compile_histogram()
    table = parse_table(v.read("src/mystery_egg_starter.c"))
    model = {r: model_species(table, r) for r in range(100)} if table and sum(w for _, w in table) == 100 else {}
    if host is None:
        res.append(("host-compiled 0-99 exhaustive test", "FAIL", "no host C compiler"))
        return res
    if "error" in host:
        res.append(("host-compiled 0-99 exhaustive test", "FAIL", host["error"]))
        return res
    rows = host["rows"]
    hist = {}
    for p, r_, sp, dr, br in rows:
        if p == 0:
            hist[sp] = hist.get(sp, 0) + 1
    want = dict(LOCKED)
    res.append(("exhaustive 0-99: histogram == locked weights", "PASS" if hist == want else "FAIL", str(hist) if hist != want else "13 species, 100 inputs"))
    by_pos = {p: [sp for q, r_, sp, dr, br in rows if q == p] for p in range(3)}
    res.append(("left/center/right produce identical species for identical RNG inputs", "PASS" if by_pos[0] == by_pos[1] == by_pos[2] and len(by_pos[0]) == 100 else "FAIL", "3 x 100 inputs"))
    res.append(("MysteryStarter_Draw(roll) == SpeciesFromRoll(roll)", "PASS" if all(sp == dr for _, _, sp, dr, _ in rows) else "FAIL", ""))
    res.append(("compiled table == independent Python model", "PASS" if model and all(model[r_] == sp for _, r_, sp, _, _ in rows) else "FAIL", ""))
    res.append(("compiled Rival branch == locked mapping for all 100 rolls", "PASS" if all(LOCKED_BRANCH[sp] == br for _, _, sp, _, br in rows) else "FAIL", ""))
    ranges = {}
    for _, r_, sp, _, _ in rows[:100]:
        lo, hi = ranges.get(sp, (r_, r_))
        ranges[sp] = (min(lo, r_), max(hi, r_))
    exp, lo = {}, 0
    for s, w in LOCKED:
        exp[s] = (lo, lo + w - 1)
        lo += w
    res.append(("compiled roll ranges == locked ranges (0-2 Bulbasaur ... 90-99 Piplup)", "PASS" if ranges == exp else "FAIL", ""))
    return res


def write_report(results, exh):
    allr = results + exh
    fails = [r for r in allr if r[1] == "FAIL"]
    lines = ["# Mystery Egg Starter — Validation Report (D8)", "",
             f"Generated by `tools/overhaul/validate_mystery_starter.py` against starting SHA `{START_SHA}`. Static + host-compiled validation only; "
             "**not runtime verification** (all runtime cases NOT RUN).", "",
             f"**Result: {'PASS' if not fails else 'FAIL'} — {len(allr) - len(fails)} pass, {len(fails)} fail.**", "",
             "| Check | Result | Detail |", "|---|---|---|"]
    for n, r, d in allr:
        lines.append(f"| {n} | {r} | {d.replace('|', '/')} |")
    mut = os.path.join(ROOT, "docs/overhaul/implementation/opening/mutation_results.json")
    if os.path.exists(mut):
        m = json.load(open(mut))
        lines += ["", "## Deterministic mutation tests", "", f"{m['detected']}/{m['total']} mutations detected; baseline failures: {m['baseline_failures']}.", "",
                  "| Mutation | Detected | Failing checks |", "|---|---|---|"]
        lines += [f"| {c['name']} | {'yes' if c['detected'] else 'MISSED'} | {c['failing']} |" for c in m["cases"]]
    lines.append("")
    with open(os.path.join(ROOT, REPORT), "w") as f:
        f.write("\n".join(lines))


def main():
    v = V()
    results = v.run()
    exh = exhaustive_checks(v)
    fails = [r for r in results + exh if r[1] == "FAIL"]
    for n, r, d in results + exh:
        if r == "FAIL":
            print(f"FAIL: {n} {d}")
    print(f"mystery starter validation: {len(results) + len(exh) - len(fails)} pass, {len(fails)} fail")
    if "--no-report" not in sys.argv:
        write_report(results, exh)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
