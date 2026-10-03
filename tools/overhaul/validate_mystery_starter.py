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
        self.rec("chooser has no per-position sprite species", not re.search(r"MakePokemonSprite\s*\(|STARTER_OPTION_\d", cleaned))
        self.rec("no species constants in chooser other than SPECIES_EGG", not [s for s in re.findall(r"SPECIES_\w+", cleaned) if s != "SPECIES_EGG"])
        self.rec("no cry before hatch", "Sound_PlayPokemonCry" not in cleaned)
        self.rec("no species data lookups in chooser (gender/name/type)", not re.search(r"Pokemon_GetGenderOf|GetSpeciesName|SPECIES_NAME|GetSpeciesType|SpeciesData_", cleaned))
        self.rec("chooser message index independent of cursor position", not re.search(r"360,\s*\d\s*\+\s*app->cursorPosition", cleaned))
        self.rec("Poke Ball models stay hidden after the intro", not re.search(r"Set3DGraphicsIsVisible\(&app->starter3DGraphics\[[234]\],\s*TRUE\)", cleaned))
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
        src = strip_comments(self.read("src/mystery_egg_starter.c"))
        scrcmd = strip_comments(self.read("src/scrcmd.c"))
        draw = func_body(src, "MysteryStarter_Draw") or ""
        self.rec("exactly one RNG call in the starter module", len(RNG_CALL.findall(src)) == 1, f"{len(RNG_CALL.findall(src))}")
        self.rec("the RNG call is inside MysteryStarter_Draw", len(RNG_CALL.findall(draw)) == 1)
        self.rec("draw is LCRNG_Next() % MYSTERY_STARTER_ROLL_RANGE", "LCRNG_Next() % MYSTERY_STARTER_ROLL_RANGE" in draw)
        self.rec("SpeciesFromRoll is RNG-free", not RNG_CALL.search(func_body(src, "MysteryStarter_SpeciesFromRoll") or "x("))
        calls = 0
        for path in glob.glob(os.path.join(ROOT, "src", "**", "*.c"), recursive=True):
            rel = os.path.relpath(path, ROOT)
            text = strip_comments(self.read(rel))
            if rel != "src/mystery_egg_starter.c":
                calls += len(re.findall(r"\bMysteryStarter_Draw\s*\(", text))
        self.rec("MysteryStarter_Draw has exactly one caller", calls == 1, f"{calls}")
        save = func_body(scrcmd, "ScrCmd_SaveChosenStarter") or ""
        self.rec("the caller is ScrCmd_SaveChosenStarter", "MysteryStarter_Draw()" in save)
        self.rec("result persisted immediately via SystemVars_SetPlayerStarter", re.search(r"SystemVars_SetPlayerStarter\([^;]*species\)", save) is not None)
        self.rec("draw happens once per call (no loop around it)", not re.search(r"\b(for|while)\b", save))
        for fn in ("ScrCmd_GiveMysteryStarterEgg", "ScrCmd_HatchMysteryStarterEgg", "ScrCmd_GetPlayerStarterBranch", "ScrCmd_StartChooseStarterScene"):
            self.rec(f"no RNG/draw in {fn}", not RNG_CALL.search(func_body(scrcmd, fn) or "x(") and "MysteryStarter_Draw" not in (func_body(scrcmd, fn) or ""))
        give = func_body(scrcmd, "ScrCmd_GiveMysteryStarterEgg") or ""
        self.rec("egg is bound to the persisted species (reads VAR_PLAYER_STARTER)", "SystemVars_GetPlayerStarter(" in give and "Egg_CreateMysteryStarterEgg(egg, species" in give)
        self.rec("save format unchanged (no new save fields)", "VAR_" not in self.read("include/struct_defs/choose_starter_data.h"))
        r201 = self.read("res/field/scripts/scripts_route_201.s")
        body = r201[r201.index("Route201_Briefcase:"):r201.index("Route201_DawnLeave:")]
        cmds = [l.strip().split()[0] for l in body.splitlines() if l.strip() and not l.strip().endswith(":")]
        need = ["StartChooseStarterScene", "SaveChosenStarter", "ReturnToField", "GiveMysteryStarterEgg", "HatchMysteryStarterEgg"]
        pos = [cmds.index(c) if c in cmds else -1 for c in need]
        self.rec("Route 201 order: choose -> save/draw -> return -> give egg -> hatch", -1 not in pos and pos == sorted(pos), str(pos))
        self.rec("hatch precedes Rowan departure", "HatchMysteryStarterEgg" in cmds and cmds.index("HatchMysteryStarterEgg") < cmds.index("ApplyMovement", cmds.index("HatchMysteryStarterEgg")))
        self.rec("hatch is in the same label chain before the first Rival battle", "StartFirstBattle" not in body and "Route201_StartRivalBattle:" in r201)
        self.rec("old direct GivePokemon starter award removed from Route201_Briefcase", "GivePokemon" not in body)
        self.rec("Route 201 draws no random numbers", not re.search(r"\bGetRandom", r201))
        self.rec("Rowan/counterpart/Barry flow labels preserved", all(x in r201 for x in ("Route201_DawnLeave:", "Route201_LucasLeave:", "Route201_CounterpartLeave:",
                 "Route201_AskUpForABattle:", "Route201_StartRivalBattle:", "Route201_HandleRivalBattleEnd:", "StartFirstBattle TRAINER_RIVAL_ROUTE_201_TURTWIG")))
        self.rec("first Rival battle always follows a hatched Level-5 Pokemon (flow cannot skip the hatch)",
                 r201.count("HatchMysteryStarterEgg") == 1 and r201.index("HatchMysteryStarterEgg") < r201.index("Route201_StartRivalBattle:") and
                 "Route201_Briefcase" in r201 and r201.count("SaveChosenStarter") == 1)

        self.check_hatch_lifecycle(r201)

    def check_hatch_lifecycle(self, r201):
        """D8 runtime-QA regression: the script must mirror vanilla CommonScript_HatchEgg (Message, WaitABPress, fade out, close, hatch, fade in) so no
        message/fade is left stacked around the native FieldTask_HatchEgg FinishMap/StartMap lifecycle."""
        body = r201[r201.index("Route201_Briefcase:"):r201.index("Route201_DawnLeave:")]
        cmds = [l.strip().split()[0] for l in body.splitlines() if l.strip() and not l.strip().endswith(":")]
        i = cmds.index("GiveMysteryStarterEgg") if "GiveMysteryStarterEgg" in cmds else -1
        want = ["GiveMysteryStarterEgg", "Message", "WaitABPress", "FadeScreenOut", "WaitFadeScreen", "CloseMessage", "HatchMysteryStarterEgg", "FadeScreenIn", "WaitFadeScreen"]
        self.rec("Route 201 hatch sequence mirrors vanilla CommonScript_HatchEgg", i >= 0 and cmds[i:i + len(want)] == want, str(cmds[i:i + len(want)] if i >= 0 else None))
        self.rec("hatch task invoked exactly once", body.count("HatchMysteryStarterEgg") == 1 and r201.count("HatchMysteryStarterEgg") == 1)
        h = cmds.index("HatchMysteryStarterEgg") if "HatchMysteryStarterEgg" in cmds else -1
        window = cmds[i:h + 3] if i >= 0 and h >= 0 else []
        self.rec("exactly one FadeScreenOut/FadeScreenIn pair around the hatch (no stacked fades)", window.count("FadeScreenOut") == 1 and window.count("FadeScreenIn") == 1)
        fo = cmds.index("FadeScreenOut", i) if i >= 0 and "FadeScreenOut" in cmds[i:] else -1
        self.rec("no message is printed while the screen is faded out for the hatch", fo >= 0 and h > fo and "Message" not in cmds[fo:h])
        hs = strip_comments(self.read("src/unk_0203D1B8.c"))
        fn = func_body(hs, "FieldSystem_HatchMysteryStarterEgg") or ""
        self.rec("starter hatch calls EggHatch_HatchEgg exactly once and no extra transition", fn.count("EggHatch_HatchEgg(") == 1 and "FieldTransition_" not in fn)
        eh = strip_comments(self.read("src/egg_hatch.c"))
        task = func_body(eh, "FieldTask_HatchEgg") or ""
        self.rec("native hatch task owns FinishMap then StartMap (field returns after hatch)", task.count("FieldTransition_FinishMap(") == 1 and task.count("FieldTransition_StartMap(") == 1 and task.index("FieldTransition_FinishMap(") < task.index("FieldTransition_StartMap("))

    # -- level / hatch / breeding ----------------------------------------------------------------------------------------------------
    def check_output_and_breeding(self):
        hdr = self.read("include/mystery_egg_starter.h")
        self.rec("output level constant == 5", re.search(r"#define MYSTERY_STARTER_LEVEL\s+5\b", hdr) is not None)
        dc = strip_comments(self.read("src/overlay005/daycare.c"))
        self.rec("starter egg created at MYSTERY_STARTER_LEVEL", "metLocation, MYSTERY_STARTER_LEVEL);" in (func_body(dc, "Egg_CreateMysteryStarterEgg") or ""))
        self.rec("ordinary Egg_CreateEgg stays level 1", "metLocation, 1);" in (func_body(dc, "Egg_CreateEgg") or ""))
        self.rec("ordinary Egg_CreateHatchedMon stays level 1", "Egg_CreateHatchedMonAtLevel(egg, heapID, 1)" in (func_body(dc, "Egg_CreateHatchedMon") or ""))
        hs = strip_comments(self.read("src/unk_0203D1B8.c"))
        self.rec("starter hatch uses MYSTERY_STARTER_LEVEL", "args.hatchLevel = MYSTERY_STARTER_LEVEL;" in (func_body(hs, "FieldSystem_HatchMysteryStarterEgg") or ""))
        self.rec("ordinary FieldSystem_HatchEgg leaves hatchLevel 0", "args.hatchLevel = 0;" in (func_body(hs, "FieldSystem_HatchEgg") or ""))
        self.rec("starter hatch skips the Happy Happy Egg Club TV segment", "HappyHappyEggClub" not in (func_body(hs, "FieldSystem_HatchMysteryStarterEgg") or "x"))
        eh = strip_comments(self.read("src/egg_hatch.c"))
        self.rec("hatch scene: level override only when hatchLevel > 1", re.search(r"if \(app->args\.hatchLevel > 1\) \{\s*Egg_CreateHatchedMonAtLevel\(app->args\.mon, HEAP_ID_FIELD2, app->args\.hatchLevel\);\s*\} else \{\s*Egg_CreateHatchedMon\(", eh) is not None)
        gen = func_body(dc, "Egg_CreateEggAtLevel") or ""
        self.rec("starter egg has no inheritance / Day Care state", not re.search(r"Daycare|Inherit|parent|BoxMon_GetPair", gen, re.I))
        self.rec("starter egg keeps random IV generation (no guaranteed IV/nature/shiny)", "INIT_IVS_RANDOM, FALSE, 0, OTID_NOT_SET, 0" in gen)
        # ordinary breeding source: the only daycare.c delta vs the starting SHA is the level plumbing above
        base = git_show("src/overlay005/daycare.c")
        if base is None:
            self.rec("daycare.c delta limited to level plumbing", False, "start SHA unavailable")
        else:
            cur = self.read("src/overlay005/daycare.c")
            delta = [l[1:].strip() for l in difflib.unified_diff(base.splitlines(), cur.splitlines(), lineterm="", n=0)
                     if l[:1] in "+-" and not l.startswith(("+++", "---")) and l[1:].strip()]
            bad = [l for l in delta if not any(re.search(a, l) for a in DAYCARE_ALLOWED) and l not in ("{", "}")]
            self.rec("daycare.c delta limited to level plumbing (breeding constants/logic unchanged)", not bad, "; ".join(bad[:4]))
        for p in ("include/constants/daycare.h", "src/daycare_save.c", "include/struct_defs/daycare.h"):
            b = git_show(p)
            self.rec(f"{p} unchanged", b is None or b == self.read(p))
        self.rec("hatch-cycle / step-counter constants unchanged", all(
            (git_show(p) or "") == self.read(p) for p in ("include/constants/daycare.h",)))
        for p in sorted(glob.glob(os.path.join(ROOT, "docs/overhaul/implementation/breeding/*.json"))):
            rel = os.path.relpath(p, ROOT)
            self.rec(f"breeding manifest unchanged: {os.path.basename(rel)}", (git_show(rel) or "") == self.read(rel))

    # -- Rival branch -------------------------------------------------------------------------------------------------------------------------
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
            self.rec(f"{fn} derives from the branch, not the actual species", "SystemVars_GetPlayerStarterBranch" in b and "playerStarter" not in b)
        self.rec("SystemVars_GetPlayerStarter still returns the actual species", re.search(r"return TryGetVarValue\(varsFlags, VAR_PLAYER_STARTER\);", func_body(sv, "SystemVars_GetPlayerStarter") or "") is not None)
        branch = func_body(sv, "SystemVars_GetPlayerStarterBranch") or ""
        self.rec("branch helper is a pure function of the actual species (no new save var)", "MysteryStarter_GetRivalBranch(TryGetVarValue(varsFlags, VAR_PLAYER_STARTER))" in branch)
        legacy, branch_users, wrong = [], [], []
        for p in sorted(glob.glob(os.path.join(ROOT, "res/field/scripts/*.s"))):
            rel = os.path.relpath(p, ROOT)
            t = self.read(rel)
            if "GetPlayerStarterSpecies" in t and not rel.endswith("sandgem_town_pokemon_research_lab.s"):
                legacy.append(os.path.basename(rel))
            if "GetPlayerStarterBranch" in t:
                branch_users.append(os.path.basename(rel))
                # every comparison of the queried value must be against one of the three branch species
                for m in re.finditer(r"(GoToIfEq|CallIfEq) VAR_RESULT, (SPECIES_\w+)", t):
                    if m.group(2) not in SINNOH:
                        wrong.append(f"{os.path.basename(rel)}:{m.group(2)}")
        self.rec("no active Rival/branch script reads the actual starter species", not legacy, ",".join(legacy))
        self.rec("Sandgem lab starter-gift offers keep the actual species (later gifts unchanged)", "GetPlayerStarterSpecies VAR_0x8000" in self.read("res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s"))
        self.rec("branch consumers compare only against Turtwig/Chimchar/Piplup", not wrong, ",".join(wrong))
        expect = {"scripts_route_201.s", "scripts_route_203.s", "scripts_route_209_gate_to_hearthome_city.s", "scripts_pastoria_city.s", "scripts_canalave_city.s",
                  "scripts_pokemon_league_north_pokecenter_1f.s", "scripts_fight_area.s", "scripts_survival_area.s", "scripts_spear_pillar.s"}
        self.rec("every Rival branch point queries the branch (Route 201/203/209, Pastoria, Canalave, League, Fight Area, Survival Area, Spear Pillar)",
                 expect <= set(branch_users), ",".join(sorted(expect - set(branch_users))))
        rival_labels = [l for p in glob.glob(os.path.join(ROOT, "res/field/scripts/*.s")) for l in re.findall(r"^\w*Rival\w*:", self.read(os.path.relpath(p, ROOT)), flags=re.M)]
        dup = [l for l in rival_labels if re.search(r"Bulbasaur|Charmander|Squirtle|Pikachu|Chikorita|Cyndaquil|Totodile|Treecko|Torchic|Mudkip", l)]
        self.rec("no thirteen-way Rival duplication (no Rival label for non-Sinnoh species)", not dup, ",".join(dup))
        trainers = [t for p in glob.glob(os.path.join(ROOT, "res/field/scripts/*.s")) for t in re.findall(r"TRAINER_RIVAL_\w*(?:BULBASAUR|CHARMANDER|SQUIRTLE|PIKACHU|CHIKORITA|CYNDAQUIL|TOTODILE|TREECKO|TORCHIC|MUDKIP)\w*", self.read(os.path.relpath(p, ROOT)))]
        self.rec("no Rival trainer IDs for non-Sinnoh starters", not trainers)
        pool = {"Grass": "TURTWIG", "Fire": "CHIMCHAR", "Water": "PIPLUP"}
        self.rec("manifest declares exactly three Rival branches", self.manifest.get("rival_branch_count") == 3 and len(self.manifest["rival_branches"]) == 3 and
                 {v: k for k, v in self.manifest["rival_branches"].items()} == {k: "SPECIES_" + v for k, v in pool.items()})
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
